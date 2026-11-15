"""Price and option pattern around class-2 M&A announcements.

The announcement session is the clock. The stock return that day and over the
prior 10 sessions is descriptive. A qualifying option is one contract, judged
only against that stock's own monthly or weekly history, and it has to still
be open into the announcement. Earnings dates on the same names are the
ordinary-news comparison.
"""
import json
import statistics
from datetime import date
from pathlib import Path

from insider_footprint import choose_earnings, earnings_dates
from insider_resolved import (
    BASELINE,
    WINDOW,
    connect,
    evaluate_period,
    fetch,
    load_keeps,
    load_sessions,
    window_before,
)


def held_into_event(oi_path) -> bool:
    """True when open interest on the announcement morning is still at least half the peak."""
    if not oi_path or oi_path[-1] is None:
        return False
    values = [value for value in oi_path if value is not None]
    if len(values) < 2:
        return False
    peak = max(values)
    return oi_path[-1] >= 50 and peak > 0 and oi_path[-1] >= 0.5 * peak


def price_move(stock, sessions, index, event):
    if event not in index or index[event] < 11:
        return None, None
    previous = sessions[index[event] - 1]
    base = sessions[index[event] - 11]
    if event not in stock or previous not in stock or base not in stock or not stock[previous] or not stock[base]:
        return None, None
    announcement = stock[event] / stock[previous] - 1
    prior = stock[previous] / stock[base] - 1
    return announcement, prior


def contract_path(chain, sessions, index, strike, expiry, start, end):
    path = []
    begin = index.get(start)
    stop = index.get(end)
    if begin is None or stop is None:
        return path
    for i in range(begin, stop + 1):
        day = sessions[i]
        oi = None
        for row in chain.get(day, []):
            if float(row['strike']) == strike and row['edate'] == expiry:
                oi = int(row['oi'] or 0)
                break
        path.append(oi)
    return path


def study(connection, sessions, index, symbol, event):
    signal = window_before(sessions, index, event, WINDOW, 0)
    if not signal or signal[0] not in index:
        return dict(eligible=False, hit=False, held=False)
    baseline = window_before(sessions, index, signal[0], BASELINE, 0)
    if not baseline:
        return dict(eligible=False, hit=False, held=False)
    chain, stock = fetch(connection, symbol, baseline[0], event)
    scored = evaluate_period(chain, stock, sessions, index, signal, baseline, event)
    announcement, prior = price_move(stock, sessions, index, event)
    held = False
    chosen = None
    if scored.get('matches'):
        chosen = max(scored['matches'], key=lambda row: row['volume'])
        path = contract_path(chain, sessions, index, chosen['strike'], chosen['edate'],
                             date.fromisoformat(chosen['qdate']), event)
        held = held_into_event(path)
        chosen = dict(strike=chosen['strike'], expiry=chosen['expiry'], qdate=chosen['qdate'],
                      volume=chosen['volume'], oi=chosen['oi'])
    return dict(eligible=scored.get('eligible', False), hit=bool(scored.get('hit')), held=held,
                cycle=scored.get('cycle'), announcement=announcement, prior=prior, contract=chosen)


def _median(values):
    values = [value for value in values if value is not None]
    if not values:
        return None
    return float(statistics.median(values))


def _fmt(value):
    return 'n/a' if value is None else f'{value * 100:.1f}%'


def render(summary) -> str:
    price = summary['price']
    options = summary['options']
    earnings = summary['earnings']
    lines = [
        '# M&A news, price, and options',
        '',
        'Class-2 announcements are the clock. The same-day close-to-close return is the reaction. The prior 10 sessions are the path into that news. A flat path is a prior return between −5% and +5%. A run-up is a prior return above 10%. Options use one strike and expiry, compared only with that stock’s own monthly or weekly history. Held means open interest on the announcement morning is still at least half the peak since the print. Earnings dates on the same names are the ordinary-news comparison.',
        '',
        f"Price on {price['n']} announcements: median reaction {_fmt(price['median_announcement'])}, median prior 10 sessions {_fmt(price['median_prior'])}. {price['flat']} were flat into the news. {price['runup']} had already risen more than 10%.",
        '',
        f"Options: {options['hits']} of {options['eligible']} announcements had a qualifying contract. {options['held']} of those were still open into the announcement.",
        '',
        f"Earnings on the same names: {earnings['hits']} of {earnings['eligible']} had a qualifying contract, and {earnings['held']} were still open into the earnings reaction.",
        '',
        'Announcements where the qualifying contract was still open:',
        '',
    ]
    if summary['held_names']:
        for row in summary['held_names']:
            lines.append(
                f"- {row['symbol']} {row['event']} ({row['cycle']}): {row['expiry']} {row['strike']} "
                f"on {row['qdate']}, volume {row['volume']} against {row['oi']} open, "
                f"prior {_fmt(row['prior'])}, reaction {_fmt(row['announcement'])}. {row['detail']}"
            )
    else:
        lines.append('None.')
    lines += ['', 'A listed name is a description of the tape, not an identification of a trader.', '']
    return '\n'.join(lines)


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    keeps = [row for row in load_keeps(root) if row['tier'] == 'A']
    details = {}
    payload = json.loads((root / 'data/price_jump_news_reviews.json').read_text())
    for row in payload['reviews']:
        if str(row.get('cause_class', '')).startswith('2_'):
            details[(row['symbol'].upper(), row['qdate'])] = row.get('detail') or ''
    connection = connect()
    rows = []
    earnings_rows = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute('START TRANSACTION READ ONLY')
        occupied = {}
        for row in keeps:
            occupied.setdefault(row['symbol'], set()).add(row['qdate'])
        earnings = earnings_dates(connection, sorted({row['symbol'] for row in keeps}))
        for row in keeps:
            if row['qdate'] not in index:
                continue
            examined = study(connection, sessions, index, row['symbol'], row['qdate'])
            examined.update(symbol=row['symbol'], event=row['qdate'].isoformat(),
                            detail=details.get((row['symbol'], row['qdate'].isoformat()), ''))
            rows.append(examined)
            print(row['symbol'], row['qdate'], 'held' if examined['held'] else ('hit' if examined['hit'] else 'no'), flush=True)
            chosen = choose_earnings(row['symbol'], row['qdate'], earnings, index, sessions, occupied)
            if chosen is None or chosen not in index:
                continue
            earn = study(connection, sessions, index, row['symbol'], chosen)
            earn.update(symbol=row['symbol'], event=chosen.isoformat())
            earnings_rows.append(earn)
    finally:
        connection.rollback()
        connection.close()
    priced = [row for row in rows if row.get('announcement') is not None]
    eligible = [row for row in rows if row.get('eligible')]
    hits = [row for row in eligible if row.get('hit')]
    held = [row for row in hits if row.get('held')]
    earn_eligible = [row for row in earnings_rows if row.get('eligible')]
    summary = dict(
        price=dict(
            n=len(priced),
            median_announcement=_median([row['announcement'] for row in priced]),
            median_prior=_median([row['prior'] for row in priced]),
            flat=sum(row['prior'] is not None and abs(row['prior']) <= 0.05 for row in priced),
            runup=sum(row['prior'] is not None and row['prior'] > 0.10 for row in priced),
        ),
        options=dict(eligible=len(eligible), hits=len(hits), held=len(held)),
        earnings=dict(
            eligible=len(earn_eligible),
            hits=sum(row.get('hit') for row in earn_eligible),
            held=sum(row.get('held') for row in earn_eligible if row.get('hit')),
        ),
        held_names=[dict(
            symbol=row['symbol'], event=row['event'], cycle=row.get('cycle'),
            strike=row['contract']['strike'], expiry=row['contract']['expiry'],
            qdate=row['contract']['qdate'], volume=row['contract']['volume'], oi=row['contract']['oi'],
            prior=row.get('prior'), announcement=row.get('announcement'), detail=row.get('detail') or '',
        ) for row in held],
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'ma_news_pattern.json').write_text(json.dumps(dict(summary=summary, events=rows, earnings=earnings_rows), indent=2, default=str) + '\n')
    (folder / 'MA_NEWS_PATTERN.md').write_text(render(summary))
    print(json.dumps(summary['price'], indent=2), flush=True)
    print(json.dumps(summary['options'], indent=2), flush=True)
    print(json.dumps(summary['earnings'], indent=2), flush=True)
    return summary


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
