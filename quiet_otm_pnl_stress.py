"""Stress test of the multi-day short-dated OTM screen's 20-session call P&L.

The entry contract is chosen from the scoring day's quotes. The sale uses the
bid on the exit day. Nothing after the entry is used to pick the strike.
"""
from __future__ import annotations

import json
import random
import statistics
from datetime import date, timedelta
from pathlib import Path

from insider_resolved import connect, expiry_class, load_sessions
from quiet_otm_screen import _news, _screen_symbol
from quiet_screen import _exit_day, _nearest_monthly, _option_return, _push, distribution
from walkforward_score import classify_news, horizon_end_index

HOLD = 20
SEED = 20261113
SCREEN = 'multi_q5'


def dedupe_trades(trades: list[dict], index: dict) -> tuple[list[dict], list[dict]]:
    """Keep the earliest open trade in a name. A later signal is a duplicate while that hold is open."""
    kept, dropped = [], []
    open_until = {}
    for trade in sorted(trades, key=lambda item: (item['entry'], item['symbol'])):
        entry_i = index[date.fromisoformat(trade['entry'])]
        previous = open_until.get(trade['symbol'])
        if previous is not None and entry_i < previous:
            dropped.append(trade)
            continue
        exit_day = date.fromisoformat(trade['exit']) if trade.get('exit') else None
        open_until[trade['symbol']] = index[exit_day] if exit_day in index else entry_i + HOLD
        kept.append(trade)
    return kept, dropped


def trimmed(values: list[float], drop: int) -> dict:
    ordered = sorted(values, reverse=True)
    kept = ordered[drop:] if drop < len(ordered) else []
    stats = distribution(kept)
    stats['dropped'] = min(drop, len(ordered))
    return stats


def slate_returns(trades: list[dict]) -> list[float]:
    """Equal-weight call return of the filled names in each scoring date."""
    by_day = {}
    for trade in trades:
        if trade.get('call_return') is None:
            continue
        by_day.setdefault(trade['entry'], []).append(trade['call_return'])
    return [sum(values) / len(values) for values in by_day.values() if values]


def by_year(trades: list[dict]) -> dict:
    grouped = {}
    for trade in trades:
        if trade.get('call_return') is None:
            continue
        grouped.setdefault(trade['entry'][:4], []).append(trade['call_return'])
    return {year: distribution(values) for year, values in sorted(grouped.items())}


def by_hit(trades: list[dict]) -> dict:
    grouped = {}
    for trade in trades:
        if trade.get('call_return') is None:
            continue
        grouped.setdefault(trade.get('what') or 'other', []).append(trade['call_return'])
    return {kind: distribution(grouped.get(kind, [])) for kind in ('ma', 'earnings', 'other')}


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    earn_map, ma_map = _news(root)
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            cursor.execute(
                "SELECT DISTINCT symbol FROM optionstat WHERE qdate BETWEEN '2022-01-01' AND '2026-11-12'"
            )
            symbols = sorted(row['symbol'] for row in cursor.fetchall())
            cursor.execute(
                "SELECT symbol, splitdate FROM split WHERE splitdate BETWEEN '2021-10-01' AND '2026-11-12'"
            )
            splits = {(row['symbol'], row['splitdate']) for row in cursor.fetchall()}
    finally:
        connection.close()
    heap = {}
    quiet = {}
    for n, symbol in enumerate(symbols, start=1):
        try:
            result = _screen_symbol(symbol, sessions, index, splits, earn_map.get(symbol, set()), {})
        except Exception as exc:  # noqa: BLE001
            print(f'skip {symbol} {exc}', flush=True)
            continue
        for row in result['candidates']:
            if row.get('multi') and row.get('quiet_5') and row.get('five_ratio') is not None:
                _push(heap.setdefault(row['day'], []), (row['five_ratio'], row))
        for day in result.get('quiet_days') or []:
            quiet.setdefault(day, []).append(symbol)
        if n % 200 == 0:
            print(f'stress scan {n}/{len(symbols)} days {len(heap)}', flush=True)
    monthlies = []
    day = date(2021, 10, 1)
    while day <= date(2027, 3, 1):
        if expiry_class(day) == 'monthly':
            monthlies.append(day)
        day += timedelta(days=1)
    screen_trades = _legs(heap, sessions, index, monthlies, ma_map, earn_map, picks=3)
    rng = random.Random(SEED)
    random_picks = {}
    for day, names in quiet.items():
        if day not in heap or len(heap[day]) < 3:
            continue
        pool = list(dict.fromkeys(names))
        if len(pool) < 3:
            continue
        random_picks[day] = rng.sample(pool, 3)
    random_trades = _price_picks(random_picks, sessions, index, monthlies, ma_map, earn_map)
    filled = [trade for trade in screen_trades if trade.get('call_return') is not None]
    kept, dropped = dedupe_trades(filled, index)
    report = dict(
        pricing='ask on the scoring day, bid on the exit day, strike chosen from that day\'s delta only',
        published_slate_median=1.061,
        raw_trades=distribution([trade['call_return'] for trade in filled]),
        raw_slates=distribution(slate_returns(filled)),
        drop_top_5_trades=trimmed([trade['call_return'] for trade in filled], 5),
        drop_top_10_trades=trimmed([trade['call_return'] for trade in filled], 10),
        drop_top_5_slates=distribution(slate_returns(_without_largest(filled, 5))),
        drop_top_10_slates=distribution(slate_returns(_without_largest(filled, 10))),
        by_year=by_year(filled),
        by_hit=by_hit(filled),
        duplicate_trades=len(dropped),
        deduped_trades=distribution([trade['call_return'] for trade in kept]),
        deduped_slates=distribution(slate_returns(kept)),
        random_quiet_slates=distribution(slate_returns(
            [trade for trade in random_trades if trade.get('call_return') is not None])),
        random_quiet_trades=distribution(
            [trade['call_return'] for trade in random_trades if trade.get('call_return') is not None]),
        example_fill=_example_fill(filled),
    )
    _write(root, report)
    return report


def _without_largest(trades: list[dict], drop: int) -> list[dict]:
    ranked = sorted(trades, key=lambda trade: trade['call_return'], reverse=True)
    banned = {(trade['symbol'], trade['entry']) for trade in ranked[:drop]}
    return [trade for trade in trades if (trade['symbol'], trade['entry']) not in banned]


def _legs(heap, sessions, index, monthlies, ma_map, earn_map, picks):
    chosen = {}
    for day, rows in heap.items():
        if len(rows) < picks:
            continue
        chosen[day] = [row for _score, row in rows[:picks]]
    return _price_picks(chosen, sessions, index, monthlies, ma_map, earn_map)


def _price_picks(picks_by_day, sessions, index, monthlies, ma_map, earn_map):
    plans = []
    needed = {}
    for day, rows in picks_by_day.items():
        entry = date.fromisoformat(day) if isinstance(day, str) else day
        expiry = _nearest_monthly(entry, monthlies)
        exit_day = _exit_day(sessions, index, entry, 20, expiry) if expiry and entry in index else None
        key = entry.isoformat()
        for row in rows:
            symbol = row if isinstance(row, str) else row['symbol']
            plans.append((key, symbol, expiry, exit_day, row if isinstance(row, dict) else None))
            if expiry and exit_day:
                needed.setdefault(symbol, {}).setdefault(expiry, set()).update((entry, exit_day))
    quotes = _quotes(needed)
    trades = []
    for entry_key, symbol, expiry, exit_day, row in plans:
        entry = date.fromisoformat(entry_key)
        option = None
        if expiry and exit_day:
            option = _option_return(quotes.get((symbol, expiry), []), entry, exit_day)
        end_i = horizon_end_index(sessions, index, entry, 20) if entry in index else None
        what = 'other'
        if end_i is not None:
            what = classify_news(symbol, entry, sessions[end_i], sessions, index, ma_map, earn_map)
        trades.append(dict(
            symbol=symbol, entry=entry_key,
            exit=None if exit_day is None else exit_day.isoformat(),
            call_return=option, what=what,
            ratio=None if row is None else row.get('five_ratio'),
            spike_days=None if row is None else row.get('spike_days'),
            consecutive=None if row is None else row.get('consecutive'),
        ))
    return trades


def _quotes(needed):
    quotes = {}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            for symbol, expiries in needed.items():
                for expiry, dates in expiries.items():
                    marks = ','.join(['%s'] * len(dates))
                    cursor.execute(
                        f'''SELECT qdate, strike, delta, bid, ask FROM optiondaily
                            WHERE underlying=%s AND `type`='call' AND edate=%s AND qdate IN ({marks})''',
                        (symbol, expiry, *sorted(dates)),
                    )
                    quotes[(symbol, expiry)] = cursor.fetchall()
    finally:
        connection.close()
    return quotes


def _example_fill(trades):
    filled = [trade for trade in trades if trade.get('call_return') is not None]
    if not filled:
        return None
    trade = sorted(filled, key=lambda item: item['entry'])[len(filled) // 2]
    return dict(trade)


def _write(root: Path, report: dict) -> None:
    folder = root / 'results' / 'insider_footprint'
    (folder / 'quiet_otm_pnl_stress.json').write_text(json.dumps(report, indent=2) + '\n')
    text = render(report)
    (folder / 'QUIET_OTM_PNL.md').write_text(text)
    path = folder / 'WALKFORWARD.md'
    prior = path.read_text() if path.exists() else ''
    marker = '## Multi-day call P&L stress test, 2026-11-13'
    if marker in prior:
        prior = prior.split(marker)[0].rstrip() + '\n'
    path.write_text(prior.rstrip() + '\n\n' + text)
    print(text, flush=True)


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def render(report: dict) -> str:
    raw = report['raw_slates']
    deduped = report['deduped_slates']
    random_base = report['random_quiet_slates']
    lines = [
        '## Multi-day call P&L stress test, 2026-11-13',
        '',
        'This is the 20-session call book for the multi-day short-dated OTM top 3. The contract is the nearest monthly call whose delta that morning is closest to 0.30 and between 0.20 and 0.40. It is bought at that day\'s ask and sold at the bid 20 sessions later, or on the last session on or before expiry if that comes first. The strike is chosen only from the entry day\'s quotes.',
        '',
        f"Published slate median: {_fmt(report['published_slate_median'])}. Recomputed slate median: {_fmt(raw.get('median'))}. Recomputed slate mean: {_fmt(raw.get('mean'))} across {raw.get('n')} dates. Individual filled trades: {report['raw_trades'].get('n')}, median {_fmt(report['raw_trades'].get('median'))}, mean {_fmt(report['raw_trades'].get('mean'))}.",
        '',
        f"After removing the 5 largest trades, the remaining trades have median {_fmt(report['drop_top_5_trades'].get('median'))} and mean {_fmt(report['drop_top_5_trades'].get('mean'))}. The slate median with those trades removed is {_fmt(report['drop_top_5_slates'].get('median'))}. After removing the 10 largest, trade median {_fmt(report['drop_top_10_trades'].get('median'))}, trade mean {_fmt(report['drop_top_10_trades'].get('mean'))}, slate median {_fmt(report['drop_top_10_slates'].get('median'))}.",
        '',
        f"Overlapping later signals in a name already held: {report['duplicate_trades']}. After keeping only the first open trade, the trade median is {_fmt(report['deduped_trades'].get('median'))} and the slate median is {_fmt(deduped.get('median'))}. Deduped slate mean: {_fmt(deduped.get('mean'))}.",
        '',
        f"The same call bought on three random quiet stocks on the same dates has slate median {_fmt(random_base.get('median'))} and mean {_fmt(random_base.get('mean'))} across {random_base.get('n')} dates.",
        '',
        '### By year',
        '',
        '| Year | Trades | Mean | Median |',
        '| --- | ---: | ---: | ---: |',
    ]
    for year, cell in report['by_year'].items():
        lines.append(f"| {year} | {cell['n']} | {_fmt(cell['mean'])} | {_fmt(cell['median'])} |")
    lines += ['', '### By what the next 20 sessions contained', '', '| Type | Trades | Mean | Median |', '| --- | ---: | ---: | ---: |']
    for kind, label in (('ma', 'M&A'), ('earnings', 'Earnings'), ('other', 'Other')):
        cell = report['by_hit'].get(kind) or {}
        lines.append(f"| {label} | {cell.get('n', 0)} | {_fmt(cell.get('mean'))} | {_fmt(cell.get('median'))} |")
    lines.append('')
    lines.append('The book survives only if the deduped slate median stays above the random quiet-stock call and the trade median stays positive after the 10 largest trades are removed.')
    lines.append('')
    survives = (
        deduped.get('median') is not None and random_base.get('median') is not None
        and deduped['median'] > random_base['median']
        and report['drop_top_10_trades'].get('median') is not None
        and report['drop_top_10_trades']['median'] > 0
    )
    lines += [
        '',
        'The edge survives this cut.' if survives else 'The edge does not survive this cut. The recomputed book is no longer clearly above the random quiet-stock call, or the median turns down once the largest trades or the overlapping repeats are removed.',
        '',
    ]
    return '\n'.join(lines)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
