"""Build explicit horizon labels and purged partitions without inventing negatives."""
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path

from exploratory_patterns import valid
from research_cohort import write_rows


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Disclosure timestamps must include a timezone')
    return result.astimezone(timezone.utc)


def calendar_rows(root):
    from market_calendar import sessions
    # Verify the versioned checksum before loading its timestamp columns.
    sessions(root=root)
    return json.loads((root/'data/calendar/nyse_sessions.json').read_text())


def disclosure_status(event, signal_day, entry_day):
    """Conservative date-only contamination; absence of a finding is unknown."""
    lower = event.get('earlier_public_date_lower')
    upper = event.get('earlier_public_date_upper')
    if lower and signal_day >= lower:
        return 'at_or_after_known_earlier_disclosure_boundary'
    if lower and entry_day and entry_day >= lower:
        return 'entry_proxy_not_strictly_before_earlier_disclosure_date'
    if upper and not lower:
        return 'earlier_public_process_start_unresolved'
    if event.get('first_public_disclosure_verified'):
        return 'verified_disclosure_review'
    return 'first_disclosure_review_pending'


def assign_label(row, events, reviews):
    """Positives need reviewed events; zero needs a complete scoped outcome review."""
    if not row['outcome_window_complete']:
        return None, [], 'insufficient_calendar_or_followup'
    signal = utc(row['feature_close_utc'])
    finish = utc(row['outcome_end_utc'])
    entry = utc(row['entry_close_proxy_utc'])
    matches, not_executable = [], []
    unresolved = False
    for event in events:
        if event['symbol'] != row['symbol']:
            continue
        if not (event.get('training_label_ready') and event.get('first_public_disclosure_verified')
                and event.get('corporate_action_review_complete')
                and event.get('price_jump_at_least_15pct')):
            # An unreviewed candidate inside this interval prevents a certified zero.
            if row['qdate'] <= event['announcement_date'] <= row['outcome_end']:
                unresolved = True
            continue
        lower = event.get('first_public_lower_utc')
        upper = event.get('first_public_upper_utc')
        if not lower or not upper:
            unresolved = True
            continue
        low, high = utc(lower), utc(upper)
        if low > high:
            raise ValueError('Reversed disclosure interval')
        if high <= signal or low > finish:
            continue
        if not (signal < low and high <= finish):
            unresolved = True
            continue
        if entry < low:
            matches.append(event['event_id'])
        else:
            not_executable.append(event['event_id'])
    if matches:
        return 1, sorted(set(matches)), 'verified_executable_positive'
    if not_executable:
        return None, sorted(set(not_executable)), 'announcement_before_entry_proxy'
    if unresolved:
        return None, [], 'candidate_or_disclosure_review_unresolved'
    for review in reviews:
        if (review.get('symbol') == row['symbol'] and review.get('complete') is True
                and review.get('source') and review.get('locator')
                and review.get('security_identity_verified') is True
                and review.get('start_utc') and review.get('end_utc')
                and utc(review['start_utc']) <= signal and finish <= utc(review['end_utc'])):
            return 0, [], 'negative_from_complete_scoped_outcome_review'
    return None, [], 'incomplete_outcome_registry'


def partition_rows(rows, partitions):
    event_partitions = defaultdict(set)
    for row in rows:
        partition = next((p for p in partitions if p['start'] <= row['qdate'] <= p['end']), None)
        row['partition'] = partition['name'] if partition else 'outside_protocol'
        row['purge_reason'] = None
        if partition and (row['feature_start'] is None or row['outcome_end'] is None or
                          row['feature_start'] < partition['start'] or row['outcome_end'] > partition['end']):
            row['purge_reason'] = 'feature_or_outcome_window_crosses_partition'
        for event in set(row['context_event_ids'] + row['outcome_event_ids']):
            event_partitions[event].add(row['partition'])
    crossing = {event for event, parts in event_partitions.items() if len(parts) > 1}
    for row in rows:
        if crossing.intersection(row['context_event_ids'] + row['outcome_event_ids']):
            row['purge_reason'] = 'event_spans_partitions'
    return rows


def build(event_features, background, events, calendar, protocol, reviews, followup_end):
    positions = {r['session']: i for i, r in enumerate(calendar)}
    event_map = {r['event_id']: r for r in events}
    merged = {}
    for source, observations in [('event', event_features), ('background', background)]:
        for item in observations:
            key = item['symbol'], item['qdate']
            context = item.get('event_id')
            if key not in merged:
                merged[key] = dict(item, sample_sources=[], context_event_ids=[])
            row = merged[key]
            # A repeated stock-day must not silently combine different feature values.
            for name in ('chain_observed', 'otm_call_volume', 'otm_mean20', 'volume_data_valid'):
                if name in item and name in row and item[name] != row[name]:
                    raise ValueError(f'Conflicting feature snapshot for {key}: {name}')
            if source not in row['sample_sources']:
                row['sample_sources'].append(source)
            if context and context not in row['context_event_ids']:
                row['context_event_ids'].append(context)
    output = []
    for key, original in sorted(merged.items()):
        row = dict(original)
        i = positions[row['qdate']]
        end = i + protocol['prediction_horizon_sessions']
        baseline = i - protocol['baseline_sessions']
        last = calendar[end] if end < len(calendar) else None
        next_day = calendar[i+1] if i+1 < len(calendar) else None
        row.update(observation_id=f'{key[0]}:{key[1]}',
                   feature_start=calendar[baseline]['session'] if baseline >= 0 else None,
                   feature_end=row['qdate'], feature_close_utc=calendar[i]['market_close_utc'],
                   outcome_start=next_day['session'] if next_day else None,
                   outcome_end=last['session'] if last else None,
                   outcome_end_utc=last['market_close_utc'] if last else None,
                   entry_close_proxy_utc=next_day['market_close_utc'] if next_day else None,
                   outcome_window_complete=bool(last and last['session'] <= followup_end),
                   feature_coverage_ready=valid(row),
                   historical_security_identity_verified=False,
                   vendor_delivery_timing_verified=False,
                   quote_eligibility_verified=False)
        row['disclosure_diagnostics'] = {
            eid: disclosure_status(event_map[eid], row['qdate'], next_day['session'] if next_day else None)
            for eid in row['context_event_ids']}
        row['training_label'], row['outcome_event_ids'], row['label_status'] = assign_label(row, events, reviews)
        row['research_eligible'] = False  # Identity, delivery timing, and tradability are unverified.
        output.append(row)
    return partition_rows(output, protocol['partitions'])


def run(root=Path('.')):
    paths = dict(event_features='results/reviewed_cohort/features.json',
                 background='results/background_sample/observations.json',
                 events='results/reviewed_cohort/events.json',
                 protocol='data/evaluation_protocol.json', reviews='data/outcome_coverage_reviews.json')
    loaded = {k: json.loads((root/p).read_text()) for k, p in paths.items()}
    # A complete calendar is not evidence of complete outcome follow-up.
    followup_end = max((r['announcement_date'] for r in loaded['events']), default='2012-01-01')
    rows = build(loaded['event_features'], loaded['background'], loaded['events'],
                 calendar_rows(root), loaded['protocol'], loaded['reviews']['reviews'], followup_end)
    folder = root/'results/research_dataset'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'observations', rows)
    manifest = dict(observations=len(rows), outcome_followup_proxy=followup_end,
                    label_status_counts=dict(Counter(r['label_status'] for r in rows)),
                    partition_counts=dict(Counter(r['partition'] for r in rows)),
                    purge_reason_counts=dict(Counter(r['purge_reason'] for r in rows if r['purge_reason'])),
                    feature_coverage_ready=sum(r['feature_coverage_ready'] for r in rows),
                    research_eligible=sum(r['research_eligible'] for r in rows),
                    known_positive_labels=sum(r['training_label'] == 1 for r in rows),
                    known_negative_labels=sum(r['training_label'] == 0 for r in rows),
                    source_sha256={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths.values()},
                    gates=['Incomplete first-disclosure, corporate-action, and security identity review.',
                           'No complete scoped outcome reviews certify negatives.',
                           'No verified natural-prevalence historical optionable frame.',
                           'Vendor delivery timing and contract deliverables remain unverified.',
                           'Reserved 2026 test has no extracted observations and is not authorized.'])
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Time-safe observation and label audit', '',
             f"{len(rows)} distinct stock-days; {manifest['known_positive_labels']} verified positives, "
             f"{manifest['known_negative_labels']} certified negatives. Unknown labels remain null.", '',
             'Feature history is the preceding 20 exchange sessions. Outcomes run after the '
             'feature close through the close of the tenth subsequent exchange session. Entry '
             'uses the next-session close as a conservative timing proxy, never an asserted fill.', '',
             'Partitions and purge rules are frozen in data/evaluation_protocol.json. '
             '2023–2025 is a previously explored development audit, not an untouched test. '
             'Calendar availability does not certify event follow-up.', '',
             '## Outstanding evidence gates', '', *['- '+g for g in manifest['gates']], '',
             'No model accuracy or trading performance is inferred from this artifact. '
             'Disclosure diagnostics identify known contamination or unresolved chronology '
             'without asserting that earlier public information was absent.', '']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
