"""Quiet stock, loud short-dated OTM calls.

The surge is measured on calls with strike above the spot and 1–45 days to
expiry, against that same series' own prior 20-session average. A delta
0.10–0.35 slice and a single-strike concentration cut are variants. Rules
were fixed before the scan.
"""
from __future__ import annotations

import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

from insider_resolved import connect, expiry_class, load_sessions
from quiet_screen import (
    MIN_BASELINE, SINGLE_MIN, _add_universe, _attach_oi, _empty_counts, _exit_day,
    _jumps, _nearest_monthly, _option_return, _push, classify_volume, confirms_open,
    distribution, evaluate_index, slate_hit_summary,
)
from walkforward_score import END, START, classify_news, horizon_end_index

CHAIN_FROM = date(2021, 10, 1)
HORIZON_SET = (10, 20)
SCREENS = (
    'single_q5', 'multi_q5', 'single_q5_oi', 'multi_q5_oi', 'single_q5_earn', 'multi_q5_earn',
    'single_q3', 'multi_q3', 'single_delta', 'multi_delta', 'single_conc', 'multi_conc',
)
FOCUS = ('lantheus_2022', 'maxar_2022', 'pfizer_2021', 'zogenix_2022')
SQL = '''
SELECT qdate, SUM(vol) otm, MAX(vol) max_leg, SUM(oi) oi, SUM(band) band, SUM(band_oi) band_oi
FROM (
  SELECT qdate, edate, strike, SUM(volume) vol, SUM(oi) oi,
         SUM(CASE WHEN delta>=0.10 AND delta<=0.35 THEN volume ELSE 0 END) band,
         SUM(CASE WHEN delta>=0.10 AND delta<=0.35 THEN oi ELSE 0 END) band_oi
  FROM optiondaily
  WHERE underlying=%s AND `type`='call' AND qdate BETWEEN %s AND %s
    AND underlying_last>0 AND strike>underlying_last
    AND DATEDIFF(edate, qdate) BETWEEN 1 AND 45
  GROUP BY qdate, edate, strike
) legs
GROUP BY qdate
'''


def apply_floors(loud: dict, volumes: list[float], mean: float) -> dict:
    """Baseline average at least 100, and the loudest day at least 500 contracts."""
    loud = dict(loud)
    if mean < MIN_BASELINE or not volumes or volumes[loud['loudest']] < SINGLE_MIN:
        loud['single'] = False
        loud['multi'] = False
    return loud


def _series_rows(sessions, quotes, daily, volume_key, oi_key):
    rows = []
    for day in sessions:
        quote = quotes.get(day) or {}
        option = daily.get(day) or {}
        rows.append(dict(
            day=day,
            close=quote.get('close'),
            stock_vol=quote.get('volume'),
            call=float(option.get(volume_key) or 0),
            put=0.0,
            call_oi=None if option.get(oi_key) is None else float(option[oi_key]),
            max_leg=float(option.get('max_leg') or 0),
            otm=float(option.get('otm') or 0),
        ))
    _attach_oi(rows)
    return rows


def _screen_symbol(symbol, sessions, index, splits, earn_dates, case_ranges):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute(SQL, (symbol, CHAIN_FROM, END))
            daily = {row['qdate']: row for row in cursor.fetchall()}
            cursor.execute(
                'SELECT qdate, close, volume FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s',
                (symbol, CHAIN_FROM, END),
            )
            quotes = {
                row['qdate']: dict(close=float(row['close']), volume=float(row['volume'] or 0))
                for row in cursor.fetchall() if row['close']
            }
    finally:
        connection.close()
    if not quotes:
        return dict(counts={}, candidates=[], cases=[])
    otm_rows = _series_rows(sessions, quotes, daily, 'otm', 'oi')
    delta_rows = _series_rows(sessions, quotes, daily, 'band', 'band_oi')
    closes = {day: quotes[day]['close'] for day in quotes}
    counts = {'otm': {}, 'delta': {}}
    candidates = []
    cases = []
    for pos, row in enumerate(otm_rows):
        found = evaluate_index(otm_rows, pos)
        if found is None or not found['tradable']:
            continue
        loud = apply_floors(found, [item['call'] for item in otm_rows[pos - 4:pos + 1]], found['mean_call'])
        found.update(loud)
        jumps = _jumps(symbol, sessions, index, row['day'], closes, splits)
        found['jumps'] = jumps
        found['symbol'] = symbol
        found['day'] = row['day'].isoformat()
        found['earnings_soon'] = any(day in earn_dates for day in sessions[pos + 1:pos + 6])
        found['concentrated'] = row['otm'] > 0 and row['max_leg'] / row['otm'] >= 0.50
        bucket = counts['otm'].setdefault(found['day'], _empty_counts())
        if found['mean_call'] >= MIN_BASELINE:
            _add_universe(bucket, jumps)
            if found['quiet_5']:
                quiet = counts.setdefault('quiet_otm', {}).setdefault(found['day'], _empty_counts())
                _add_universe(quiet, jumps)
        delta = evaluate_index(delta_rows, pos)
        if delta is not None:
            delta_loud = apply_floors(delta, [item['call'] for item in delta_rows[pos - 4:pos + 1]], delta['mean_call'])
            found['delta_single'] = delta_loud['single'] and delta['quiet_5']
            found['delta_multi'] = delta_loud['multi'] and delta['quiet_5']
            found['delta_ratio'] = delta_loud['ratio']
            found['delta_five'] = delta_loud['five_ratio']
            if delta['mean_call'] >= MIN_BASELINE and delta['quiet_5']:
                quiet = counts.setdefault('quiet_delta', {}).setdefault(found['day'], _empty_counts())
                _add_universe(quiet, jumps)
        else:
            found['delta_single'] = found['delta_multi'] = False
            found['delta_ratio'] = found['delta_five'] = None
        if found['single'] or found['multi'] or found['delta_single'] or found['delta_multi']:
            if found['quiet_5'] or found['quiet_3']:
                candidates.append(found)
        for start, end, case_id in case_ranges.get(symbol, []):
            if start <= row['day'] <= end:
                cases.append(dict(
                    id=case_id, symbol=symbol, day=found['day'], single=found['single'],
                    multi=found['multi'], quiet_5=found['quiet_5'], ratio=found['ratio'],
                    r10=found['r10'], spike_days=found['spike_days'], consecutive=found['consecutive'],
                    mean_call=found['mean_call'],
                ))
    return dict(counts=counts, candidates=candidates, cases=cases)


def _place(heaps, row):
    def add(name, score):
        if score is None:
            return
        _push(heaps[name].setdefault(row['day'], []), (score, row))
    if row['single'] and row['quiet_5']:
        add('single_q5', row['ratio'])
        if row.get('oi_single'):
            add('single_q5_oi', row['ratio'])
        if not row['earnings_soon']:
            add('single_q5_earn', row['ratio'])
        if row['concentrated']:
            add('single_conc', row['ratio'])
    if row['single'] and row['quiet_3']:
        add('single_q3', row['ratio'])
    if row['multi'] and row['quiet_5']:
        add('multi_q5', row['five_ratio'])
        if row.get('oi_multi'):
            add('multi_q5_oi', row['five_ratio'])
        if not row['earnings_soon']:
            add('multi_q5_earn', row['five_ratio'])
        if row['concentrated']:
            add('multi_conc', row['five_ratio'])
    if row['multi'] and row['quiet_3']:
        add('multi_q3', row['five_ratio'])
    if row['delta_single']:
        add('single_delta', row['delta_ratio'])
    if row['delta_multi']:
        add('multi_delta', row['delta_five'])


def _pnl(heaps, sessions, index, monthlies):
    needed = {}
    plans = []
    for screen in ('single_q5', 'multi_q5'):
        for day, heap in heaps.get(screen, {}).items():
            entry = date.fromisoformat(day)
            expiry = _nearest_monthly(entry, monthlies)
            if expiry is None or entry not in index:
                continue
            for horizon in HORIZON_SET:
                exit_day = _exit_day(sessions, index, entry, horizon, expiry)
                if exit_day is None:
                    continue
                for picks in (3, 4):
                    if len(heap) < picks:
                        continue
                    for _score, row in heap[:picks]:
                        plans.append((screen, picks, day, horizon, row, exit_day, expiry))
                        needed.setdefault(row['symbol'], {}).setdefault(expiry, set()).update((entry, exit_day))
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
    by_slate = {}
    for screen, picks, day, horizon, row, exit_day, expiry in plans:
        flag = (row.get('jumps') or {}).get(str(horizon)) or {}
        option = _option_return(quotes.get((row['symbol'], expiry), []), date.fromisoformat(day), exit_day)
        by_slate.setdefault((screen, picks, day, horizon), []).append(option if option is not None else None)
    summary = {}
    for (screen, picks, day, horizon), legs in by_slate.items():
        calls = [value for value in legs if value is not None]
        if not calls:
            continue
        bucket = summary.setdefault(screen, {}).setdefault(str(picks), {}).setdefault(str(horizon), [])
        bucket.append(sum(calls) / len(calls))
    return {
        screen: {
            picks: {horizon: distribution(values) for horizon, values in horizons.items()}
            for picks, horizons in sizes.items()
        }
        for screen, sizes in summary.items()
    }


def _exit_day(sessions, index, entry, horizon, expiry):
    return _exit_day_impl(sessions, index, entry, horizon, expiry)


def _exit_day_impl(sessions, index, entry, horizon, expiry):
    from quiet_screen import _exit_day as impl
    return impl(sessions, index, entry, horizon, expiry)


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    earn_map, ma_map = _news(root)
    cases = json.loads((root / 'data' / 'sec_cases.json').read_text())['cases']
    ranges = {}
    for case in cases:
        ranges.setdefault(case['symbol'], []).append(
            (date.fromisoformat(case['trade_start']), date.fromisoformat(case['event_date']), case['id']))
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            cursor.execute('SELECT DISTINCT symbol FROM optionstat WHERE qdate BETWEEN %s AND %s', (START, END))
            symbols = sorted(row['symbol'] for row in cursor.fetchall())
            cursor.execute('SELECT symbol, splitdate FROM split WHERE splitdate BETWEEN %s AND %s', (CHAIN_FROM, END))
            splits = {(row['symbol'], row['splitdate']) for row in cursor.fetchall()}
    finally:
        connection.close()
    totals = {'otm': {}, 'quiet_otm': {}, 'quiet_delta': {}}
    heaps = {name: {} for name in SCREENS}
    qualifier_counts = {name: {} for name in SCREENS}
    case_rows = []
    lock = threading.Lock()
    done = 0

    def merge(result):
        for name, days in result['counts'].items():
            dest = totals.setdefault(name, {})
            for day, horizons in days.items():
                bucket = dest.setdefault(day, _empty_counts())
                for horizon, cell in horizons.items():
                    for key, value in cell.items():
                        bucket[horizon][key] += value
        for row in result['candidates']:
            for name, _score in _tags(row):
                qualifier_counts[name][row['day']] = qualifier_counts[name].get(row['day'], 0) + 1
            _place(heaps, row)
        case_rows.extend(result['cases'])

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(_screen_symbol, symbol, sessions, index, splits, earn_map.get(symbol, set()), ranges): symbol
            for symbol in symbols
        }
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                print(f'skip {symbol} {exc}', flush=True)
                continue
            with lock:
                merge(result)
                done += 1
                if done % 100 == 0:
                    print(f'screened {done}/{len(symbols)}', flush=True)
    monthlies = []
    day = CHAIN_FROM
    while day <= date(2027, 3, 1):
        if expiry_class(day) == 'monthly':
            monthlies.append(day)
        day += timedelta(days=1)
    pnl = _pnl(heaps, sessions, index, monthlies)
    report = _assemble(heaps, totals, qualifier_counts, sessions, index, ma_map, earn_map, case_rows, pnl)
    _write(root, report)
    return report


def _tags(row):
    specs = []
    if row['single'] and row['quiet_5'] and row.get('ratio') is not None:
        specs += [('single_q5', row['ratio'])]
        if row.get('oi_single'):
            specs.append(('single_q5_oi', row['ratio']))
        if not row['earnings_soon']:
            specs.append(('single_q5_earn', row['ratio']))
        if row.get('concentrated'):
            specs.append(('single_conc', row['ratio']))
        if row['quiet_3']:
            specs.append(('single_q3', row['ratio']))
    if row['multi'] and row['quiet_5'] and row.get('five_ratio') is not None:
        specs += [('multi_q5', row['five_ratio'])]
        if row.get('oi_multi'):
            specs.append(('multi_q5_oi', row['five_ratio']))
        if not row['earnings_soon']:
            specs.append(('multi_q5_earn', row['five_ratio']))
        if row.get('concentrated'):
            specs.append(('multi_conc', row['five_ratio']))
        if row['quiet_3']:
            specs.append(('multi_q3', row['five_ratio']))
    if row.get('delta_single') and row.get('delta_ratio') is not None:
        specs.append(('single_delta', row['delta_ratio']))
    if row.get('delta_multi') and row.get('delta_five') is not None:
        specs.append(('multi_delta', row['delta_five']))
    return specs


def _news(root: Path):
    from quiet_screen import _news as impl
    return impl(root)


def _assemble(heaps, totals, qualifier_counts, sessions, index, ma_map, earn_map, case_rows, pnl):
    screens = {}
    for name, days in heaps.items():
        quiet_key = 'quiet_delta' if 'delta' in name else 'quiet_otm'
        records = []
        for day, heap in days.items():
            score_day = date.fromisoformat(day)
            slate = []
            for score, row in heap:
                news = {}
                for horizon in HORIZON_SET:
                    end_i = horizon_end_index(sessions, index, score_day, horizon) if score_day in index else None
                    news[str(horizon)] = 'other' if end_i is None else classify_news(
                        row['symbol'], score_day, sessions[end_i], sessions, index, ma_map, earn_map)
                slate.append(dict(row, score=score, news=news))
            records.append(dict(
                slate=slate,
                qualifiers=qualifier_counts.get(name, {}).get(day, len(slate)),
                universe={
                    'filtered': totals.get('otm', {}).get(day, _empty_counts()),
                    quiet_key: totals.get(quiet_key, {}).get(day, _empty_counts()),
                },
                quiet_key=quiet_key,
            ))
        block = {}
        for picks in (3, 4):
            block[str(picks)] = {}
            for horizon in HORIZON_SET:
                block[str(picks)][str(horizon)] = slate_hit_summary(records, picks, horizon, 'peak', 'filtered')
        screens[name] = block
    return dict(
        screens=screens,
        qualifier_counts={name: _count_summary(days) for name, days in qualifier_counts.items()},
        examples=_examples(heaps, sessions, index, ma_map, earn_map),
        cases=_focus_cases(case_rows),
        pnl=pnl,
    )


def _count_summary(days):
    from quiet_screen import _count_summary as impl
    return impl(days)


def _examples(heaps, sessions, index, ma_map, earn_map):
    rows = []
    for name in ('single_q5', 'multi_q5'):
        for day, heap in heaps.get(name, {}).items():
            for _score, row in heap[:4]:
                flag = (row.get('jumps') or {}).get('20') or {}
                if not flag.get('peak'):
                    continue
                score_day = date.fromisoformat(day)
                end_i = horizon_end_index(sessions, index, score_day, 20) if score_day in index else None
                kind = 'other' if end_i is None else classify_news(
                    row['symbol'], score_day, sessions[end_i], sessions, index, ma_map, earn_map)
                rows.append(dict(
                    symbol=row['symbol'], day=day, ratio=row.get('ratio'), five_ratio=row.get('five_ratio'),
                    r10=row.get('r10'), spike_days=row.get('spike_days'), consecutive=row.get('consecutive'),
                    single=name.startswith('single'), what=kind,
                ))
    rows.sort(key=lambda item: ({'ma': 0, 'earnings': 1, 'other': 2}[item['what']], -(item['ratio'] or 0)))
    picked, seen = [], {}
    for row in rows:
        if seen.get(row['symbol'], 0) >= 2:
            continue
        picked.append(row)
        seen[row['symbol']] = seen.get(row['symbol'], 0) + 1
        if len(picked) >= 20:
            break
    return picked


def _focus_cases(case_rows):
    found = {case_id: False for case_id in FOCUS}
    detail = {}
    for row in case_rows:
        if row['id'] not in found:
            continue
        passed = row.get('quiet_5') and (row.get('single') or row.get('multi'))
        if passed:
            found[row['id']] = True
            current = detail.get(row['id'])
            if current is None or not (current.get('quiet_5') and (current.get('single') or current.get('multi'))):
                detail[row['id']] = row
        elif row['id'] not in detail:
            detail[row['id']] = row
    return dict(flagged=found, detail=detail)


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def render(report: dict) -> str:
    lines = [
        '## Short-dated OTM calls, quiet stock, 2026-11-13',
        '',
        'The volume is only calls with strike above the spot and 1–45 days to expiry. A single day is that volume at least 5 times its own prior 20-session average and at least 500 contracts. A multi-day build is two or more of the last five sessions at least 3 times that average, or a five-session total at least 5 times a normal five-session total spread over two or more days. The loudest day is still at least 500. The prior 20-session average of this same volume is at least 100. The stock’s 10-session move is under 5% (a second cut uses 3%), the scoring day is under 3%, and stock volume is under twice its median. Price is at least $5 and median dollar volume is at least $5 million. A delta 0.10–0.35 slice, a next-morning open-interest increase, an earnings blackout, and a single strike holding at least half the short-dated OTM volume are variants. The comparison is a random quiet stock with the same average. Downside hit rates are not in this test.',
        '',
        '| Screen | Slate | Horizon | Dates | Date hit rate | Quiet base | Misses per hit | M&A | Earnings | Other |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    titles = {
        'single_q5': 'OTM strike, single, under 5%',
        'multi_q5': 'OTM strike, multi-day, under 5%',
        'single_q5_oi': 'Single, open-interest confirmation',
        'multi_q5_oi': 'Multi-day, open-interest confirmation',
        'single_q5_earn': 'Single, no earnings in 5 sessions',
        'multi_q5_earn': 'Multi-day, no earnings in 5 sessions',
        'single_q3': 'Single, 10-session move under 3%',
        'multi_q3': 'Multi-day, 10-session move under 3%',
        'single_delta': 'Delta 0.10–0.35, single',
        'multi_delta': 'Delta 0.10–0.35, multi-day',
        'single_conc': 'One strike at least half, single',
        'multi_conc': 'One strike at least half, multi-day',
    }
    for name, title in titles.items():
        block = (report.get('screens') or {}).get(name) or {}
        for picks in ('3', '4'):
            for horizon in ('10', '20'):
                cell = block.get(picks, {}).get(horizon)
                if not cell:
                    continue
                lines.append(
                    f"| {title} | {picks} | {horizon} | {cell['dates']} | {_fmt(cell['date_hit_rate'])} | "
                    f"{_fmt(cell['quiet_base'])} | {_fmt(cell['false_picks_per_hit'])} | "
                    f"{cell['hits']['ma']} | {cell['hits']['earnings']} | {cell['hits']['other']} |"
                )
    lines += ['', '### Call P&L', '', 'Nearest monthly call with delta closest to 0.30, bought at the ask and sold at the bid.', '']
    lines.append('| Screen | Slate | Horizon | Slates | Mean | Median | Hit rate | Worst decile |')
    lines.append('| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    for screen, title in (('single_q5', 'single'), ('multi_q5', 'multi')):
        for picks, horizons in (report.get('pnl') or {}).get(screen, {}).items():
            for horizon, cell in horizons.items():
                lines.append(
                    f"| {title} | {picks} | {horizon} | {cell.get('n', 0)} | {_fmt(cell.get('mean'))} | "
                    f"{_fmt(cell.get('median'))} | {_fmt(cell.get('hit_rate'))} | {_fmt(cell.get('worst_decile'))} |"
                )
    lines += ['', '### The four previously loud resolved cases', '']
    flagged = (report.get('cases') or {}).get('flagged') or {}
    detail = (report.get('cases') or {}).get('detail') or {}
    for case_id in FOCUS:
        row = detail.get(case_id) or {}
        state = 'flagged' if flagged.get(case_id) else 'not flagged'
        lines.append(
            f"- {case_id} {row.get('symbol', '')} {state}. "
            f"Sample day {row.get('day', 'n/a')}, ratio {_fmt(row.get('ratio'))}, "
            f"10-session return {_fmt(row.get('r10'))}."
        )
    lines += ['', '### Examples with a 15% high within 20 sessions', '']
    for row in report.get('examples') or []:
        kind = 'single day' if row.get('single') else 'multi-day'
        lines.append(
            f"- {row['symbol']} {row['day']} {kind}, ratio {_fmt(row.get('ratio'))}, "
            f"10-session return {_fmt(row.get('r10'))}, spike days {row.get('spike_days')} "
            f"({row.get('consecutive')} consecutive), later {row.get('what')}."
        )
    lines += ['', 'A qualifying name is a review tag. It is not an identification of a trader.', '']
    return '\n'.join(lines)


def _write(root: Path, report: dict) -> None:
    folder = root / 'results' / 'insider_footprint'
    (folder / 'quiet_otm_screen.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
    text = render(report)
    (folder / 'QUIET_OTM.md').write_text(text)
    path = folder / 'WALKFORWARD.md'
    prior = path.read_text() if path.exists() else ''
    marker = '## Short-dated OTM calls, quiet stock, 2026-11-13'
    if marker in prior:
        prior = prior.split(marker)[0].rstrip() + '\n'
    path.write_text(prior.rstrip() + '\n\n' + text)
    print(text, flush=True)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
