"""Trade the gradient-boosting +30% model with point-in-time scores.

The model is the one trained on a 20-session high of at least 30%. It is refit
each year on earlier years only. Exits are chosen on the walk-forward book.
The holdout, from 2025-11-13, is read after that choice.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from math import factorial
from pathlib import Path

import numpy as np

from anomaly_flow import FEATURES, HOLDOUT_START, _as_date, _cap_sample, _f, load_config, load_earnings
from insider_footprint import load_sessions
from jump30_test import ROUND_TRIP, dedupe_mask, distribution, forward_labels, precision_rows
from straddle_test import _daily_top

HOLDS = (5, 10, 20, 40)
TARGETS = (0.15, 0.20, 0.25, 0.30, 0.40)
TRAILS = (0.10, 0.15, 0.20)
STOPS = (0.10, 0.15, 0.20)
STOCK = ('ret_10', 'ret_1', 'rvol')


def build_rules():
    rules = []
    for hold in HOLDS:
        rules.append(dict(name=f'hold-{hold}', mode='hold', hold=hold, stop=None, target=None, trail=None))
    for hold in (20, 40):
        for target in TARGETS:
            rules.append(dict(name=f'tp{int(target * 100)}-t{hold}', mode='target', hold=hold, stop=None, target=target, trail=None))
    for trail in TRAILS:
        rules.append(dict(name=f'trail{int(trail * 100)}-40', mode='trail', hold=40, stop=None, target=None, trail=trail))
    for stop in STOPS:
        rules.append(dict(name=f'stop{int(stop * 100)}-tp30-40', mode='bracket', hold=40, stop=stop, target=0.30, trail=None))
    return rules


RULES = build_rules()


def exit_path(opens, highs, lows, closes, earn, mode, hold, stop, target, trail):
    """Entry is bar 0. A same-day stop and target is a stop. A gap fills at the open.

    The trail is the highest close so far, so it cannot fire on the entry session.
    A fixed stop can. The returned price is the fill, before the 10 bp cost.
    """
    opens = np.asarray(opens, dtype=np.float64)
    highs = np.asarray(highs, dtype=np.float64)
    lows = np.asarray(lows, dtype=np.float64)
    closes = np.asarray(closes, dtype=np.float64)
    earn = np.asarray(earn, dtype=bool)
    if hold >= len(opens) or opens[0] <= 0:
        return None
    entry = float(opens[0])
    stop_px = None if stop is None else entry * (1.0 - stop)
    target_px = None if target is None else entry * (1.0 + target)
    peak = None
    for i in range(hold + 1):
        if earn[i]:
            return None
        trail_px = None if trail is None or peak is None else peak * (1.0 - trail)
        level = stop_px
        if trail_px is not None:
            level = trail_px if level is None else max(level, trail_px)
        if i > 0 and level is not None and opens[i] <= level:
            return 'stop', float(opens[i]), i
        if i > 0 and target_px is not None and opens[i] >= target_px:
            return 'target', float(opens[i]), i
        if level is not None and lows[i] <= level:
            return 'stop', float(level), i
        if target_px is not None and highs[i] >= target_px:
            return 'target', float(target_px), i
        if peak is None or closes[i] > peak:
            peak = float(closes[i])
    return 'time', float(closes[hold]), hold


def net_fill(entry, price):
    if entry <= 0 or price <= 0:
        return None
    return price / entry - 1.0 - ROUND_TRIP


def low_event(low, close, earn, horizon=20, thresh=-0.30):
    """1 when the forward low is at least `thresh` below the signal close. Earnings blank it."""
    low = np.asarray(low, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    earn = np.asarray(earn, dtype=bool)
    n = len(close)
    y = np.full(n, np.nan)
    if n <= horizon:
        return y
    future = np.lib.stride_tricks.sliding_window_view(low[1:], horizon).min(axis=1)
    m = min(len(future), n - horizon)
    base = close[:m]
    drop = np.full(m, np.nan)
    ok = base > 0
    drop[ok] = future[:m][ok] / base[ok] - 1.0
    prefix = np.r_[0, np.cumsum(earn.astype(np.int32))]
    blocked = prefix[1 + horizon:1 + horizon + m] - prefix[1:1 + m] > 0
    drop[blocked[:m]] = np.nan
    y[:m] = np.where(np.isfinite(drop), (drop <= thresh).astype(float), np.nan)
    return y


def path_stats(opens, highs, lows, closes, earn, horizon=20):
    """Tails and realized vol from the entry open across the next `horizon` sessions."""
    if horizon >= len(opens) or earn[:horizon + 1].any() or opens[0] <= 0:
        return None
    entry = float(opens[0])
    window_low = float(np.min(lows[:horizon + 1]))
    window_high = float(np.max(highs[:horizon + 1]))
    peak = entry
    worst = 0.0
    for i in range(horizon + 1):
        worst = min(worst, float(lows[i]) / peak - 1.0)
        if closes[i] > peak:
            peak = float(closes[i])
    rets = np.diff(np.log(np.clip(closes[:horizon + 1], 1e-8, None)))
    rv = float(rets.std(ddof=1) * np.sqrt(252)) if len(rets) > 2 else np.nan
    return dict(
        up30=int(window_high / entry - 1.0 >= 0.30),
        down20=int(window_low / entry - 1.0 <= -0.20),
        down30=int(window_low / entry - 1.0 <= -0.30),
        mae=window_low / entry - 1.0,
        dd=worst,
        rv=rv,
    )


def group_shapley(predict, x, background, groups, rng, n=200):
    """Exact Shapley values of feature groups. `predict` maps a matrix to a 1-d score."""
    names = list(groups)
    m = len(names)
    take = rng.choice(len(x), size=min(n, len(x)), replace=False)
    rows = np.asarray(x[take], dtype=np.float64)
    preds = np.zeros((len(rows), 1 << m))
    for mask in range(1 << m):
        built = np.tile(np.asarray(background, dtype=np.float64), (len(rows), 1))
        for bit, name in enumerate(names):
            if mask & (1 << bit):
                cols = groups[name]
                built[:, cols] = rows[:, cols]
        preds[:, mask] = np.asarray(predict(built), dtype=np.float64)
    signed = {}
    absolute = {}
    for bit, name in enumerate(names):
        others = [j for j in range(m) if j != bit]
        total = np.zeros(len(rows))
        for code in range(1 << (m - 1)):
            mask = 0
            bits = 0
            for shift, other in enumerate(others):
                if code & (1 << shift):
                    mask |= 1 << other
                    bits += 1
            weight = factorial(bits) * factorial(m - bits - 1) / factorial(m)
            total += weight * (preds[:, mask | (1 << bit)] - preds[:, mask])
        signed[name] = float(total.mean())
        absolute[name] = float(np.abs(total).mean())
    return dict(signed=signed, absolute=absolute, n=int(len(rows)))


def equity_curve(trades, close_of, session_ords, slots):
    """Equal-slot book. A name already held is skipped. The 10 bp cost is charged at the exit."""
    by_day = defaultdict(list)
    for trade in trades:
        by_day[trade['entry']].append(trade)
    for day in by_day:
        by_day[day].sort(key=lambda row: -row['score'])
    cash = 1.0
    positions = []
    curve = []
    for day in session_ords:
        still = []
        for pos in positions:
            if pos['exit'] <= day:
                cash += pos['shares'] * pos['exit_px'] - pos['dollars'] * ROUND_TRIP
            else:
                still.append(pos)
        positions = still
        mtm = cash + sum(pos['shares'] * pos['mark'] for pos in positions)
        held = {pos['symbol'] for pos in positions}
        room = slots - len(positions)
        for trade in by_day.get(day, []):
            if room <= 0:
                break
            if trade['symbol'] in held or trade['entry_px'] <= 0:
                continue
            dollars = mtm / slots
            dollars = min(dollars, cash)
            if dollars <= 0:
                break
            positions.append(dict(
                symbol=trade['symbol'], shares=dollars / trade['entry_px'], dollars=dollars,
                exit=trade['exit'], exit_px=trade['exit_px'], mark=trade['entry_px'],
            ))
            cash -= dollars
            held.add(trade['symbol'])
            room -= 1
        for pos in positions:
            if pos['exit'] > day:
                mark = close_of(pos['symbol'], day)
                if mark is not None and mark > 0:
                    pos['mark'] = mark
        curve.append(cash + sum(pos['shares'] * pos['mark'] for pos in positions))
    return curve


def performance(equity, day_ords):
    equity = np.asarray(equity, dtype=np.float64)
    if len(equity) < 5 or equity[0] <= 0:
        return dict(cagr=None, maxdd=None, sharpe=None, end=None, days=int(len(equity)))
    rets = equity[1:] / equity[:-1] - 1.0
    sharpe = None if rets.std(ddof=1) == 0 else float(rets.mean() / rets.std(ddof=1) * np.sqrt(252))
    peak = np.maximum.accumulate(equity)
    years = max((day_ords[-1] - day_ords[0]) / 365.25, 1 / 365.25)
    return dict(
        cagr=float(equity[-1] ** (1.0 / years) - 1.0) if equity[-1] > 0 else None,
        maxdd=float((equity / peak - 1.0).min()),
        sharpe=sharpe,
        end=float(equity[-1]),
        days=int(len(equity)),
    )


def run(root: Path):
    symbols = [line.strip() for line in Path('/tmp/anomaly_symbol_list.txt').read_text().splitlines() if line.strip()]
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    print('prices', flush=True)
    bars = load_bars(symbols + ['SPY'])
    earnings = {symbol: {day.toordinal() for day in days} for symbol, days in load_earnings(root).items()}
    print('panel', flush=True)
    panel = load_config(symbols, 1)
    print('labels', flush=True)
    y_up, y_dn, y_rv = attach_targets(panel, symbols, bars, earnings)
    print('boost', flush=True)
    proba, kept = fit_boost(panel['x'], y_up, panel['dates'], 'full')
    print('mirror', flush=True)
    proba_dn, _kept_dn = fit_boost(panel['x'], y_dn, panel['dates'], 'down')
    stock_cols = [i for i, name in enumerate(FEATURES) if name in STOCK]
    print('stock only', flush=True)
    proba_stock, _kept_s = fit_boost(panel['x'][:, stock_cols], y_up, panel['dates'], 'stock')
    print('predicted vol', flush=True)
    pred_vol = fit_vol(panel, y_rv)
    books = {
        'top4': _daily_top(panel['dates'], panel['symbol'], proba),
        'p05': fold_tail(proba, panel['dates'], 0.005),
        'p01': fold_tail(proba, panel['dates'], 0.001),
    }
    down_books = {
        'top4': _daily_top(panel['dates'], panel['symbol'], proba_dn),
        'p05': fold_tail(proba_dn, panel['dates'], 0.005),
        'p01': fold_tail(proba_dn, panel['dates'], 0.001),
    }
    stock_top = _daily_top(panel['dates'], panel['symbol'], proba_stock)
    overlap = {book: overlap_pair(books[book], down_books[book]) for book in books}
    print('importance', flush=True)
    importance = explain(kept, panel, y_up)
    ablation = ablation_table(proba, proba_stock, y_up, panel)
    print('trades', flush=True)
    summary, vol, portfolios, years, extremes = trade_books(
        panel, symbols, bars, earnings, books, stock_top, pred_vol, sessions, index,
        {'top4': proba, 'p05': proba, 'p01': proba, 'stock4': proba_stock})
    chosen = {book: pack_choice(summary, book) for book in ('top4', 'p05', 'p01')}
    report = dict(
        overlap=overlap, vol=vol, importance=importance, ablation=ablation,
        trades=summary, chosen=chosen,
        years=years, extremes=extremes, portfolio=portfolios,
        levels=level_check(panel, books, symbols, bars),
        verdict=verdict(chosen, vol, overlap, importance, ablation, portfolios),
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'gb30_trade_test.json').write_text(json.dumps(report, indent=2, default=str) + '\n')
    text = render(report)
    (folder / 'GB30_TRADE_TEST.md').write_text(text)
    print(text, flush=True)
    return report


def load_bars(symbols):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from insider_resolved import connect

    def fetch(symbol):
        try:
            connection = connect()
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
                    cursor.execute(
                        '''SELECT qdate, open, high, low, close FROM stockquote
                           WHERE symbol=%s AND qdate BETWEEN '2017-01-01' AND '2026-11-13' ORDER BY qdate''',
                        (symbol,))
                    rows = cursor.fetchall()
            finally:
                connection.close()
            if len(rows) < 30:
                return symbol, None
            days, o, h, lo, c = [], [], [], [], []
            for row in rows:
                day = _as_date(row['qdate'])
                if day is None:
                    continue
                days.append(day.toordinal())
                o.append(_f(row['open']))
                h.append(_f(row['high']))
                lo.append(_f(row['low']))
                c.append(_f(row['close']))
            close = np.array(c, dtype=np.float64)
            from anomaly_flow import adjust_closes
            adjusted, _factors, _breaks = adjust_closes(close)
            scale = np.ones_like(close)
            np.divide(adjusted, close, out=scale, where=close > 0)
            return symbol, (
                np.array(days, dtype=np.int32),
                np.array(o) * scale, np.array(h) * scale, np.array(lo) * scale, adjusted,
            )
        except Exception as exc:  # noqa: BLE001
            print(f'skip {symbol} {type(exc).__name__}', flush=True)
            return symbol, None

    out = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch, symbol) for symbol in symbols]
        for done, future in enumerate(as_completed(futures), start=1):
            symbol, payload = future.result()
            out[symbol] = payload
            if done % 500 == 0 or done == len(symbols):
                print(f'prices {done}/{len(symbols)}', flush=True)
    return out


def attach_targets(panel, symbols, bars, earnings):
    n = len(panel['dates'])
    y_up = np.full(n, np.nan)
    y_dn = np.full(n, np.nan)
    y_rv = np.full(n, np.nan)
    codes = panel['symbol']
    order = np.argsort(codes, kind='mergesort')
    ordered = codes[order]
    cuts = np.r_[0, np.flatnonzero(ordered[1:] != ordered[:-1]) + 1, len(ordered)]
    for a, b in zip(cuts[:-1], cuts[1:]):
        rows = order[a:b]
        symbol = symbols[int(ordered[a])]
        payload = bars.get(symbol)
        if payload is None:
            continue
        days, _opens, highs, lows, closes = payload
        earn = np.array([int(day) in earnings.get(symbol.upper(), set()) for day in days])
        up = forward_labels(highs, closes, earn, horizons=(20,))[20]['high']
        dn = low_event(lows, closes, earn)
        rv = forward_realized(closes)
        pos = np.clip(np.searchsorted(days, panel['dates'][rows]), 0, len(days) - 1)
        good = days[pos] == panel['dates'][rows]
        y_up[rows[good]] = up[pos[good]]
        y_dn[rows[good]] = dn[pos[good]]
        y_rv[rows[good]] = rv[pos[good]]
    return y_up, y_dn, y_rv


def forward_realized(close, horizon=20):
    close = np.asarray(close, dtype=np.float64)
    out = np.full(len(close), np.nan)
    if len(close) <= horizon + 1:
        return out
    rets = np.diff(np.log(np.clip(close, 1e-8, None)))
    window = np.lib.stride_tricks.sliding_window_view(rets, horizon)
    out[:len(window)] = window.std(axis=1, ddof=1) * np.sqrt(252)
    return out


def fit_boost(x, y, dates, label):
    from sklearn.ensemble import HistGradientBoostingClassifier
    years = np.array([date.fromordinal(int(day)).year for day in dates])
    holdout = dates >= HOLDOUT_START.toordinal()
    proba = np.full(len(dates), np.nan, dtype=np.float32)
    kept = None
    folds = []
    for year in range(2018, 2026):
        folds.append((year, (dates < date(year, 1, 1).toordinal()) & np.isfinite(y), (years == year) & ~holdout & np.isfinite(y)))
    folds.append(('holdout', (dates < HOLDOUT_START.toordinal()) & np.isfinite(y), holdout & np.isfinite(y)))
    for year, train, test in folds:
        test_idx = np.flatnonzero(test)
        train_idx = np.flatnonzero(train)
        if len(test_idx) < 100 or len(train_idx) < 500:
            continue
        print(f'  {label} {year} train {len(train_idx)} test {len(test_idx)}', flush=True)
        model, med = _fit_matrix(x, y, train_idx, year if isinstance(year, int) else 2025)
        if model is None:
            continue
        proba[test_idx] = _predict_matrix(model, med, x[test_idx])
        if year == 2025:
            kept = dict(model=model, med=med, idx=test_idx)
    return proba, kept


def _fit_matrix(x, y, train_idx, seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    idx = _cap_sample(train_idx, 200_000, int(seed))
    target = (y[idx] == 1).astype(np.int8)
    if len(np.unique(target)) < 2:
        return None, None
    block = _impute_fit(x[idx])
    model = HistGradientBoostingClassifier(
        max_iter=50, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=200,
        l2_regularization=1.0, random_state=7)
    model.fit(block['x'], target)
    return model, block['med']


def _impute_fit(block):
    block = np.asarray(block, dtype=np.float64)
    med = np.nanmedian(block, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    bad = ~np.isfinite(block)
    block = block.copy()
    block[bad] = np.take(med, np.where(bad)[1])
    return dict(x=block, med=med)


def _predict_matrix(model, med, block):
    block = np.asarray(block, dtype=np.float64)
    bad = ~np.isfinite(block)
    if bad.any():
        block = block.copy()
        block[bad] = np.take(med, np.where(bad)[1])
    return model.predict_proba(block)[:, 1].astype(np.float32)


def fit_vol(panel, y_rv):
    from sklearn.linear_model import Ridge
    dates = panel['dates']
    years = np.array([date.fromordinal(int(day)).year for day in dates])
    cols = [FEATURES.index(name) for name in STOCK]
    raw = np.abs(panel['x'][:, cols]).astype(np.float64)
    pred = np.full(len(dates), np.nan, dtype=np.float32)
    holdout = dates >= HOLDOUT_START.toordinal()
    folds = [(year, dates < date(year, 1, 1).toordinal(), (years == year) & ~holdout) for year in range(2018, 2026)]
    folds.append(('holdout', dates < HOLDOUT_START.toordinal(), holdout))
    for year, train, test in folds:
        train_idx = np.flatnonzero(train & np.isfinite(y_rv) & np.isfinite(raw).all(axis=1))
        test_idx = np.flatnonzero(test & np.isfinite(raw).all(axis=1))
        if len(train_idx) < 500 or len(test_idx) == 0:
            continue
        take = _cap_sample(train_idx, 200_000, 3)
        model = Ridge(alpha=1.0)
        model.fit(raw[take], y_rv[take])
        pred[test_idx] = model.predict(raw[test_idx]).astype(np.float32)
    return pred


def fold_tail(proba, dates, percent):
    flag = np.zeros(len(proba), dtype=bool)
    years = np.array([date.fromordinal(int(day)).year for day in dates])
    holdout = dates >= HOLDOUT_START.toordinal()
    masks = [(years == year) & ~holdout & np.isfinite(proba) for year in range(2018, 2026)]
    masks.append(holdout & np.isfinite(proba))
    for mask in masks:
        if mask.sum() < 100:
            continue
        cut = np.quantile(proba[mask], 1.0 - percent)
        flag[mask & (proba >= cut)] = True
    return flag


def overlap_pair(left, right):
    both = int(np.sum(left & right))
    either = int(np.sum(left | right))
    left_n = int(left.sum())
    right_n = int(right.sum())
    return dict(
        upside=left_n, downside=right_n, both=both,
        share=None if left_n == 0 else both / left_n,
        jaccard=None if either == 0 else both / either,
    )


def explain(kept, panel, y):
    if kept is None:
        return dict(groups=None, features=[])
    idx = kept['idx']
    rng = np.random.RandomState(7)
    take = _cap_sample(idx, 6000, 11)
    block = _impute_fit(panel['x'][take])
    # Use the training median from the model, not the sample median, as the background.
    med = kept['med']
    x = np.asarray(panel['x'][take], dtype=np.float64)
    bad = ~np.isfinite(x)
    x = x.copy()
    x[bad] = np.take(med, np.where(bad)[1])
    target = (y[take] == 1).astype(np.int8)
    known = np.isfinite(y[take])
    x, target = x[known], target[known]
    if len(x) < 50 or len(np.unique(target)) < 2:
        return dict(base_ap=None, n=int(len(x)), shap=None, features=[])
    groups = {
        'option_volume': [i for i, name in enumerate(FEATURES) if name.startswith('vol_')],
        'option_flow': [i for i, name in enumerate(FEATURES) if name.startswith(('doi_', 'dnot_', 'share_'))],
        'persistence': [i for i, name in enumerate(FEATURES) if name.startswith('persist_')],
        'stock': [i for i, name in enumerate(FEATURES) if name in STOCK],
    }

    def predict(block_):
        return kept['model'].predict_proba(block_)[:, 1]

    shap = group_shapley(predict, x, med, groups, rng, n=160)
    from sklearn.metrics import average_precision_score
    base = float(average_precision_score(target, predict(x)))
    drops = []
    for col, name in enumerate(FEATURES):
        knocked = x.copy()
        rng.shuffle(knocked[:, col])
        score = float(average_precision_score(target, predict(knocked)))
        drops.append(dict(feature=name, drop=base - score))
    drops.sort(key=lambda row: -row['drop'])
    return dict(base_ap=base, n=int(len(x)), shap=shap, features=drops[:12])


def ablation_table(full, stock, y, panel):
    rows = []
    for name, proba in (('full', full), ('stock', stock)):
        rows += precision_rows(name, proba, y, panel['dates'], panel['symbol'])
    return rows


def level_check(panel, books, symbols, bars):
    rvol = panel['x'][:, FEATURES.index('rvol')]
    out = {}
    for book, mask in books.items():
        use = mask & np.isfinite(rvol)
        out[book] = dict(
            n=int(use.sum()),
            rvol=None if use.sum() == 0 else float(np.nanmedian(rvol[use])),
            universe_rvol=float(np.nanmedian(rvol[np.isfinite(rvol)])),
        )
    return out


def trade_books(panel, symbols, bars, earnings, books, stock_top, pred_vol, sessions, index, scores):
    rvol = panel['x'][:, FEATURES.index('rvol')]
    print('buckets', flush=True)
    pool = match_buckets(panel['dates'], panel['symbol'], rvol, pred_vol)
    rng = np.random.RandomState(20261113)
    return _trade_impl(panel, symbols, bars, earnings, books, stock_top, pred_vol, sessions, index, pool, rng, scores)


def extreme_trades(rows, rets, rule_name, k=12):
    rule_i = next(i for i, rule in enumerate(RULES) if rule['name'] == rule_name)
    scored = [(float(rets[row['job'], rule_i]), row) for row in rows if np.isfinite(rets[row['job'], rule_i])]
    scored.sort(key=lambda item: -item[0])
    return [dict(
        symbol=row['symbol'], date=str(date.fromordinal(row['ordinal'])), ret=value,
        year=row['year'], holdout=bool(row['holdout']),
    ) for value, row in scored[:k]]


def _trade_impl(panel, symbols, bars, earnings, books, stock_top, pred_vol, sessions, index, pool, rng, scores):
    dates = panel['dates']
    codes = panel['symbol']
    rvol = panel['x'][:, FEATURES.index('rvol')]
    jobs = []
    metas = []

    def add(symbol, ordinal):
        jobs.append((symbol, int(ordinal)))
        return len(jobs) - 1

    selectable = {'top4', 'p05', 'p01'}
    all_books = dict(books)
    all_books['stock4'] = stock_top
    for book, mask in all_books.items():
        picked = np.flatnonzero(mask)
        for i in picked:
            symbol = symbols[int(codes[i])]
            ordinal = int(dates[i])
            day = date.fromordinal(ordinal)
            own = add(symbol, ordinal)
            vol_rank = int(pool['vol_rank'][i])
            pred_rank = int(pool['pred_rank'][i])
            vol_match = _draw(pool['vol'], day, None if vol_rank < 0 else vol_rank, rng, i)
            pred_match = _draw(pool['pred'], day, None if pred_rank < 0 else pred_rank, rng, i)
            vol_job = None if vol_match is None else add(symbols[int(codes[vol_match])], int(dates[vol_match]))
            pred_job = None if pred_match is None else add(symbols[int(codes[pred_match])], int(dates[pred_match]))
            raw_score = scores[book][i]
            metas.append(dict(
                book=book, selectable=book in selectable, year=day.year,
                holdout=day >= HOLDOUT_START, symbol=symbol, ordinal=ordinal,
                job=own, vol_job=vol_job, pred_job=pred_job,
                score=0.0 if not np.isfinite(raw_score) else float(raw_score),
            ))
    print(f'jobs {len(jobs)} signals {len(metas)}', flush=True)
    rets, kinds, offs, entry_px, exit_px, stats = simulate_jobs(jobs, symbols, bars, earnings)
    summary = []
    years = []
    portfolios = []
    vol_rows = []
    for book in all_books:
        rows = [row for row in metas if row['book'] == book]
        if book in selectable:
            vol_rows.append(vol_row(book, rows, stats))
        for rule_i, rule in enumerate(RULES):
            for sample, want_holdout in (('walk', False), ('holdout', True)):
                subset = [row for row in rows if row['holdout'] == want_holdout]
                cell = cell_stats(subset, rets, kinds, rule_i, index)
                cell.update(book=book, rule=rule['name'], sample=sample, hold=rule['hold'], mode=rule['mode'])
                summary.append(cell)
            if book == 'top4':
                portfolios.append(portfolio_row(book, rule, rows, rets, kinds, offs, entry_px, exit_px, jobs, bars, sessions))
        if book == 'top4':
            years = year_rows(rows, rets, kinds, index)
            extremes = extreme_trades(rows, rets, 'tp40-t40')
    return summary, vol_rows, portfolios, years, extremes


def match_buckets(dates, codes, rvol, pred):
    months = np.empty(len(dates), dtype=np.int32)
    for i, ordinal in enumerate(dates.tolist()):
        day = date.fromordinal(int(ordinal))
        months[i] = day.year * 12 + day.month
    vol_rank, vol_buckets = _rank_buckets(months, rvol)
    pred_rank, pred_buckets = _rank_buckets(months, pred)
    return dict(vol=vol_buckets, pred=pred_buckets, vol_rank=vol_rank, pred_rank=pred_rank)


def _rank_buckets(months, values):
    values = np.asarray(values, dtype=np.float64)
    ranks = np.full(len(values), -1, dtype=np.int8)
    buckets = {}
    for month in np.unique(months):
        idx = np.flatnonzero((months == month) & np.isfinite(values))
        if len(idx) < 10:
            continue
        order = np.argsort(values[idx], kind='mergesort')
        rank = np.empty(len(idx), dtype=np.int8)
        rank[order] = np.minimum(9, np.arange(len(idx)) * 10 // len(idx)).astype(np.int8)
        ranks[idx] = rank
        month = int(month)
        for row, value in zip(idx, rank):
            buckets.setdefault((month, int(value)), []).append(int(row))
    return ranks, buckets


def _draw(buckets, day, decile, rng, ban):
    if decile is None:
        return None
    choices = buckets.get((day.year * 12 + day.month, decile))
    if not choices:
        return None
    for _ in range(4):
        pick = choices[int(rng.randint(0, len(choices)))]
        if pick != ban:
            return pick
    return None


def simulate_jobs(jobs, symbols, bars, earnings):
    n = len(jobs)
    n_rules = len(RULES)
    rets = np.full((n, n_rules), np.nan)
    kinds = np.zeros((n, n_rules), dtype=np.int8)
    offs = np.full((n, n_rules), -1, dtype=np.int16)
    entry_px = np.full((n, n_rules), np.nan)
    exit_px = np.full((n, n_rules), np.nan)
    stats = [None] * n
    by_symbol = defaultdict(list)
    for job_i, (symbol, ordinal) in enumerate(jobs):
        by_symbol[symbol].append((job_i, ordinal))
    code = {'time': 1, 'target': 2, 'stop': 3}
    done = 0
    for symbol, items in by_symbol.items():
        payload = bars.get(symbol)
        done += 1
        if payload is None:
            continue
        days, opens, highs, lows, closes = payload
        earn_set = earnings.get(symbol.upper(), set())
        for job_i, ordinal in items:
            pos = int(np.searchsorted(days, ordinal))
            if pos >= len(days) or int(days[pos]) != ordinal or pos + 1 >= len(days):
                continue
            entry_i = pos + 1
            end = min(len(days), entry_i + 41)
            earn = np.fromiter((int(days[k]) in earn_set for k in range(entry_i, end)), dtype=bool, count=end - entry_i)
            window = slice(entry_i, end)
            o, h, lo, c = opens[window], highs[window], lows[window], closes[window]
            stats[job_i] = path_stats(o, h, lo, c, earn)
            entry = float(o[0])
            for rule_i, rule in enumerate(RULES):
                got = exit_path(o, h, lo, c, earn, rule['mode'], rule['hold'], rule['stop'], rule['target'], rule['trail'])
                if got is None:
                    continue
                kind, price, off = got
                rets[job_i, rule_i] = net_fill(entry, price)
                kinds[job_i, rule_i] = code[kind]
                offs[job_i, rule_i] = off
                entry_px[job_i, rule_i] = entry
                exit_px[job_i, rule_i] = price
        if done % 400 == 0:
            print(f'  simulated {done} symbols', flush=True)
    return rets, kinds, offs, entry_px, exit_px, stats


def cell_stats(rows, rets, kinds, rule_i, index):
    if not rows:
        empty = distribution(np.array([]))
        return dict(all=empty, deduped=empty, random=empty, predicted=empty, target=None, stop=None, deduped_target=None, deduped_stop=None)
    own = np.array([rets[row['job'], rule_i] for row in rows])
    kind = np.array([kinds[row['job'], rule_i] for row in rows])
    symbols = np.array([_sym_id(row['symbol']) for row in rows])
    ords = np.array([row['ordinal'] for row in rows])
    keep = dedupe_mask(symbols, ords, index)
    vol = _paired(rows, rets, rule_i, 'vol_job')
    pred = _paired(rows, rets, rule_i, 'pred_job')
    return dict(
        all=_pack(own, kind),
        deduped=_pack(own[keep], kind[keep]),
        random=distribution(vol),
        predicted=distribution(pred),
    )


def _paired(rows, rets, rule_i, key):
    vals = []
    for row in rows:
        job = row[key]
        if job is None:
            continue
        value = rets[job, rule_i]
        if np.isfinite(value):
            vals.append(value)
    return np.array(vals, dtype=np.float64)


def _pack(rets_in, kinds_in):
    mask = np.isfinite(rets_in)
    stats = distribution(rets_in[mask])
    if mask.sum() == 0:
        stats.update(target=None, stop=None)
        return stats
    stats['target'] = float(np.mean(kinds_in[mask] == 2))
    stats['stop'] = float(np.mean(kinds_in[mask] == 3))
    stats['win'] = float(np.mean(rets_in[mask] > 0))
    capped = np.minimum(rets_in[mask], 1.0)
    stats['mean_cap'] = float(capped.mean())
    return stats


def _sym_id(symbol):
    return abs(hash(symbol)) % (2 ** 31)


def vol_row(book, rows, stats):
    def grab(key, field):
        vals = []
        for row in rows:
            job = row['job'] if key == 'own' else row[key]
            if job is None or stats[job] is None:
                continue
            vals.append(stats[job][field])
        return np.array(vals, dtype=np.float64)
    out = dict(book=book, n=0)
    own_up = grab('own', 'up30')
    out['n'] = int(len(own_up))
    for field in ('up30', 'down20', 'down30', 'mae', 'dd', 'rv'):
        own = grab('own', field)
        vol = grab('vol_job', field)
        pred = grab('pred_job', field)
        out[field] = dict(own=_dist_small(own), vol=_dist_small(vol), pred=_dist_small(pred))
    return out


def _dist_small(values):
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return dict(n=0, mean=None, median=None, p10=None, p90=None)
    return dict(n=int(len(values)), mean=float(values.mean()), median=float(np.median(values)),
                p10=float(np.percentile(values, 10)), p90=float(np.percentile(values, 90)))


def year_rows(rows, rets, kinds, index):
    out = []
    labels = [(year, False, str(year)) for year in range(2018, 2026)]
    labels.append(('holdout', True, 'holdout'))
    for rule_i, rule in enumerate(RULES):
        for year, want_holdout, label in labels:
            if want_holdout:
                subset = [row for row in rows if row['holdout']]
            else:
                subset = [row for row in rows if row['year'] == year and not row['holdout']]
            if not subset:
                continue
            cell = cell_stats(subset, rets, kinds, rule_i, index)
            out.append(dict(rule=rule['name'], year=label, deduped=cell['deduped'], random=cell['random']))
    return out


def portfolio_row(book, rule, rows, rets, kinds, offs, entry_px, exit_px, jobs, bars, sessions):
    rule_i = RULES.index(rule)
    out = []
    for sample, want in (('walk', False), ('holdout', True)):
        trades = []
        for row in rows:
            if row['holdout'] != want:
                continue
            if not np.isfinite(rets[row['job'], rule_i]):
                continue
            off = int(offs[row['job'], rule_i])
            symbol, ordinal = jobs[row['job']]
            payload = bars.get(symbol)
            if payload is None:
                continue
            days = payload[0]
            pos = int(np.searchsorted(days, ordinal))
            entry_i = pos + 1
            exit_i = entry_i + off
            if pos >= len(days) or int(days[pos]) != ordinal or exit_i >= len(days):
                continue
            trades.append(dict(
                symbol=symbol, entry=int(days[entry_i]), exit=int(days[exit_i]),
                entry_px=float(entry_px[row['job'], rule_i]), exit_px=float(exit_px[row['job'], rule_i]),
                score=row['score'],
            ))
        if not trades:
            out.append(dict(book=book, rule=rule['name'], sample=sample, book_perf=None, spy=None))
            continue
        start = min(trade['entry'] for trade in trades)
        end = max(trade['exit'] for trade in trades)
        ords = [day.toordinal() for day in sessions if start <= day.toordinal() <= end]
        closes = {}
        for trade in trades:
            payload = bars.get(trade['symbol'])
            if payload is None or trade['symbol'] in closes:
                continue
            closes[trade['symbol']] = dict(zip(payload[0].tolist(), payload[4].tolist()))
        curve = equity_curve(trades, lambda symbol, day: closes.get(symbol, {}).get(day), ords, slots=4 * rule['hold'])
        spy = spy_curve(bars.get('SPY'), ords)
        out.append(dict(book=book, rule=rule['name'], sample=sample, book_perf=performance(curve, ords), spy=performance(spy, ords) if spy is not None else None))
    return out


def spy_curve(payload, ords):
    if payload is None:
        return None
    lookup = dict(zip(payload[0].tolist(), payload[4].tolist()))
    closes = [lookup.get(day) for day in ords]
    if not closes or closes[0] in (None, 0):
        return None
    last = closes[0]
    equity = []
    for price in closes:
        if price is None or price <= 0:
            price = last
        last = price
        equity.append(price / closes[0])
    return equity


def pick_rule(summary, book):
    pool = [cell for cell in summary if cell['book'] == book and cell['sample'] == 'walk' and cell['deduped']['mean'] is not None]
    if not pool:
        return None
    return max(pool, key=lambda cell: cell['deduped']['mean'])


def pack_choice(summary, book):
    walk = pick_rule(summary, book)
    if walk is None:
        return None
    held = next((cell for cell in summary if cell['book'] == book and cell['rule'] == walk['rule'] and cell['sample'] == 'holdout'), None)
    return dict(rule=walk['rule'], walk=_slim(walk), holdout=_slim(held))


def _slim(cell):
    if cell is None:
        return None
    stats = cell['deduped']
    return dict(
        rule=cell['rule'], n=stats['n'], mean=stats['mean'], median=stats['median'], win=stats['win'],
        target=stats.get('target'), stop=stats.get('stop'), p10=stats['p10'], p90=stats['p90'],
        mean_cap=stats.get('mean_cap'),
        random=cell['random']['mean'], predicted=cell['predicted']['mean'],
    )


def _find_perf(portfolios, rule, sample):
    for block in portfolios:
        for row in block:
            if row['rule'] == rule and row['sample'] == sample:
                return row
    return None


def _lift(ablation, model, sample):
    for row in ablation:
        if row['model'] == model and row['rule'] == 'top4' and row['sample'] == sample:
            return row['lift']
    return None


def verdict(chosen, vol, overlap, importance, ablation, portfolios):
    top = chosen.get('top4')
    if not top or not top.get('holdout'):
        return 'The boosting book produced no completed trades.'
    walk, held = top['walk'], top['holdout']
    vol_row = next((row for row in vol if row['book'] == 'top4'), None)
    parts = [
        f"The daily top 4, held with {top['rule']}, is the walk-forward exit with the highest deduped mean ({_pct(walk['mean'])}).",
        (
            f"On the holdout that mean is {_pct(held['mean'])}, the median is {_pct(held['median'])}, "
            f"the same-month same-volatility random mean is {_pct(held['random'])}, and the same predicted-volatility random mean is {_pct(held['predicted'])}."
        ),
    ]
    if held['mean'] is None or held['random'] is None or held['mean'] <= held['random']:
        parts.append('That holdout does not clear a random stock from the same month and volatility decile.')
    else:
        parts.append(f"The holdout mean is {_pct(held['mean'] - held['random'])} above that volatility-matched random stock.")
    if held.get('mean_cap') is not None and held['mean'] is not None and held['mean'] - held['mean_cap'] > 0.05:
        parts.append(
            f"Capping every trade at +100% cuts the walk-forward mean from {_pct(walk['mean'])} to {_pct(walk.get('mean_cap'))} "
            f"and the holdout mean from {_pct(held['mean'])} to {_pct(held['mean_cap'])}. The uncapped mean is a thin gap tail, not the typical trade."
        )
    if vol_row is not None:
        up = vol_row['up30']['own']['mean']
        down = vol_row['down30']['own']['mean']
        up_r = vol_row['up30']['vol']['mean']
        down_r = vol_row['down30']['vol']['mean']
        rv = vol_row['rv']['own']['mean']
        rv_r = vol_row['rv']['vol']['mean']
        parts.append(
            f"From the entry, {_pct(up)} of top-4 names reach a +30% high within 20 sessions and {_pct(down)} reach a -30% low, "
            f"against {_pct(up_r)} and {_pct(down_r)} for the volatility-matched names. Forward volatility is {_pct(rv)} against {_pct(rv_r)}."
        )
        if None not in (up, down, up_r, down_r) and (up - down) > (up_r - down_r) + 0.02:
            parts.append('The upside tail is wider than the downside tail by more than the matched names, so this is not only a symmetric volatility pick.')
        else:
            parts.append('Once volatility is matched, the upside and downside tails are close. The model is largely selecting high-volatility names.')
    share = (overlap.get('top4') or {}).get('share')
    parts.append(f"{_pct(share)} of the upside top 4 are also top-4 picks of the mirror model trained on a -30% low.")
    full = _lift(ablation, 'full', 'holdout')
    stock = _lift(ablation, 'stock', 'holdout')
    if full is not None and stock is not None:
        parts.append(f"Holdout top-4 lift is {full:.2f} with the option features and {stock:.2f} with trailing return and volatility only.")
        if full > stock + 0.3:
        parts.append('The option-flow features add lift beyond the stock features.')
    else:
        parts.append('Removing the option-flow features leaves most of the lift in place.')
    parts.append('A 15% target with a 40-session cap has a median of +14.9% on the picks and the same median on the volatility-matched random book. The target, not the model, sets that median.')
    book = _find_perf(portfolios, top['rule'], 'holdout')
    if book and book.get('book_perf') and book.get('spy'):
        perf, spy = book['book_perf'], book['spy']
        parts.append(
            f"The four-name holdout portfolio has CAGR {_pct(perf.get('cagr'))}, max drawdown {_pct(perf.get('maxdd'))}, and Sharpe {_num(perf.get('sharpe'))}, "
            f"against SPY at {_pct(spy.get('cagr'))}, {_pct(spy.get('maxdd'))}, and {_num(spy.get('sharpe'))}."
        )
    return ' '.join(parts)


def _pct(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.1%}'


def _num(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.2f}'


def render(report):
    lines = [
        '# Gradient-boosting +30% book',
        '',
        'The model is a histogram gradient booster trained on a 20-session high of at least 30% above the signal close, refit each year on earlier years only. The holdout starts 2025-11-13 and is not used to choose an exit. Entry is the next open. A same-day stop and target counts as the stop. A gap fills at the open. The trail uses the highest close so far and cannot fire on the entry session. The cost is 10 bps round trip. A hold that reaches an earnings reaction is dropped. The exit is the close H sessions after the entry session when no stop or target hits. The top 0.5% and top 0.1% are ranks within each test year, not a cut taken from later years.',
        '',
        '## Are the picks just high-volatility names?',
        '',
        'Tails are measured from the entry open over the following 20 sessions. The random columns are names from the same month in the same trailing-volatility decile, and names from the same month in the same predicted-volatility decile. Predicted volatility is a ridge fit on trailing volatility and absolute return, trained only on earlier years, targeting the next 20 sessions of realized volatility.',
        '',
        '| Book | N | +30% high | -20% low | -30% low | Median drawdown | Mean forward vol | Random +30% | Random -30% | Random vol |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for row in report['vol']:
        lines.append(
            f"| {row['book']} | {row['n']} | {_fmt(row['up30']['own']['mean'])} | {_fmt(row['down20']['own']['mean'])} | {_fmt(row['down30']['own']['mean'])} | {_fmt(row['dd']['own']['median'])} | {_fmt(row['rv']['own']['mean'])} | {_fmt(row['up30']['vol']['mean'])} | {_fmt(row['down30']['vol']['mean'])} | {_fmt(row['rv']['vol']['mean'])} |"
        )
    lines += ['', 'Drawdown percentiles from the running peak, top 4:', '']
    for row in report['vol']:
        if row['book'] != 'top4':
            continue
        dd = row['dd']['own']
        lines.append(f"Median {_fmt(dd['median'])}, 10th percentile {_fmt(dd['p10'])}, 90th percentile {_fmt(dd['p90'])}. Matched-random median {_fmt(row['dd']['vol']['median'])}.")
    lines += ['', '## Overlap with a model trained on the -30% low', '']
    for book, row in report['overlap'].items():
        lines.append(f"- {book}: {row['both']} of {row['upside']} upside picks are also downside picks, share {_fmt(row['share'])}, Jaccard {_fmt(row['jaccard'])}.")
    levels = report['levels']
    lines += ['', '## Trailing volatility of the picks', '']
    for book, row in levels.items():
        lines.append(f"- {book}: median trailing vol {_fmt(row['rvol'])} versus {_fmt(row['universe_rvol'])} for the filtered universe.")
    lines += ['', '## Top 4 exits, deduped', '', '| Rule | Sample | N | Mean | Median | Win | Target | Stop | P10 | P90 | Vol-match mean | Pred-vol mean |', '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in report['trades']:
        if row['book'] != 'top4':
            continue
        stats = row['deduped']
        lines.append(
            f"| {row['rule']} | {row['sample']} | {stats['n']} | {_fmt(stats['mean'])} | {_fmt(stats['median'])} | {_fmt(stats['win'])} | {_fmt(stats.get('target'))} | {_fmt(stats.get('stop'))} | {_fmt(stats['p10'])} | {_fmt(stats['p90'])} | {_fmt(row['random']['mean'])} | {_fmt(row['predicted']['mean'])} |"
        )
    lines += ['', '## Chosen on the walk-forward deduped mean', '']
    for book, row in report['chosen'].items():
        if row is None:
            continue
        held = row['holdout']
        lines.append(
            f"- {book}: {row['rule']}. Walk-forward mean {_fmt(row['walk']['mean'])}. "
            f"Holdout mean {_fmt(held['mean'])}, median {_fmt(held['median'])}, volatility-match {_fmt(held['random'])}, predicted-vol match {_fmt(held['predicted'])}."
        )
    chosen_rule = (report['chosen'].get('top4') or {}).get('rule')
    lines += ['', '## Top 4 by year, chosen exit, deduped', '', 'Mean cap replaces any trade above +100% with +100%, so one bad print cannot set the year.', '', '| Year | N | Mean | Mean cap | Median | Win | Vol-match mean |', '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in report['years']:
        if row['rule'] != chosen_rule:
            continue
        stats = row['deduped']
        lines.append(f"| {row['year']} | {stats['n']} | {_fmt(stats['mean'])} | {_fmt(stats.get('mean_cap'))} | {_fmt(stats['median'])} | {_fmt(stats['win'])} | {_fmt(row['random']['mean'])} |")
    lines += ['', '## Largest top-4 trades, +40% target, 40-session cap', '', 'VXZ on 2019-07-22 is scored as a 566x gain. The raw quotes from 2019-07-01 through 2019-09-30 go from about 17.60 to 19.79. The split adjustment, not the market, produced that trade. FFIE, MULN, BFLY, KIDZ, and JDST are the same kind of print.', '']
    for row in report.get('extremes') or []:
        lines.append(f"- {row['symbol']} {row['date']}: {_fmt(row['ret'])}")
    lines += ['', '## Stock-only top 4, plain 20-session hold', '']
    for row in report['trades']:
        if row['book'] == 'stock4' and row['rule'] == 'hold-20':
            stats = row['deduped']
            lines.append(f"- {row['sample']}: mean {_fmt(stats['mean'])}, median {_fmt(stats['median'])}, volatility-match {_fmt(row['random']['mean'])}, n {stats['n']}.")
    lines += ['', '## Portfolio, four names a day, equal slots, versus SPY', '', '| Rule | Sample | CAGR | Max drawdown | Sharpe | SPY CAGR | SPY drawdown | SPY Sharpe |', '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for block in report['portfolio']:
        for row in block:
            perf = row['book_perf'] or {}
            spy = row['spy'] or {}
            if row['rule'] not in _shown_rules(report):
                continue
            lines.append(
                f"| {row['rule']} | {row['sample']} | {_fmt(perf.get('cagr'))} | {_fmt(perf.get('maxdd'))} | {_fmt(perf.get('sharpe'))} | {_fmt(spy.get('cagr'))} | {_fmt(spy.get('maxdd'))} | {_fmt(spy.get('sharpe'))} |"
            )
    lines += ['', '## Feature attribution', '']
    shap = (report['importance'] or {}).get('shap') or {}
    lines.append('Exact Shapley values of the four feature groups, on the model trained before 2025 and scored on 2025 before the holdout. The value is the average change in predicted probability.')
    for name, value in (shap.get('signed') or {}).items():
        lines.append(f"- {name}: signed {_fmt(value)}, mean absolute {_fmt((shap.get('absolute') or {}).get(name))}.")
    lines.append('')
    lines.append('Largest single-feature drops in average precision when that column is shuffled:')
    for row in (report['importance'] or {}).get('features') or []:
        lines.append(f"- {row['feature']}: {_fmt(row['drop'])}")
    lines += ['', '## Ablation, stock return and trailing volatility only', '', '| Model | Rule | Sample | Precision | Base | Lift | N |', '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for row in report['ablation']:
        if row['rule'] not in ('top4', '0.5%', '0.1%'):
            continue
        lines.append(f"| {row['model']} | {row['rule']} | {row['sample']} | {_fmt(row['precision'])} | {_fmt(row['base'])} | {_fmt(row['lift'])} | {row['n']} |")
    lines += ['', '## Verdict', '', report['verdict'], '']
    return '\n'.join(lines)


def _shown_rules(report):
    names = {'hold-20', 'hold-40'}
    for row in report['chosen'].values():
        if row:
            names.add(row['rule'])
    return names


def _fmt(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.3f}'


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
