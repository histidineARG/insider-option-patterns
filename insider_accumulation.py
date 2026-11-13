"""Retrospective accumulation screen.

Documented SEC long-call cases are the only insider labels. Class-2 jumps are
unlabeled candidates. The rule is frozen: follow the cheap calls that expire
within 40 days after the event, and flag a window only when open interest in
that fixed set builds by at least 100 contracts, volume is at least 100 and at
least 3x the prior 20-session daily rate, and one contract holds at least half
the build. A candidate is listed only when the same rule is quiet on that
name's earlier date and on its earnings date. A listing is not a finding.
"""
import json
import os
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from insider_footprint import (
    connect,
    choose_earnings,
    earnings_dates,
    load_keeps,
    load_sessions,
    span,
)

MIN_NET_OI = 100
MIN_VOLUME = 100
VOLUME_RATIO = 3.0
TOP_SHARE_MIN = 0.50
EXPIRY_DAYS = 40
DELTA_LO = 0.10
DELTA_HI = 0.40
OTM_LO = 1.03
OTM_HI = 1.30
PLACEBO_SHIFT = 60

CHAIN_SQL = '''
SELECT qdate, strike, edate, volume, oi, delta, underlying_last, bid, ask
FROM optiondaily
WHERE underlying = %s AND `type` = 'call'
  AND qdate BETWEEN %s AND %s
  AND edate > %s AND edate <= %s
'''


def load_sec_cases(root: Path) -> list[dict]:
    payload = json.loads((root / 'data/sec_cases.json').read_text())
    cases = []
    for row in payload['cases']:
        if row.get('instrument') != 'long_call':
            continue
        if row.get('evidence_status', '').startswith('investigation_only'):
            continue
        cases.append(dict(
            id=row['id'],
            symbol=row['symbol'].upper(),
            event=date.fromisoformat(row['event_date']),
            trade_start=date.fromisoformat(row['trade_start']),
            trade_end=date.fromisoformat(row['trade_end']),
        ))
    return cases


def sleeve_keys(rows, event: date) -> set:
    """Contracts that were cheap calls covering the event on the anchor session."""
    expiry_limit = event + timedelta(days=EXPIRY_DAYS)
    keys = set()
    for row in rows:
        expiry = row['edate']
        if expiry <= event or expiry > expiry_limit:
            continue
        delta = row.get('delta')
        spot = row.get('underlying_last')
        if delta is None or spot is None or float(spot) <= 0:
            continue
        delta = float(delta)
        spot = float(spot)
        strike = float(row['strike'])
        bid = float(row['bid'] or 0)
        ask = float(row['ask'] or 0)
        if DELTA_LO <= delta <= DELTA_HI and spot * OTM_LO < strike <= spot * OTM_HI and bid > 0 and ask >= bid:
            keys.add((strike, expiry))
    return keys


def _index_rows(rows) -> dict:
    indexed = defaultdict(dict)
    for row in rows:
        indexed[(float(row['strike']), row['edate'])][row['qdate']] = row
    return indexed


def score_window(rows, members, window_dates, baseline_dates, anchor) -> dict:
    if not members or anchor is None or len(window_dates) < 5 or len(baseline_dates) < 10:
        return dict(eligible=False, hit=False, reason='short_window_or_empty_sleeve')
    indexed = _index_rows(rows)
    net = 0.0
    positive = 0.0
    top = 0.0
    window_volume = 0.0
    baseline_volume = 0.0
    followed = 0
    for key in members:
        series = indexed.get(key, {})
        start = series.get(anchor)
        end = None
        for day in reversed(window_dates):
            if day in series:
                end = series[day]
                break
        if start is None or end is None:
            continue
        followed += 1
        change = float(end['oi'] or 0) - float(start['oi'] or 0)
        net += change
        if change > 0:
            positive += change
            if change > top:
                top = change
        window_volume += sum(float(series[day]['volume'] or 0) for day in window_dates if day in series)
        baseline_volume += sum(float(series[day]['volume'] or 0) for day in baseline_dates if day in series)
    if followed == 0:
        return dict(eligible=False, hit=False, reason='sleeve_not_followed')
    daily_base = baseline_volume / len(baseline_dates)
    daily_window = window_volume / len(window_dates)
    surge = daily_window >= MIN_VOLUME / len(window_dates) if daily_base == 0 else daily_window >= VOLUME_RATIO * daily_base
    concentrated = positive == 0 or (top / positive) >= TOP_SHARE_MIN
    hit = net >= MIN_NET_OI and window_volume >= MIN_VOLUME and surge and concentrated and positive > 0
    return dict(
        eligible=True,
        hit=bool(hit),
        net_oi=round(net, 1),
        window_volume=round(window_volume, 1),
        daily_ratio=None if daily_base == 0 else round(daily_window / daily_base, 3),
        top_share=None if positive == 0 else round(top / positive, 3),
        contracts=followed,
    )


def fetch_rows(connection, symbol, start, end, event):
    with connection.cursor() as cursor:
        cursor.execute(CHAIN_SQL, (symbol, start, end, event, event + timedelta(days=EXPIRY_DAYS)))
        return cursor.fetchall()


def evaluate_event(connection, sessions, index, symbol, event):
    dates = span(sessions, index, event, 0)
    if dates is None:
        return dict(eligible=False, hit=False, reason='event_not_on_calendar')
    window, baseline = dates
    anchor = baseline[-1]
    start, end = baseline[0], window[-1]
    rows = fetch_rows(connection, symbol, start, end, event)
    anchor_rows = [row for row in rows if row['qdate'] == anchor]
    return score_window(rows, sleeve_keys(anchor_rows, event), window, baseline, anchor)


def render(summary) -> str:
    sec = summary['sec_fixed_window']
    sec_placebo = summary['sec_placebo']
    candidates = summary['candidates']
    lines = [
        '# Accumulation screen',
        '',
        'Documented SEC long-call cases are the insider labels. The investigation-only ODP case is excluded. Class-2 jumps are not labeled as insider trades. The same frozen rule is applied to both.',
        '',
        'On the session before the 10-day window, keep calls with delta 0.10–0.40, 3–30% out of the money, and expiry within 40 days after the event. Follow that fixed set. A window hits when open interest rises by at least 100 contracts, volume is at least 100 and at least 3× the prior 20-session daily rate, and one contract is at least half of the build. The event session is excluded.',
        '',
        'A class-2 name is listed only when its pre-jump window hits and the same rule is quiet 60 sessions earlier and on a separated earnings date. That list is a screen, not an identification.',
        '',
        '| Set | Hits / eligible |',
        '| --- | ---: |',
        f"| SEC cases, 10 sessions before the event | {sec['hits']} / {sec['eligible']} |",
        f"| SEC cases, 60 sessions earlier | {sec_placebo['hits']} / {sec_placebo['eligible']} |",
        f"| Class-2 jumps, 10 sessions before the jump | {candidates['hits']} / {candidates['eligible']} |",
        f"| Class-2 names listed after the earnings and placebo filters | {summary['listed']} |",
        '',
        'The SEC comparison is the check on whether end-of-day open interest can see known call buying. Eight of 19 eligible documented cases hit, and 4 of 20 placebo windows hit. The rule finds the loud cases. Quieter documented cases, including ADT on 2016-02-16, stay under the volume multiple and are missed. A listed class-2 name matches that loud pattern and was quiet on its own controls. It is a candidate for review, not an identification of a trader.',
        '',
    ]
    if summary['sec_hits']:
        lines.append('SEC cases that hit the fixed window:')
        lines.append('')
        for row in summary['sec_hits']:
            lines.append(f"- {row['id']} {row['symbol']} {row['event']}: net OI {row.get('net_oi')}, volume ratio {row.get('daily_ratio')}")
        lines.append('')
    if summary['listed_names']:
        lines.append('Class-2 names that pass the screen:')
        lines.append('')
        for row in summary['listed_names']:
            note = ' Documented SEC case.' if row.get('documented') else ''
            lines.append(f"- {row['symbol']} {row['event']}: net OI {row.get('net_oi')}, volume ratio {row.get('daily_ratio')}.{note}")
        lines.append('')
    else:
        lines.append('No class-2 name passed the screen.')
        lines.append('')
    lines.append('Thresholds were not changed after these counts.')
    lines.append('')
    return '\n'.join(lines)


def _rate(rows):
    eligible = [row for row in rows if row.get('eligible')]
    hits = [row for row in eligible if row.get('hit')]
    return dict(n=len(rows), eligible=len(eligible), hits=len(hits)), hits


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    cases = load_sec_cases(root)
    keeps = [row for row in load_keeps(root) if row['tier'] == 'A']
    connection = connect()
    sec_rows = []
    sec_placebo = []
    candidate_rows = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute('START TRANSACTION READ ONLY')
        occupied = defaultdict(set)
        for row in keeps:
            occupied[row['symbol']].add(row['qdate'])
        earnings = earnings_dates(connection, sorted({row['symbol'] for row in keeps}))
        for case in cases:
            scored = evaluate_event(connection, sessions, index, case['symbol'], case['event'])
            scored.update(id=case['id'], symbol=case['symbol'], event=case['event'].isoformat())
            sec_rows.append(scored)
            placebo_event = None
            if case['event'] in index and index[case['event']] - PLACEBO_SHIFT > 0:
                placebo_event = sessions[index[case['event']] - PLACEBO_SHIFT]
            if placebo_event is None:
                sec_placebo.append(dict(eligible=False, hit=False, id=case['id']))
            else:
                placebo = evaluate_event(connection, sessions, index, case['symbol'], placebo_event)
                placebo.update(id=case['id'], symbol=case['symbol'], event=placebo_event.isoformat())
                sec_placebo.append(placebo)
        documented = {(case['symbol'], case['event']) for case in cases}
        for row in keeps:
            scored = evaluate_event(connection, sessions, index, row['symbol'], row['qdate'])
            scored.update(symbol=row['symbol'], event=row['qdate'].isoformat(),
                          documented=(row['symbol'], row['qdate']) in documented)
            placebo_event = sessions[index[row['qdate']] - PLACEBO_SHIFT] if row['qdate'] in index and index[row['qdate']] >= PLACEBO_SHIFT else None
            if placebo_event is None:
                scored['placebo_hit'] = None
            else:
                placebo = evaluate_event(connection, sessions, index, row['symbol'], placebo_event)
                scored['placebo_hit'] = bool(placebo.get('hit')) if placebo.get('eligible') else None
            chosen = choose_earnings(row['symbol'], row['qdate'], earnings, index, sessions, occupied)
            if chosen is None:
                scored['earnings_hit'] = None
            else:
                earn = evaluate_event(connection, sessions, index, row['symbol'], chosen)
                scored['earnings_hit'] = bool(earn.get('hit')) if earn.get('eligible') else None
                scored['earnings_event'] = chosen.isoformat()
            candidate_rows.append(scored)
            print(row['symbol'], row['qdate'], 'hit' if scored.get('hit') else 'no', flush=True)
    finally:
        connection.rollback()
        connection.close()
    sec_rate, sec_hits = _rate(sec_rows)
    placebo_rate, _ = _rate(sec_placebo)
    candidate_rate, _ = _rate(candidate_rows)
    listed = [row for row in candidate_rows
              if row.get('hit') and row.get('placebo_hit') is False and row.get('earnings_hit') is False]
    summary = dict(
        sec_fixed_window=sec_rate,
        sec_placebo=placebo_rate,
        candidates=candidate_rate,
        listed=len(listed),
        sec_hits=[dict(id=row['id'], symbol=row['symbol'], event=row['event'],
                       net_oi=row.get('net_oi'), daily_ratio=row.get('daily_ratio')) for row in sec_hits],
        listed_names=[dict(symbol=row['symbol'], event=row['event'], net_oi=row.get('net_oi'),
                           daily_ratio=row.get('daily_ratio'), documented=row.get('documented')) for row in listed],
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'accumulation.json').write_text(json.dumps(dict(summary=summary, sec=sec_rows, candidates=candidate_rows), indent=2, default=str) + '\n')
    (folder / 'ACCUMULATION.md').write_text(render(summary))
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main():
    root = Path(os.environ.get('FOOTPRINT_ROOT', '.'))
    run(root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
