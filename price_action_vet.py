"""Offline stock price-action audit for reviewed cohort events.

Checks close-to-close arithmetic, reaction-session calendar mapping, earlier-public
contamination of the measured window, and known source/identity hazards. Does not
alter prices, flip training_label_ready, or invent disclosure verification.
"""
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re

from market_calendar import sessions
from research_cohort import write_rows


THRESHOLD_PCT = 15.0
ARITH_TOL = 1e-9


def expected_sessions(announcement_date, announcement_session, calendar):
    event = date.fromisoformat(announcement_date)
    after = announcement_session == 'after_close'
    reaction = next(d for d in calendar if d > event or (d == event and not after))
    previous = calendar[calendar.index(reaction) - 1]
    return str(reaction), str(previous)


def recomputed_return(previous_close, reaction_close):
    if previous_close is None or reaction_close is None:
        return None
    if previous_close <= 0 or reaction_close <= 0:
        return None
    return (reaction_close / previous_close - 1) * 100


def earlier_public_flags(event):
    """Classify how earlier-public dates intersect the measured jump window."""
    flags = []
    lo = event.get('earlier_public_date_lower')
    hi = event.get('earlier_public_date_upper')
    previous = event.get('previous_session')
    reaction = event.get('reaction_date')
    if lo and previous and lo == previous:
        flags.append('earlier_public_on_previous_session')
    elif lo and previous and lo < previous:
        flags.append('earlier_public_strictly_before_previous_session')
    if lo and previous and reaction and previous < lo < reaction:
        flags.append('earlier_public_between_previous_and_reaction')
    if lo and reaction and lo == reaction:
        flags.append('earlier_public_same_calendar_day_as_reaction')
    if hi and not lo and previous and hi <= previous:
        flags.append('unresolved_earlier_process_on_or_before_previous_session')
    return flags


def status_hazards(event):
    """Hazards from review status / finding fields that affect price interpretation."""
    hazards = []
    status = event.get('review_status') or ''
    notes = event.get('share_class_notes') or ''
    if 'price_source_conflict' in status:
        hazards.append('price_source_conflict')
    # Require a real ADS mention; reject phrases like "not ADS".
    ads_noted = 'ads_terms' in status
    if not ads_noted:
        for match in re.finditer(r'\bADSs?\b', notes, flags=re.I):
            prefix = notes[max(0, match.start() - 4):match.start()].lower()
            if prefix.endswith('not '):
                continue
            ads_noted = True
            break
    if ads_noted:
        hazards.append('ads_or_ordinary_share_comparison_hazard')
    if 'identity_corrected' in status:
        hazards.append('issuer_identity_was_corrected')
    finding = (event.get('finding') or '').lower()
    if '26.40' in finding or 'price-source conflict' in finding:
        if 'price_source_conflict' not in hazards:
            hazards.append('price_source_conflict')
    return hazards


def classify(flags, hazards, measurement_ok, jump_ok):
    if not measurement_ok:
        return 'measurement_failed'
    if not jump_ok:
        return 'below_threshold_or_unmeasurable'
    if 'earlier_public_on_previous_session' in flags:
        return 'jump_ok_prior_close_may_reflect_earlier_public'
    if 'earlier_public_between_previous_and_reaction' in flags:
        return 'jump_ok_gap_may_include_earlier_public'
    if 'earlier_public_same_calendar_day_as_reaction' in flags:
        return 'jump_ok_same_day_earlier_disclosure'
    if 'earlier_public_strictly_before_previous_session' in flags:
        return 'jump_ok_earlier_public_before_measured_window'
    if 'unresolved_earlier_process_on_or_before_previous_session' in flags:
        return 'jump_ok_prior_process_unresolved'
    if 'price_source_conflict' in hazards:
        return 'jump_ok_price_source_conflict'
    if 'ads_or_ordinary_share_comparison_hazard' in hazards:
        return 'jump_ok_ads_security'
    return 'jump_ok'


def evaluate(event, calendar):
    row = dict(
        event_id=event.get('event_id') or f"{event['symbol']}:{event['announcement_date']}",
        symbol=event['symbol'],
        announcement_date=event['announcement_date'],
        announcement_session=event.get('announcement_session'),
        stored_reaction_date=event.get('reaction_date'),
        stored_previous_session=event.get('previous_session'),
        previous_close=event.get('previous_close'),
        reaction_close=event.get('reaction_close'),
        stored_close_return_pct=event.get('close_return_pct'),
        stored_jump_flag=event.get('price_jump_at_least_15pct'),
        review_status=event.get('review_status'),
    )
    issues = []
    session = event.get('announcement_session')
    if session not in ('before_open', 'intraday', 'after_close', 'nontrading_day'):
        issues.append(f'unusable_announcement_session:{session}')
        expected_reaction = expected_previous = None
    else:
        expected_reaction, expected_previous = expected_sessions(
            event['announcement_date'], session, calendar)
        row['expected_reaction_date'] = expected_reaction
        row['expected_previous_session'] = expected_previous
        if event.get('reaction_date') != expected_reaction:
            issues.append('reaction_date_mismatch')
        if event.get('previous_session') != expected_previous:
            issues.append('previous_session_mismatch')

    calc = recomputed_return(event.get('previous_close'), event.get('reaction_close'))
    row['recomputed_close_return_pct'] = calc
    if calc is None:
        issues.append('missing_or_invalid_closes')
    else:
        stored = event.get('close_return_pct')
        if stored is None or abs(calc - stored) > ARITH_TOL:
            issues.append('close_return_arithmetic_mismatch')
        jump = calc >= THRESHOLD_PCT
        row['recomputed_jump_at_least_15pct'] = jump
        if bool(event.get('price_jump_at_least_15pct')) != jump:
            issues.append('jump_flag_inconsistent_with_return')

    flags = earlier_public_flags(event)
    hazards = status_hazards(event)
    # Deduplicate while preserving order.
    hazards = list(dict.fromkeys(hazards))
    measurement_ok = not any(
        i.startswith('unusable_') or i in (
            'reaction_date_mismatch', 'previous_session_mismatch',
            'missing_or_invalid_closes', 'close_return_arithmetic_mismatch',
            'jump_flag_inconsistent_with_return')
        for i in issues)
    jump_ok = bool(row.get('recomputed_jump_at_least_15pct'))
    status = classify(flags, hazards, measurement_ok, jump_ok)
    row.update(
        contamination_flags=flags,
        hazards=hazards,
        issues=issues,
        price_action_status=status,
        measurement_ok=measurement_ok,
        jump_ok=jump_ok,
        earlier_public_date_lower=event.get('earlier_public_date_lower'),
        earlier_public_date_upper=event.get('earlier_public_date_upper'),
    )
    return row


def notes_for(row):
    parts = [f"status={row['price_action_status']}"]
    if row.get('recomputed_close_return_pct') is not None:
        parts.append(f"close_return={row['recomputed_close_return_pct']:.2f}%")
    if row['contamination_flags']:
        parts.append('contamination=' + ','.join(row['contamination_flags']))
    if row['hazards']:
        parts.append('hazards=' + ','.join(row['hazards']))
    if row['issues']:
        parts.append('issues=' + ','.join(row['issues']))
    return '; '.join(parts)


def run(root=Path('.')):
    calendar = sessions(root=root)
    events = json.loads((root / 'results/reviewed_cohort/events.json').read_text())
    rows = [evaluate(event, calendar) for event in events]
    folder = root / 'results/price_action_vet'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'checks', rows)
    status_counts = dict(Counter(r['price_action_status'] for r in rows))
    manifest = dict(
        events=len(rows),
        measurement_ok=sum(r['measurement_ok'] for r in rows),
        jump_ok=sum(r['jump_ok'] for r in rows),
        status_counts=status_counts,
        contamination_flag_counts=dict(Counter(
            f for r in rows for f in r['contamination_flags'])),
        hazard_counts=dict(Counter(h for r in rows for h in r['hazards'])),
        source_sha256={
            'results/reviewed_cohort/events.json':
                hashlib.sha256((root / 'results/reviewed_cohort/events.json').read_bytes()).hexdigest(),
            'data/calendar/nyse_sessions.json':
                hashlib.sha256((root / 'data/calendar/nyse_sessions.json').read_bytes()).hexdigest(),
        },
        notes=[
            'Offline audit of stored closes and session mapping; prices were not requeryed.',
            'Contamination flags describe earlier-public intersection with the jump window.',
            'Hazards (ADS, price-source conflict, identity correction) do not invent negatives.',
            'This tool does not set training_label_ready or first_public_disclosure_verified.',
        ],
    )
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = [
        '# Stock price-action vetting', '',
        f"{manifest['events']} events audited offline from stored closes and the NYSE calendar "
        f"snapshot. {manifest['measurement_ok']} have consistent arithmetic and reaction-session "
        f"mapping; {manifest['jump_ok']} recompute to ≥{THRESHOLD_PCT:g}% close-to-close.",
        '',
        'Contamination of the measured window and source/identity hazards are reported separately. '
        'They do not rewrite prices or authorize training labels.',
        '',
        '| Event | Return | Status | Flags / hazards |',
        '| --- | ---: | --- | --- |',
    ]
    for r in sorted(rows, key=lambda x: x['announcement_date']):
        ret = (f"{r['recomputed_close_return_pct']:.2f}%"
               if r.get('recomputed_close_return_pct') is not None else 'n/a')
        extras = ', '.join(r['contamination_flags'] + r['hazards'] + r['issues']) or 'none'
        lines.append(f"| {r['event_id']} | {ret} | {r['price_action_status']} | {extras} |")
    lines += [
        '',
        'Status meanings: `jump_ok` is clean measurement; '
        '`jump_ok_prior_close_may_reflect_earlier_public` means earlier public falls on the '
        'previous session used as the jump denominator; '
        '`jump_ok_earlier_public_before_measured_window` means an earlier episode before that '
        'previous close (announcement-day jump math can still hold); '
        '`jump_ok_same_day_earlier_disclosure` means an earlier report on the reaction date; '
        '`jump_ok_prior_process_unresolved` means an older public process/rumor upper bound only; '
        '`jump_ok_price_source_conflict` / `jump_ok_ads_security` preserve interpretation hazards '
        'without invalidating the local close-to-close math.',
        '',
    ]
    (folder / 'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
