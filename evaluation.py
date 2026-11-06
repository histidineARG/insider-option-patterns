"""Gated fixed-rule and logistic evaluation with episode clustering."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

from exploratory_patterns import alert, valid
from research_cohort import write_rows


REQUIRED_GATES = [
    'verified_outcome_labels',
    'historical_security_identity',
    'complete_population_frame',
    'natural_prevalence_or_valid_sampling_design',
    'vendor_delivery_timing',
    'passed_coverage_audit',
]


def blocked_gates(dataset_manifest, protocol, observations):
    """Evidence gates for population metrics; descriptive interfaces stay available."""
    required = protocol.get('population_evaluation_requires', REQUIRED_GATES)
    blocked = []
    labeled = [r for r in observations if r.get('training_label') in (0, 1)]
    if not labeled or dataset_manifest.get('known_positive_labels', 0) == 0:
        blocked.append('verified_outcome_labels')
    if not any(r.get('historical_security_identity_verified') for r in observations):
        blocked.append('historical_security_identity')
    if dataset_manifest.get('research_eligible', 0) == 0:
        blocked.append('complete_population_frame')
        blocked.append('natural_prevalence_or_valid_sampling_design')
    if not any(r.get('vendor_delivery_timing_verified') for r in observations):
        blocked.append('vendor_delivery_timing')
    if not any(r.get('quote_eligibility_verified') for r in observations):
        blocked.append('passed_coverage_audit')
    if protocol.get('test_authorized') is not True:
        # Reserved test may not be consumed; development partitions remain auditable.
        pass
    return [g for g in required if g in blocked]


def logistic_features(row, names):
    volume = row.get('otm_call_volume') or 0
    mean20 = row.get('otm_mean20') or 0
    values = {
        'log1p_otm_call_volume': math.log1p(volume),
        'log1p_otm_mean20': math.log1p(mean20),
        'call_share': row.get('call_share') if row.get('call_share') is not None else 0.0,
        'top_otm_call_share': row.get('top_otm_call_share') if row.get('top_otm_call_share') is not None else 0.0,
        'zero_volume_baseline': 1.0 if row.get('zero_volume_baseline') else 0.0,
    }
    return [values[name] for name in names]


def fit_logistic(rows, names, l2=0.01, iterations=2000, learning_rate=0.1):
    """Pure-Python L2 logistic; refuses empty or single-class training sets."""
    labeled = [r for r in rows if r.get('training_label') in (0, 1) and valid(r)]
    if len({r['training_label'] for r in labeled}) < 2:
        raise ValueError('Logistic fit requires both classes among valid labeled rows')
    dim = len(names) + 1
    weights = [0.0] * dim
    for _ in range(iterations):
        grad = [0.0] * dim
        for row in labeled:
            x = [1.0] + logistic_features(row, names)
            z = sum(w * v for w, v in zip(weights, x))
            # Stable sigmoid.
            prob = 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))
            err = prob - row['training_label']
            for i, v in enumerate(x):
                grad[i] += err * v
        n = len(labeled)
        for i in range(dim):
            penalty = 0.0 if i == 0 else l2 * weights[i]
            weights[i] -= learning_rate * ((grad[i] / n) + penalty)
    return weights


def predict_proba(row, weights, names):
    x = [1.0] + logistic_features(row, names)
    z = sum(w * v for w, v in zip(weights, x))
    return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))


def alert_episodes(rows, fired, cooldown_sessions, calendar_index):
    """Collapse same-symbol alerts separated by fewer than cooldown sessions."""
    by_symbol = defaultdict(list)
    for row, hit in zip(rows, fired):
        if hit:
            by_symbol[row['symbol']].append(row)
    episodes = []
    for symbol, items in sorted(by_symbol.items()):
        items = sorted(items, key=lambda r: r['qdate'])
        current = None
        for row in items:
            idx = calendar_index[row['qdate']]
            if current is None or idx - current['last_index'] > cooldown_sessions:
                current = dict(symbol=symbol, start=row['qdate'], end=row['qdate'],
                               last_index=idx, observation_ids=[row['observation_id']],
                               outcome_event_ids=list(row.get('outcome_event_ids') or []),
                               labels=[row.get('training_label')])
                episodes.append(current)
            else:
                current['end'] = row['qdate']
                current['last_index'] = idx
                current['observation_ids'].append(row['observation_id'])
                current['outcome_event_ids'] = sorted(set(current['outcome_event_ids'] +
                                                         (row.get('outcome_event_ids') or [])))
                current['labels'].append(row.get('training_label'))
    for episode in episodes:
        labels = [x for x in episode['labels'] if x in (0, 1)]
        episode['episode_label'] = 1 if any(x == 1 for x in labels) else (0 if labels and all(x == 0 for x in labels) else None)
        del episode['labels']
        del episode['last_index']
    return episodes


def fixed_rule_diagnostics(rows, protocol, calendar_index):
    summary = []
    episode_rows = []
    for minimum_volume, multiple in protocol['fixed_rules']:
        key = f'volume_{minimum_volume}_ratio_{multiple}'
        eligible = [r for r in rows if valid(r) and r.get('purge_reason') is None
                    and r.get('partition') != 'reserved_test']
        fired = [bool(alert(r, minimum_volume, multiple)) for r in eligible]
        episodes = alert_episodes(eligible, fired, protocol['episode_cooldown_sessions'], calendar_index)
        labeled = [r for r in eligible if r.get('training_label') in (0, 1)]
        summary.append(dict(
            rule=key, min_otm_call_volume=minimum_volume, min_ratio20=multiple,
            eligible_observations=len(eligible),
            alert_observations=sum(fired),
            alert_episodes=len(episodes),
            labeled_observations=len(labeled),
            labeled_alert_observations=sum(bool(alert(r, minimum_volume, multiple)) for r in labeled),
            population_metrics_authorized=False))
        for episode in episodes:
            episode_rows.append(dict(episode, rule=key))
    return summary, episode_rows


def event_recall_stub(events, episodes):
    """Count only when event-level executable labels exist; otherwise remain null."""
    ready = [e for e in events if e.get('training_label_ready')]
    if not ready:
        return dict(eligible_events=0, events_with_timely_episode=None, recall=None)
    hit = 0
    for event in ready:
        matched = [ep for ep in episodes if event['event_id'] in ep.get('outcome_event_ids', [])]
        if matched:
            hit += 1
    return dict(eligible_events=len(ready), events_with_timely_episode=hit,
                recall=(hit / len(ready) if ready else None))


def run(root=Path('.')):
    protocol = json.loads((root/'data/evaluation_protocol.json').read_text())
    observations = json.loads((root/'results/research_dataset/observations.json').read_text())
    dataset_manifest = json.loads((root/'results/research_dataset/manifest.json').read_text())
    events = json.loads((root/'results/reviewed_cohort/events.json').read_text())
    calendar = json.loads((root/'data/calendar/nyse_sessions.json').read_text())
    calendar_index = {r['session']: i for i, r in enumerate(calendar)}
    blocked = blocked_gates(dataset_manifest, protocol, observations)
    summary, episodes = fixed_rule_diagnostics(observations, protocol, calendar_index)
    logistic_status = 'blocked_by_evidence_gates'
    logistic_weights = None
    if not blocked:
        train = [r for r in observations if r.get('partition') == 'train' and r.get('purge_reason') is None]
        logistic_weights = fit_logistic(train, protocol['logistic_features'],
                                        l2=protocol['logistic_l2'],
                                        iterations=protocol['logistic_iterations'],
                                        learning_rate=protocol['logistic_learning_rate'])
        logistic_status = 'fitted_on_train'
    folder = root/'results/evaluation'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'fixed_rule_summary', summary)
    write_rows(folder, 'alert_episodes', episodes)
    recall = event_recall_stub(events, episodes)
    manifest = dict(
        observations=len(observations),
        blocked_gates=blocked,
        population_evaluation_authorized=not blocked,
        test_authorized=bool(protocol.get('test_authorized')),
        logistic_status=logistic_status,
        logistic_weights=logistic_weights,
        event_recall=recall,
        fixed_rule_summary=summary,
        source_sha256={
            'results/research_dataset/observations.json':
                hashlib.sha256((root/'results/research_dataset/observations.json').read_bytes()).hexdigest(),
            'data/evaluation_protocol.json':
                hashlib.sha256((root/'data/evaluation_protocol.json').read_bytes()).hexdigest(),
        })
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Gated chronological evaluation', '',
             'Fixed-rule episode construction and logistic interfaces are implemented against '
             'the time-safe observation table. Population accuracy, precision, false-positive '
             'rates, and trading returns remain unauthorized while evidence gates fail.', '',
             '## Blocked gates' if blocked else '## Gates', '']
    if blocked:
        lines += [f'- {g}' for g in blocked]
    else:
        lines.append('- None; population metrics may proceed under the frozen protocol.')
    lines += ['', '## Fixed-rule episode diagnostics', '',
              '| Rule | Eligible observations | Alert observations | Alert episodes | Labeled observations |',
              '| --- | ---: | ---: | ---: | ---: |']
    for row in summary:
        lines.append(f"| {row['rule']} | {row['eligible_observations']} | {row['alert_observations']} | "
                     f"{row['alert_episodes']} | {row['labeled_observations']} |")
    lines += ['', f"Logistic status: {logistic_status}. Reserved test authorization: "
              f"{protocol.get('test_authorized')}. Event-level recall remains null until "
              'training-ready events exist.', '',
              'No threshold is selected from these diagnostics. Bootstrap clustered uncertainty '
              'and validation threshold selection stay deferred until labels and population '
              'membership pass audit.', '']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
