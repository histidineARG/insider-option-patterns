"""Stock price-action audit for reviewed cohort events.

Offline mode checks stored close-to-close arithmetic, reaction-session calendar
mapping, earlier-public contamination, and source/identity hazards.

Deep mode (--deep) requeries OHLCV windows and measures pre-announcement drift,
largest pre-jump days, gap vs close structure, volume surge context, moves on
earlier-public dates, post-announcement fade, and cash-offer premium vs reaction
close. Does not alter raw prices, flip training_label_ready, or invent disclosure
verification.
"""
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import statistics

from market_calendar import sessions
from research_cohort import write_rows


THRESHOLD_PCT = 15.0
ARITH_TOL = 1e-9
PRE_SESSIONS = 30
POST_SESSIONS = 5
DRIFT_LOOKBACKS = (1, 5, 10, 20)
LARGE_PRE_MOVE_PCT = 5.0


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
    return (float(reaction_close) / float(previous_close) - 1) * 100


def pct_change(start, end):
    if start is None or end is None or float(start) <= 0:
        return None
    return (float(end) / float(start) - 1) * 100


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


def parse_cash_offer_usd(text):
    """Extract a single USD cash offer when consideration notes state one clearly."""
    if not text:
        return None
    lowered = text.lower()
    if 'sek' in lowered or 'cash-and-stock' in lowered or 'mixed cash' in lowered:
        return None
    # Ignore deal-value language like "$1.7 billion" / "~$3B equity value".
    cleaned = re.sub(
        r'\$\s*[0-9]+(?:\.[0-9]+)?\s*(?:billion|million|[BbMm])\b',
        '', text, flags=re.I)
    per_share = re.findall(
        r'\$\s*([0-9]+(?:\.[0-9]+)?)\s*(?:per(?:\s+common)?\s+share|/share)\b',
        cleaned, flags=re.I)
    if len(per_share) == 1:
        return float(per_share[0])
    if 'cvr' in lowered:
        match = re.search(r'\$\s*([0-9]+(?:\.[0-9]+)?)', cleaned)
        return float(match.group(1)) if match else None
    matches = re.findall(r'\$\s*([0-9]+(?:\.[0-9]+)?)', cleaned)
    if len(matches) == 1:
        return float(matches[0])
    return None


def quote_rows_to_dicts(rows):
    out = []
    for r in rows:
        out.append(dict(
            qdate=str(r['qdate']),
            open=float(r['open']),
            high=float(r['high']),
            low=float(r['low']),
            close=float(r['close']),
            volume=int(r['volume']),
        ))
    return out


def session_return(quotes, day, prev_day):
    cur = quotes.get(day)
    prev = quotes.get(prev_day)
    if not cur or not prev:
        return None
    return pct_change(prev['close'], cur['close'])


def path_analysis(event, calendar, quotes):
    """Compute multi-session price-path metrics from a quote window."""
    reaction = event.get('reaction_date')
    previous = event.get('previous_session')
    by_date = {q['qdate']: q for q in quotes}
    out = dict(path_sessions=len(quotes), path_query_ok=bool(quotes))
    if reaction not in by_date or previous not in by_date:
        out['path_issues'] = ['missing_reaction_or_previous_quote']
        return out

    prev_q = by_date[previous]
    react_q = by_date[reaction]
    close_ret = pct_change(prev_q['close'], react_q['close'])
    open_gap = pct_change(prev_q['close'], react_q['open'])
    high_ret = pct_change(prev_q['close'], react_q['high'])
    low_ret = pct_change(prev_q['close'], react_q['low'])
    out.update(
        path_previous_close=prev_q['close'],
        path_reaction_open=react_q['open'],
        path_reaction_high=react_q['high'],
        path_reaction_low=react_q['low'],
        path_reaction_close=react_q['close'],
        path_reaction_volume=react_q['volume'],
        path_previous_volume=prev_q['volume'],
        path_close_return_pct=close_ret,
        path_open_gap_pct=open_gap,
        path_high_return_pct=high_ret,
        path_low_return_pct=low_ret,
        path_reaction_range_pct=pct_change(react_q['low'], react_q['high']) if react_q['low'] else None,
        path_close_vs_open_pct=pct_change(react_q['open'], react_q['close']),
    )
    if close_ret not in (None, 0):
        out['gap_share_of_close_return'] = open_gap / close_ret if open_gap is not None else None
    else:
        out['gap_share_of_close_return'] = None
    out['gap_dominated'] = bool(
        open_gap is not None and close_ret is not None and open_gap >= 0.85 * close_ret and close_ret >= THRESHOLD_PCT)

    # Pre-announcement drift ending at previous close.
    try:
        ri = calendar.index(date.fromisoformat(reaction))
    except ValueError:
        out['path_issues'] = ['reaction_not_on_calendar']
        return out
    pre_days = [str(d) for d in calendar[max(0, ri - PRE_SESSIONS):ri]]
    post_days = [str(d) for d in calendar[ri + 1:ri + 1 + POST_SESSIONS]]
    out['pre_session_count_available'] = sum(d in by_date for d in pre_days)
    out['post_session_count_available'] = sum(d in by_date for d in post_days)

    for n in DRIFT_LOOKBACKS:
        # n sessions ending at previous: calendar[ri-1-n] close → previous close.
        if ri - 1 - n < 0:
            out[f'drift_{n}d_to_previous_pct'] = None
            continue
        start = str(calendar[ri - 1 - n])
        out[f'drift_{n}d_to_previous_pct'] = (
            pct_change(by_date[start]['close'], prev_q['close']) if start in by_date else None)

    # Largest absolute close-to-close move in the 20 sessions before reaction.
    look = [str(d) for d in calendar[max(0, ri - 20):ri]]
    day_moves = []
    for i, day in enumerate(look):
        if i == 0:
            continue
        prev_day = look[i - 1]
        ret = session_return(by_date, day, prev_day)
        if ret is None:
            continue
        day_moves.append(dict(session=day, close_return_pct=ret, volume=by_date[day]['volume']))
    out['pre20_day_move_count'] = len(day_moves)
    if day_moves:
        biggest = max(day_moves, key=lambda r: abs(r['close_return_pct']))
        out['largest_abs_pre20_move_pct'] = biggest['close_return_pct']
        out['largest_abs_pre20_move_session'] = biggest['session']
        out['pre20_up_days'] = sum(r['close_return_pct'] > 0 for r in day_moves)
        out['pre20_down_days'] = sum(r['close_return_pct'] < 0 for r in day_moves)
        out['pre20_mean_abs_move_pct'] = statistics.mean(abs(r['close_return_pct']) for r in day_moves)
        out['large_pre_moves_ge_5pct'] = [
            r for r in day_moves if abs(r['close_return_pct']) >= LARGE_PRE_MOVE_PCT]
    else:
        out['largest_abs_pre20_move_pct'] = None
        out['large_pre_moves_ge_5pct'] = []

    # Volume context vs prior 20 sessions (same definition as confirmation screen).
    baseline_days = [str(d) for d in calendar[max(0, ri - 20):ri]]
    baseline_vols = [by_date[d]['volume'] for d in baseline_days if d in by_date and by_date[d]['volume'] > 0]
    out['volume_baseline_sessions'] = len(baseline_vols)
    if len(baseline_vols) == 20:
        avg = statistics.mean(baseline_vols)
        out['path_volume_avg20'] = avg
        out['path_volume_ratio20'] = react_q['volume'] / avg if avg else None
        out['path_volume_surge_2x'] = bool(out['path_volume_ratio20'] and out['path_volume_ratio20'] >= 2)
        out['path_above_max_volume20'] = react_q['volume'] > max(baseline_vols)
    else:
        out['path_volume_avg20'] = None
        out['path_volume_ratio20'] = None
        out['path_volume_surge_2x'] = None
        out['path_above_max_volume20'] = None
        out['volume_baseline_incomplete'] = True

    # Moves on earlier-public boundary dates (session close-to-close).
    earlier_moves = []
    for label, raw in (('lower', event.get('earlier_public_date_lower')),
                       ('upper', event.get('earlier_public_date_upper'))):
        if not raw:
            continue
        day = date.fromisoformat(raw)
        if day not in calendar:
            # Map nontrading disclosure dates to the next session for path inspection.
            nxt = next((d for d in calendar if d > day), None)
            earlier_moves.append(dict(
                bound=label, disclosure_date=raw, mapped_session=str(nxt) if nxt else None,
                note='disclosure_date_not_a_session'))
            day = nxt
            if day is None:
                continue
        else:
            earlier_moves.append(dict(bound=label, disclosure_date=raw, mapped_session=str(day)))
        idx = calendar.index(day)
        if idx == 0:
            continue
        prev_day = calendar[idx - 1]
        ret = session_return(by_date, str(day), str(prev_day))
        earlier_moves[-1].update(
            previous_session=str(prev_day),
            close_return_pct=ret,
            volume=by_date[str(day)]['volume'] if str(day) in by_date else None,
            open_gap_pct=(pct_change(by_date[str(prev_day)]['close'], by_date[str(day)]['open'])
                          if str(day) in by_date and str(prev_day) in by_date else None),
        )
    out['earlier_public_session_moves'] = earlier_moves

    # Post-announcement path from reaction close.
    for n, day in enumerate(post_days, start=1):
        out[f'post_{n}d_close_return_from_reaction_pct'] = (
            pct_change(react_q['close'], by_date[day]['close']) if day in by_date else None)

    # Cash offer premium vs previous and reaction closes.
    offer = parse_cash_offer_usd(event.get('consideration_notes') or '')
    out['parsed_cash_offer_usd'] = offer
    if offer and prev_q['close'] > 0:
        out['offer_premium_vs_previous_pct'] = (offer / prev_q['close'] - 1) * 100
        out['reaction_close_vs_offer_pct'] = (react_q['close'] / offer - 1) * 100
        out['reaction_close_below_offer'] = react_q['close'] < offer
    else:
        out['offer_premium_vs_previous_pct'] = None
        out['reaction_close_vs_offer_pct'] = None
        out['reaction_close_below_offer'] = None

    # Move on the previous session itself (denominator day), from the session before it.
    if ri >= 2:
        prev_prev = str(calendar[ri - 2])
        prev_session_ret = session_return(by_date, previous, prev_prev)
        out['previous_session_return_pct'] = prev_session_ret
        out['previous_session_volume'] = prev_q['volume']
    else:
        out['previous_session_return_pct'] = None

    # Path diagnostics that deepen contamination / leak interpretation.
    path_flags = []
    if out.get('drift_5d_to_previous_pct') is not None and out['drift_5d_to_previous_pct'] >= 10:
        path_flags.append('strong_5d_pre_drift_ge_10pct')
    if out.get('drift_20d_to_previous_pct') is not None and out['drift_20d_to_previous_pct'] >= 20:
        path_flags.append('strong_20d_pre_drift_ge_20pct')
    prev_ret = out.get('previous_session_return_pct')
    if prev_ret is not None and abs(prev_ret) >= LARGE_PRE_MOVE_PCT:
        path_flags.append('previous_session_abs_move_ge_5pct')
    if prev_ret is not None and prev_ret >= THRESHOLD_PCT:
        path_flags.append('previous_session_already_ge_15pct')
    if any(abs(r['close_return_pct']) >= 10 for r in out.get('large_pre_moves_ge_5pct', [])
           if r['session'] != reaction):
        path_flags.append('ge_10pct_single_day_move_in_pre20')
    for move in earlier_moves:
        # Same-calendar-day earlier disclosure is the reaction session itself.
        if move.get('mapped_session') == reaction:
            continue
        ret = move.get('close_return_pct')
        if ret is None and move.get('mapped_session'):
            path_flags.append(f"earlier_public_{move['bound']}_quote_missing_in_window")
        elif ret is not None and ret >= THRESHOLD_PCT:
            path_flags.append(f"earlier_public_{move['bound']}_session_also_ge_15pct")
        elif ret is not None and abs(ret) >= LARGE_PRE_MOVE_PCT:
            path_flags.append(f"earlier_public_{move['bound']}_session_abs_ge_5pct")
    if out.get('gap_dominated'):
        path_flags.append('reaction_mostly_overnight_gap')
    if out.get('path_volume_surge_2x') is False:
        path_flags.append('no_2x_volume_surge')
    if out.get('reaction_close_below_offer') is False and offer:
        path_flags.append('reaction_close_at_or_above_cash_offer')
    out['path_flags'] = path_flags
    return out


def evaluate(event, calendar, quotes=None):
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
        stored_open_gap_pct=event.get('open_gap_pct'),
        stored_high_return_pct=event.get('high_return_pct'),
        stored_volume_ratio20=event.get('volume_ratio20'),
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
    if quotes is not None:
        path = path_analysis(event, calendar, quotes)
        row.update(path)
        # Reconcile stored reaction metrics against requeryed path.
        if path.get('path_close_return_pct') is not None and calc is not None:
            if abs(path['path_close_return_pct'] - calc) > 1e-6:
                row['issues'] = list(row['issues']) + ['stored_vs_path_return_mismatch']
                row['measurement_ok'] = False
                row['price_action_status'] = 'measurement_failed'
    return row


def notes_for(row):
    parts = [f"status={row['price_action_status']}"]
    if row.get('recomputed_close_return_pct') is not None:
        parts.append(f"close_return={row['recomputed_close_return_pct']:.2f}%")
    if row.get('path_open_gap_pct') is not None:
        parts.append(f"open_gap={row['path_open_gap_pct']:.2f}%")
    if row.get('drift_5d_to_previous_pct') is not None:
        parts.append(f"drift5d={row['drift_5d_to_previous_pct']:.2f}%")
    if row.get('drift_20d_to_previous_pct') is not None:
        parts.append(f"drift20d={row['drift_20d_to_previous_pct']:.2f}%")
    if row.get('path_volume_ratio20') is not None:
        parts.append(f"vol20={row['path_volume_ratio20']:.2f}x")
    if row.get('offer_premium_vs_previous_pct') is not None:
        parts.append(f"offer_prem={row['offer_premium_vs_previous_pct']:.2f}%")
    if row.get('contamination_flags'):
        parts.append('contamination=' + ','.join(row['contamination_flags']))
    if row.get('path_flags'):
        parts.append('path=' + ','.join(row['path_flags']))
    if row.get('hazards'):
        parts.append('hazards=' + ','.join(row['hazards']))
    if row.get('issues'):
        parts.append('issues=' + ','.join(row['issues']))
    return '; '.join(parts)


def fetch_window(cursor, symbol, start, end):
    cursor.execute(
        'SELECT qdate,open,high,low,close,volume FROM stockquote '
        'WHERE symbol=%s AND qdate BETWEEN %s AND %s ORDER BY qdate',
        (symbol, start, end))
    return quote_rows_to_dicts(cursor.fetchall())


def write_report(folder, rows, manifest):
    lines = [
        '# Stock price-action vetting', '',
        f"{manifest['events']} events audited. {manifest['measurement_ok']} have consistent "
        f"arithmetic and reaction-session mapping; {manifest['jump_ok']} recompute to "
        f"≥{THRESHOLD_PCT:g}% close-to-close.",
        '',
    ]
    if manifest.get('deep'):
        lines += [
            'Deep mode requeries OHLCV around each event and reports pre-announcement drift, '
            'gap structure, volume context, earlier-public session moves, post-move fade, and '
            'cash-offer premium comparisons. Prices are not rewritten; labels stay unauthorized.',
            '',
            '| Event | Close | Gap | 5d drift | 20d drift | Vol20 | Offer prem | Status | Path flags |',
            '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |',
        ]
        for r in sorted(rows, key=lambda x: x['announcement_date']):
            def fmt(key, digits=2, suffix='%'):
                v = r.get(key)
                return 'n/a' if v is None else f"{v:.{digits}f}{suffix}"
            vol = r.get('path_volume_ratio20')
            vol_s = 'n/a' if vol is None else f"{vol:.2f}x"
            flags = ', '.join(r.get('path_flags') or []) or 'none'
            lines.append(
                f"| {r['event_id']} | {fmt('recomputed_close_return_pct')} | "
                f"{fmt('path_open_gap_pct')} | {fmt('drift_5d_to_previous_pct')} | "
                f"{fmt('drift_20d_to_previous_pct')} | {vol_s} | "
                f"{fmt('offer_premium_vs_previous_pct')} | {r['price_action_status']} | {flags} |")
    else:
        lines += [
            'Offline mode uses stored closes only.',
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
        'Contamination / hazard statuses describe disclosure and identity interpretation. '
        'Path flags are additional price-series diagnostics and do not invent training labels.',
        '',
    ]
    (folder / 'REPORT.md').write_text('\n'.join(lines))


def run(root=Path('.'), deep=False, connection_factory=None):
    calendar = sessions(root=root)
    events = json.loads((root / 'results/reviewed_cohort/events.json').read_text())
    rows = []
    windows = []
    if deep:
        from sec_match import connection as default_connection
        factory = connection_factory or default_connection
        with factory() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
                cursor.execute('START TRANSACTION READ ONLY')
                try:
                    for event in events:
                        reaction = date.fromisoformat(event['reaction_date'])
                        try:
                            ri = calendar.index(reaction)
                        except ValueError:
                            row = evaluate(event, calendar, quotes=[])
                            row['issues'] = list(row.get('issues') or []) + ['reaction_not_on_calendar']
                            rows.append(row)
                            continue
                        start = calendar[max(0, ri - PRE_SESSIONS)]
                        end = calendar[min(len(calendar) - 1, ri + POST_SESSIONS)]
                        # Extend the window to cover known earlier-public dates when present.
                        for raw in (event.get('earlier_public_date_lower'),
                                    event.get('earlier_public_date_upper')):
                            if not raw:
                                continue
                            day = date.fromisoformat(raw)
                            if day < start:
                                # Include one prior session for close-to-close on that day.
                                prior = next((d for d in reversed(calendar) if d < day), None)
                                start = prior or day
                            if day > end:
                                end = day
                        quotes = fetch_window(cursor, event['symbol'], start, end)
                        windows.append(dict(
                            event_id=event['event_id'], symbol=event['symbol'],
                            window_start=str(start), window_end=str(end), quotes=quotes))
                        rows.append(evaluate(event, calendar, quotes=quotes))
                finally:
                    conn.rollback()
    else:
        rows = [evaluate(event, calendar) for event in events]

    folder = root / 'results/price_action_vet'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'checks', rows)
    if deep:
        (folder / 'windows.json').write_text(json.dumps(windows, indent=2) + '\n')
    path_flag_counts = dict(Counter(f for r in rows for f in r.get('path_flags') or []))
    manifest = dict(
        events=len(rows),
        deep=bool(deep),
        measurement_ok=sum(r['measurement_ok'] for r in rows),
        jump_ok=sum(r['jump_ok'] for r in rows),
        status_counts=dict(Counter(r['price_action_status'] for r in rows)),
        contamination_flag_counts=dict(Counter(
            f for r in rows for f in r['contamination_flags'])),
        hazard_counts=dict(Counter(h for r in rows for h in r['hazards'])),
        path_flag_counts=path_flag_counts,
        gap_dominated=sum(bool(r.get('gap_dominated')) for r in rows),
        volume_surge_2x=sum(bool(r.get('path_volume_surge_2x')) for r in rows),
        offer_parsed=sum(r.get('parsed_cash_offer_usd') is not None for r in rows),
        source_sha256={
            'results/reviewed_cohort/events.json':
                hashlib.sha256((root / 'results/reviewed_cohort/events.json').read_bytes()).hexdigest(),
            'data/calendar/nyse_sessions.json':
                hashlib.sha256((root / 'data/calendar/nyse_sessions.json').read_bytes()).hexdigest(),
        },
        notes=[
            'Deep mode requeries stockquote OHLCV; offline mode does not.',
            'Contamination flags describe earlier-public intersection with the jump window.',
            'Path flags are diagnostics only; they do not invent negatives or training labels.',
            'This tool does not set training_label_ready or first_public_disclosure_verified.',
        ],
    )
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    write_report(folder, rows, manifest)
    return manifest


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deep', action='store_true',
                        help='Requery OHLCV windows and compute path metrics')
    args = parser.parse_args()
    print(json.dumps(run(deep=args.deep), indent=2))
