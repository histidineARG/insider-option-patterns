"""Screen rebuilt from the resolved SEC option cases.

Development recall is only the cases large enough to move an end-of-day chain:
Heinz, Bioverativ, and Kaman. Kraft, Joy, Lantheus, and Maxar are too small and
are not counted as misses. Incyte is a peer trade and is reported on its own.
Class-2 jumps are unlabeled. The 15% announcement gap stays the event marker.
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

from insider_footprint import choose_earnings, connect, earnings_dates, load_keeps, load_sessions

WINDOW = 15
PLACEBO_SHIFT = 60
DTE_LO = 20
DTE_HI = 130
OTM_LO = 0.03
OTM_HI = 0.40
DELTA_LO = 0.05
DELTA_HI = 0.50
MIN_VOLUME = 100
MAX_CONTRACTS = 3
STOCK_MOVE = 0.15

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


def in_sleeve(row) -> bool:
    spot = float(row['underlying_last'] or 0)
    if spot <= 0:
        return False
    bid = float(row['bid'] or 0)
    ask = float(row['ask'] or 0)
    if bid <= 0 or ask < bid:
        return False
    dte = (row['edate'] - row['qdate']).days
    if not DTE_LO <= dte <= DTE_HI:
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


def score_day(rows, next_rows, stock_return) -> dict:
    if stock_return is not None and abs(stock_return) >= STOCK_MOVE:
        return dict(hit=False, reason='stock_already_moved', contracts=0)
    large = []
    for row in rows:
        if not in_sleeve(row):
            continue
        # Size is judged on this contract alone. Volume and open interest are
        # never added across expiries: a front month dying and a back month
        # opening are not one position.
        if is_large(row['volume'], row['oi'], same_contract_oi(row, next_rows)):
            large.append(row)
    if len(large) > MAX_CONTRACTS:
        return dict(hit=False, reason='broad_chain', contracts=len(large))
    if not large:
        return dict(hit=False, contracts=0)
    top = max(large, key=lambda row: int(row['volume'] or 0))
    return dict(
        hit=True,
        contracts=len(large),
        volume=sum(int(row['volume'] or 0) for row in large),
        strike=float(top['strike']),
        expiry=top['edate'].isoformat() if hasattr(top['edate'], 'isoformat') else str(top['edate']),
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
        cursor.execute(CHAIN_SQL, (symbol, start, end, DTE_LO - 10, DTE_HI))
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


def evaluate_days(chain, stock, sessions, index, days) -> dict:
    hits = []
    for day in days:
        nxt = sessions[index[day] + 1] if day in index and index[day] + 1 < len(sessions) else None
        scored = score_day(chain.get(day, []), chain.get(nxt, []), stock_return(stock, sessions, index, day))
        if scored['hit']:
            scored['qdate'] = day.isoformat()
            hits.append(scored)
    return dict(eligible=bool(days), hit=bool(hits), days=len(days),
                alert_dates=[row['qdate'] for row in hits],
                volume=sum(row['volume'] for row in hits),
                contracts=max((row['contracts'] for row in hits), default=0))


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
        'Each strike and expiry is its own series. Volume and open interest are not added across expiries, and a session on or after expiry is not treated as a change in the position. A call qualifies at 20–130 days to expiry and either 3–40% out of the money or delta 0.05–0.50. That contract is large when its own volume is at least 100 and at least the open interest already open in it, or when the next session’s open interest in that same contract rises by at least 100 and by at least half the volume. At most three contracts may qualify on a day. A day whose stock already moved 15% is excluded. Kraft, Joy, Lantheus, and Maxar are below the size one contract can show and are not misses.',
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
            lines.append(f"- {row['symbol']} {row['event']}: {', '.join(row['alert_dates'])}")
    else:
        lines.append('None.')
    lines += [
        '',
        'Heinz is one contract, the June 65 call: 2,593 contracts against 364 open, and that same contract has 2,626 open the next session. Kaman is the March 30 call. Kraft’s documented June 67.5 call, 361 contracts against about 20,000 open, does not qualify. The Kraft session still lights on two other June strikes because their own next-day open interest rose. That confirmation is loose on a liquid series, so the class-2 list is a first pass.',
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

        def pull(symbol, days):
            span = cover(days, sessions, index)
            if span is None:
                return {}, {}
            pad_start = sessions[max(0, index[span[0]] - 2)] if span[0] in index else span[0]
            return fetch(connection, symbol, pad_start, span[1])

        for case in cases:
            reaction = reaction_day(sessions, index, case['event'], case['timing'])
            trade_days = [day for day in sessions_between(sessions, case['trade_start'], case['trade_end'])
                          if reaction is None or day < reaction]
            chain, stock = pull(case['symbol'], trade_days)
            scored = evaluate_days(chain, stock, sessions, index, trade_days)
            placebo_days = window_before(sessions, index, reaction, max(len(trade_days), 1), PLACEBO_SHIFT) if reaction else None
            if not placebo_days:
                placebo_hit = None
            else:
                pchain, pstock = pull(case['symbol'], placebo_days)
                placebo_hit = evaluate_days(pchain, pstock, sessions, index, placebo_days)['hit']
            scored.update(id=case['id'], symbol=case['symbol'], group=case['group'],
                          placebo_hit=placebo_hit)
            case_rows.append(scored)
            print(case['id'], 'hit' if scored['hit'] else 'no', flush=True)

        for row in keeps:
            if row['qdate'] not in index:
                continue
            days = window_before(sessions, index, row['qdate'], WINDOW, 0)
            chain, stock = pull(row['symbol'], days)
            scored = evaluate_days(chain, stock, sessions, index, days or [])
            placebo_days = window_before(sessions, index, row['qdate'], WINDOW, PLACEBO_SHIFT)
            if not placebo_days:
                scored['placebo_hit'] = None
            else:
                pchain, pstock = pull(row['symbol'], placebo_days)
                scored['placebo_hit'] = evaluate_days(pchain, pstock, sessions, index, placebo_days)['hit']
            chosen = choose_earnings(row['symbol'], row['qdate'], earnings, index, sessions, occupied)
            if chosen is None or chosen not in index:
                scored['earnings_hit'] = None
            else:
                earn_days = window_before(sessions, index, chosen, WINDOW, 0)
                echain, estock = pull(row['symbol'], earn_days)
                scored['earnings_hit'] = evaluate_days(echain, estock, sessions, index, earn_days or [])['hit']
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
        listed_names=[dict(symbol=row['symbol'], event=row['event'], alert_dates=row['alert_dates']) for row in listed],
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
