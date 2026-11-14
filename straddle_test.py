"""Long straddles and strangles on the anomaly tail.

The signal rules, earnings screen, and walk-forward split are the ones already
used in the anomaly test. A contract is chosen from the signal day's chain only.
The holdout is not used to pick a rule.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from anomaly_flow import (
    HOLDOUT_START, _as_date, _cap_sample, _f, _folds, _score_pair, load_config, load_earnings,
)
from insider_footprint import load_sessions

SLIP = 0.05
TARGET_DTE = 25
BAND = (20, 30)
ALLOWED = (8, 45)
DELTA_BAND = (0.10, 0.40)
HOLDS = ('d5', 'd10', 'expiry')
SOURCES = (
    ('hbos', 1, 'p1'), ('hbos', 1, 'p05'), ('hbos', 1, 'top4'),
    ('hbos', 5, 'p1'), ('hbos', 5, 'p05'), ('hbos', 5, 'top4'),
    ('iforest', 1, 'p1'), ('iforest', 1, 'p05'), ('iforest', 1, 'top4'),
)
SEED = 20261113


def choose_expiry(pairs: list[tuple[date, int]]) -> date | None:
    """Prefer an expiry inside 20-30 DTE. Otherwise the closest inside 8-45."""
    inside = [item for item in pairs if BAND[0] <= item[1] <= BAND[1]]
    pool = inside or [item for item in pairs if ALLOWED[0] <= item[1] <= ALLOWED[1]]
    if not pool:
        return None
    pool.sort(key=lambda item: (abs(item[1] - TARGET_DTE), item[0]))
    return pool[0][0]


def choose_strike(strikes: list[float], spot: float) -> float | None:
    if not strikes or spot <= 0:
        return None
    return min(strikes, key=lambda strike: (abs(strike - spot), strike))


def choose_strangle_leg(rows: list[dict], spot: float, side: str) -> dict | None:
    """25-delta wing. Calls stay above the spot and puts stay below it."""
    picked = []
    for row in rows:
        delta = row.get('delta')
        if delta is None or not np.isfinite(delta):
            continue
        magnitude = abs(float(delta))
        if not (DELTA_BAND[0] <= magnitude <= DELTA_BAND[1]):
            continue
        if side == 'call' and row['strike'] <= spot:
            continue
        if side == 'put' and row['strike'] >= spot:
            continue
        picked.append(row)
    if not picked:
        return None
    picked.sort(key=lambda row: (abs(abs(float(row['delta'])) - 0.25), row['strike']))
    return picked[0]


def leg_costs(bid, ask) -> dict | None:
    """Ask/bid fill, and a mid fill that pays 5 percent and sells 5 percent."""
    if bid is None or ask is None:
        return None
    bid, ask = float(bid), float(ask)
    if bid <= 0 or ask <= 0 or ask < bid:
        return None
    mid = 0.5 * (bid + ask)
    return dict(ask=ask, bid=bid, mid_in=mid * (1.0 + SLIP), mid_out=mid * (1.0 - SLIP))


def combo_return(entry: float, exit_price: float) -> float | None:
    if entry is None or exit_price is None or entry <= 0 or exit_price < 0:
        return None
    return exit_price / entry - 1.0


def hold_exit(entry: date, expiry: date, sessions: list[date], index: dict, kind: str) -> date | None:
    """Five sessions, ten sessions, or the last session at least two days before expiry."""
    if entry not in index:
        return None
    start = index[entry]
    if kind == 'expiry':
        target = expiry - timedelta(days=2)
        exit_day = None
        for day in sessions[start + 1:]:
            if day > target:
                break
            exit_day = day
        if exit_day is None:
            target = expiry - timedelta(days=1)
            for day in sessions[start + 1:]:
                if day > target:
                    break
                exit_day = day
        return exit_day
    step = 5 if kind == 'd5' else 10
    exit_i = start + step
    if exit_i >= len(sessions):
        return None
    exit_day = sessions[exit_i]
    last_live = None
    for day in sessions[start + 1:]:
        if day <= expiry:
            last_live = day
        else:
            break
    if last_live is None:
        return None
    return exit_day if exit_day <= last_live else last_live


def crosses_earnings(entry: date, exit_day: date, sessions: list[date], index: dict, reactions: set[date]) -> bool:
    start = index[entry]
    stop = index.get(exit_day)
    if stop is None:
        return False
    return any(day in reactions for day in sessions[start + 1:stop + 1])


def dedupe_trades(trades: list[dict], index: dict, gap: int = 10) -> list[dict]:
    """Keep the earliest open trade in a name. The next one waits ten sessions."""
    kept = []
    last = {}
    for trade in sorted(trades, key=lambda item: (item['entry'], item['symbol'])):
        if trade['entry'] not in index:
            continue
        previous = last.get(trade['symbol'])
        if previous is not None and index[trade['entry']] < previous + gap:
            continue
        last[trade['symbol']] = index[trade['entry']]
        kept.append(trade)
    return kept


def trailing_iv(dates: list[date], iv: np.ndarray, query: date, lookback: int = 100, minimum: int = 40):
    """Entry IV against the prior 100 prints. The entry print is not in the baseline."""
    if query not in dates:
        return None
    i = dates.index(query) if not isinstance(dates, dict) else dates[query]
    entry = float(iv[i])
    window = iv[max(0, i - lookback):i]
    window = window[np.isfinite(window) & (window > 0)]
    if len(window) < minimum or not np.isfinite(entry) or entry <= 0:
        return entry if np.isfinite(entry) and entry > 0 else None, None, None
    return entry, float(window.mean()), float(np.mean(window <= entry))


def realized_vol(closes: list[float]) -> float | None:
    closes = np.asarray(closes, dtype=np.float64)
    if len(closes) < 3 or np.any(closes[:-1] <= 0):
        return None
    returns = np.diff(closes) / closes[:-1]
    if len(returns) < 2 or not np.isfinite(returns).all():
        return None
    return float(returns.std() * np.sqrt(252))


def equity_curve(trades: list[dict], sessions: list[date], lock: int) -> dict:
    """Equal premium. Each entry day updates one of `lock` sleeves, so capital recycles on that cadence."""
    if not trades:
        return dict(terminal=None, max_drawdown=None)
    index = {day: i for i, day in enumerate(sessions)}
    by_day = {}
    for trade in trades:
        if trade['entry'] not in index or trade.get('quote') is None:
            continue
        by_day.setdefault(trade['entry'], []).append(trade['quote'])
    sleeves = np.ones(lock) / lock
    equity = []
    for i, day in enumerate(sessions):
        rets = by_day.get(day)
        if rets:
            sleeves[i % lock] *= 1.0 + float(np.mean(rets))
        equity.append(float(sleeves.sum()))
    path = np.asarray(equity)
    peak = np.maximum.accumulate(path)
    drawdown = float(np.max(1.0 - path / peak))
    return dict(terminal=float(path[-1]), max_drawdown=drawdown)


def clustered_mean(symbols: list[str], values: list[float], reps: int = 300, seed: int = 11):
    if len(values) < 20:
        return None, None
    order = {}
    for symbol, value in zip(symbols, values):
        order.setdefault(symbol, []).append(value)
    groups = list(order.values())
    rng = np.random.RandomState(seed)
    means = np.empty(reps)
    n = len(groups)
    for i in range(reps):
        draw = rng.randint(0, n, size=n)
        sample = [item for j in draw for item in groups[j]]
        means[i] = np.mean(sample)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def summarize(trades: list[dict], field: str) -> dict:
    values = [trade[field] for trade in trades if trade.get(field) is not None and np.isfinite(trade[field])]
    if not values:
        return dict(n=0, mean=None, median=None, win=None, pnl=None, ci=(None, None))
    array = np.asarray(values, dtype=np.float64)
    symbols = [trade['symbol'] for trade in trades if trade.get(field) is not None and np.isfinite(trade[field])]
    return dict(
        n=int(len(array)),
        mean=float(array.mean()),
        median=float(np.median(array)),
        win=float(np.mean(array > 0)),
        pnl=float(array.mean()),
        ci=clustered_mean(symbols, array.tolist()),
    )


def _daily_top(dates: np.ndarray, codes: np.ndarray, scores: np.ndarray, k: int = 4) -> np.ndarray:
    mask = np.zeros(len(scores), dtype=bool)
    finite = np.isfinite(scores)
    if finite.sum() < k:
        return mask
    order = np.argsort(dates, kind='mergesort')
    ordered_dates = dates[order]
    cuts = np.r_[0, np.flatnonzero(np.diff(ordered_dates)) + 1, len(order)]
    for start, stop in zip(cuts[:-1], cuts[1:]):
        rows = order[start:stop]
        usable = rows[np.isfinite(scores[rows])]
        if len(usable) < k:
            continue
        rank = np.lexsort((codes[usable], -scores[usable]))
        mask[usable[rank[:k]]] = True
    return mask


def score_signals(symbols: list[str]):
    """HBOS on the 1-day and 5-day windows, and isolation forest on the 1-day window."""
    wanted = {1: ('hbos', 'iforest'), 5: ('hbos',)}
    panels = {}
    flags = {}
    for window, methods in wanted.items():
        index = {pair: i for i, pair in enumerate(
            [(w, b) for w in (1, 3, 5) for b in (50, 100)])}[(window, 100)]
        print(f'load {window}d/100', flush=True)
        panel = load_config(symbols, index)
        panels[window] = panel
        for kind in methods:
            scores = np.full(len(panel['dates']), np.nan, dtype=np.float32)
            top1 = np.zeros(len(scores), dtype=bool)
            top05 = np.zeros(len(scores), dtype=bool)
            for train_mask, test_mask, is_holdout in _folds(panel['dates']):
                train_idx = np.flatnonzero(train_mask)
                test_idx = np.flatnonzero(test_mask)
                if len(test_idx) == 0 or len(train_idx) < 500:
                    continue
                ref = _cap_sample(train_idx, 20000, 19)
                label = 'holdout' if is_holdout else str(date.fromordinal(int(panel['dates'][test_idx[0]])).year)
                print(f'  {kind} {window}d {label}', flush=True)
                scored, cuts = _score_pair(
                    kind, panel['x'][train_idx], panel['x'][test_idx], panel['x'][ref],
                    seed=len(train_idx) % 10000 + window)
                if scored is None:
                    continue
                scores[test_idx] = scored
                top1[test_idx] = scored >= cuts['0.01']
                top05[test_idx] = scored >= cuts['0.005']
            flags[(kind, window)] = dict(
                scores=scores, p1=top1, p05=top05,
                top4=_daily_top(panel['dates'], panel['symbol'], scores),
            )
    return panels, flags


def signal_rows(symbols, panels, flags) -> list[dict]:
    rows = []
    for (kind, window), pack in flags.items():
        panel = panels[window]
        for rule, mask in (('p1', pack['p1']), ('p05', pack['p05']), ('top4', pack['top4'])):
            hit = np.flatnonzero(mask)
            for i in hit:
                rows.append(dict(
                    symbol=symbols[int(panel['symbol'][i])],
                    entry=date.fromordinal(int(panel['dates'][i])).isoformat(),
                    source=kind, window=window, rule=rule,
                ))
    return rows


def match_random(signals: list[dict], pool: dict, rng: np.random.RandomState) -> list[dict]:
    """One filtered name from the same month and the same IV-rank quintile."""
    matched = []
    for signal in signals:
        day = date.fromisoformat(signal['entry'])
        key = (day.year, day.month, signal.get('quintile'))
        choices = pool.get(key) or pool.get((day.year, day.month, None)) or []
        choices = [item for item in choices if item['symbol'] != signal['symbol'] or item['entry'] != signal['entry']]
        if not choices:
            matched.append(None)
            continue
        matched.append(choices[int(rng.randint(0, len(choices)))])
    return matched


def iv_snapshot(dates: list[date], iv: np.ndarray, query: date, lookup: dict | None = None):
    """Entry IV versus the prior 100 prints. The entry print is outside the baseline."""
    if lookup is None:
        lookup = {day: i for i, day in enumerate(dates)}
    i = lookup.get(query)
    if i is None:
        return None, None, None
    raw = iv[i]
    entry = float(raw) if np.isfinite(raw) and raw > 0 else None
    window = iv[max(0, i - 100):i]
    window = window[np.isfinite(window) & (window > 0)]
    if entry is None or len(window) < 40:
        return entry, None, None
    return entry, float(window.mean()), float(np.mean(window <= entry))


def select_structure(chain: list[dict], spot: float, kind: str) -> tuple[date, dict, dict] | None:
    expiries = sorted({row['edate'] for row in chain})
    pairs = [(expiry, (expiry - chain[0]['qdate']).days) for expiry in expiries]
    # DTE is relative to the quote day. All rows in `chain` share the entry day.
    entry = chain[0]['qdate']
    pairs = [(expiry, (expiry - entry).days) for expiry in expiries]
    expiry = choose_expiry(pairs)
    if expiry is None:
        return None
    live = [row for row in chain if row['edate'] == expiry]
    if kind == 'straddle':
        strike = choose_strike([row['strike'] for row in live], spot)
        call = next((row for row in live if row['side'] == 'call' and abs(row['strike'] - strike) < 1e-6), None)
        put = next((row for row in live if row['side'] == 'put' and abs(row['strike'] - strike) < 1e-6), None)
        if call is None or put is None:
            return None
        return expiry, call, put
    call = choose_strangle_leg([row for row in live if row['side'] == 'call'], spot, 'call')
    put = choose_strangle_leg([row for row in live if row['side'] == 'put'], spot, 'put')
    if call is None or put is None:
        return None
    return expiry, call, put


def price_combo(entry_call, entry_put, exit_call, exit_put) -> dict | None:
    first = leg_costs(entry_call.get('bid'), entry_call.get('ask'))
    second = leg_costs(entry_put.get('bid'), entry_put.get('ask'))
    later_call = leg_costs(exit_call.get('bid'), exit_call.get('ask')) if exit_call else None
    later_put = leg_costs(exit_put.get('bid'), exit_put.get('ask')) if exit_put else None
    if not first or not second or not later_call or not later_put:
        return None
    quote = combo_return(first['ask'] + second['ask'], later_call['bid'] + later_put['bid'])
    mid = combo_return(first['mid_in'] + second['mid_in'], later_call['mid_out'] + later_put['mid_out'])
    if quote is None or mid is None:
        return None
    return dict(quote=quote, mid=mid, premium=first['ask'] + second['ask'])


def run(root: Path):
    symbols = [line.strip() for line in Path('/tmp/anomaly_symbol_list.txt').read_text().splitlines() if line.strip()]
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    panels, flags = score_signals(symbols)
    signals = signal_rows(symbols, panels, flags)
    print(f'signals {len(signals)}', flush=True)
    universe = []
    panel = panels[1]
    for i in range(len(panel['dates'])):
        if not np.isfinite(flags[('hbos', 1)]['scores'][i]):
            continue
        universe.append(dict(
            symbol=symbols[int(panel['symbol'][i])],
            entry=date.fromordinal(int(panel['dates'][i])).isoformat(),
        ))
    print(f'universe days {len(universe)}', flush=True)
    del panels, flags
    earnings = load_earnings(root)
    trades, coverage = price_all(signals, universe, sessions, index, earnings)
    report = build_report(trades, coverage, sessions)
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'straddle_test.json').write_text(json.dumps(report, indent=2) + '\n')
    text = render(report)
    (folder / 'STRADDLE_TEST.md').write_text(text)
    print(text, flush=True)
    return report


def price_all(signals, universe, sessions, index, earnings):
    """Implied vol first, then the matched names, then one chain pull per name."""
    interest = {}
    for row in universe:
        interest.setdefault(row['symbol'], set()).add(date.fromisoformat(row['entry']))
    for row in signals:
        interest.setdefault(row['symbol'], set()).add(date.fromisoformat(row['entry']))
    print(f'iv names {len(interest)}', flush=True)
    iv_store = _map_symbols(sorted(interest), lambda symbol: _safe_iv(symbol, interest[symbol]))
    for row in signals:
        snap = iv_store.get(row['symbol'], {}).get(row['entry'])
        row['iv'] = None if not snap else snap[0]
        row['iv_base'] = None if not snap else snap[1]
        row['iv_rank'] = None if not snap else snap[2]
        row['quintile'] = None if row['iv_rank'] is None else min(4, int(row['iv_rank'] * 5))
    pool = {}
    for row in universe:
        snap = iv_store.get(row['symbol'], {}).get(row['entry'])
        quintile = None if not snap or snap[2] is None else min(4, int(snap[2] * 5))
        pool.setdefault((date.fromisoformat(row['entry']).year, date.fromisoformat(row['entry']).month, quintile), []).append((row['symbol'], row['entry']))
    rng = np.random.RandomState(SEED)
    pairs = []
    for signal in signals:
        day = date.fromisoformat(signal['entry'])
        choices = pool.get((day.year, day.month, signal.get('quintile'))) or []
        pick = choices[int(rng.randint(0, len(choices)))] if choices else None
        if pick is not None and pick[0] == signal['symbol'] and len(choices) > 1:
            pick = choices[int(rng.randint(0, len(choices)))]
        pairs.append((signal, pick))
    quote_days = {}
    for signal, pick in pairs:
        quote_days.setdefault(signal['symbol'], set()).add(date.fromisoformat(signal['entry']))
        if pick is not None:
            quote_days.setdefault(pick[0], set()).add(date.fromisoformat(pick[1]))
    print(f'chain names {len(quote_days)}', flush=True)
    priced = _map_symbols(
        sorted(quote_days),
        lambda symbol: _safe_price(symbol, quote_days[symbol], sessions, index, earnings.get(symbol.upper(), [])),
    )
    coverage = dict(no_quote=0, no_structure=0, no_exit=0, earnings=0, priced=0)
    enriched = []
    for signal, pick in pairs:
        books, counts = priced.get(signal['symbol'], ({}, coverage))
        for key, value in counts.items():
            pass
        random_books = {}
        if pick is not None and pick[0] in priced:
            random_books = priced[pick[0]][0].get(pick[1], {})
        enriched.append(dict(
            signal=signal,
            books=priced.get(signal['symbol'], ({}, {}))[0].get(signal['entry'], {}),
            random=random_books,
        ))
    for _symbol, (_books, counts) in priced.items():
        for key, value in counts.items():
            coverage[key] = coverage.get(key, 0) + value
    return enriched, coverage


def _map_symbols(symbols, function):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    out = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(function, symbol) for symbol in symbols]
        for done, future in enumerate(as_completed(futures), start=1):
            symbol, payload = future.result()
            out[symbol] = payload
            if done % 250 == 0 or done == len(symbols):
                print(f'names {done}/{len(symbols)}', flush=True)
    return out


def iv_for_symbol(symbol, days: set[date]):
    from insider_resolved import connect
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            cursor.execute(
                '''SELECT qdate, meanIV FROM optionstat
                   WHERE symbol=%s AND qdate BETWEEN '2016-06-01' AND '2026-11-13' ''',
                (symbol,))
            rows = [(_as_date(row['qdate']), _f(row['meanIV'])) for row in cursor.fetchall() if _as_date(row['qdate'])]
    finally:
        connection.close()
    rows.sort()
    iv_dates = [day for day, _value in rows]
    iv = np.array([value for _day, value in rows], dtype=np.float64)
    lookup = {day: i for i, day in enumerate(iv_dates)}
    return symbol, {day.isoformat(): iv_snapshot(iv_dates, iv, day, lookup) for day in days}


def _safe_iv(symbol, days):
    try:
        return iv_for_symbol(symbol, days)
    except Exception as exc:  # noqa: BLE001
        print(f'skip iv {symbol} {type(exc).__name__}', flush=True)
        return symbol, {}


def _safe_price(symbol, days, sessions, index, reactions):
    try:
        return price_symbol(symbol, days, sessions, index, reactions)
    except Exception as exc:  # noqa: BLE001
        print(f'skip chain {symbol} {type(exc).__name__}', flush=True)
        return symbol, ({}, dict(no_quote=0, no_structure=0, no_exit=0, earnings=0, priced=0))


def price_symbol(symbol, days: set[date], sessions, index, reactions):
    plans, counts = _plan(symbol, days, sessions, index, set(reactions))
    return symbol, (plans, counts)


def _plan(symbol, days, sessions, index, reactions):
    from insider_resolved import connect
    counts = dict(no_quote=0, no_structure=0, no_exit=0, earnings=0, priced=0)
    if not days:
        return {}, counts
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            cursor.execute(
                '''SELECT qdate, close FROM stockquote
                   WHERE symbol=%s AND qdate BETWEEN '2017-01-01' AND '2026-11-13' ''',
                (symbol,))
            closes = {_as_date(row['qdate']): _f(row['close']) for row in cursor.fetchall() if _as_date(row['qdate'])}
            marks = ','.join(['%s'] * len(days))
            cursor.execute(
                f'''SELECT qdate, edate, `type` AS side, strike, delta, bid, ask, underlying_last
                    FROM optiondaily WHERE underlying=%s AND qdate IN ({marks})
                    AND DATEDIFF(edate, qdate) BETWEEN 0 AND 50''',
                (symbol, *sorted(days)),
            )
            chain = {}
            for row in cursor.fetchall():
                day = _as_date(row['qdate'])
                chain.setdefault(day, []).append(dict(
                    qdate=day, edate=_as_date(row['edate']), side=row['side'], strike=_f(row['strike']),
                    delta=None if row['delta'] is None else _f(row['delta']),
                    bid=_f(row['bid']), ask=_f(row['ask']), spot=_f(row['underlying_last']),
                ))
    finally:
        connection.close()
    planned = {}
    needed = {}
    for day in days:
        rows = chain.get(day) or []
        spot = next((row['spot'] for row in rows if row['spot'] > 0), closes.get(day, 0.0))
        day_book = {}
        for structure in ('straddle', 'strangle'):
            chosen = select_structure(rows, spot, structure) if rows and spot > 0 else None
            if chosen is None:
                counts['no_structure'] += 1
                continue
            expiry, call, put = chosen
            for hold in HOLDS:
                exit_day = hold_exit(day, expiry, sessions, index, hold)
                if exit_day is None:
                    counts['no_exit'] += 1
                    continue
                if crosses_earnings(day, exit_day, sessions, index, reactions):
                    counts['earnings'] += 1
                    continue
                day_book[(structure, hold)] = dict(call=call, put=put, exit=exit_day, expiry=expiry)
                needed.setdefault(exit_day, []).append((day, (structure, hold)))
        planned[day.isoformat()] = day_book
    if needed:
        _fill_exits(symbol, planned, needed, counts, closes)
    return planned, counts


def _match_leg(rows, leg):
    for row in rows:
        if row['side'] == leg['side'] and row['edate'] == leg['edate'] and abs(row['strike'] - leg['strike']) < 1e-6:
            return row
    return None


def _fill_exits(symbol, trades, missing, counts, closes):
    from insider_resolved import connect
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            marks = ','.join(['%s'] * len(missing))
            cursor.execute(
                f'''SELECT qdate, edate, `type` AS side, strike, bid, ask
                    FROM optiondaily WHERE underlying=%s AND qdate IN ({marks})
                    AND DATEDIFF(edate, qdate) BETWEEN 0 AND 50''',
                (symbol, *sorted(missing)),
            )
            chain = {}
            for row in cursor.fetchall():
                day = _as_date(row['qdate'])
                chain.setdefault(day, []).append(dict(
                    edate=_as_date(row['edate']), side=row['side'], strike=_f(row['strike']),
                    bid=_f(row['bid']), ask=_f(row['ask']),
                ))
    finally:
        connection.close()
    close_dates = sorted(closes)
    for exit_day, jobs in missing.items():
        for day, key in jobs:
            payload = trades[day.isoformat()][key]
            priced_leg = price_combo(
                payload['call'], payload['put'],
                _match_leg(chain.get(exit_day, []), payload['call']),
                _match_leg(chain.get(exit_day, []), payload['put']),
            )
            if priced_leg is None:
                counts['no_quote'] += 1
                trades[day.isoformat()][key] = {}
                continue
            path = [closes[item] for item in close_dates if day <= item <= exit_day and closes.get(item, 0) > 0]
            priced_leg['exit'] = exit_day
            priced_leg['realized'] = realized_vol(path)
            counts['priced'] += 1
            trades[day.isoformat()][key] = priced_leg


def build_report(enriched, coverage, sessions) -> dict:
    index = {day: i for i, day in enumerate(sessions)}
    books = []
    for structure in ('straddle', 'strangle'):
        for source, window, rule in SOURCES:
            for hold in HOLDS:
                for sample in ('walk', 'holdout'):
                    trades = _collect(enriched, source, window, rule, structure, hold, sample)
                    deduped = dedupe_trades(trades, index)
                    lock = 5 if hold == 'd5' else 10 if hold == 'd10' else 20
                    cell = dict(
                        source=source, window=window, rule=rule, structure=structure, hold=hold, sample=sample,
                        quote=summarize(trades, 'quote'), mid=summarize(trades, 'mid'),
                        deduped=summarize(deduped, 'quote'),
                        random=summarize(trades, 'random_quote'),
                        curve=equity_curve(deduped, sessions, lock),
                        iv_premium=_iv_gap(trades), realized_gap=_realized_gap(trades),
                    )
                    books.append(cell)
    chosen = _choose(books)
    return dict(coverage=coverage, books=books, chosen=chosen, verdict=verdict_text(books, chosen))


def _collect(enriched, source, window, rule, structure, hold, sample):
    rows = []
    for item in enriched:
        signal = item['signal']
        if signal['source'] != source or signal['window'] != window or signal['rule'] != rule:
            continue
        day = date.fromisoformat(signal['entry'])
        is_holdout = day >= HOLDOUT_START
        if sample == 'holdout' and not is_holdout:
            continue
        if sample == 'walk' and is_holdout:
            continue
        book = item['books'].get((structure, hold))
        if not book or 'quote' not in book:
            continue
        random_book = item['random'].get((structure, hold)) if item.get('random') else None
        rows.append(dict(
            symbol=signal['symbol'], entry=day, exit=book.get('exit'),
            quote=book['quote'], mid=book['mid'],
            random_quote=None if not random_book else random_book.get('quote'),
            iv=signal.get('iv'), iv_base=signal.get('iv_base'), realized=book.get('realized'),
        ))
    return rows


def _iv_gap(trades):
    gaps = [trade['iv'] / trade['iv_base'] - 1.0 for trade in trades if trade.get('iv') and trade.get('iv_base')]
    if not gaps:
        return None
    return float(np.mean(gaps))


def _realized_gap(trades):
    gaps = [trade['realized'] - trade['iv'] for trade in trades if trade.get('realized') is not None and trade.get('iv')]
    if not gaps:
        return None
    return float(np.mean(gaps))


def _choose(books):
    """Pick the walk-forward straddle with the highest deduped ask/bid mean. The holdout is read after that."""
    pool = [book for book in books if book['structure'] == 'straddle' and book['sample'] == 'walk' and book['deduped']['mean'] is not None]
    if not pool:
        return None
    return max(pool, key=lambda book: book['deduped']['mean'])


def verdict_text(books, chosen) -> str:
    if chosen is None:
        return 'No priced straddle book was available, so there is nothing to trade.'
    held = next((book for book in books if book['structure'] == 'straddle' and book['sample'] == 'holdout'
                 and book['source'] == chosen['source'] and book['window'] == chosen['window']
                 and book['rule'] == chosen['rule'] and book['hold'] == chosen['hold']), None)
    walk_edge = chosen['deduped']['mean'] - (chosen['random']['mean'] or 0)
    hold_edge = None if held is None or held['deduped']['mean'] is None or held['random']['mean'] is None else held['deduped']['mean'] - held['random']['mean']
    ok = (
        chosen['deduped']['mean'] is not None and chosen['deduped']['mean'] > 0
        and held is not None and held['deduped']['mean'] is not None and held['deduped']['mean'] > 0
        and hold_edge is not None and hold_edge > 0
        and held['deduped']['median'] is not None and held['deduped']['median'] > -0.10
    )
    name = f"{chosen['source']} {chosen['window']}-day {chosen['rule']} held {chosen['hold']}"
    hold_text = 'n/a' if hold_edge is None else f'{hold_edge:.3f}'
    if ok:
        return (
            f'{name} is the walk-forward straddle with the highest deduped ask/bid mean. '
            'That same rule still makes money in the holdout and beats the matched random straddles. '
            'It is the only rule the holdout was allowed to confirm.'
        )
    return (
        f'{name} is the walk-forward straddle with the highest deduped ask/bid mean. '
        f'Its edge versus matched random straddles is {walk_edge:.3f} in the walk-forward and {hold_text} in the holdout. '
        'It is not tradable after the ask/bid cost. The holdout book does not clear both a positive mean and the matched random book, or the typical trade still gives back a large share of the premium.'
    )


def render(report: dict) -> str:
    lines = [
        '# Long straddles on the anomaly tail',
        '',
        'Signals are the anomaly-test HBOS scores for the 1-day and 5-day windows, and the isolation-forest scores for the 1-day window, all against the 100-day baseline. Top 1% and top 0.5% use the training-score threshold. Top 4 is the four highest scores that day. The holdout from 2025-11-13 was not used to pick the rule.',
        '',
        'The straddle buys the call and put at the strike closest to the spot. The expiry is the one closest to 25 days, preferring 20-30 days and otherwise staying inside 8-45. The strangle buys the 25-delta call above the spot and the 25-delta put below it, on that same expiry. Entries are the ask and exits are the bid. The other cost is the mid plus 5% at entry and the mid minus 5% at exit. A hold that reaches an earnings reaction is left out of the book.',
        '',
        f"Priced legs: {report['coverage'].get('priced', 0)}. Dropped for no valid bid/ask: {report['coverage'].get('no_quote', 0)}. No listed structure: {report['coverage'].get('no_structure', 0)}. No exit session: {report['coverage'].get('no_exit', 0)}. Left out because the hold crosses earnings: {report['coverage'].get('earnings', 0)}.",
        '',
        'Return is the change in premium. The interval is a ticker bootstrap of the deduped ask/bid trades. Random is the same structure on a filtered name from the same month and the same IV-rank quintile.',
        '',
        '| Signal | Rule | Structure | Hold | Sample | N | Quote mean | Quote median | Win | Deduped mean | Deduped CI | Random mean | Mid mean | IV vs 100-day | Realized minus IV | Terminal | Max DD |',
        '| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for book in report['books']:
        if book['structure'] == 'strangle' and (book['rule'] == 'p05' or book['hold'] == 'd5'):
            continue
        quote, deduped, random = book['quote'], book['deduped'], book['random']
        lines.append(
            f"| {book['source']} {book['window']}d | {book['rule']} | {book['structure']} | {book['hold']} | {book['sample']} | {quote['n']} | {_n(quote['mean'])} | {_n(quote['median'])} | {_n(quote['win'])} | {_n(deduped['mean'])} | {_span(deduped['ci'])} | {_n(random['mean'])} | {_n(book['mid']['mean'])} | {_n(book['iv_premium'])} | {_n(book['realized_gap'])} | {_n(book['curve']['terminal'])} | {_n(book['curve']['max_drawdown'])} |"
        )
    lines += ['', '## Verdict', '', report['verdict'], '']
    return '\n'.join(lines)


def _n(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.3f}'


def _span(pair):
    if not pair or pair[0] is None:
        return 'n/a'
    return f'{pair[0]:.3f} to {pair[1]:.3f}'


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
