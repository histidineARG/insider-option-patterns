"""Screen rebuilt from the resolved SEC option cases.

Development recall is only the cases large enough to move an end-of-day chain:
Heinz, Bioverativ, and Kaman. Kraft, Joy, Lantheus, and Maxar are too small and
are not counted as misses. Incyte is a peer trade and is reported on its own.
Class-2 jumps are unlabeled. The 15% announcement gap stays the event marker.
"""
import calendar
import json
import os
import statistics
from datetime import date, timedelta
from pathlib import Path

from insider_footprint import choose_earnings, connect, earnings_dates, load_keeps, load_sessions

WINDOW = 15
BASELINE = 40
PLACEBO_SHIFT = 60
DTE_HI = 130
OTM_LO = 0.03
OTM_HI = 0.40
DELTA_LO = 0.05
DELTA_HI = 0.50
MIN_VOLUME = 100
OWN_MULTIPLE = 3.0
MIN_BASELINE = 10
MAX_CONTRACTS = 3
STOCK_MOVE = 0.15
# February 2015 is the first standard monthly expiration on a Friday.
FRIDAY_MONTHLY_FROM = date(2015, 2, 1)

IN_REACH = {'heinz_2013', 'bioverativ_2018', 'kaman_2024'}
OUT_OF_REACH = {'kraft_2015', 'joy_2016', 'lantheus_2022', 'maxar_2022'}
PEER = {'incy_2016'}
RESOLVED_STATUSES = {
    'settlement_announced',
    'settled_admin_findings',
    'civil_liability_verdict_reported_2024_04_08',
    'default_judgment_reported_2020_12_15',
    'complaint_with_partial_defendant_consent_judgments_2026_03',
}

# The pull is wider than the sleeve so the next session of a 20-day contract
# is still present for the open-interest check. in_sleeve applies the real bounds.
CHAIN_SQL = '''
SELECT qdate, strike, edate, volume, oi, delta, underlying_last, bid, ask
FROM optiondaily
WHERE underlying = %s AND `type` = 'call' AND qdate BETWEEN %s AND %s
  AND DATEDIFF(edate, qdate) BETWEEN %s AND %s
'''
STOCK_SQL = '''
SELECT qdate, close FROM stockquote
WHERE symbol = %s AND qdate BETWEEN %s AND %s
'''


def third_friday(year: int, month: int) -> date:
    fridays = [day for day in calendar.Calendar().itermonthdates(year, month)
               if day.month == month and day.weekday() == 4]
    return fridays[2]


def expiry_class(edate: date) -> str:
    """Monthly, weekly, or other. Monthlies are Saturdays before February 2015."""
    if edate < FRIDAY_MONTHLY_FROM:
        monthly = third_friday(edate.year, edate.month) + timedelta(days=1)
    else:
        monthly = third_friday(edate.year, edate.month)
    if edate == monthly:
        return 'monthly'
    if edate.weekday() == 4:
        return 'weekly'
    return 'other'


def own_threshold(peaks) -> float | None:
    """Three times this stock's own median loudest single-contract day, at least 100."""
    if len(peaks) < MIN_BASELINE:
        return None
    return max(float(MIN_VOLUME), OWN_MULTIPLE * float(statistics.median(peaks)))


def in_sleeve(row) -> bool:
    spot = float(row['underlying_last'] or 0)
    if spot <= 0:
        return False
    bid = float(row['bid'] or 0)
    ask = float(row['ask'] or 0)
    if bid <= 0 or ask < bid:
        return False
    dte = (row['edate'] - row['qdate']).days
    if not 1 <= dte <= DTE_HI:
        return False
    if row['qdate'] >= row['edate']:
        return False
    otm = float(row['strike']) / spot - 1
    delta = row.get('delta')
    delta_ok = delta is not None and DELTA_LO <= float(delta) <= DELTA_HI
    otm_ok = OTM_LO <= otm <= OTM_HI
    return delta_ok or otm_ok


def same_contract_oi(row, next_rows):
    """Open interest of this strike and expiry on the next session.

    A later session on or after expiry is the contract dying, not a sale.
    A different expiry is a different contract and is ignored.
    """
    expiry = row['edate']
    strike = float(row['strike'])
    for follower in next_rows:
        if float(follower['strike']) != strike or follower['edate'] != expiry:
            continue
        if follower['qdate'] >= expiry:
            return None
        return follower['oi']
    return None


def is_large(volume, open_interest, next_open_interest) -> bool:
    volume = int(volume or 0)
    open_interest = int(open_interest or 0)
    if volume < MIN_VOLUME:
        return False
    if open_interest <= 0 or volume >= open_interest:
        return True
    if next_open_interest is None:
        return False
    increase = int(next_open_interest) - open_interest
    return increase >= 100 and increase >= 0.5 * volume


def class_peak(rows, klass: str) -> int:
    """Largest single-strike volume that day in one expiry class. Expiries are not added."""
    peak = 0
    for row in rows:
        if expiry_class(row['edate']) != klass:
            continue
        dte = (row['edate'] - row['qdate']).days
        if 1 <= dte <= DTE_HI:
            peak = max(peak, int(row['volume'] or 0))
    return peak


def score_day(rows, next_rows, stock_return, thresholds, event) -> dict:
    if stock_return is not None and abs(stock_return) >= STOCK_MOVE:
        return dict(hit=False, reason='stock_already_moved', contracts=0)
    large = []
    for row in rows:
        if not in_sleeve(row) or row['edate'] <= event:
            continue
        klass = expiry_class(row['edate'])
        # A monthly-only name has no weekly threshold, so a weekly cannot qualify.
        bar = thresholds.get(klass)
        if bar is None or int(row['volume'] or 0) < bar:
            continue
        # Size is judged on this contract alone. Volume and open interest are
        # never added across expiries: a front month dying and a back month
        # opening are not one position.
        if is_large(row['volume'], row['oi'], same_contract_oi(row, next_rows)):
            large.append(row)
    matches = [contract_match(row, next_rows) for row in large]
    if len(large) > MAX_CONTRACTS:
        return dict(hit=False, reason='broad_chain', contracts=len(large), matches=matches)
    if not large:
        return dict(hit=False, contracts=0, matches=[])
    top = max(large, key=lambda row: int(row['volume'] or 0))
    return dict(
        hit=True,
        contracts=len(large),
        volume=sum(int(row['volume'] or 0) for row in large),
        strike=float(top['strike']),
        expiry=top['edate'].isoformat() if hasattr(top['edate'], 'isoformat') else str(top['edate']),
        matches=matches,
    )


def contract_match(row, next_rows) -> dict:
    nxt = same_contract_oi(row, next_rows)
    return dict(
        strike=float(row['strike']),
        expiry=row['edate'].isoformat() if hasattr(row['edate'], 'isoformat') else str(row['edate']),
        edate=row['edate'],
        volume=int(row['volume'] or 0),
        oi=int(row['oi'] or 0),
        next_oi=None if nxt is None else int(nxt),
        klass=expiry_class(row['edate']),
    )


def load_resolved(root: Path) -> list[dict]:
    payload = json.loads((root / 'data/sec_cases.json').read_text())
    cases = []
    for row in payload['cases']:
        if row.get('evidence_status') not in RESOLVED_STATUSES:
            continue
        if row['id'] in OUT_OF_REACH:
            group = 'out_of_reach'
        elif row['id'] in PEER:
            group = 'peer'
        elif row['id'] in IN_REACH:
            group = 'in_reach'
        else:
            group = 'unsized'
        cases.append(dict(
            id=row['id'], symbol=row['symbol'].upper(), group=group,
            trade_start=date.fromisoformat(row['trade_start']),
            trade_end=date.fromisoformat(row['trade_end']),
            event=date.fromisoformat(row['event_date']),
            timing=row.get('announcement_session') or 'unknown',
            documented_contracts=row.get('documented_contracts'),
        ))
    return cases


def reaction_day(sessions, index, event: date, timing: str):
    if timing in ('after_close', 'nontrading_day'):
        return next((day for day in sessions if day > event), None)
    if event in index:
        return event
    return next((day for day in sessions if day >= event), None)


def sessions_between(sessions, start: date, end: date) -> list[date]:
    return [day for day in sessions if start <= day <= end]


def window_before(sessions, index, event: date, length: int, shift: int = 0):
    if event not in index:
        return None
    stop = index[event] - shift
    begin = stop - length
    if begin < 0 or stop <= 0:
        return None
    return sessions[begin:stop]


def _by_day(rows) -> dict:
    grouped = {}
    for row in rows:
        grouped.setdefault(row['qdate'], []).append(row)
    return grouped


def fetch(connection, symbol, start, end):
    with connection.cursor() as cursor:
        cursor.execute(CHAIN_SQL, (symbol, start, end, 0, DTE_HI + 10))
        chain = _by_day(cursor.fetchall())
        cursor.execute(STOCK_SQL, (symbol, start - timedelta(days=7), end))
        stock = {row['qdate']: float(row['close']) for row in cursor.fetchall()}
    return chain, stock


def stock_return(stock, sessions, index, day):
    if day not in index or index[day] == 0:
        return None
    prev = sessions[index[day] - 1]
    if day not in stock or prev not in stock or not stock[prev]:
        return None
    return stock[day] / stock[prev] - 1


def evaluate_period(chain, stock, sessions, index, signal, baseline, event) -> dict:
    """Flag a contract only when it is unusual versus this stock's own expiry class."""
    if not signal or len(baseline) < MIN_BASELINE:
        return dict(eligible=False, hit=False, alert_dates=[], cycle='unknown')
    history = list(baseline) + list(signal)
    listed = set()
    for day in history:
        for row in chain.get(day, []):
            listed.add(expiry_class(row['edate']))
    cycle = 'weekly' if 'weekly' in listed else 'monthly'
    classes = ['monthly'] + (['weekly'] if cycle == 'weekly' else [])
    thresholds = {klass: own_threshold([class_peak(chain.get(day, []), klass) for day in baseline])
                  for klass in classes}
    thresholds = {klass: bar for klass, bar in thresholds.items() if bar is not None}
    if not thresholds:
        return dict(eligible=False, hit=False, alert_dates=[], cycle=cycle)
    hits = []
    for day in signal:
        nxt = sessions[index[day] + 1] if day in index and index[day] + 1 < len(sessions) else None
        scored = score_day(chain.get(day, []), chain.get(nxt, []),
                           stock_return(stock, sessions, index, day), thresholds, event)
        if scored['hit']:
            for match in scored['matches']:
                match = dict(match)
                match['qdate'] = day.isoformat()
                hits.append(match)
    return dict(eligible=True, hit=bool(hits), days=len(signal), cycle=cycle,
                matches=hits,
                thresholds={k: round(v, 1) for k, v in thresholds.items()},
                alert_dates=sorted({row['qdate'] for row in hits}),
                volume=sum(row['volume'] for row in hits),
                contracts=max((sum(1 for row in hits if row['qdate'] == day) for day in {row['qdate'] for row in hits}), default=0))


def cover(days, sessions, index):
    if not days:
        return None
    last = days[-1]
    nxt = sessions[index[last] + 1] if last in index and index[last] + 1 < len(sessions) else last
    return days[0], nxt


def render(summary) -> str:
    reach = summary['in_reach']
    lines = [
        '# Resolved-case screen',
        '',
        'Each strike and expiry is its own series. A name is compared only with its own history of the same expiry type. Before February 2015 a monthly is the Saturday after the third Friday; after that it is the third Friday. Any other Friday is a weekly. A monthly-only name is not asked for a weekly. A contract is unusual when its volume is at least 100 and at least three times that stock’s own median loudest single-contract day in that expiry type, and the print is large against the open interest already in that same contract. A day whose stock already moved 15% is excluded. Kraft, Joy, Lantheus, and Maxar are below the size one contract can show and are not misses.',
        '',
        f"In-reach resolved cases, trade dates versus a same-length window 60 sessions earlier: {reach['hits']} of {reach['eligible']} hit on the trade dates, {reach['placebo_hits']} of those placebo windows also hit, and {reach['clean']} hit only on the trade dates.",
        '',
    ]
    for row in summary['in_reach_rows']:
        lines.append(f"- {row['id']} {row['symbol']}: trade hit {row['hit']}, placebo hit {row['placebo_hit']}, dates {', '.join(row['alert_dates']) or 'none'}")
    lines += [
        '',
        f"Incyte, the peer verdict, trade hit {summary['peer']['hit']}. It is not part of the target-jump recall.",
        '',
        f"Class-2 names with a hit in the 15 sessions before the jump, and quiet on the earlier window and on earnings: {summary['listed']}.",
        '',
    ]
    if summary['listed_names']:
        for row in summary['listed_names']:
            lines.append(f"- {row['symbol']} {row['event']} ({row.get('cycle') or 'unknown'}): {', '.join(row['alert_dates'])}")
    else:
        lines.append('None.')
    lines += [
        '',
        'The baseline is the 40 sessions before the signal window, using only that stock’s monthly volume for a monthly contract and only its weekly volume for a weekly contract.',
        '',
        'The out-of-reach settled cases were not scored as failures: Kraft, Joy, Lantheus, Maxar.',
        '',
    ]
    return '\n'.join(lines)


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    cases = load_resolved(root)
    keeps = [row for row in load_keeps(root) if row['tier'] == 'A']
    connection = connect()
    case_rows = []
    candidate_rows = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute('START TRANSACTION READ ONLY')
        occupied = {}
        for row in keeps:
            occupied.setdefault(row['symbol'], set()).add(row['qdate'])
        earnings = earnings_dates(connection, sorted({row['symbol'] for row in keeps}))

        def study(symbol, signal, event):
            if not signal or signal[0] not in index:
                return dict(eligible=False, hit=False, alert_dates=[], cycle='unknown')
            baseline = window_before(sessions, index, signal[0], BASELINE, 0)
            if not baseline:
                return dict(eligible=False, hit=False, alert_dates=[], cycle='unknown')
            last = signal[-1]
            nxt = sessions[index[last] + 1] if index[last] + 1 < len(sessions) else last
            chain, stock = fetch(connection, symbol, baseline[0], nxt)
            return evaluate_period(chain, stock, sessions, index, signal, baseline, event)

        for case in cases:
            reaction = reaction_day(sessions, index, case['event'], case['timing'])
            trade_days = [day for day in sessions_between(sessions, case['trade_start'], case['trade_end'])
                          if reaction is None or day < reaction]
            scored = study(case['symbol'], trade_days, reaction or case['event'])
            placebo_days = window_before(sessions, index, reaction, max(len(trade_days), 1), PLACEBO_SHIFT) if reaction else None
            placebo_event = sessions[index[reaction] - PLACEBO_SHIFT] if reaction in index and index[reaction] >= PLACEBO_SHIFT else None
            if not placebo_days or placebo_event is None:
                scored['placebo_hit'] = None
            else:
                scored['placebo_hit'] = study(case['symbol'], placebo_days, placebo_event)['hit']
            scored.update(id=case['id'], symbol=case['symbol'], group=case['group'])
            case_rows.append(scored)
            print(case['id'], scored.get('cycle'), 'hit' if scored['hit'] else 'no', flush=True)

        for row in keeps:
            if row['qdate'] not in index:
                continue
            days = window_before(sessions, index, row['qdate'], WINDOW, 0)
            scored = study(row['symbol'], days, row['qdate'])
            placebo_days = window_before(sessions, index, row['qdate'], WINDOW, PLACEBO_SHIFT)
            placebo_event = sessions[index[row['qdate']] - PLACEBO_SHIFT] if index[row['qdate']] >= PLACEBO_SHIFT else None
            if not placebo_days or placebo_event is None:
                scored['placebo_hit'] = None
            else:
                scored['placebo_hit'] = study(row['symbol'], placebo_days, placebo_event)['hit']
            chosen = choose_earnings(row['symbol'], row['qdate'], earnings, index, sessions, occupied)
            if chosen is None or chosen not in index:
                scored['earnings_hit'] = None
            else:
                earn_days = window_before(sessions, index, chosen, WINDOW, 0)
                scored['earnings_hit'] = study(row['symbol'], earn_days, chosen)['hit']
            scored.update(symbol=row['symbol'], event=row['qdate'].isoformat())
            candidate_rows.append(scored)
    finally:
        connection.rollback()
        connection.close()

    reach = [row for row in case_rows if row['group'] == 'in_reach']
    clean = [row for row in reach if row['hit'] and row['placebo_hit'] is False]
    listed = [row for row in candidate_rows
              if row['hit'] and row.get('placebo_hit') is False and row.get('earnings_hit') is False]
    peer = next((row for row in case_rows if row['group'] == 'peer'), dict(hit=False))
    summary = dict(
        in_reach=dict(eligible=len(reach), hits=sum(row['hit'] for row in reach),
                      placebo_hits=sum(row['placebo_hit'] is True for row in reach), clean=len(clean)),
        in_reach_rows=[dict(id=row['id'], symbol=row['symbol'], hit=row['hit'],
                            placebo_hit=row['placebo_hit'], alert_dates=row['alert_dates']) for row in reach],
        peer=dict(hit=bool(peer.get('hit')), alert_dates=peer.get('alert_dates') or []),
        listed=len(listed),
        listed_names=[dict(symbol=row['symbol'], event=row['event'], cycle=row.get('cycle'),
                           alert_dates=row['alert_dates']) for row in listed],
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'resolved_screen.json').write_text(json.dumps(dict(summary=summary, cases=case_rows, candidates=candidate_rows), indent=2) + '\n')
    (folder / 'RESOLVED_SCREEN.md').write_text(render(summary))
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main():
    run(Path(os.environ.get('FOOTPRINT_ROOT', '.')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
