"""Quiet stock, loud call volume.

The stock stays quiet. Call volume rises on one day or across several days.
Rules below were fixed before the 2022–2026 scan. Coefficients are not used
for the rank; the rank is the call-volume ratio times the out-of-the-money share.
"""
from __future__ import annotations

import json
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

from insider_resolved import connect, expiry_class, load_sessions
from walkforward_score import (
    END, START, classify_news, forward_flags, horizon_end_index, random_hit_probability,
)

BASELINE = 20
SPIKE = 5
MIN_PRICE = 5.0
MIN_DOLLAR = 5_000_000.0
MIN_BASELINE = 100.0
SINGLE_X = 5.0
SINGLE_MIN = 500.0
MULTI_X = 3.0
MULTI_DAYS = 2
CUMULATIVE_X = 5.0
OTM_MIN = 0.40
OI_SHARE = 0.50
QUIET_DAY = 0.03
QUIET_10 = (0.05, 0.03)
HORIZON_SET = (5, 10, 20)
CHAIN_FROM = date(2021, 10, 1)


def _mean(values) -> float:
    return sum(values) / len(values) if values else 0.0


def consecutive_spikes(flags: list[bool]) -> int:
    best = current = 0
    for flag in flags:
        if flag:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def classify_volume(spike_calls: list[float], mean_call: float) -> dict:
    """Single-day spike and multi-day build. The baseline mean is the prior 20 sessions."""
    big = [value >= SINGLE_MIN and value >= SINGLE_X * mean_call for value in spike_calls]
    spikes = [value > 0 and value >= MULTI_X * mean_call for value in spike_calls]
    total = sum(spike_calls)
    normal_five = SPIKE * mean_call
    spread = sum(value > 0 and mean_call > 0 and value >= mean_call for value in spike_calls) >= MULTI_DAYS
    multi = sum(spikes) >= MULTI_DAYS or (mean_call > 0 and spread and total >= CUMULATIVE_X * normal_five)
    single = sum(big) >= 1 and not multi
    loudest = max(range(len(spike_calls)), key=lambda i: spike_calls[i]) if spike_calls else 0
    ratio = (spike_calls[loudest] / mean_call) if mean_call > 0 else None
    five_ratio = (total / normal_five) if normal_five > 0 else None
    return dict(
        single=single,
        multi=multi,
        spike_days=sum(spikes),
        consecutive=consecutive_spikes(spikes),
        big_days=sum(big),
        loudest=loudest,
        ratio=ratio,
        five_ratio=five_ratio,
        total=total,
    )


def confirms_open(call_volume: float, oi_increase: float | None) -> bool:
    if oi_increase is None or call_volume <= 0:
        return False
    return oi_increase >= OI_SHARE * call_volume


def tradable(close: float | None, dollar_median: float | None) -> bool:
    return close is not None and close >= MIN_PRICE and dollar_median is not None and dollar_median >= MIN_DOLLAR


def quiet_stock(r10: float | None, rday: float | None, stock_volume: float | None, stock_median: float | None, limit: float) -> bool:
    if r10 is None or rday is None or stock_volume is None or not stock_median:
        return False
    if abs(r10) >= limit or abs(rday) >= QUIET_DAY:
        return False
    return stock_volume < 2.0 * stock_median


def rank_score(ratio: float | None, otm_share: float | None) -> float | None:
    if ratio is None or otm_share is None or otm_share < OTM_MIN:
        return None
    return ratio * otm_share


def evaluate_index(rows: list[dict], index: int) -> dict | None:
    """rows are session records ending in calendar order. index is the scoring session."""
    if index < BASELINE + SPIKE - 1 or index < 10:
        return None
    window = rows[index - (BASELINE + SPIKE - 1):index + 1]
    base = window[:BASELINE]
    spike = window[BASELINE:]
    if len(base) != BASELINE or len(spike) != SPIKE:
        return None
    if any(item.get('close') in (None, 0) for item in (rows[index], rows[index - 1], rows[index - 10])):
        return None
    mean_call = _mean([item['call'] for item in base])
    mean_total = _mean([item['call'] + item['put'] for item in base])
    loud = classify_volume([item['call'] for item in spike], mean_call)
    dollars = []
    for item in rows[index - 19:index + 1]:
        if item.get('close') and item.get('stock_vol') is not None:
            dollars.append(item['close'] * item['stock_vol'])
    dollar_median = statistics.median(dollars) if len(dollars) == 20 else None
    prior_volume = [item['stock_vol'] for item in rows[index - 20:index] if item.get('stock_vol') is not None]
    stock_median = statistics.median(prior_volume) if len(prior_volume) == 20 else None
    close = rows[index]['close']
    r10 = close / rows[index - 10]['close'] - 1
    rday = close / rows[index - 1]['close'] - 1
    gates = {}
    for limit in QUIET_10:
        gates[limit] = quiet_stock(r10, rday, rows[index].get('stock_vol'), stock_median, limit)
    spike_flags = [item['call'] > 0 and item['call'] >= MULTI_X * mean_call for item in spike]
    loudest = spike[loud['loudest']]
    oi_single = confirms_open(loudest['call'], loudest.get('oi_increase'))
    oi_multi = any(
        confirms_open(item['call'], item.get('oi_increase'))
        for item, flag in zip(spike, spike_flags) if flag
    )
    return dict(
        day=rows[index]['day'],
        **loud,
        mean_call=mean_call,
        mean_total=mean_total,
        r10=r10,
        rday=rday,
        close=close,
        tradable=tradable(close, dollar_median),
        quiet_5=gates[0.05],
        quiet_3=gates[0.03],
        oi_single=oi_single,
        oi_multi=oi_multi,
        oi=oi_single or oi_multi,
    )


def _attach_oi(rows: list[dict]) -> None:
    for pos, row in enumerate(rows[:-1]):
        nxt = rows[pos + 1].get('call_oi')
        if row.get('call_oi') is not None and nxt is not None:
            row['oi_increase'] = nxt - row['call_oi']
        else:
            row['oi_increase'] = None
    if rows:
        rows[-1]['oi_increase'] = None


def _push(heap, item):
    if item[0] is None:
        return
    if len(heap) < 4:
        heap.append(item)
        heap.sort(reverse=True)
    elif item[0] > heap[-1][0]:
        heap[-1] = item
        heap.sort(reverse=True)


def distribution(values: list[float]) -> dict:
    if not values:
        return dict(n=0, mean=None, median=None, hit_rate=None, worst_decile=None)
    ordered = sorted(values)
    return dict(
        n=len(values),
        mean=sum(values) / len(values),
        median=statistics.median(values),
        hit_rate=sum(value > 0 for value in values) / len(values),
        worst_decile=ordered[int(0.10 * (len(ordered) - 1))],
    )


def _empty_counts():
    return {str(horizon): dict(eligible=0, terminal=0, peak=0) for horizon in HORIZON_SET}


def _add_universe(bucket, jumps):
    for horizon in HORIZON_SET:
        flag = jumps.get(str(horizon))
        if not flag:
            continue
        cell = bucket[str(horizon)]
        cell['eligible'] += 1
        if flag['terminal']:
            cell['terminal'] += 1
        if flag['peak']:
            cell['peak'] += 1


def slate_hit_summary(records, picks, horizon, kind, universe_key):
    dates = hits = pick_hits = pick_n = false_picks = 0
    base_filtered = []
    base_quiet = []
    news = dict(ma=0, earnings=0, other=0)
    qualifiers = []
    for row in records:
        slate = row['slate'][:picks]
        if len(slate) < picks:
            continue
        flags = [item['jumps'].get(str(horizon)) for item in slate]
        if any(flag is None for flag in flags):
            continue
        dates += 1
        qualifiers.append(row.get('qualifiers', 0))
        jumped = [item for item, flag in zip(slate, flags) if flag[kind]]
        pick_n += picks
        pick_hits += len(jumped)
        false_picks += picks - len(jumped)
        if jumped:
            hits += 1
        for item in jumped:
            label = item['news'].get(str(horizon), 'other')
            news[label] = news.get(label, 0) + 1
        filtered = row['universe'][universe_key][str(horizon)]
        quiet = row['universe'][row['quiet_key']][str(horizon)]
        prob = random_hit_probability(filtered['eligible'], filtered[kind], picks)
        quiet_prob = random_hit_probability(quiet['eligible'], quiet[kind], picks)
        if prob is not None:
            base_filtered.append(prob)
        if quiet_prob is not None:
            base_quiet.append(quiet_prob)
    return dict(
        dates=dates,
        qualifiers_mean=(sum(qualifiers) / len(qualifiers)) if qualifiers else None,
        date_hit_rate=(hits / dates) if dates else None,
        filtered_base=(sum(base_filtered) / len(base_filtered)) if base_filtered else None,
        quiet_base=(sum(base_quiet) / len(base_quiet)) if base_quiet else None,
        pick_hit_rate=(pick_hits / pick_n) if pick_n else None,
        false_picks_per_hit=(false_picks / pick_hits) if pick_hits else None,
        hits=dict(ma=news['ma'], earnings=news['earnings'], other=news['other'], total=pick_hits),
    )


UNIVERSES = (
    'tradable_call', 'tradable_total', 'quiet_call_5', 'quiet_call_3', 'quiet_total_5', 'quiet_total_3',
)
SCREENS = (
    'single_call_q5', 'single_call_q5_oi', 'single_call_q5_earn', 'single_call_q3', 'single_total_q5',
    'multi_call_q5', 'multi_call_q5_oi', 'multi_call_q5_earn', 'multi_call_q3', 'multi_total_q5',
)


def _jumps(symbol, sessions, index, day, closes, splits):
    spot = closes.get(day)
    out = {}
    start = index[day]
    for horizon in HORIZON_SET:
        end_i = horizon_end_index(sessions, index, day, horizon)
        if end_i is None:
            out[str(horizon)] = None
            continue
        future_days = sessions[start + 1:end_i + 1]
        future = [closes.get(item) for item in future_days]
        flag = forward_flags(spot, future, any((symbol, item) in splits for item in future_days))
        if flag and not flag['bad'] and future[-1]:
            flag = dict(flag, stock_return=future[-1] / spot - 1)
        elif flag:
            flag = dict(flag, stock_return=None)
        out[str(horizon)] = flag
    return out


def _screen_symbol(symbol, sessions, index, splits, earn_dates, case_ranges):
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            cursor.execute(
                'SELECT qdate, callvol, putvol, callOI FROM optionstat WHERE symbol=%s AND qdate BETWEEN %s AND %s',
                (symbol, CHAIN_FROM, END),
            )
            options = {row['qdate']: row for row in cursor.fetchall()}
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
    rows = []
    for day in sessions:
        quote = quotes.get(day) or {}
        option = options.get(day)
        rows.append(dict(
            day=day,
            close=quote.get('close'),
            stock_vol=quote.get('volume'),
            call=0.0 if option is None else float(option['callvol'] or 0),
            put=0.0 if option is None else float(option['putvol'] or 0),
            call_oi=None if option is None or option['callOI'] is None else float(option['callOI']),
        ))
    _attach_oi(rows)
    closes = {row['day']: row['close'] for row in rows if row['close']}
    counts = {name: {} for name in UNIVERSES}
    candidates = []
    cases = []
    ranges = case_ranges.get(symbol, [])
    for pos, row in enumerate(rows):
        found = evaluate_index(rows, pos)
        if found is None or not found['tradable']:
            continue
        jumps = _jumps(symbol, sessions, index, row['day'], closes, splits)
        found['jumps'] = jumps
        found['earnings_soon'] = any(day in earn_dates for day in sessions[pos + 1:pos + 6])
        def bump(name):
            bucket = counts[name].setdefault(row['day'].isoformat(), _empty_counts())
            _add_universe(bucket, jumps)
        if found['mean_call'] >= MIN_BASELINE:
            bump('tradable_call')
            if found['quiet_5']:
                bump('quiet_call_5')
            if found['quiet_3']:
                bump('quiet_call_3')
        if found['mean_total'] >= MIN_BASELINE:
            bump('tradable_total')
            if found['quiet_5']:
                bump('quiet_total_5')
            if found['quiet_3']:
                bump('quiet_total_3')
        if (found['single'] or found['multi']) and (found['quiet_5'] or found['quiet_3']) and (
                found['mean_call'] >= MIN_BASELINE or found['mean_total'] >= MIN_BASELINE):
            found['symbol'] = symbol
            found['day'] = row['day'].isoformat()
            candidates.append(found)
        for start, end, case_id in ranges:
            if start <= row['day'] <= end:
                cases.append(dict(id=case_id, symbol=symbol, day=row['day'].isoformat(),
                                  single=found['single'], multi=found['multi'], ratio=found['ratio'],
                                  r10=found['r10'], spike_days=found['spike_days'],
                                  consecutive=found['consecutive'], quiet_5=found['quiet_5'],
                                  mean_call=found['mean_call'], close=found['close']))
    return dict(counts=counts, candidates=candidates, cases=cases)


def _otm_shares(symbol, days):
    if not days:
        return {}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            marks = ','.join(['%s'] * len(days))
            cursor.execute(
                f'''SELECT qdate,
                           SUM(CASE WHEN `type`='call' THEN volume ELSE 0 END) AS call_vol,
                           SUM(CASE WHEN `type`='call' AND delta>=0.10 AND delta<=0.35
                                    AND DATEDIFF(edate, qdate) BETWEEN 5 AND 45
                               THEN volume ELSE 0 END) AS otm_vol
                    FROM optiondaily
                    WHERE underlying=%s AND qdate IN ({marks})
                    GROUP BY qdate''',
                (symbol, *days),
            )
            return {
                row['qdate']: (float(row['otm_vol'] or 0), float(row['call_vol'] or 0))
                for row in cursor.fetchall()
            }
    finally:
        connection.close()


def _apply_otm(candidates, sessions, index):
    by_symbol = {}
    for row in candidates:
        start = index[date.fromisoformat(row['day'])]
        needed = sessions[max(0, start - 4):start + 1]
        by_symbol.setdefault(row['symbol'], set()).update(needed)
    shares = {}
    symbols = list(by_symbol)

    def work(symbol):
        return symbol, _otm_shares(symbol, sorted(by_symbol[symbol]))

    with ThreadPoolExecutor(max_workers=4) as pool:
        for n, (symbol, found) in enumerate(pool.map(work, symbols), start=1):
            shares[symbol] = found
            if n % 200 == 0:
                print(f'otm {n}/{len(symbols)}', flush=True)
    print(f'otm symbols {len(symbols)}', flush=True)
    kept = []
    for row in candidates:
        day = date.fromisoformat(row['day'])
        start = index[day]
        window = sessions[max(0, start - 4):start + 1]
        loud_day = window[row['loudest']] if row['loudest'] < len(window) else day
        call_sum = otm_sum = 0.0
        for item in window:
            otm, call = shares.get(row['symbol'], {}).get(item, (0.0, 0.0))
            call_sum += call
            otm_sum += otm
        loud_otm, loud_call = shares.get(row['symbol'], {}).get(loud_day, (0.0, 0.0))
        row['otm_day'] = (loud_otm / loud_call) if loud_call else None
        row['otm_five'] = (otm_sum / call_sum) if call_sum else None
        row['single_score'] = rank_score(row['ratio'], row['otm_day'])
        row['multi_score'] = rank_score(row['five_ratio'], row['otm_five'])
        if row['single_score'] is not None or row['multi_score'] is not None:
            kept.append(row)
    return kept


def _tags(row):
    specs = []
    if row['single'] and row['mean_call'] >= MIN_BASELINE and row['quiet_5'] and row.get('single_score') is not None:
        specs.append(('single_call_q5', row['single_score']))
        if row.get('oi_single'):
            specs.append(('single_call_q5_oi', row['single_score']))
        if not row.get('earnings_soon'):
            specs.append(('single_call_q5_earn', row['single_score']))
        if row.get('quiet_3'):
            specs.append(('single_call_q3', row['single_score']))
    if row['single'] and row['mean_total'] >= MIN_BASELINE and row['quiet_5'] and row.get('single_score') is not None:
        specs.append(('single_total_q5', row['single_score']))
    if row['multi'] and row['mean_call'] >= MIN_BASELINE and row['quiet_5'] and row.get('multi_score') is not None:
        specs.append(('multi_call_q5', row['multi_score']))
        if row.get('oi_multi'):
            specs.append(('multi_call_q5_oi', row['multi_score']))
        if not row.get('earnings_soon'):
            specs.append(('multi_call_q5_earn', row['multi_score']))
        if row.get('quiet_3'):
            specs.append(('multi_call_q3', row['multi_score']))
    if row['multi'] and row['mean_total'] >= MIN_BASELINE and row['quiet_5'] and row.get('multi_score') is not None:
        specs.append(('multi_total_q5', row['multi_score']))
    return specs


def _place(heaps, row):
    for name, score in _tags(row):
        _push(heaps[name].setdefault(row['day'], []), (score, row))


def _nearest_monthly(day, monthlies):
    for item in monthlies:
        if item > day:
            return item
    return None


def _option_return(rows, entry, exit_day):
    band = [row for row in rows if row['qdate'] == entry and row['delta'] is not None
            and 0.20 <= float(row['delta']) <= 0.40 and row['ask'] and float(row['ask']) > 0
            and (row['bid'] is None or float(row['ask']) >= float(row['bid']))]
    if not band:
        return None
    chosen = min(band, key=lambda row: abs(float(row['delta']) - 0.30))
    ask = float(chosen['ask'])
    later = [row for row in rows if row['qdate'] == exit_day and row['strike'] == chosen['strike']
             and row['bid'] and float(row['bid']) > 0]
    if not later:
        return None
    return float(later[0]['bid']) / ask - 1


def _exit_day(sessions, index, entry, horizon, expiry):
    end_i = horizon_end_index(sessions, index, entry, horizon)
    if end_i is None:
        return None
    exit_i = index[entry]
    for pos in range(index[entry] + 1, end_i + 1):
        if sessions[pos] <= expiry:
            exit_i = pos
        else:
            break
    if exit_i == index[entry]:
        return None
    return sessions[exit_i]


def _pnl(heaps, sessions, index, monthlies):
    needed = {}
    plans = []
    for screen in ('single_call_q5', 'multi_call_q5'):
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
                    for score, row in heap[:picks]:
                        plans.append((screen, day, horizon, row, exit_day, expiry, picks))
                        needed.setdefault(row['symbol'], {}).setdefault(expiry, set()).update((entry, exit_day))
    quotes = {}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            for n, (symbol, expiries) in enumerate(needed.items(), start=1):
                for expiry, dates in expiries.items():
                    marks = ','.join(['%s'] * len(dates))
                    cursor.execute(
                        f'''SELECT qdate, strike, delta, bid, ask FROM optiondaily
                            WHERE underlying=%s AND `type`='call' AND edate=%s AND qdate IN ({marks})''',
                        (symbol, expiry, *sorted(dates)),
                    )
                    quotes[(symbol, expiry)] = cursor.fetchall()
                if n % 100 == 0:
                    print(f'option quotes {n}/{len(needed)}', flush=True)
    finally:
        connection.close()
    grouped = {}
    by_slate = {}
    for screen, day, horizon, row, exit_day, expiry, picks in plans:
        entry = date.fromisoformat(day)
        flag = (row.get('jumps') or {}).get(str(horizon)) or {}
        stock = flag.get('stock_return')
        option = _option_return(quotes.get((row['symbol'], expiry), []), entry, exit_day)
        by_slate.setdefault((screen, picks, day, horizon), []).append((stock, option))
    for (screen, picks, day, horizon), legs in by_slate.items():
        bucket = grouped.setdefault(screen, {}).setdefault(str(picks), {}).setdefault(
            str(horizon), {'stock': [], 'call': [], 'years': {}})
        stocks = [stock for stock, _option in legs if stock is not None]
        calls = [option for _stock, option in legs if option is not None]
        year = day[:4]
        if stocks:
            value = sum(stocks) / len(stocks)
            bucket['stock'].append(value)
            bucket['years'].setdefault(year, {}).setdefault('stock', []).append(value)
        if calls:
            value = sum(calls) / len(calls)
            bucket['call'].append(value)
            bucket['years'].setdefault(year, {}).setdefault('call', []).append(value)
    summary = {}
    for screen, sizes in grouped.items():
        summary[screen] = {}
        for picks, horizons in sizes.items():
            summary[screen][picks] = {}
            for horizon, bucket in horizons.items():
                summary[screen][picks][horizon] = dict(
                    stock=distribution(bucket['stock']),
                    call=distribution(bucket['call']),
                    by_year={
                        year: {kind: distribution(values) for kind, values in kinds.items()}
                        for year, kinds in bucket['years'].items()
                    },
                )
    return summary


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    earn_map, ma_map = _news(root)
    cases = _cases(root)
    case_ranges = {}
    for case in cases:
        case_ranges.setdefault(case['symbol'], []).append(
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
    totals = {name: {} for name in UNIVERSES}
    candidates = []
    case_rows = []
    lock = threading.Lock()
    done = 0

    def merge(result):
        for name, days in result['counts'].items():
            dest = totals[name]
            for day, horizons in days.items():
                bucket = dest.setdefault(day, _empty_counts())
                for horizon, cell in horizons.items():
                    for key, value in cell.items():
                        bucket[horizon][key] += value
        candidates.extend(result['candidates'])
        case_rows.extend(result['cases'])

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {
            pool.submit(_screen_symbol, symbol, sessions, index, splits, earn_map.get(symbol, set()), case_ranges): symbol
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
                if done % 200 == 0:
                    print(f'screened {done}/{len(symbols)} candidates {len(candidates)}', flush=True)
    print(f'candidates {len(candidates)}', flush=True)
    kept = _apply_otm(candidates, sessions, index)
    print(f'with otm share {len(kept)}', flush=True)
    heaps = {name: {} for name in SCREENS}
    qualifier_counts = {name: {} for name in SCREENS}
    for row in kept:
        for name, _score in _tags(row):
            qualifier_counts[name][row['day']] = qualifier_counts[name].get(row['day'], 0) + 1
        _place(heaps, row)
    monthlies = []
    day = CHAIN_FROM
    while day <= date(2027, 3, 1):
        if expiry_class(day) == 'monthly':
            monthlies.append(day)
        day += timedelta(days=1)
    pnl = _pnl(heaps, sessions, index, monthlies)
    report = _assemble(heaps, totals, qualifier_counts, sessions, index, ma_map, earn_map, case_rows, kept, pnl)
    _write(root, report)
    return report


def _news(root: Path):
    earn, ma = {}, {}
    path = root / 'data' / 'edgar_deals' / 'earnings_8k_2022_2026.json'
    if path.exists():
        for row in json.loads(path.read_text()):
            if row.get('symbol') and row.get('reaction_session'):
                earn.setdefault(row['symbol'], set()).add(date.fromisoformat(row['reaction_session']))
    deals = root / 'data' / 'edgar_deals' / 'announcements.json'
    if deals.exists():
        for row in json.loads(deals.read_text()):
            if row.get('symbol') and row.get('qdate'):
                ma.setdefault(row['symbol'], set()).add(date.fromisoformat(row['qdate']))
    pool = root / 'results' / 'insider_footprint' / 'ma_news_pool.json'
    if pool.exists():
        for row in json.loads(pool.read_text())['events']:
            if row.get('qdate', '') >= '2022-01-01':
                ma.setdefault(row['symbol'], set()).add(date.fromisoformat(row['qdate']))
    return earn, ma


def _cases(root: Path):
    payload = json.loads((root / 'data' / 'sec_cases.json').read_text())
    return payload['cases']


def _assemble(heaps, totals, qualifier_counts, sessions, index, ma_map, earn_map, case_rows, kept, pnl):
    screens = {}
    for name, days in heaps.items():
        records = []
        quiet_key = 'quiet_call_3' if name.endswith('q3') else 'quiet_call_5'
        universe_key = 'tradable_total' if 'total' in name else 'tradable_call'
        if name.endswith('q3') and 'total' in name:
            quiet_key = 'quiet_total_3'
        for day, heap in days.items():
            score_day = date.fromisoformat(day)
            slate = []
            for score, row in heap:
                news = {}
                for horizon in HORIZON_SET:
                    end_i = horizon_end_index(sessions, index, score_day, horizon) if score_day in index else None
                    if end_i is None:
                        news[str(horizon)] = 'other'
                    else:
                        news[str(horizon)] = classify_news(row['symbol'], score_day, sessions[end_i], sessions, index, ma_map, earn_map)
                slate.append(dict(row, score=score, news=news))
            records.append(dict(
                slate=slate, qualifiers=qualifier_counts.get(name, {}).get(day, len(slate)),
                universe={key: totals.get(key, {}).get(day, _empty_counts()) for key in UNIVERSES},
                quiet_key=quiet_key,
            ))
        block = {}
        for picks in (3, 4):
            block[str(picks)] = {}
            for horizon in HORIZON_SET:
                block[str(picks)][str(horizon)] = {
                    'terminal': slate_hit_summary(records, picks, horizon, 'terminal', universe_key),
                    'peak': slate_hit_summary(records, picks, horizon, 'peak', universe_key),
                }
        screens[name] = block
    examples = _examples(kept, sessions, index, ma_map, earn_map)
    return dict(
        symbols=None,
        screens=screens,
        qualifier_counts={name: _count_summary(days) for name, days in qualifier_counts.items()},
        examples=examples,
        cases=case_rows,
        pnl=pnl,
        edgar_coverage=_coverage(),
    )


def _count_summary(days: dict) -> dict:
    values = list(days.values())
    if not values:
        return dict(days=0, mean=None, median=None, share_at_least_3=None)
    return dict(
        days=len(values),
        mean=sum(values) / len(values),
        median=statistics.median(values),
        share_at_least_3=sum(value >= 3 for value in values) / len(values),
    )


def _examples(kept, sessions, index, ma_map, earn_map):
    rows = []
    for row in kept:
        flag = (row.get('jumps') or {}).get('20')
        if not flag or not flag.get('peak'):
            continue
        if row.get('single_score') is None and row.get('multi_score') is None:
            continue
        day = date.fromisoformat(row['day'])
        end_i = horizon_end_index(sessions, index, day, 20) if day in index else None
        kind = 'other'
        if end_i is not None:
            kind = classify_news(row['symbol'], day, sessions[end_i], sessions, index, ma_map, earn_map)
        rows.append(dict(
            symbol=row['symbol'], day=row['day'], ratio=row.get('ratio'), five_ratio=row.get('five_ratio'),
            r10=row.get('r10'), spike_days=row.get('spike_days'), consecutive=row.get('consecutive'),
            single=row.get('single'), multi=row.get('multi'), what=kind, close=row.get('close'),
        ))
    rows.sort(key=lambda item: ({'ma': 0, 'earnings': 1, 'other': 2}[item['what']], -(item['ratio'] or 0)))
    picked = []
    seen = {}
    for row in rows:
        if seen.get(row['symbol'], 0) >= 2:
            continue
        picked.append(row)
        seen[row['symbol']] = seen.get(row['symbol'], 0) + 1
        if len(picked) >= 20:
            break
    return picked


def _coverage():
    return dict(
        note='An earlier request for company_tickers.json returned 403. The retry succeeded and was used with display tickers and cik2symbol.',
        deals=18044,
        proxy_display_ticker='1185/1896',
        tender_display_ticker='710/1201',
        recommendation_display_ticker='586/1050',
        earnings_rows=42026,
    )


def _write(root: Path, report: dict) -> None:
    folder = root / 'results' / 'insider_footprint'
    (folder / 'quiet_screen.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
    text = render(report)
    (folder / 'QUIET_SCREEN.md').write_text(text)
    for name in ('WALKFORWARD.md', 'VALIDATION.md'):
        path = folder / name
        prior = path.read_text() if path.exists() else ''
        marker = '## Quiet stock, loud options, 2026-11-13'
        if marker in prior:
            prior = prior.split(marker)[0].rstrip() + '\n'
        path.write_text(prior.rstrip() + '\n\n' + text)
    print(text, flush=True)


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def render(report: dict) -> str:
    lines = [
        '## Quiet stock, loud options, 2026-11-13',
        '',
        'The stock is quiet and call volume rises on one day or across several days. A single day is call volume at least 5 times the prior 20-session mean and at least 500 contracts, without a second elevated day. A multi-day build is two or more of the last five sessions at least 3 times that mean, or a five-session total at least 5 times a normal five-session total spread over two or more days. The prior 20 sessions sit before that five-session window and average at least 100 contracts. Out-of-the-money calls (delta 0.10–0.35, 5–45 days) are at least 40% of call volume. The 10-session absolute return is under 5% (a second cut uses 3%), the scoring day is under 3%, and stock volume is under twice its prior 20-session median. Price is at least $5 and median dollar volume is at least $5 million. Names are ordered by the call-volume ratio times the out-of-the-money share. Open-interest confirmation and the earnings blackout are reported beside the main screen. Downside hit rates are not part of this test.',
        '',
        report.get('edgar_coverage', {}).get('note', ''),
        '',
    ]
    for name, title in (
        ('single_call_q5', 'Single day, call baseline, 10-session move under 5%'),
        ('multi_call_q5', 'Multi-day build, call baseline, 10-session move under 5%'),
        ('single_call_q5_oi', 'Single day, next-morning open-interest confirmation'),
        ('multi_call_q5_oi', 'Multi-day, next-morning open-interest confirmation'),
        ('single_call_q5_earn', 'Single day, no earnings filing in the next 5 sessions'),
        ('multi_call_q5_earn', 'Multi-day, no earnings filing in the next 5 sessions'),
        ('single_call_q3', 'Single day, 10-session move under 3%'),
        ('multi_call_q3', 'Multi-day, 10-session move under 3%'),
        ('single_total_q5', 'Single day, calls-plus-puts baseline at least 100'),
        ('multi_total_q5', 'Multi-day, calls-plus-puts baseline at least 100'),
    ):
        block = (report.get('screens') or {}).get(name)
        if not block:
            continue
        counts = (report.get('qualifier_counts') or {}).get(name) or {}
        lines += [
            f'### {title}',
            '',
            f"Days with a qualifying name: {counts.get('days', 0)}. Mean qualifiers on those days: {_fmt(counts.get('mean'))}. Share of those days with at least 3: {_fmt(counts.get('share_at_least_3'))}.",
            '',
            '| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |',
            '| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
        ]
        for picks in ('3', '4'):
            for horizon in ('5', '10', '20'):
                for kind in ('terminal', 'peak'):
                    cell = block.get(picks, {}).get(horizon, {}).get(kind)
                    if not cell:
                        continue
                    lines.append(
                        f"| {picks} | {horizon} | {kind} | {cell['dates']} | {_fmt(cell['date_hit_rate'])} | "
                        f"{_fmt(cell['filtered_base'])} | {_fmt(cell['quiet_base'])} | {_fmt(cell['pick_hit_rate'])} | "
                        f"{_fmt(cell['false_picks_per_hit'])} | {cell['hits']['ma']} | {cell['hits']['earnings']} | {cell['hits']['other']} |"
                    )
        lines.append('')
    lines += ['### Equal-weight P&L', '']
    lines.append('Stock is bought at the scoring close. The call is the nearest monthly contract whose delta is closest to 0.30 and between 0.20 and 0.40, bought at the ask and sold at the bid on the horizon or at expiry, whichever comes first. Each slate’s return is the average of the names that have a price. Hit rate is the share of those slate returns that are positive.')
    lines.append('')
    lines.append('| Screen | Horizon | Leg | Slates | Mean | Median | Hit rate | Worst decile |')
    lines.append('| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |')
    year_notes = []
    for screen, title in (('single_call_q5', 'single'), ('multi_call_q5', 'multi')):
        for picks, horizons in (report.get('pnl') or {}).get(screen, {}).items():
            for horizon, legs in horizons.items():
                for leg in ('stock', 'call'):
                    cell = legs.get(leg) or {}
                    lines.append(
                        f"| {title} {picks} | {horizon} | {leg} | {cell.get('n', 0)} | {_fmt(cell.get('mean'))} | "
                        f"{_fmt(cell.get('median'))} | {_fmt(cell.get('hit_rate'))} | {_fmt(cell.get('worst_decile'))} |"
                    )
                years = legs.get('by_year') or {}
                bits = []
                for year in sorted(years):
                    stock = years[year].get('stock') or {}
                    call = years[year].get('call') or {}
                    bits.append(f"{year} stock {_fmt(stock.get('mean'))} / call {_fmt(call.get('mean'))}")
                if bits:
                    year_notes.append(f"{title} top {picks}, {horizon} sessions, mean by year: " + '; '.join(bits) + '.')
    lines.append('')
    lines.extend(year_notes)
    lines.append('')
    lines += ['### Examples with a 15% rise within 20 sessions', '']
    for row in report.get('examples') or []:
        kind = 'single day' if row.get('single') and not row.get('multi') else 'multi-day'
        lines.append(
            f"- {row['symbol']} {row['day']} {kind}, call ratio {_fmt(row.get('ratio'))}, "
            f"10-session return {_fmt(row.get('r10'))}, spike days {row.get('spike_days')} "
            f"({row.get('consecutive')} consecutive), later {row.get('what')}."
        )
    lines += ['', '### Resolved cases on this screen', '']
    shown = {}
    for row in report.get('cases') or []:
        if not (row.get('single') or row.get('multi')):
            continue
        shown.setdefault(row['id'], row)
    if not shown:
        lines.append('No resolved-case trade window had a loud call day.')
    lines.append('These are loud call days inside the documented trade window. A day passes the stock gate only when the 10-session move is under 5%.')
    for case_id, row in shown.items():
        quiet = 'stock quiet' if row.get('quiet_5') else 'stock already moved'
        lines.append(
            f"- {case_id} {row['symbol']} {row['day']} ratio {_fmt(row.get('ratio'))}, "
            f"10-session return {_fmt(row.get('r10'))}, spike days {row.get('spike_days')}, {quiet}."
        )
    lines += [
        '',
        'A qualifying name is a review tag. It is not an identification of a trader.',
        '',
    ]
    return '\n'.join(lines)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
