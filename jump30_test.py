"""+30% events, anomaly enrichment, a direct classifier, and a timed stock hold.

The trade has no stop and no target. It is bought at the next open and sold at
the close a fixed number of sessions later. The holdout is not used to pick
the signal or the hold.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np

from anomaly_flow import (
    FEATURES, HOLDOUT_START, _as_date, _cap_sample, _f, _folds, _score_pair, clustered_lift, load_config, load_earnings,
)
from insider_footprint import load_sessions
from straddle_test import _daily_top

HORIZONS = (5, 10, 20, 40)
HOLDS = (5, 10, 20, 40)
ROUND_TRIP = 0.001
WINDOWS = (1, 3, 5)
SOURCES = (
    ('hbos', 1, 'p1'), ('hbos', 1, 'p05'), ('hbos', 1, 'top4'),
    ('hbos', 3, 'p1'), ('hbos', 3, 'p05'), ('hbos', 3, 'top4'),
    ('hbos', 5, 'p1'), ('hbos', 5, 'p05'), ('hbos', 5, 'top4'),
    ('iforest', 1, 'p1'), ('iforest', 1, 'p05'), ('iforest', 1, 'top4'),
    ('iforest', 3, 'p1'), ('iforest', 3, 'p05'), ('iforest', 3, 'top4'),
    ('iforest', 5, 'p1'), ('iforest', 5, 'p05'), ('iforest', 5, 'top4'),
)


def forward_labels(high, close, earn, horizons=HORIZONS):
    """High-based and close-to-close gains. An earnings print inside the window blanks the label."""
    high = np.asarray(high, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    earn = np.asarray(earn, dtype=bool)
    n = len(close)
    prefix = np.r_[0, np.cumsum(earn.astype(np.int32))]
    out = {}
    for horizon in horizons:
        high_y = np.full(n, np.nan)
        close_y = np.full(n, np.nan)
        if n > horizon:
            future_high = np.lib.stride_tricks.sliding_window_view(high[1:], horizon).max(axis=1)
            m = min(len(future_high), n - horizon)
            base = close[:m]
            ok = base > 0
            gain = np.full(m, np.nan)
            gain[ok] = future_high[:m][ok] / base[ok] - 1.0
            close_gain = np.full(n - horizon, np.nan)
            ok_c = close[:n - horizon] > 0
            close_gain[ok_c] = close[horizon:][ok_c] / close[:n - horizon][ok_c] - 1.0
            blocked = prefix[1 + horizon:1 + horizon + m] - prefix[1:1 + m] > 0
            gain[blocked[:m]] = np.nan
            close_blocked = prefix[1 + horizon:1 + horizon + (n - horizon)] - prefix[1:1 + (n - horizon)] > 0
            close_gain[close_blocked] = np.nan
            high_y[:m] = np.where(np.isfinite(gain), (gain >= 0.30).astype(float), np.nan)
            close_y[:n - horizon] = np.where(np.isfinite(close_gain), (close_gain >= 0.30).astype(float), np.nan)
        out[horizon] = dict(high=high_y, close=close_y)
    return out


def net_hold(entry_open: float, exit_close: float) -> float | None:
    if entry_open <= 0 or exit_close <= 0:
        return None
    return exit_close / entry_open - 1.0 - ROUND_TRIP


def distribution(returns: np.ndarray) -> dict:
    returns = np.asarray(returns, dtype=np.float64)
    returns = returns[np.isfinite(returns)]
    if len(returns) == 0:
        return dict(n=0, mean=None, median=None, p10=None, p25=None, p75=None, p90=None,
                    up30=None, down20=None, win=None)
    return dict(
        n=int(len(returns)),
        mean=float(returns.mean()),
        median=float(np.median(returns)),
        p10=float(np.percentile(returns, 10)),
        p25=float(np.percentile(returns, 25)),
        p75=float(np.percentile(returns, 75)),
        p90=float(np.percentile(returns, 90)),
        up30=float(np.mean(returns >= 0.30 - ROUND_TRIP)),
        down20=float(np.mean(returns <= -0.20)),
        win=float(np.mean(returns > 0)),
    )


def dedupe_mask(symbols: np.ndarray, dates: np.ndarray, index: dict, gap: int = 20) -> np.ndarray:
    keep = np.zeros(len(dates), dtype=bool)
    last = {}
    for i in np.argsort(dates, kind='mergesort'):
        day = date.fromordinal(int(dates[i]))
        if day not in index:
            continue
        previous = last.get(int(symbols[i]))
        if previous is not None and index[day] < previous + gap:
            continue
        last[int(symbols[i])] = index[day]
        keep[i] = True
    return keep


def run(root: Path):
    symbols = [line.strip() for line in Path('/tmp/anomaly_symbol_list.txt').read_text().splitlines() if line.strip()]
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    print('prices', flush=True)
    bars = load_prices(symbols)
    earnings = {symbol: {day.toordinal() for day in days} for symbol, days in load_earnings(root).items()}
    sectors = load_sectors()
    enrichment = []
    feature_gap = []
    sector_rows = []
    model_report = []
    trade_rows = []
    pool = {}
    kept_x = None
    for window in WINDOWS:
        cfg = {pair: i for i, pair in enumerate([(w, b) for w in (1, 3, 5) for b in (50, 100)])}[(window, 100)]
        print(f'load {window}d/100', flush=True)
        panel = load_config(symbols, cfg)
        print(f'score {window}d', flush=True)
        scored = score_window(panel, window)
        labels = labels_for_panel(panel, symbols, bars, earnings)
        base = base_rates(labels, panel['dates'])
        enrichment += lift_table(scored, labels, panel, window)
        if window == 1 and not pool:
            pool = match_pool(panel, symbols)
        trade_rows += stock_trades(scored, panel, symbols, bars, earnings, window, pool)
        if window == 1:
            feature_gap = feature_enrichment(panel, labels)
            sector_rows = sector_enrichment(panel, symbols, sectors, labels, scored)
            model_report, proba = fit_models(panel, labels, symbols)
            trade_rows += model_trades(proba, panel, symbols, bars, earnings, pool)
            kept_x = True
        del panel, scored, labels
    print(f'trade rows {len(trade_rows)}', flush=True)
    summary = summarize_trades(trade_rows, index)
    chosen = choose(summary)
    held = twin(summary, chosen)
    calls = price_calls(chosen, trade_rows, symbols, earnings, sessions, index) if chosen else {}
    report = dict(
        base=base, enrichment=enrichment, features=feature_gap, sectors=sector_rows,
        models=model_report, trades=summary, chosen=tag(chosen), holdout=tag(held),
        calls=calls, has_features=kept_x is not None,
        missing=['Market cap is not usable: the cap table has 28 rows and no current names.'],
        verdict=verdict_text(chosen, held, calls),
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'jump30_test.json').write_text(json.dumps(report, indent=2) + '\n')
    text = render(report)
    (folder / 'JUMP30_TEST.md').write_text(text)
    print(text, flush=True)
    return report


def load_prices(symbols):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from insider_resolved import connect

    def fetch(symbol):
        try:
            connection = connect()
            try:
                with connection.cursor() as cursor:
                    cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
                    cursor.execute(
                        '''SELECT qdate, open, high, low, close, volume FROM stockquote
                           WHERE symbol=%s AND qdate BETWEEN '2017-01-01' AND '2026-11-13' ORDER BY qdate''',
                        (symbol,))
                    rows = cursor.fetchall()
            finally:
                connection.close()
            if len(rows) < 30:
                return symbol, None
            days, o, h, c, v = [], [], [], [], []
            for row in rows:
                day = _as_date(row['qdate'])
                if day is None:
                    continue
                days.append(day.toordinal())
                o.append(_f(row['open']))
                h.append(_f(row['high']))
                c.append(_f(row['close']))
                v.append(_f(row['volume']))
            close = np.array(c)
            from anomaly_flow import adjust_closes as adj
            adjusted, _fcts, _br = adj(close)
            scale = np.ones_like(close)
            np.divide(adjusted, close, out=scale, where=close > 0)
            dollar = adjusted * np.array(v)
            med = np.full(len(dollar), np.nan)
            csum = np.cumsum(dollar)
            for i in range(20, len(dollar)):
                med[i] = (csum[i] - csum[i - 20]) / 20.0
            return symbol, (
                np.array(days, dtype=np.int32), np.array(o) * scale, np.array(h) * scale, adjusted, med)
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


def load_sectors():
    from insider_resolved import connect
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT symbol, sector FROM company WHERE sector IS NOT NULL AND sector<>''")
            return {row['symbol'].upper(): row['sector'] for row in cursor.fetchall()}
    finally:
        connection.close()


def score_window(panel, window):
    out = {}
    for kind in ('hbos', 'iforest'):
        scores = np.full(len(panel['dates']), np.nan, dtype=np.float32)
        flags = {p: np.zeros(len(scores), dtype=bool) for p in (0.01, 0.005, 0.001)}
        for train_mask, test_mask, _holdout in _folds(panel['dates']):
            train_idx = np.flatnonzero(train_mask)
            test_idx = np.flatnonzero(test_mask)
            if len(test_idx) == 0 or len(train_idx) < 500:
                continue
            ref = _cap_sample(train_idx, 20000, 19)
            print(f'  {kind} {window}d {date.fromordinal(int(panel["dates"][test_idx[0]])).year}', flush=True)
            scored, cuts = _score_pair(kind, panel['x'][train_idx], panel['x'][test_idx], panel['x'][ref], seed=len(train_idx) % 10000 + window)
            if scored is None:
                continue
            scores[test_idx] = scored
            for percent, key in ((0.01, '0.01'), (0.005, '0.005'), (0.001, '0.001')):
                flags[percent][test_idx] = scored >= cuts[key]
        out[kind] = dict(scores=scores, flags=flags, top4=_daily_top(panel['dates'], panel['symbol'], scores))
    return out


def labels_for_panel(panel, symbols, bars, earnings):
    n = len(panel['dates'])
    labels = {h: dict(high=np.full(n, np.nan), close=np.full(n, np.nan)) for h in HORIZONS}
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
        days, _opens, highs, closes, _dollar = payload
        earn = np.array([int(day) in earnings.get(symbol.upper(), set()) for day in days])
        local = forward_labels(highs, closes, earn)
        pos = np.searchsorted(days, panel['dates'][rows])
        pos = np.clip(pos, 0, len(days) - 1)
        good = days[pos] == panel['dates'][rows]
        for horizon in HORIZONS:
            for kind in ('high', 'close'):
                taken = np.full(len(rows), np.nan)
                taken[good] = local[horizon][kind][pos[good]]
                labels[horizon][kind][rows] = taken
    return labels


def base_rates(labels, dates):
    rows = []
    holdout = dates >= HOLDOUT_START.toordinal()
    walk = (dates < HOLDOUT_START.toordinal()) & np.array([date.fromordinal(int(d)).year >= 2018 for d in dates])
    for horizon in HORIZONS:
        for kind in ('high', 'close'):
            for sample, mask in (('walk', walk), ('holdout', holdout)):
                values = labels[horizon][kind][mask]
                known = values[np.isfinite(values)]
                rows.append(dict(horizon=horizon, kind=kind, sample=sample, n=int(len(known)),
                                 rate=None if len(known) == 0 else float(known.mean())))
    return rows


def lift_table(scored, labels, panel, window):
    rows = []
    dates = panel['dates']
    holdout = dates >= HOLDOUT_START.toordinal()
    walk = (dates < HOLDOUT_START.toordinal()) & np.array([date.fromordinal(int(d)).year >= 2018 for d in dates])
    for kind, pack in scored.items():
        for percent, mask in (('1%', pack['flags'][0.01]), ('0.5%', pack['flags'][0.005]), ('0.1%', pack['flags'][0.001]), ('top4', pack['top4'])):
            for horizon in HORIZONS:
                for event_kind in ('high', 'close'):
                    y = labels[horizon][event_kind]
                    for sample, sample_mask in (('walk', walk), ('holdout', holdout)):
                        known = sample_mask & np.isfinite(y)
                        if known.sum() < 100:
                            continue
                        flagged = mask & known
                        base = float(np.mean(y[known] == 1))
                        cond = float(np.mean(y[flagged] == 1)) if flagged.sum() else None
                        lift = None if not cond or not base else cond / base
                        ci = (None, None)
                        if percent in ('1%', '0.1%') and horizon == 20 and event_kind == 'high':
                            ci = clustered_lift(panel['symbol'][known], flagged[known], y[known])
                        rows.append(dict(
                            method=kind, window=window, percent=percent, horizon=horizon, event=event_kind,
                            sample=sample, base=base, cond=cond, lift=lift, n=int(flagged.sum()), ci=ci,
                        ))
    return rows


def feature_enrichment(panel, labels):
    y = labels[20]['high']
    dates = panel['dates']
    walk = (dates < HOLDOUT_START.toordinal()) & np.isfinite(y) & np.array([date.fromordinal(int(d)).year >= 2018 for d in dates])
    event = walk & (y == 1)
    other = walk & (y == 0)
    if event.sum() < 50 or other.sum() < 50:
        return []
    gap = np.nanmean(panel['x'][event], axis=0) - np.nanmean(panel['x'][other], axis=0)
    order = np.argsort(-np.nan_to_num(gap, nan=-1e9))
    return [dict(feature=FEATURES[int(i)], event=float(np.nanmean(panel['x'][event, int(i)])),
                 other=float(np.nanmean(panel['x'][other, int(i)]))) for i in order[:8]]


def sector_enrichment(panel, symbols, sectors, labels, scored):
    y = labels[20]['high']
    dates = panel['dates']
    walk = (dates < HOLDOUT_START.toordinal()) & np.isfinite(y)
    flag = scored['hbos']['flags'][0.01]
    counts = {}
    for i in np.flatnonzero(walk):
        sector = sectors.get(symbols[int(panel['symbol'][i])].upper(), 'unknown')
        bucket = counts.setdefault(sector, dict(base=0, event=0, top=0, top_event=0))
        bucket['base'] += 1
        if y[i] == 1:
            bucket['event'] += 1
        if flag[i]:
            bucket['top'] += 1
            if y[i] == 1:
                bucket['top_event'] += 1
    rows = []
    for sector, bucket in counts.items():
        if bucket['top'] < 40 or bucket['base'] < 200:
            continue
        base = bucket['event'] / bucket['base']
        cond = bucket['top_event'] / bucket['top']
        rows.append(dict(sector=sector, base=base, top=cond, lift=None if base == 0 else cond / base, n=bucket['top']))
    rows.sort(key=lambda row: -(row['lift'] or 0))
    return rows[:8]


def fit_models(panel, labels, symbols):
    y = labels[20]['high']
    dates = panel['dates']
    x = panel['x']
    years = np.array([date.fromordinal(int(d)).year for d in dates])
    holdout = dates >= HOLDOUT_START.toordinal()
    report = []
    saved = None
    for kind in ('logistic', 'boost'):
        proba = np.full(len(dates), np.nan, dtype=np.float32)
        for year in range(2018, 2026):
            test = (years == year) & ~holdout & np.isfinite(y)
            train = (dates < date(year, 1, 1).toordinal()) & np.isfinite(y)
            if test.sum() < 100 or train.sum() < 500:
                continue
            print(f'  model {kind} {year}', flush=True)
            got = _fit_predict(kind, x[train], y[train], x[test], year)
            if got is not None:
                proba[np.flatnonzero(test)] = got
        test = holdout & np.isfinite(y)
        train = (dates < HOLDOUT_START.toordinal()) & np.isfinite(y)
        print(f'  model {kind} holdout', flush=True)
        got = _fit_predict(kind, x[train], y[train], x[test], 2025)
        if got is not None:
            proba[np.flatnonzero(test)] = got
        report += precision_rows(kind, proba, y, dates, panel['symbol'])
        if kind == 'boost':
            saved = proba
    return report, saved


def _fit_predict(kind, train_x, train_y, test_x, seed):
    idx = np.flatnonzero(np.isfinite(train_y))
    idx = _cap_sample(idx, 200_000, seed)
    y = (train_y[idx] == 1).astype(np.int8)
    if len(np.unique(y)) < 2:
        return None
    x = train_x[idx].astype(np.float64)
    med = np.nanmedian(x, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    bad = ~np.isfinite(x)
    x[bad] = np.take(med, np.where(bad)[1])
    test = test_x.astype(np.float64)
    bad = ~np.isfinite(test)
    test[bad] = np.take(med, np.where(bad)[1])
    if kind == 'logistic':
        from sklearn.linear_model import LogisticRegression
        center, spread = x.mean(0), x.std(0)
        spread[spread < 1e-8] = 1.0
        model = LogisticRegression(C=1.0, solver='lbfgs', max_iter=200)
        model.fit((x - center) / spread, y)
        return model.predict_proba((test - center) / spread)[:, 1].astype(np.float32)
    from sklearn.ensemble import HistGradientBoostingClassifier
    model = HistGradientBoostingClassifier(max_iter=50, learning_rate=0.08, max_leaf_nodes=31, min_samples_leaf=200, l2_regularization=1.0, random_state=7)
    model.fit(x, y)
    return model.predict_proba(test)[:, 1].astype(np.float32)


def precision_rows(kind, proba, y, dates, symbols):
    rows = []
    holdout = dates >= HOLDOUT_START.toordinal()
    walk = ~holdout & np.isfinite(proba) & np.isfinite(y) & np.array([date.fromordinal(int(d)).year >= 2018 for d in dates])
    for sample, mask in (('walk', walk), ('holdout', holdout & np.isfinite(proba) & np.isfinite(y))):
        if mask.sum() < 100:
            continue
        base = float(np.mean(y[mask] == 1))
        top4 = _daily_top(dates, symbols, np.where(mask, proba, np.nan))
        hit = top4 & mask
        cond = float(np.mean(y[hit] == 1)) if hit.sum() else None
        rows.append(dict(model=kind, rule='top4', sample=sample, precision=cond, base=base,
                         lift=None if not cond or not base else cond / base, n=int(hit.sum())))
        finite = proba[mask]
        for percent, label in ((0.005, '0.5%'), (0.001, '0.1%')):
            cut = np.quantile(finite, 1 - percent)
            picked = mask & (proba >= cut)
            cond = float(np.mean(y[picked] == 1)) if picked.sum() else None
            rows.append(dict(model=kind, rule=label, sample=sample, precision=cond, base=base,
                             lift=None if not cond or not base else cond / base, n=int(picked.sum())))
    return rows


def match_pool(panel, symbols):
    dates = panel['dates']
    rvol = panel['x'][:, -1]
    months = np.empty(len(dates), dtype=np.int32)
    for i, ordinal in enumerate(dates.tolist()):
        day = date.fromordinal(int(ordinal))
        months[i] = day.year * 12 + day.month
    decile = np.full(len(dates), -1, dtype=np.int8)
    buckets = {}
    sorted_rvol = {}
    for month in np.unique(months):
        idx = np.flatnonzero((months == month) & np.isfinite(rvol))
        if len(idx) >= 10:
            order = np.argsort(rvol[idx])
            ranks = np.empty(len(order), dtype=np.int8)
            ranks[order] = np.minimum(9, np.arange(len(order)) * 10 // len(order))
            decile[idx] = ranks
            sorted_rvol[int(month)] = np.sort(rvol[idx])
        for i in np.flatnonzero(months == month):
            buckets.setdefault((int(month), int(decile[i])), []).append(int(i))
    return dict(dates=dates, symbol=panel['symbol'], rvol=rvol, months=months, buckets=buckets, sorted=sorted_rvol, names=symbols)


def _pick_match(pool, day, rvol, rng):
    month = day.year * 12 + day.month
    bucket = -1
    ordered = pool['sorted'].get(month)
    if rvol is not None and ordered is not None and len(ordered):
        bucket = int(min(9, np.searchsorted(ordered, rvol, side='right') * 10 / len(ordered)))
    choices = pool['buckets'].get((month, bucket)) or pool['buckets'].get((month, -1)) or []
    if not choices:
        return None
    return choices[int(rng.randint(0, len(choices)))]


def model_trades(proba, panel, symbols, bars, earnings, pool):
    if proba is None:
        return []
    rng = np.random.RandomState(7)
    dates = panel['dates']
    codes = panel['symbol']
    rvol = panel['x'][:, -1]
    rows = []
    top4 = _daily_top(dates, codes, proba)
    finite = proba[np.isfinite(proba)]
    cut = float(np.quantile(finite, 0.995)) if len(finite) else np.inf
    for i in np.flatnonzero(np.isfinite(proba) & (top4 | (proba >= cut))):
        rule = 'top4' if top4[i] else 'p05'
        symbol = symbols[int(codes[i])]
        day = date.fromordinal(int(dates[i]))
        trade = _one_trade(symbol, int(dates[i]), 'boost', 1, rule, float(proba[i]), bars, earnings)
        if trade is None:
            continue
        match = _pick_match(pool, day, None if not np.isfinite(rvol[i]) else float(rvol[i]), rng)
        if match is not None:
            other = _one_trade(symbols[int(pool['symbol'][match])], int(pool['dates'][match]), 'boost', 1, rule, 0.0, bars, earnings)
            if other is not None:
                trade['random'] = other['holds']
        rows.append(trade)
    return rows


def stock_trades(scored, panel, symbols, bars, earnings, window, pool):
    """Next-open entry, exit at the close after a fixed number of the name's sessions."""
    rng = np.random.RandomState(20261113 + window)
    rows = []
    codes = panel['symbol']
    dates = panel['dates']
    rvol = panel['x'][:, -1]
    for kind, pack in scored.items():
        for rule, mask in (('p1', pack['flags'][0.01]), ('p05', pack['flags'][0.005]), ('top4', pack['top4'])):
            for i in np.flatnonzero(mask & np.isfinite(pack['scores'])):
                symbol = symbols[int(codes[i])]
                day = date.fromordinal(int(dates[i]))
                trade = _one_trade(symbol, int(dates[i]), kind, window, rule, float(pack['scores'][i]), bars, earnings)
                if trade is None:
                    continue
                match = _pick_match(pool, day, None if not np.isfinite(rvol[i]) else float(rvol[i]), rng) if pool else None
                if match is not None:
                    other = _one_trade(symbols[int(pool['symbol'][match])], int(pool['dates'][match]), kind, window, rule, 0.0, bars, earnings)
                    if other is not None:
                        trade['random'] = other['holds']
                rows.append(trade)
    return rows


def _one_trade(symbol, ordinal, source, window, rule, score, bars, earnings):
    payload = bars.get(symbol)
    if payload is None:
        return None
    days, opens, _highs, closes, _dollar = payload
    pos = int(np.searchsorted(days, ordinal))
    if pos >= len(days) or int(days[pos]) != ordinal or pos + 1 >= len(days):
        return None
    entry_i = pos + 1
    entry = float(opens[entry_i])
    if entry <= 0:
        return None
    earn = earnings.get(symbol.upper(), set())
    holds = {}
    for hold in HOLDS:
        exit_i = entry_i + hold
        if exit_i >= len(days):
            continue
        if any(int(days[j]) in earn for j in range(entry_i, exit_i + 1)):
            continue
        ret = net_hold(entry, float(closes[exit_i]))
        if ret is None:
            continue
        holds[hold] = ret
    if not holds:
        return None
    return dict(symbol=symbol, date=date.fromordinal(ordinal), source=source, window=window, rule=rule, score=score, holds=holds)


def summarize_trades(rows, index):
    cells = []
    rules = sorted({(row['source'], row['window'], row['rule']) for row in rows})
    for source, window, rule in rules:
        subset = [row for row in rows if row['source'] == source and row['window'] == window and row['rule'] == rule]
        for hold in HOLDS:
            for sample in ('walk', 'holdout'):
                picked = [row for row in subset if (row['date'] >= HOLDOUT_START) == (sample == 'holdout') and hold in row['holds']]
                if not picked:
                    continue
                returns = np.array([row['holds'][hold] for row in picked])
                random_returns = np.array([row['random'][hold] for row in picked if row.get('random') and hold in row['random']], dtype=float)
                ids = {name: i for i, name in enumerate(dict.fromkeys(row['symbol'] for row in picked))}
                symbols = np.array([ids[row['symbol']] for row in picked])
                dates = np.array([row['date'].toordinal() for row in picked])
                keep = dedupe_mask(symbols, dates, index)
                cells.append(dict(
                    source=source, window=window, rule=rule, hold=hold, sample=sample,
                    all=distribution(returns), deduped=distribution(returns[keep]),
                    random=distribution(random_returns),
                ))
    return cells


def choose(cells):
    pool = [cell for cell in cells if cell['sample'] == 'walk' and cell['deduped']['mean'] is not None]
    if not pool:
        return None
    return max(pool, key=lambda cell: cell['deduped']['mean'])


def twin(cells, chosen):
    if chosen is None:
        return None
    for cell in cells:
        if (cell['sample'] == 'holdout' and cell['source'] == chosen['source'] and cell['window'] == chosen['window']
                and cell['rule'] == chosen['rule'] and cell['hold'] == chosen['hold']):
            return cell
    return None


def tag(cell):
    return cell


def price_calls(chosen, rows, symbols, earnings, sessions, index):
    if chosen is None:
        return dict(n=0, dropped=0)
    picked = [row for row in rows if row['source'] == chosen['source'] and row['rule'] == chosen['rule'] and chosen['hold'] in row['holds']]
    print(f'calls {len(picked)}', flush=True)
    from collections import defaultdict
    from insider_resolved import connect
    by_symbol = defaultdict(list)
    for row in picked:
        by_symbol[row['symbol']].append(row)
    returns = []
    dropped = 0
    for symbol, group in by_symbol.items():
        try:
            got, miss = _calls_for_symbol(symbol, group, chosen['hold'], earnings.get(symbol.upper(), set()), connect)
        except Exception as exc:  # noqa: BLE001
            print(f'skip call {symbol} {type(exc).__name__}', flush=True)
            dropped += len(group)
            continue
        returns.extend(got)
        dropped += miss
    return dict(n=len(returns), dropped=dropped, dist=distribution(np.array(returns, dtype=float)), hold=chosen['hold'],
                source=chosen['source'], rule=chosen['rule'])


def _calls_for_symbol(symbol, group, hold, earnings, connect):
    dates = sorted({row['date'] for row in group})
    # Exit dates are hold sessions after the next open. Approximate with the row's own calendar via a second query of all chain days.
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            marks = ','.join(['%s'] * len(dates))
            cursor.execute(
                f'''SELECT qdate, edate, strike, delta, bid, ask
                    FROM optiondaily WHERE underlying=%s AND `type`='call' AND qdate IN ({marks})
                    AND DATEDIFF(edate, qdate) BETWEEN 30 AND 60''',
                (symbol, *dates),
            )
            chain = {}
            for row in cursor.fetchall():
                day = _as_date(row['qdate'])
                chain.setdefault(day, []).append(row)
    finally:
        connection.close()
    returns = []
    missed = 0
    for row in group:
        legs = chain.get(row['date']) or []
        picked = None
        best = 1.0
        for leg in legs:
            delta = leg['delta']
            if delta is None:
                continue
            delta = float(delta)
            if 0.20 <= delta <= 0.30 and abs(delta - 0.25) < best and float(leg['ask']) > 0 and float(leg['bid']) >= 0 and float(leg['ask']) >= float(leg['bid']):
                best = abs(delta - 0.25)
                picked = leg
        if picked is None:
            missed += 1
            continue
        # Exit quote is loaded lazily per expiry below.
        returns.append((row, picked))
    if not returns:
        return [], missed
    exit_needed = {}
    # Without the stock calendar here, skip exits we cannot see. The caller passes only entry dates.
    # A second query uses edate and a wide date list is not available, so mark these as needing the exit fetch.
    pending = returns
    returns = []
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            cursor.execute(
                '''SELECT qdate, close FROM stockquote WHERE symbol=%s AND qdate BETWEEN '2017-01-01' AND '2026-11-13' ORDER BY qdate''',
                (symbol,))
            days = [_as_date(row['qdate']) for row in cursor.fetchall() if _as_date(row['qdate'])]
    finally:
        connection.close()
    lookup = {day: i for i, day in enumerate(days)}
    wanted = {}
    plans = []
    for row, leg in pending:
        i = lookup.get(row['date'])
        if i is None or i + 1 + hold >= len(days):
            missed += 1
            continue
        exit_day = days[i + 1 + hold]
        if any(days[j].toordinal() in earnings for j in range(i + 1, i + 2 + hold)):
            missed += 1
            continue
        plans.append((row, leg, exit_day))
        wanted.setdefault(exit_day, []).append(leg)
    if not plans:
        return [], missed
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=120000')
            marks = ','.join(['%s'] * len(wanted))
            cursor.execute(
                f'''SELECT qdate, edate, strike, bid, ask FROM optiondaily
                    WHERE underlying=%s AND `type`='call' AND qdate IN ({marks})''',
                (symbol, *sorted(wanted)),
            )
            exits = {}
            for row in cursor.fetchall():
                exits.setdefault((_as_date(row['qdate']), _as_date(row['edate']), float(row['strike'])), row)
    finally:
        connection.close()
    out = []
    for row, leg, exit_day in plans:
        key = (exit_day, _as_date(leg['edate']), float(leg['strike']))
        later = exits.get(key)
        if later is None or float(later['bid']) <= 0 or float(leg['ask']) <= 0:
            missed += 1
            continue
        out.append(float(later['bid']) / float(leg['ask']) - 1.0 - ROUND_TRIP)
    return out, missed


def verdict_text(chosen, held, calls) -> str:
    if chosen is None or held is None:
        return 'No timed hold was priced, so there is no comparison with a random stock.'
    name = f"{chosen['source']} {chosen['window']}-day {chosen['rule']}, {chosen['hold']} sessions"
    signal = held['deduped']['mean']
    # Random is not stored on the trade cell in this version. The comparison is in the table when present.
    random = held['random']['mean']
    edge = None if signal is None or random is None else signal - random
    edge_text = 'n/a' if edge is None else f'{edge:.3f}'
    if signal is not None and signal > 0 and edge is not None and edge > 0:
        return (
            f'{name} is the walk-forward hold with the highest deduped mean. '
            f'The holdout mean stays positive and beats the matched random hold by {edge_text}.'
        )
    return (
        f'{name} is the walk-forward hold with the highest deduped mean. '
        f'The holdout deduped mean is {_fmt(signal)} and the matched random mean is {_fmt(random)}, a difference of {edge_text}. '
        'The timed hold does not beat a random stock from the same month and volatility decile with a positive expectancy.'
    )


def render(report: dict) -> str:
    lines = [
        '# +30% events and a timed stock hold',
        '',
        'A +30% event is a forward high, or a close, at least 30% above the signal close within 5, 10, 20, or 40 sessions. An earnings reaction inside that window blanks the event. The trade is separate: buy the next open and sell the close after 5, 10, 20, or 40 of the name\'s sessions. There is no stop and no target. The cost is 10 bps round trip. The hold with the highest deduped walk-forward mean is the one whose holdout is read.',
        '',
        report['missing'][0],
        '',
        '## Base rate in the filtered universe',
        '',
        '| Kind | Horizon | Sample | N | Rate |',
        '| --- | ---: | --- | ---: | ---: |',
    ]
    for row in report['base']:
        lines.append(f"| {row['kind']} | {row['horizon']} | {row['sample']} | {row['n']} | {_fmt(row['rate'])} |")
    lines += ['', '## Lift for a 20-session high of at least 30%', '', '| Method | Window | Tail | Sample | Lift | Conditional | Base | N | Interval |', '| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |']
    for row in report['enrichment']:
        if row['horizon'] != 20 or row['event'] != 'high':
            continue
        if row['percent'] not in ('1%', '0.5%', '0.1%'):
            continue
        lines.append(
            f"| {row['method']} | {row['window']} | {row['percent']} | {row['sample']} | {_fmt(row['lift'])} | {_fmt(row['cond'])} | {_fmt(row['base'])} | {row['n']} | {_span(row['ci'])} |"
        )
    lines += ['', '## Features higher before a 20-session +30% high', '']
    for row in report['features']:
        lines.append(f"- {row['feature']}: event {row['event']:.3f}, other names {row['other']:.3f}")
    lines += ['', '## Sector, HBOS top 1%, 20-session high', '']
    for row in report['sectors']:
        lines.append(f"- {row['sector']}: top-1% rate {_fmt(row['top'])} versus base {_fmt(row['base'])}, lift {_fmt(row['lift'])}, n {row['n']}")
    lines += ['', '## Classifier precision on the 20-session +30% high', '', '| Model | Rule | Sample | Precision | Base | Lift | N |', '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for row in report['models']:
        lines.append(f"| {row['model']} | {row['rule']} | {row['sample']} | {_fmt(row['precision'])} | {_fmt(row['base'])} | {_fmt(row['lift'])} | {row['n']} |")
    lines += ['', '## Timed stock hold, deduped', '', '| Signal | Hold | Sample | N | Mean | Median | P10 | P90 | At least +30% | At or below -20% | Win | Random mean |', '| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in report['trades']:
        if row['rule'] not in ('p1', 'top4', 'p05') or row['window'] not in (1, 5):
            continue
        if row['hold'] not in (10, 20, 40):
            continue
        stats = row['deduped']
        lines.append(
            f"| {row['source']} {row['window']}d {row['rule']} | {row['hold']} | {row['sample']} | {stats['n']} | {_fmt(stats['mean'])} | {_fmt(stats['median'])} | {_fmt(stats['p10'])} | {_fmt(stats['p90'])} | {_fmt(stats['up30'])} | {_fmt(stats['down20'])} | {_fmt(stats['win'])} | {_fmt(row['random']['mean'])} |"
        )
    chosen = report.get('chosen') or {}
    calls = report.get('calls') or {}
    lines += ['', '## Chosen hold and the call', '']
    if chosen:
        lines.append(f"Walk-forward choice: {chosen['source']} {chosen['window']}-day {chosen['rule']}, exit after {chosen['hold']} sessions. Holdout deduped mean {_fmt((report.get('holdout') or {}).get('deduped', {}).get('mean'))}.")
    dist = calls.get('dist') or {}
    lines.append(f"OTM call on that rule, ask in and bid out, same time exit: n {calls.get('n', 0)}, dropped {calls.get('dropped', 0)}, mean {_fmt(dist.get('mean'))}, median {_fmt(dist.get('median'))}, at least +30% {_fmt(dist.get('up30'))}, at or below -20% {_fmt(dist.get('down20'))}.")
    lines += ['', '## Verdict', '', report['verdict'], '']
    return '\n'.join(lines)


def _fmt(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.3f}'


def _span(pair):
    if not pair or pair[0] is None:
        return 'n/a'
    return f'{pair[0]:.2f} to {pair[1]:.2f}'


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
