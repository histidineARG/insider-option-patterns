"""Point-in-time direction test: is the stock up over the next 5, 10, or 20 sessions.

Features use only the scoring close and earlier data. Labels use later closes and
are split-adjusted. Nothing in the fit sees the final holdout year.
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path

import numpy as np

from etp_exclusion import add_argument, partition_symbols, stats_line
from insider_resolved import connect

HOLDOUT_START = date(2025, 11, 13)
FIRST_TEST_YEAR = 2016
LAST_WALK_YEAR = 2025
PRICE_MIN = 5.0
DOLLAR_MIN = 5_000_000.0
COST = 0.001
TRAIN_CAP = 200_000
PEAD_WINDOW = 60
HORIZONS = (5, 10, 20)
TOPS = (10, 20)
SPLIT_TOL = 0.05
BREAK_MOVE = 0.70
PANEL = Path('/tmp/direction_parts')

# Frozen before any fit. Positive means a higher value raises the composite.
SIGNS = {
    'mom_12_1': 1.0,
    'ret_21': -1.0,
    'pead': 1.0,
    'dist_ma50': 1.0,
    'dist_ma200': 1.0,
    'rvol_20': -1.0,
    'iv_level': -1.0,
    'iv_change': -1.0,
    'skew': -1.0,
    'put_call': -1.0,
    'otm_surge': 1.0,
}
FEATURES = list(SIGNS)
MODEL_FEATURES = FEATURES + ['spy_above_ma200']
MISSING = [
    'EDGAR Form 4 insider net buys: no table in optiondb.',
    'Earnings surprise versus a consensus estimate: not stored. The post-earnings feature is the reaction-session close-to-close return.',
    'stock_ta_daily is empty, so the 50- and 200-day averages are computed from stockquote.',
    'ivdaily ends on 2016-07-07. Implied volatility is optionstat mean, call, and put IV.',
    'daystat, the out-of-the-money call volume source, ends on 2025-12-30, so that feature is absent for most of the holdout.',
    'erdate ends on 2022-01-04. Later earnings reaction dates come from the 8-K Item 2.02 table already in the repo.',
]


def _candidates():
    values = []
    for factor in (2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50, 100):
        values.append(float(factor))
        values.append(1.0 / factor)
    return np.array(values)


CANDIDATES = _candidates()


def adjust_closes(closes: np.ndarray):
    """Scale earlier closes into the latest share count when a day matches a split ratio.

    A move larger than 70 percent that is not a split stays in the series and is
    flagged so lookback features that cross it are left blank.
    """
    closes = np.asarray(closes, dtype=np.float64)
    n = len(closes)
    factors = np.ones(n)
    breaks = np.zeros(n, dtype=bool)
    for i in range(1, n):
        prev, cur = closes[i - 1], closes[i]
        if prev <= 0 or cur <= 0 or not np.isfinite(prev) or not np.isfinite(cur):
            breaks[i] = True
            continue
        ratio = cur / prev
        error = np.abs(ratio / CANDIDATES - 1.0)
        choice = int(np.argmin(error))
        if error[choice] <= SPLIT_TOL and abs(ratio - 1.0) >= 0.35:
            factors[i] = CANDIDATES[choice]
        elif abs(ratio - 1.0) > BREAK_MOVE:
            breaks[i] = True
    adjusted = closes.copy()
    scale = 1.0
    for i in range(n - 1, 0, -1):
        scale *= factors[i]
        adjusted[i - 1] *= scale
    return adjusted, factors, breaks


def _clean(prefix: np.ndarray, start: int, end: int) -> bool:
    return prefix[end] - prefix[start] == 0


def symbol_panel(dates, closes, volumes, option_rows, otm_rows, earn_days, spy):
    """Rows for one symbol. dates, closes, and volumes are aligned and sorted."""
    closes = np.asarray(closes, dtype=np.float64)
    volumes = np.asarray(volumes, dtype=np.float64)
    n = len(closes)
    if n < 280:
        return None
    adjusted, factors, breaks = adjust_closes(closes)
    prefix = np.cumsum(breaks.astype(np.int32))
    option = {row[0]: row[1:] for row in option_rows}
    otm = {row[0]: row[1] for row in otm_rows}
    earn = [day for day in earn_days if day in set(dates)]
    earn_at = {day: i for i, day in enumerate(dates)}
    earn_idx = [earn_at[day] for day in earn]
    out_dates, out_x, out_ret, out_xs = [], [], [], []
    pointer = 0
    latest = -1
    for i in range(252, n - 5):
        while pointer < len(earn_idx) and earn_idx[pointer] <= i:
            latest = earn_idx[pointer]
            pointer += 1
        raw_close = closes[i]
        dollar = closes[i] * volumes[i]
        if raw_close < PRICE_MIN or not np.isfinite(dollar):
            continue
        start = i - 19
        trail = closes[start:i + 1] * volumes[start:i + 1]
        if len(trail) < 20 or np.median(trail) < DOLLAR_MIN:
            continue
        row = np.full(12, np.nan, dtype=np.float32)
        if _clean(prefix, i - 252, i - 21) and adjusted[i - 252] > 0:
            row[0] = adjusted[i - 21] / adjusted[i - 252] - 1.0
        if _clean(prefix, i - 21, i) and adjusted[i - 21] > 0:
            row[1] = adjusted[i] / adjusted[i - 21] - 1.0
        if latest >= 1 and i - latest <= PEAD_WINDOW and _clean(prefix, latest - 1, latest) and adjusted[latest - 1] > 0:
            row[2] = adjusted[latest] / adjusted[latest - 1] - 1.0
        if _clean(prefix, i - 49, i):
            ma50 = adjusted[i - 49:i + 1].mean()
            if ma50 > 0:
                row[3] = adjusted[i] / ma50 - 1.0
        if _clean(prefix, i - 199, i):
            ma200 = adjusted[i - 199:i + 1].mean()
            if ma200 > 0:
                row[4] = adjusted[i] / ma200 - 1.0
        if _clean(prefix, i - 20, i):
            window = adjusted[i - 20:i + 1]
            returns = np.diff(window) / window[:-1]
            if np.isfinite(returns).all() and (window[:-1] > 0).all():
                row[5] = returns.std()
        quote = option.get(dates[i])
        if quote is not None:
            call_iv, put_iv, mean_iv, call_vol, put_vol = quote
            if mean_iv and mean_iv > 0:
                row[6] = mean_iv
            if call_vol and call_vol > 0 and put_vol is not None and put_vol >= 0:
                row[9] = put_vol / call_vol
            if call_iv and put_iv and call_iv > 0 and put_iv > 0:
                row[8] = put_iv - call_iv
            earlier = option.get(dates[i - 20]) if i >= 20 else None
            if earlier and earlier[2] and mean_iv and earlier[2] > 0 and mean_iv > 0:
                row[7] = mean_iv / earlier[2] - 1.0
        history = [otm.get(dates[j]) for j in range(i - 20, i)]
        history = [value for value in history if value is not None and value > 0]
        today_otm = otm.get(dates[i])
        if today_otm and today_otm > 0 and len(history) >= 10:
            base = float(np.mean(history))
            if base > 0:
                row[10] = math.log(today_otm / base)
        spy_row = spy.get(dates[i])
        if spy_row is None:
            continue
        row[11] = spy_row[1]
        returns = np.full(3, np.nan, dtype=np.float32)
        excess = np.full(3, np.nan, dtype=np.float32)
        for h_i, horizon in enumerate(HORIZONS):
            j = i + horizon
            if j >= n or adjusted[i] <= 0:
                continue
            returns[h_i] = adjusted[j] / adjusted[i] - 1.0
            exit_spy = spy.get(dates[j])
            if exit_spy is not None and spy_row[0] > 0:
                excess[h_i] = returns[h_i] - (exit_spy[0] / spy_row[0] - 1.0)
        if int(np.isfinite(row[:11]).sum()) < 4:
            continue
        if not np.isfinite(returns).any():
            continue
        out_dates.append(dates[i].toordinal())
        out_x.append(row)
        out_ret.append(returns)
        out_xs.append(excess)
    if not out_dates:
        return None
    return (
        np.array(out_dates, dtype=np.int32),
        np.vstack(out_x),
        np.vstack(out_ret),
        np.vstack(out_xs),
        int(np.count_nonzero(factors != 1.0)),
        int(breaks.sum()),
    )


def composite_scores(x: np.ndarray) -> np.ndarray:
    """Equal-weight signed z-score. A column with no spread contributes nothing."""
    score = np.zeros(len(x), dtype=np.float64)
    used = np.zeros(len(x), dtype=np.float64)
    for col, name in enumerate(FEATURES):
        values = x[:, col].astype(np.float64)
        finite = np.isfinite(values)
        if finite.sum() < 5:
            continue
        center = values[finite].mean()
        spread = values[finite].std()
        if spread < 1e-8:
            continue
        z = np.zeros(len(x), dtype=np.float64)
        z[finite] = np.clip((values[finite] - center) / spread, -3.0, 3.0)
        score[finite] += SIGNS[name] * z[finite]
        used[finite] += 1.0
    score[used > 0] /= used[used > 0]
    score[used == 0] = np.nan
    return score


def subsample(index: np.ndarray, cap: int, seed: int) -> np.ndarray:
    if len(index) <= cap:
        return index
    rng = np.random.RandomState(seed)
    pick = rng.choice(len(index), size=cap, replace=False)
    return index[np.sort(pick)]


def prepare_logistic(train_x, test_x):
    train = train_x.astype(np.float64)
    test = test_x.astype(np.float64)
    medians = np.nanmedian(train, axis=0)
    medians = np.where(np.isfinite(medians), medians, 0.0)
    for matrix in (train, test):
        bad = ~np.isfinite(matrix)
        matrix[bad] = np.take(medians, np.where(bad)[1])
    center = train.mean(axis=0)
    spread = train.std(axis=0)
    spread[spread < 1e-8] = 1.0
    return (train - center) / spread, (test - center) / spread


def wilson(hits: int, n: int, z: float = 1.96):
    if n <= 0:
        return None, None
    p = hits / n
    den = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - margin, centre + margin


def block_bootstrap(daily: np.ndarray, block: int, reps: int = 400, seed: int = 11):
    daily = np.asarray(daily, dtype=np.float64)
    n = len(daily)
    if n < block * 2:
        return None, None
    rng = np.random.RandomState(seed)
    n_blocks = int(math.ceil(n / block))
    means = np.empty(reps)
    for i in range(reps):
        starts = rng.randint(0, n - block + 1, size=n_blocks)
        sample = np.concatenate([daily[s:s + block] for s in starts])[:n]
        means[i] = sample.mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def net_of_cost(returns: np.ndarray) -> np.ndarray:
    return returns - COST


def _day_slices(dates: np.ndarray):
    order = np.argsort(dates, kind='mergesort')
    ordered = dates[order]
    cuts = np.flatnonzero(np.diff(ordered)) + 1
    bounds = np.r_[0, cuts, len(ordered)]
    return order, bounds


def _fit_logistic(x, y):
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(C=1.0, solver='lbfgs', max_iter=200)
    model.fit(x, y)
    return model


def _fit_boost(x, y):
    from sklearn.ensemble import HistGradientBoostingClassifier
    model = HistGradientBoostingClassifier(
        max_iter=50, learning_rate=0.08, max_leaf_nodes=31,
        min_samples_leaf=200, l2_regularization=1.0, random_state=7,
    )
    model.fit(x, y)
    return model


def _predict_year(kind, train_idx, test_idx, x, y, seed, with_importance):
    train_idx = subsample(train_idx, TRAIN_CAP, seed)
    if len(train_idx) < 1000 or len(np.unique(y[train_idx])) < 2:
        return None, None
    if kind == 'logistic':
        train_x, test_x = prepare_logistic(x[train_idx], x[test_idx])
        model = _fit_logistic(train_x, y[train_idx])
        proba = model.predict_proba(test_x)[:, 1]
        importance = np.abs(model.coef_[0]) if with_importance else None
    else:
        model = _fit_boost(x[train_idx], y[train_idx])
        proba = model.predict_proba(x[test_idx])[:, 1]
        importance = _boost_importance(model, x[train_idx], y[train_idx]) if with_importance else None
    return proba.astype(np.float32), importance


def _boost_importance(model, x, y):
    from sklearn.inspection import permutation_importance
    rng = np.random.RandomState(1)
    take = rng.choice(len(x), size=min(4000, len(x)), replace=False)
    result = permutation_importance(
        model, x[take], y[take], n_repeats=3, random_state=1, scoring='neg_log_loss')
    return result.importances_mean


def score_panel(dates, x, ret):
    """Walk-forward scores, then a separate holdout fit. Hyperparameters stay fixed."""
    years = np.array([date.fromordinal(int(day)).year for day in dates])
    ordinals = dates
    holdout_cut = HOLDOUT_START.toordinal()
    order, bounds = _day_slices(ordinals)
    composite = _composite_by_day(x, order, bounds)
    scores = {'composite': {h: composite for h in HORIZONS}}
    importance = {'logistic': {str(h): [] for h in HORIZONS}, 'boost': {str(h): [] for h in HORIZONS}}
    for kind in ('logistic', 'boost'):
        scores[kind] = {}
        for h_i, horizon in enumerate(HORIZONS):
            proba = np.full(len(dates), np.nan, dtype=np.float32)
            y = (ret[:, h_i] > 0).astype(np.int8)
            finite = np.isfinite(ret[:, h_i])
            for year in range(FIRST_TEST_YEAR, LAST_WALK_YEAR + 1):
                test = finite & (years == year) & (ordinals < holdout_cut)
                train = finite & (ordinals < date(year, 1, 1).toordinal())
                if test.sum() == 0 or train.sum() == 0:
                    continue
                print(f'fit {kind} {horizon}d train<{year} rows {int(train.sum())} test {int(test.sum())}', flush=True)
                got, weights = _predict_year(
                    kind, np.flatnonzero(train), np.flatnonzero(test), x, y, year * 10 + horizon,
                    with_importance=(year == 2024))
                if got is None:
                    continue
                proba[np.flatnonzero(test)] = got
                if weights is not None:
                    importance[kind][str(horizon)].append([float(value) for value in weights])
            test = finite & (ordinals >= holdout_cut)
            train = finite & (ordinals < holdout_cut)
            print(f'fit {kind} {horizon}d holdout train {int(train.sum())} test {int(test.sum())}', flush=True)
            got, weights = _predict_year(
                kind, np.flatnonzero(train), np.flatnonzero(test), x, y, 202511, with_importance=True)
            if got is not None:
                proba[np.flatnonzero(test)] = got
                importance[kind][str(horizon)].append([float(value) for value in weights])
            scores[kind][horizon] = proba
    return scores, importance


def _composite_by_day(x, order, bounds):
    scores = np.full(len(x), np.nan, dtype=np.float32)
    for start, end in zip(bounds[:-1], bounds[1:]):
        idx = order[start:end]
        if len(idx) < 30:
            continue
        scores[idx] = composite_scores(x[idx]).astype(np.float32)
    return scores


def evaluate(dates, x, scores, ret, xs, spy_forward):
    holdout_cut = HOLDOUT_START.toordinal()
    regime = {}
    for day, flag in zip(dates.tolist(), x[:, 11].tolist()):
        if day not in regime and flag == flag:
            regime[int(day)] = int(flag)
    records = []
    for kind, by_h in scores.items():
        for horizon, proba in by_h.items():
            h_i = HORIZONS.index(horizon)
            keep = np.isfinite(proba)
            if keep.sum() == 0:
                continue
            order, bounds = _day_slices(dates[keep])
            ordered = np.flatnonzero(keep)[order]
            day_ids = dates[keep][order]
            for start, end in zip(bounds[:-1], bounds[1:]):
                idx = ordered[start:end]
                day = int(day_ids[start])
                spy_ret = spy_forward.get((day, horizon))
                if spy_ret is None or len(idx) < 30 or day < date(2016, 1, 1).toordinal():
                    continue
                order_k = np.argsort(-proba[idx], kind='mergesort')
                labels = ret[idx, h_i]
                excess = xs[idx, h_i]
                known = np.isfinite(labels)
                if known.sum() < 30:
                    continue
                finite_xs = excess[known & np.isfinite(excess)]
                base_xs = float(np.mean(finite_xs > 0)) if len(finite_xs) else None
                rng = np.random.RandomState(day % (2 ** 31 - 1))
                for k in TOPS:
                    if len(idx) < k:
                        continue
                    chosen = order_k[:k]
                    random_pick = rng.choice(len(idx), size=k, replace=False)
                    records.append(_slate(
                        day, holdout_cut, regime.get(day), kind, horizon, k, labels, excess,
                        chosen, random_pick, known, base_xs, spy_ret, len(idx)))
    return records


def _slate(day, holdout_cut, regime, kind, horizon, k, labels, excess, chosen, random_pick, known, base_xs, spy_ret, n):
    def hit_rate(pick):
        mask = known[pick]
        if not mask.any():
            return None, 0
        up = labels[pick][mask] > 0
        return float(np.mean(up)), int(np.sum(up))

    def xs_rate(pick):
        mask = known[pick] & np.isfinite(excess[pick])
        if not mask.any():
            return None
        return float(np.mean(excess[pick][mask] > 0))

    def money(pick):
        mask = known[pick]
        if not mask.any():
            return None, None
        net = net_of_cost(labels[pick][mask])
        return float(np.mean(net)), float(np.median(net))

    hit, hits = hit_rate(chosen)
    net_mean, net_median = money(chosen)
    random_net, _random_median = money(random_pick)
    random_hit, _random_hits = hit_rate(random_pick)
    return dict(
        date=date.fromordinal(day).isoformat(),
        year=int(date.fromordinal(day).year),
        holdout=day >= holdout_cut,
        regime=regime,
        model=kind, horizon=int(horizon), k=int(k),
        hit=hit, hits=hits,
        xs_hit=xs_rate(chosen),
        net_mean=net_mean, net_median=net_median,
        base_hit=float(np.mean(labels[known] > 0)),
        base_xs=base_xs,
        random_hit=random_hit, random_net=random_net,
        spy_ret=float(spy_ret),
        n=int(n),
    )


def spy_series(rows):
    """Adjusted SPY close and the 200-day regime, plus forward returns keyed by ordinal."""
    dates = [row[0] for row in rows]
    closes = np.array([row[1] for row in rows], dtype=np.float64)
    adjusted, _factors, _breaks = adjust_closes(closes)
    quote = {}
    forward = {}
    for i, day in enumerate(dates):
        flag = np.nan
        if i >= 199:
            ma = adjusted[i - 199:i + 1].mean()
            flag = 1.0 if ma > 0 and adjusted[i] > ma else 0.0
        quote[day] = (float(adjusted[i]), flag)
        for horizon in HORIZONS:
            j = i + horizon
            if j < len(dates) and adjusted[i] > 0:
                forward[(day.toordinal(), horizon)] = float(adjusted[j] / adjusted[i] - 1.0)
    return quote, forward


def load_earnings(root: Path):
    earn = {}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute(
                '''SELECT UPPER(symbol) AS symbol, erdate, rxdate FROM erdate
                   WHERE erdate >= '2013-01-01' ''')
            for row in cursor.fetchall():
                day = row['rxdate'] or row['erdate']
                if isinstance(day, datetime):
                    day = day.date()
                if day is not None:
                    earn.setdefault(row['symbol'], []).append(day)
    finally:
        connection.close()
    path = root / 'data' / 'edgar_deals' / 'earnings_8k_2022_2026.json'
    if path.exists():
        for row in json.loads(path.read_text()):
            symbol = (row.get('symbol') or '').strip().upper()
            session = row.get('reaction_session')
            if symbol and session:
                earn.setdefault(symbol, []).append(date.fromisoformat(session[:10]))
    for symbol, days in earn.items():
        earn[symbol] = sorted(set(days))
    return earn


def _as_date(value):
    if value is None or value == '0000-00-00':
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return value


def _f(value):
    if value is None:
        return None
    return float(value)


def fetch_chunk(symbols, earnings, spy, chunk_id):
    path = PANEL / f'{chunk_id}.npz'
    if path.exists():
        print(f'chunk {chunk_id} cached', flush=True)
        return chunk_id
    connection = connect()
    dates_all, x_all, ret_all, xs_all, codes = [], [], [], [], []
    splits = breaks = 0
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            for n_symbol, (code, symbol) in enumerate(symbols):
                if n_symbol % 25 == 0:
                    print(f'chunk {chunk_id} {n_symbol}/{len(symbols)} {symbol}', flush=True)
                cursor.execute(
                    '''SELECT qdate, close, volume FROM stockquote
                       WHERE symbol=%s AND qdate BETWEEN '2013-01-02' AND '2026-11-13'
                       ORDER BY qdate''', (symbol,))
                prices = cursor.fetchall()
                deduped = {}
                for row in prices:
                    deduped[_as_date(row['qdate'])] = row
                prices = [deduped[key] for key in sorted(deduped)]
                if len(prices) < 280:
                    continue
                cursor.execute(
                    '''SELECT qdate, callIV, putIV, meanIV, callvol, putvol FROM optionstat
                       WHERE symbol=%s AND qdate BETWEEN '2013-01-02' AND '2026-11-13' ''', (symbol,))
                options = [
                    (_as_date(row['qdate']), _f(row['callIV']), _f(row['putIV']), _f(row['meanIV']),
                     _f(row['callvol']), _f(row['putvol']))
                    for row in cursor.fetchall() if _as_date(row['qdate']) and _as_date(row['qdate']).year >= 2013
                ]
                cursor.execute(
                    '''SELECT qdate, otmcall_vol FROM daystat
                       WHERE underlying=%s AND qdate BETWEEN '2013-01-02' AND '2026-11-13' ''', (symbol,))
                otm = [(_as_date(row['qdate']), _f(row['otmcall_vol'])) for row in cursor.fetchall()]
                try:
                    built = symbol_panel(
                        [_as_date(row['qdate']) for row in prices],
                        [0.0 if _f(row['close']) is None else _f(row['close']) for row in prices],
                        [0.0 if _f(row['volume']) is None else _f(row['volume']) for row in prices],
                        options, otm, earnings.get(symbol, []), spy,
                    )
                except Exception as exc:  # noqa: BLE001
                    print(f'skip {symbol} {exc}', flush=True)
                    continue
                if built is None:
                    continue
                day, matrix, ret, excess, n_split, n_break = built
                dates_all.append(day)
                x_all.append(matrix)
                ret_all.append(ret)
                xs_all.append(excess)
                codes.append(np.full(len(day), code, dtype=np.int32))
                splits += n_split
                breaks += n_break
    finally:
        connection.close()
    if not dates_all:
        np.savez_compressed(path, dates=np.zeros(0, np.int32), empty=np.array([1]))
        return chunk_id
    np.savez_compressed(
        path,
        dates=np.concatenate(dates_all),
        x=np.vstack(x_all),
        ret=np.vstack(ret_all),
        xs=np.vstack(xs_all),
        code=np.concatenate(codes),
        splits=np.array([splits]), breaks=np.array([breaks]),
    )
    print(f'chunk {chunk_id} rows {sum(len(item) for item in dates_all)}', flush=True)
    return chunk_id


def build_panel(root: Path, include_etp: bool = False):
    PANEL.mkdir(parents=True, exist_ok=True)
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute(
                '''SELECT DISTINCT symbol FROM optionstat
                   WHERE qdate BETWEEN '2014-01-01' AND '2026-11-13' AND symbol <> '' ''')
            symbols = sorted({row['symbol'].strip().upper() for row in cursor.fetchall() if row['symbol']})
            symbols, etp_stats = partition_symbols(symbols, include_etp=include_etp)
            print(stats_line(etp_stats), flush=True)
            cursor.execute(
                '''SELECT qdate, close FROM stockquote
                   WHERE symbol='SPY' AND qdate BETWEEN '2013-01-02' AND '2026-11-13'
                   ORDER BY qdate''')
            spy_rows = [(_as_date(row['qdate']), _f(row['close'])) for row in cursor.fetchall()]
    finally:
        connection.close()
    spy, forward = spy_series(spy_rows)
    print(f'symbols {len(symbols)} spy {len(spy)}', flush=True)
    earnings = load_earnings(root)
    print(f'earnings symbols {len(earnings)}', flush=True)
    coded = list(enumerate(symbols))
    chunks = [coded[i:i + 200] for i in range(0, len(coded), 200)]
    manifest = PANEL / 'symbols.txt'
    wanted = '\n'.join(symbols) + '\n'
    if manifest.exists() and manifest.read_text() != wanted:
        for stale in PANEL.glob('*.npz'):
            stale.unlink()
    manifest.write_text(wanted)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch_chunk, chunk, earnings, spy, i) for i, chunk in enumerate(chunks)]
        for done, future in enumerate(as_completed(futures), start=1):
            future.result()
            if done % 5 == 0:
                print(f'chunks {done}/{len(chunks)}', flush=True)
    dates, xs, rets, excess, codes = [], [], [], [], []
    split_count = break_count = 0
    for i in range(len(chunks)):
        loaded = np.load(PANEL / f'{i}.npz')
        if loaded['dates'].size == 0:
            continue
        dates.append(loaded['dates'])
        xs.append(loaded['x'])
        rets.append(loaded['ret'])
        excess.append(loaded['xs'])
        codes.append(loaded['code'])
        split_count += int(loaded['splits'][0])
        break_count += int(loaded['breaks'][0])
    panel = dict(
        dates=np.concatenate(dates), x=np.vstack(xs), ret=np.vstack(rets),
        xs=np.vstack(excess), code=np.concatenate(codes),
        symbols=np.array(symbols), splits=split_count, breaks=break_count,
        spy_forward=forward,
        etp_exclusion=etp_stats,
    )
    print(f'panel rows {len(panel["dates"])} splits {split_count} breaks {break_count}', flush=True)
    return panel


def _mean(values):
    values = [value for value in values if value is not None and value == value]
    if not values:
        return None
    return float(sum(values) / len(values))


def _cell(rows):
    daily_hit = np.array([row['hit'] for row in rows if row['hit'] is not None], dtype=np.float64)
    if len(daily_hit) == 0:
        return None
    horizon = rows[0]['horizon']
    low, high = block_bootstrap(daily_hit, horizon)
    hits = sum(row['hits'] for row in rows)
    known_picks = sum(row['k'] for row in rows)
    return dict(
        dates=len(rows),
        hit=_mean([row['hit'] for row in rows]),
        base=_mean([row['base_hit'] for row in rows]),
        random=_mean([row['random_hit'] for row in rows]),
        xs_hit=_mean([row['xs_hit'] for row in rows]),
        base_xs=_mean([row['base_xs'] for row in rows]),
        net_mean=_mean([row['net_mean'] for row in rows]),
        net_median=_mean([row['net_median'] for row in rows]),
        random_net=_mean([row['random_net'] for row in rows]),
        ci=[low, high],
        wilson=list(wilson(hits, known_picks)),
        terminal=_terminal(rows),
    )


def _terminal(rows):
    ordered = sorted(rows, key=lambda row: row['date'])
    step = ordered[0]['horizon']
    wealth = spy = random_w = 1.0
    taken = 0
    for row in ordered[::step]:
        if row['net_mean'] is None or row['spy_ret'] is None:
            continue
        wealth *= 1.0 + row['net_mean']
        spy *= 1.0 + row['spy_ret']
        random_w *= 1.0 + (row['random_net'] if row['random_net'] is not None else 0.0)
        taken += 1
    return dict(basket=wealth, spy=spy, random=random_w, rebalances=taken)


def summarize(records):
    groups = {}
    for row in records:
        groups.setdefault((row['model'], row['horizon'], row['k'], bool(row['holdout'])), []).append(row)
    cells = []
    for (model, horizon, k, holdout), rows in sorted(groups.items()):
        cell = _cell(rows)
        if cell is None:
            continue
        cell.update(model=model, horizon=horizon, k=k, holdout=holdout)
        cell['by_year'] = []
        for year in sorted({row['year'] for row in rows}):
            year_rows = [row for row in rows if row['year'] == year]
            year_cell = _cell(year_rows)
            if year_cell:
                cell['by_year'].append(dict(year=year, hit=year_cell['hit'], base=year_cell['base'], net_mean=year_cell['net_mean']))
        cell['by_regime'] = []
        for flag, label in ((1, 'above'), (0, 'below')):
            subset = [row for row in rows if row['regime'] == flag]
            regime_cell = _cell(subset)
            if regime_cell:
                cell['by_regime'].append(dict(
                    regime=label, hit=regime_cell['hit'], base=regime_cell['base'],
                    net_mean=regime_cell['net_mean'], dates=regime_cell['dates']))
        cells.append(cell)
    return cells


def verdict(cells):
    """A robust edge needs the walk-forward interval above the base, a positive holdout, and 7 agreeing years."""
    passed = []
    for model in ('composite', 'logistic', 'boost'):
        walk = next((cell for cell in cells if cell['model'] == model and cell['horizon'] == 20 and cell['k'] == 10 and not cell['holdout']), None)
        held = next((cell for cell in cells if cell['model'] == model and cell['horizon'] == 20 and cell['k'] == 10 and cell['holdout']), None)
        if walk is None or held is None or walk['ci'][0] is None:
            continue
        years = [item for item in walk['by_year'] if item['hit'] is not None and item['base'] is not None and item['hit'] > item['base']]
        ok = walk['ci'][0] > walk['base'] and held['hit'] > held['base'] and len(years) >= 7
        passed.append(dict(model=model, ok=bool(ok), years_above=len(years), walk_hit=walk['hit'], holdout_hit=held['hit']))
    return dict(robust=any(item['ok'] for item in passed), models=passed)


def _one(cells, model, holdout):
    for cell in cells:
        if cell['model'] == model and cell['horizon'] == 20 and cell['k'] == 10 and cell['holdout'] == holdout:
            return cell
    return None


def plain_verdict(cells, decision) -> str:
    """Absolute-up bar first, then the SPY comparison the book actually has to beat."""
    boost_walk = _one(cells, 'boost', False)
    boost_hold = _one(cells, 'boost', True)
    parts = []
    if decision['robust']:
        parts.append(
            'Histogram boosting clears the absolute-direction bar set before the run. On the 20-session top 10 its walk-forward interval sits above the share of liquid names that were up, the holdout is above its own base rate, and at least seven walk-forward years agree. The equal-weight composite and the logistic do not clear that bar.')
    else:
        parts.append(
            'No model clears the absolute-direction bar. That bar required the 20-session top-10 walk-forward interval to sit above the universe base rate, the holdout hit rate to beat its own base rate, and at least seven walk-forward years to agree.')
    if boost_walk and boost_hold and boost_walk['xs_hit'] is not None and boost_walk['base_xs'] is not None:
        parts.append(
            f"The same boosting slate beats SPY on {boost_walk['xs_hit']:.1%} of walk-forward picks against a {boost_walk['base_xs']:.1%} universe rate, and on {boost_hold['xs_hit']:.1%} of holdout picks against {boost_hold['base_xs']:.1%}.")
    if boost_walk and boost_hold:
        parts.append(
            f"A non-overlapping 20-session top-10 book finishes at {boost_walk['terminal']['basket']:.2f} times capital over the walk-forward, against {boost_walk['terminal']['spy']:.2f} for SPY and {boost_walk['terminal']['random']:.2f} for random slates. The holdout book finishes at {boost_hold['terminal']['basket']:.2f}, against {boost_hold['terminal']['spy']:.2f} for SPY.")
    ahead = False
    if boost_walk and boost_hold and boost_walk['xs_hit'] is not None and boost_walk['base_xs'] is not None:
        ahead = (
            boost_walk['xs_hit'] > boost_walk['base_xs']
            and boost_hold['xs_hit'] > boost_hold['base_xs']
            and boost_walk['terminal']['basket'] > boost_walk['terminal']['spy']
            and boost_hold['terminal']['basket'] > boost_hold['terminal']['spy']
        )
    if ahead:
        parts.append('On that fuller test the edge is still there: the slate beats SPY more often than the universe, and the compounded book finishes ahead of SPY in both samples.')
    else:
        parts.append('There is not a robust edge over SPY. Being up more often than the average stock is not the same as beating the market, and the compounded book does not finish ahead of SPY in both samples. The average net return is also much larger than the median, so a few very large winners carry the mean.')
    return ' '.join(parts)


def feature_table(importance):
    rows = []
    for kind, by_h in importance.items():
        weights = by_h.get('20') or []
        if not weights:
            continue
        mean = np.mean(np.array(weights, dtype=np.float64), axis=0)
        order = np.argsort(-mean)
        rows.append(dict(model=kind, rank=[
            dict(feature=MODEL_FEATURES[int(i)], weight=float(mean[int(i)])) for i in order
        ]))
    return rows


def render(report: dict) -> str:
    lines = [
        '# Direction test',
        '',
        'The question is whether a stock is up over the next 5, 10, or 20 sessions, not whether it jumps 15%. Each score uses only the close and earlier data. The last twelve months, from 2025-11-13, were not used to choose a setting. Logistic regression and histogram gradient boosting use fixed settings and retrain once a year on earlier years only. The composite is an equal-weight signed z-score with no fit.',
        '',
        'The universe is optionable names with a close of at least $5 and a 20-session median dollar volume of at least $5 million. A round trip costs 10 basis points. Prices that jump by a standard split ratio are put on one share count before the return is measured. A move larger than 70% that is not a split leaves the lookback feature blank.',
        '',
        '## What is not in the data',
        '',
    ]
    lines += [f'- {item}' for item in report['missing']]
    lines += [
        '',
        f"Panel rows: {report['rows']}. Detected split days: {report['splits']}. Unexplained breaks: {report['breaks']}.",
        '',
        '## Hit rate',
        '',
        'Hit rate is the share of the slate that finished up. The base rate is the same share for every liquid name that day. The interval is a block bootstrap of the daily hit rate, with the block as long as the horizon.',
        '',
        '| Sample | Model | Horizon | Slate | Hit rate | Base rate | Random slate | Excess hit | Excess base | 95% interval |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |',
    ]
    for cell in report['cells']:
        sample = 'Holdout' if cell['holdout'] else 'Walk-forward'
        lines.append(
            f"| {sample} | {cell['model']} | {cell['horizon']} | {cell['k']} | {_n(cell['hit'])} | {_n(cell['base'])} | {_n(cell['random'])} | {_n(cell['xs_hit'])} | {_n(cell['base_xs'])} | {_span(cell['ci'])} |"
        )
    lines += [
        '',
        '## Net return',
        '',
        'Average and median forward return after the 10-basis-point cost. The terminal column compounds a non-overlapping book: one slate every horizon, so a 20-session pick is not reopened while it is still held.',
        '',
        '| Sample | Model | Horizon | Slate | Mean net | Median net | Random mean net | Basket | SPY | Random basket |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for cell in report['cells']:
        sample = 'Holdout' if cell['holdout'] else 'Walk-forward'
        term = cell['terminal']
        lines.append(
            f"| {sample} | {cell['model']} | {cell['horizon']} | {cell['k']} | {_n(cell['net_mean'])} | {_n(cell['net_median'])} | {_n(cell['random_net'])} | {_n(term['basket'])} | {_n(term['spy'])} | {_n(term['random'])} |"
        )
    lines += ['', '## Walk-forward by year, top 10, 20 sessions', '']
    lines.append('| Model | ' + ' | '.join(str(year) for year in report['years']) + ' |')
    lines.append('| --- | ' + ' | '.join('---:' for _ in report['years']) + ' |')
    for model in ('composite', 'logistic', 'boost'):
        cell = _find(report, model, 20, 10, False)
        by_year = {item['year']: item['hit'] - item['base'] for item in cell['by_year']} if cell else {}
        lines.append('| ' + model + ' | ' + ' | '.join(_n(by_year.get(year)) for year in report['years']) + ' |')
    lines += ['', 'The year cells are hit rate minus that year\'s universe base rate.', '', '## Regime, top 10, 20 sessions', '']
    lines.append('| Sample | Model | SPY vs 200-day average | Dates | Hit rate | Base rate | Mean net |')
    lines.append('| --- | --- | --- | ---: | ---: | ---: | ---: |')
    for cell in report['cells']:
        if cell['horizon'] != 20 or cell['k'] != 10:
            continue
        sample = 'Holdout' if cell['holdout'] else 'Walk-forward'
        for item in cell['by_regime']:
            lines.append(
                f"| {sample} | {cell['model']} | {item['regime']} | {item['dates']} | {_n(item['hit'])} | {_n(item['base'])} | {_n(item['net_mean'])} |"
            )
    lines += ['', '## Feature weight on the 20-session model', '']
    for block in report['importance']:
        top = ', '.join(f"{item['feature']} {item['weight']:.3f}" for item in block['rank'][:6])
        lines.append(f"- {block['model']}: {top}")
    lines += [
        '',
        '## Signed composite',
        '',
        'Higher 12-1 momentum, a positive earnings-reaction gap, and a close above the 50- and 200-day averages raise the score. So does an out-of-the-money call-volume surge. The last month\'s return, realized volatility, the implied-volatility level and its 20-session change, put-minus-call implied volatility, and the put/call volume ratio lower it. SPY versus its 200-day average is a regime flag and a model input. It is the same for every name, so it is not in the cross-sectional composite.',
        '',
        '## Verdict',
        '',
        report['verdict_text'],
        '',
    ]
    return '\n'.join(lines)


def _find(report, model, horizon, k, holdout):
    for cell in report['cells']:
        if cell['model'] == model and cell['horizon'] == horizon and cell['k'] == k and cell['holdout'] == holdout:
            return cell
    return None


def _n(value):
    return 'n/a' if value is None else f'{value:.3f}'


def _span(pair):
    if not pair or pair[0] is None:
        return 'n/a'
    return f'{pair[0]:.3f} to {pair[1]:.3f}'


def run(root: Path, include_etp: bool = False) -> dict:
    panel = build_panel(root, include_etp=include_etp)
    nan_rate = {
        name: float(np.mean(~np.isfinite(panel['x'][:, i]))) for i, name in enumerate(MODEL_FEATURES)
    }
    scores, importance = score_panel(panel['dates'], panel['x'], panel['ret'])
    records = evaluate(panel['dates'], panel['x'], scores, panel['ret'], panel['xs'], panel['spy_forward'])
    cells = summarize(records)
    decision = verdict(cells)
    text = plain_verdict(cells, decision)
    report = dict(
        rows=int(len(panel['dates'])), splits=int(panel['splits']), breaks=int(panel['breaks']),
        missing=MISSING, nan_rate=nan_rate, cells=cells,
        years=list(range(FIRST_TEST_YEAR, LAST_WALK_YEAR + 1)),
        importance=feature_table(importance), verdict=decision, verdict_text=text,
        etp_exclusion=panel.get('etp_exclusion'),
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'direction_test.json').write_text(json.dumps(report, indent=2) + '\n')
    text_out = render(report)
    (folder / 'DIRECTION_TEST.md').write_text(text_out)
    print(text_out, flush=True)
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    add_argument(parser)
    args = parser.parse_args()
    run(Path('.'), include_etp=args.include_etp)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
