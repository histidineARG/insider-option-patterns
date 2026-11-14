"""Options-flow anomalies over 1, 3, and 5 day windows.

The baseline is the 50 or 100 sessions before the window and does not include it.
A row is kept only when the split-adjusted close is at least $10, the name has a
listed chain that day, and average daily option volume over that baseline is at
least 100 contracts, with at least 40 valid baseline days. Earnings sessions are
removed. Nothing in a score uses a later close.
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime
from pathlib import Path

import numpy as np

HOLDOUT_START = date(2025, 11, 13)
FIRST_TEST_YEAR = 2018
PRICE_MIN = 10.0
MIN_OPTION_VOLUME = 100.0
MIN_VALID = 40
WINDOWS = (1, 3, 5)
BASELINES = (50, 100)
JUMP_HORIZONS = (1, 5, 10, 20)
TOP_PERCENTS = (0.01, 0.005, 0.001)
RATIO_CAP = 50.0
CACHE = Path('/tmp/anomaly_cache')
PULL_FROM = '2017-01-01'
PULL_TO = '2026-11-13'

SIDES = ('call', 'put')
MONEYS = ('dotm', 'otm', 'atm', 'itm')
DTES = ('d07', 'd21', 'd45', 'd90', 'dlong')
N_BUCKET = len(SIDES) * len(MONEYS) * len(DTES)
SHORT_MONEY = (0, 1)  # deep OTM, OTM
SHORT_DTE = (0, 1)    # 0-7, 8-21

METHODS = ('mahalanobis', 'hbos', 'iforest', 'lof', 'ocsvm', 'pca')


def bucket_index(side: int, money: int, dte: int) -> int:
    return (side * len(MONEYS) + money) * len(DTES) + dte


def feature_names() -> list[str]:
    names = []
    for side in SIDES:
        for money in MONEYS:
            for dte in DTES:
                names.append(f'vol_{side}_{money}_{dte}')
    names += [
        'doi_z_call_otm_short', 'doi_z_put_otm_short',
        'dnot_call', 'dnot_put',
        'share_call_otm_short', 'share_put_otm_short',
        'persist_count', 'persist_max', 'persist_mean',
        'ret_10', 'ret_1', 'rvol',
    ]
    return names


FEATURES = feature_names()
N_FEAT = len(FEATURES)
CONFIGS = [(window, baseline) for window in WINDOWS for baseline in BASELINES]


def _split_candidates():
    values = []
    for factor in (2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 50, 100):
        values.append(float(factor))
        values.append(1.0 / factor)
    return np.asarray(values)


CANDIDATES = _split_candidates()


def adjust_closes(closes: np.ndarray, tol: float = 0.05):
    """Put earlier closes on the latest share count when a day matches a split ratio."""
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
        if error[choice] <= tol and abs(ratio - 1.0) >= 0.35:
            factors[i] = CANDIDATES[choice]
        elif abs(ratio - 1.0) > 0.70:
            breaks[i] = True
    adjusted = closes.copy()
    scale = 1.0
    for i in range(n - 1, 0, -1):
        scale *= factors[i]
        adjusted[i - 1] *= scale
    return adjusted, factors, breaks


def short_ids(side: int) -> list[int]:
    return [bucket_index(side, money, dte) for money in SHORT_MONEY for dte in SHORT_DTE]


CALL_SHORT = np.array(short_ids(0))
PUT_SHORT = np.array(short_ids(1))
CALLS = np.array([bucket_index(0, money, dte) for money in range(4) for dte in range(5)])
PUTS = np.array([bucket_index(1, money, dte) for money in range(4) for dte in range(5)])


def _pad(values: np.ndarray) -> np.ndarray:
    if values.ndim == 1:
        return np.concatenate([np.zeros(1, dtype=np.float64), np.cumsum(values)])
    return np.vstack([np.zeros((1, values.shape[1]), dtype=np.float64), np.cumsum(values, axis=0)])


def _seg(padded: np.ndarray, start: np.ndarray, end: np.ndarray) -> np.ndarray:
    return padded[end] - padded[start]


def delta_oi(oi: np.ndarray) -> np.ndarray:
    """Change in open interest known at this close. Tomorrow's open interest is not used."""
    out = np.zeros_like(oi, dtype=np.float64)
    out[1:] = oi[1:] - oi[:-1]
    return out


def earnings_masks(dates: list[date], reactions: list[date]):
    """Feature block is the reaction session and the two before it. Jumps use the reaction only."""
    reaction = np.zeros(len(dates), dtype=bool)
    block = np.zeros(len(dates), dtype=bool)
    if not dates or not reactions:
        return reaction, block
    for day in reactions:
        lo, hi = 0, len(dates)
        while lo < hi:
            mid = (lo + hi) // 2
            if dates[mid] < day:
                lo = mid + 1
            else:
                hi = mid
        if lo >= len(dates) or (dates[lo] - day).days > 2:
            continue
        reaction[lo] = True
        for step in range(3):
            if lo - step >= 0:
                block[lo - step] = True
    return reaction, block


def _ratios(det_sum, base_sum, window: int, base_count) -> np.ndarray:
    det_avg = det_sum / window
    base_avg = base_sum / base_count
    quiet = base_avg < 1.0
    ratio = np.ones_like(det_avg)
    lit = quiet & (det_avg >= 1.0)
    normal = ~quiet
    ratio[lit] = det_avg[lit]
    ratio[normal] = det_avg[normal] / base_avg[normal]
    return np.clip(ratio, 0.0, RATIO_CAP)


def build_frame(adj, total_vol, has_chain, block, reaction, vol, prem, oi, dnot):
    """Window features for every baseline and length. Rows that fail a filter stay unmarked."""
    adj = np.asarray(adj, dtype=np.float64)
    n = len(adj)
    total_vol = np.asarray(total_vol, dtype=np.float64)
    has_chain = np.asarray(has_chain, dtype=bool)
    block = np.asarray(block, dtype=bool)
    reaction = np.asarray(reaction, dtype=bool)
    vol = np.asarray(vol, dtype=np.float64).reshape(n, N_BUCKET)
    prem = np.asarray(prem, dtype=np.float64).reshape(n, N_BUCKET)
    oi = np.asarray(oi, dtype=np.float64).reshape(n, N_BUCKET)
    dnot = np.asarray(dnot, dtype=np.float64).reshape(n, N_BUCKET)
    doi = delta_oi(oi)
    # Earnings sessions stay out of the baseline so a known earnings spike does not become the norm.
    clean_vol = np.where(block[:, None], 0.0, vol)
    clean_prem = np.where(block[:, None], 0.0, prem)
    clean_doi = np.where(block[:, None], 0.0, doi)
    clean_dnot = np.where(block[:, None], 0.0, dnot)
    valid = (adj > 0) & ~block
    ret = np.full(n, np.nan)
    good = (adj[1:] > 0) & (adj[:-1] > 0)
    ret[1:][good] = adj[1:][good] / adj[:-1][good] - 1.0
    c_vol, c_prem, c_doi, c_dnot = _pad(clean_vol), _pad(clean_prem), _pad(clean_doi), _pad(clean_dnot)
    c_vol_raw, c_prem_raw = _pad(vol), _pad(prem)
    c_doi_raw, c_dnot_raw = _pad(doi), _pad(dnot)
    c_tot, c_valid = _pad(total_vol), _pad(valid.astype(np.float64))
    ret_clean = np.where(block, 0.0, np.nan_to_num(ret, nan=0.0))
    c_ret, c_ret2 = _pad(ret_clean), _pad(ret_clean ** 2)
    c_block = _pad(block.astype(np.float64))
    c_react = _pad(reaction.astype(np.float64))
    y15 = np.full((n, len(JUMP_HORIZONS)), np.nan, dtype=np.float32)
    y10 = np.full(n, np.nan, dtype=np.float32)
    for h_i, horizon in enumerate(JUMP_HORIZONS):
        if n <= horizon:
            continue
        future = np.lib.stride_tricks.sliding_window_view(adj[1:], horizon).max(axis=1)
        react = _seg(c_react, np.arange(1, n - horizon + 1), np.arange(1 + horizon, n + 1))
        base = adj[:n - horizon]
        move = np.full(n - horizon, np.nan)
        ok = base > 0
        move[ok] = future[ok] / base[ok] - 1.0
        label = np.full(n, np.nan)
        known = np.isfinite(move) & (react == 0)
        label[:n - horizon][known] = (move[known] >= 0.15).astype(np.float64)
        y15[:, h_i] = label
        if horizon == 5:
            ten = np.full(n, np.nan)
            ten[:n - horizon][known] = (move[known] >= 0.10).astype(np.float64)
            y10 = ten
    out = []
    ret10 = np.full(n, np.nan)
    ret1 = ret.copy()
    if n > 10:
        ok10 = (adj[10:] > 0) & (adj[:-10] > 0)
        ret10[10:][ok10] = adj[10:][ok10] / adj[:-10][ok10] - 1.0
    for window, baseline in CONFIGS:
        start = window + baseline
        idx = np.arange(start, n)
        if len(idx) == 0:
            out.append(None)
            continue
        det_end = idx + 1
        det_start = idx - window + 1
        base_end = det_start
        base_start = base_end - baseline
        keep = (
            (_seg(c_valid, base_start, base_end) >= MIN_VALID)
            & (adj[idx] >= PRICE_MIN)
            & has_chain[idx]
            & (_seg(c_tot, base_start, base_end) / baseline >= MIN_OPTION_VOLUME)
            & (_seg(c_block, det_start, det_end) == 0)
            & np.isfinite(ret10[idx])
        )
        chosen = idx[keep]
        if len(chosen) == 0:
            out.append(None)
            continue
        det_end, det_start = chosen + 1, chosen - window + 1
        base_end, base_start = det_start, det_start - baseline
        n_valid = _seg(c_valid, base_start, base_end)
        count = n_valid[:, None]
        feat = np.full((len(chosen), N_FEAT), np.nan, dtype=np.float32)
        feat[:, :N_BUCKET] = _ratios(
            _seg(c_vol_raw, det_start, det_end), _seg(c_vol, base_start, base_end), window, count)
        for column, ids in ((N_BUCKET, CALL_SHORT), (N_BUCKET + 1, PUT_SHORT)):
            det = _seg(c_doi_raw, det_start, det_end)[:, ids].sum(axis=1) / window
            base = _seg(c_doi, base_start, base_end)[:, ids].sum(axis=1) / n_valid
            daily_sum = doi[:, ids].sum(axis=1)
            daily_sum = np.where(block, 0.0, daily_sum)
            base_sq = _seg(_pad(daily_sum ** 2), base_start, base_end) / n_valid
            std = np.sqrt(np.clip(base_sq - base ** 2, 0, None))
            z = np.zeros(len(chosen))
            np.divide(det - base, std, out=z, where=std > 1e-8)
            feat[:, column] = np.clip(z, -10, 10)
        for column, ids in ((N_BUCKET + 2, CALLS), (N_BUCKET + 3, PUTS)):
            feat[:, column] = _ratios(
                _seg(c_dnot_raw, det_start, det_end)[:, ids].sum(axis=1),
                _seg(c_dnot, base_start, base_end)[:, ids].sum(axis=1),
                window, n_valid).ravel()
        total_det = _seg(c_prem_raw, det_start, det_end).sum(axis=1)
        total_base = _seg(c_prem, base_start, base_end).sum(axis=1)
        for column, ids in ((N_BUCKET + 4, CALL_SHORT), (N_BUCKET + 5, PUT_SHORT)):
            det_share = np.divide(
                _seg(c_prem_raw, det_start, det_end)[:, ids].sum(axis=1), total_det, out=np.zeros(len(chosen)), where=total_det > 0)
            base_share = np.divide(
                _seg(c_prem, base_start, base_end)[:, ids].sum(axis=1), total_base, out=np.zeros(len(chosen)), where=total_base > 0)
            feat[:, column] = det_share - base_share
        series = prem[:, CALL_SHORT].sum(axis=1)
        clean_series = np.where(block, 0.0, series)
        base_mean = _seg(_pad(clean_series), base_start, base_end) / n_valid
        base_var = _seg(_pad(clean_series ** 2), base_start, base_end) / n_valid - base_mean ** 2
        std = np.sqrt(np.clip(base_var, 0, None))
        daily = np.zeros((len(chosen), window))
        for step in range(window):
            point = series[chosen - step]
            z = np.zeros(len(chosen))
            np.divide(point - base_mean, std, out=z, where=std > 1e-8)
            daily[:, step] = z
        feat[:, N_BUCKET + 6] = np.sum(daily > 3.0, axis=1)
        feat[:, N_BUCKET + 7] = np.max(daily, axis=1)
        feat[:, N_BUCKET + 8] = np.mean(daily, axis=1)
        feat[:, N_BUCKET + 9] = ret10[chosen]
        feat[:, N_BUCKET + 10] = ret1[chosen]
        rvol_mean = _seg(c_ret, base_start, base_end) / n_valid
        rvol_var = _seg(c_ret2, base_start, base_end) / n_valid - rvol_mean ** 2
        feat[:, N_BUCKET + 11] = np.sqrt(np.clip(rvol_var, 0, None))
        quiet = (np.abs(ret10[chosen]) < 0.05) & (np.abs(ret1[chosen]) < 0.03)
        out.append(dict(
            index=chosen.astype(np.int32),
            x=feat,
            y15=y15[chosen],
            y10=y10[chosen].astype(np.float32),
            quiet=quiet.astype(np.uint8),
        ))
    return out


def robust_threshold(train_scores: np.ndarray, percent: float) -> float:
    finite = train_scores[np.isfinite(train_scores)]
    if len(finite) < 100:
        return np.inf
    return float(np.quantile(finite, 1.0 - percent))


def lift_stats(anomaly: np.ndarray, jump: np.ndarray):
    known = np.isfinite(jump)
    anomaly = anomaly & known
    event = (jump == 1) & known
    base_n = int(known.sum())
    base_hit = int(event.sum())
    cond_n = int(anomaly.sum())
    cond_hit = int((anomaly & event).sum())
    base = base_hit / base_n if base_n else None
    cond = cond_hit / cond_n if cond_n else None
    lift = cond / base if cond is not None and base else None
    return dict(base=base, cond=cond, lift=lift, base_n=base_n, cond_n=cond_n, cond_hit=cond_hit, base_hit=base_hit)


def wilson(hits: int, n: int, z: float = 1.96):
    if n <= 0:
        return None, None
    p = hits / n
    den = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - margin, centre + margin


def clustered_lift(symbol: np.ndarray, anomaly: np.ndarray, jump: np.ndarray, reps: int = 250, seed: int = 11):
    """Resample tickers. Each ticker carries its own anomaly and jump counts."""
    known = np.isfinite(jump)
    event = (jump == 1) & known
    flag = anomaly & known
    order = np.argsort(symbol, kind='mergesort')
    sym = symbol[order]
    cuts = np.r_[0, np.flatnonzero(np.diff(sym)) + 1, len(sym)]
    n_sym = len(cuts) - 1
    both = np.zeros(n_sym)
    cond = np.zeros(n_sym)
    base_hit = np.zeros(n_sym)
    base_n = np.zeros(n_sym)
    ordered_event, ordered_flag, ordered_known = event[order], flag[order], known[order]
    for i, (a, b) in enumerate(zip(cuts[:-1], cuts[1:])):
        both[i] = np.sum(ordered_flag[a:b] & ordered_event[a:b])
        cond[i] = np.sum(ordered_flag[a:b])
        base_hit[i] = np.sum(ordered_event[a:b])
        base_n[i] = np.sum(ordered_known[a:b])
    rng = np.random.RandomState(seed)
    lifts = np.empty(reps)
    for i in range(reps):
        draw = rng.randint(0, n_sym, size=n_sym)
        c_n = cond[draw].sum()
        b_n = base_n[draw].sum()
        if c_n <= 0 or b_n <= 0 or base_hit[draw].sum() <= 0:
            lifts[i] = np.nan
            continue
        lifts[i] = (both[draw].sum() / c_n) / (base_hit[draw].sum() / b_n)
    finite = lifts[np.isfinite(lifts)]
    if len(finite) < 20:
        return None, None
    return float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))


def date_hit_rate(dates: np.ndarray, scores: np.ndarray, jump: np.ndarray, k: int):
    """Share of dates where at least one of the k highest scores jumps. Random base is 1-(1-p)^k."""
    known = np.isfinite(jump) & np.isfinite(scores)
    if known.sum() == 0:
        return None
    order = np.argsort(dates[known], kind='mergesort')
    day = dates[known][order]
    rank_score = scores[known][order]
    event = jump[known][order] == 1
    cuts = np.r_[0, np.flatnonzero(np.diff(day)) + 1, len(day)]
    hits, bases, used = [], [], 0
    for a, b in zip(cuts[:-1], cuts[1:]):
        if b - a < k:
            continue
        chosen = np.argpartition(-rank_score[a:b], k - 1)[:k]
        hits.append(float(event[a:b][chosen].any()))
        p = float(event[a:b].mean())
        bases.append(1.0 - (1.0 - p) ** k)
        used += 1
    if not hits:
        return None
    return dict(hit=float(np.mean(hits)), random=float(np.mean(bases)), dates=used)


def _impute(train: np.ndarray, test: np.ndarray):
    med = np.nanmedian(train, axis=0)
    med = np.where(np.isfinite(med), med, 0.0)
    out_train, out_test = train.copy(), test.copy()
    for matrix in (out_train, out_test):
        bad = ~np.isfinite(matrix)
        matrix[bad] = np.take(med, np.where(bad)[1])
    return out_train, out_test


def _cap_sample(idx: np.ndarray, cap: int, seed: int) -> np.ndarray:
    if len(idx) <= cap:
        return idx
    rng = np.random.RandomState(seed)
    return idx[np.sort(rng.choice(len(idx), size=cap, replace=False))]


def hbos_scores(train: np.ndarray, test: np.ndarray, bins: int = 10) -> np.ndarray:
    score = np.zeros(len(test))
    for col in range(train.shape[1]):
        column = train[:, col]
        lo, hi = np.quantile(column, [0.01, 0.99])
        if hi <= lo:
            continue
        edges = np.linspace(lo, hi, bins + 1)
        hist, _ = np.histogram(np.clip(column, lo, hi), bins=edges)
        hist = hist.astype(np.float64) + 1.0
        hist /= hist.sum()
        placed = np.clip(np.digitize(test[:, col], edges[1:-1], right=True), 0, bins - 1)
        score += -np.log(hist[placed])
    return score


def mahalanobis_scores(train: np.ndarray, test: np.ndarray) -> np.ndarray:
    from sklearn.covariance import LedoitWolf
    center = train.mean(axis=0)
    spread = train.std(axis=0)
    spread[spread < 1e-8] = 1.0
    model = LedoitWolf().fit((train - center) / spread)
    precision = model.precision_
    delta = (test - center) / spread
    return np.einsum('ij,jk,ik->i', delta, precision, delta)


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
    return 0.0 if value is None else float(value)


CHAIN_SQL = '''
SELECT qdate, `type` AS side,
  CASE
    WHEN ABS(delta) >= 0.65 THEN 3
    WHEN ABS(delta) >= 0.35 THEN 2
    WHEN ABS(delta) >= 0.15 THEN 1
    WHEN ABS(delta) >= 0.05 THEN 0
    WHEN underlying_last > 0 AND strike > 0 AND ((`type`='call' AND strike/underlying_last >= 1.10)
         OR (`type`='put' AND underlying_last/strike >= 1.10)) THEN 0
    WHEN underlying_last > 0 AND strike > 0 AND ((`type`='call' AND strike/underlying_last >= 1.02)
         OR (`type`='put' AND underlying_last/strike >= 1.02)) THEN 1
    WHEN underlying_last > 0 AND strike > 0 AND ((`type`='call' AND strike/underlying_last >= 0.98)
         OR (`type`='put' AND underlying_last/strike >= 0.98)) THEN 2
    WHEN underlying_last > 0 AND strike > 0 THEN 3
    ELSE -1
  END AS money,
  CASE
    WHEN DATEDIFF(edate, qdate) BETWEEN 0 AND 7 THEN 0
    WHEN DATEDIFF(edate, qdate) BETWEEN 8 AND 21 THEN 1
    WHEN DATEDIFF(edate, qdate) BETWEEN 22 AND 45 THEN 2
    WHEN DATEDIFF(edate, qdate) BETWEEN 46 AND 90 THEN 3
    WHEN DATEDIFF(edate, qdate) > 90 THEN 4
    ELSE -1
  END AS dteb,
  SUM(volume) AS vol,
  SUM(CASE WHEN bid > 0 AND ask >= bid THEN volume * (bid + ask) / 2 * 100 ELSE 0 END) AS prem,
  SUM(oi) AS oi,
  SUM(CASE WHEN delta IS NOT NULL AND underlying_last > 0
      THEN ABS(delta) * underlying_last * volume * 100 ELSE 0 END) AS dnot
FROM optiondaily
WHERE underlying=%s AND qdate BETWEEN %s AND %s AND volume > 0
  AND `type` IN ('call', 'put')
GROUP BY qdate, side, money, dteb
'''


def load_earnings(root: Path):
    from insider_resolved import connect
    earn = {}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute(
                '''SELECT UPPER(symbol) AS symbol, erdate, rxdate FROM erdate
                   WHERE erdate >= '2016-01-01' ''')
            for row in cursor.fetchall():
                day = _as_date(row['rxdate'] or row['erdate'])
                if day is not None and row['symbol']:
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
    return {symbol: sorted(set(days)) for symbol, days in earn.items()}


def fetch_symbol(symbol: str, earnings: dict):
    path = CACHE / f'{symbol}.npz'
    if path.exists():
        return symbol
    from insider_resolved import connect
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            cursor.execute(
                '''SELECT qdate, close FROM stockquote
                   WHERE symbol=%s AND qdate BETWEEN %s AND %s ORDER BY qdate''',
                (symbol, PULL_FROM, PULL_TO))
            prices = {}
            for row in cursor.fetchall():
                day = _as_date(row['qdate'])
                if day is not None:
                    prices[day] = _f(row['close'])
            if len(prices) < 160:
                np.savez_compressed(path, empty=np.array([1]))
                return symbol
            cursor.execute(
                '''SELECT qdate, callvol, putvol FROM optionstat
                   WHERE symbol=%s AND qdate BETWEEN %s AND %s''',
                (symbol, PULL_FROM, PULL_TO))
            chain = {}
            for row in cursor.fetchall():
                day = _as_date(row['qdate'])
                if day is not None and day.year >= 2017:
                    chain[day] = _f(row['callvol']) + _f(row['putvol'])
            cursor.execute(CHAIN_SQL, (symbol, PULL_FROM, PULL_TO))
            grouped = cursor.fetchall()
    finally:
        connection.close()
    dates = sorted(prices)
    adj, _factors, _breaks = adjust_closes(np.array([prices[day] for day in dates]))
    total = np.array([chain.get(day, 0.0) for day in dates])
    has_chain = np.array([day in chain for day in dates])
    reaction, block = earnings_masks(dates, earnings.get(symbol.upper(), []))
    vol = np.zeros((len(dates), N_BUCKET))
    prem = np.zeros_like(vol)
    oi = np.zeros_like(vol)
    dnot = np.zeros_like(vol)
    index = {day: i for i, day in enumerate(dates)}
    for row in grouped:
        day = _as_date(row['qdate'])
        money, dteb = int(row['money']), int(row['dteb'])
        if day not in index or money < 0 or dteb < 0:
            continue
        slot = bucket_index(0 if row['side'] == 'call' else 1, money, dteb)
        i = index[day]
        vol[i, slot] += _f(row['vol'])
        prem[i, slot] += _f(row['prem'])
        oi[i, slot] += _f(row['oi'])
        dnot[i, slot] += _f(row['dnot'])
    frames = build_frame(adj, total, has_chain, block, reaction, vol, prem, oi, dnot)
    payload = {'empty': np.array([0]), 'symbol': np.array(symbol)}
    kept = 0
    ordinals = np.array([day.toordinal() for day in dates], dtype=np.int32)
    for i, frame in enumerate(frames):
        if frame is None:
            payload[f'i{i}'] = np.zeros(0, dtype=np.int32)
            continue
        chosen = frame['index']
        payload[f'i{i}'] = ordinals[chosen]
        payload[f'x{i}'] = frame['x']
        payload[f'y{i}'] = frame['y15']
        payload[f't{i}'] = frame['y10']
        payload[f'q{i}'] = frame['quiet']
        kept += len(chosen)
    if kept == 0:
        np.savez_compressed(path, empty=np.array([1]), symbol=np.array(symbol))
        return symbol
    tmp = path.with_suffix('.tmp.npz')
    np.savez_compressed(tmp, **payload)
    tmp.replace(path)
    return symbol


def _safe_fetch(symbol: str, earnings: dict):
    try:
        return fetch_symbol(symbol, earnings)
    except Exception as exc:  # noqa: BLE001
        print(f'skip {symbol} {type(exc).__name__}', flush=True)
        return symbol


def build_cache(root: Path, symbols: list[str]):
    CACHE.mkdir(parents=True, exist_ok=True)
    earnings = load_earnings(root)
    print(f'earnings calendars {len(earnings)} symbols {len(symbols)}', flush=True)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    pending = [symbol for symbol in symbols if not (CACHE / f'{symbol}.npz').exists()]
    print(f'to scan {len(pending)} cached {len(symbols) - len(pending)}', flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_safe_fetch, symbol, earnings) for symbol in pending]
        for done, future in enumerate(as_completed(futures), start=1):
            future.result()
            if done % 25 == 0 or done == len(pending):
                print(f'scanned {done}/{len(pending)}', flush=True)


def load_config(symbols: list[str], config_index: int):
    dates, xs, y15, y10, quiet, codes = [], [], [], [], [], []
    covered = 0
    for code, symbol in enumerate(symbols):
        path = CACHE / f'{symbol}.npz'
        if not path.exists():
            continue
        loaded = np.load(path, allow_pickle=False)
        if int(loaded['empty'][0]) == 1 or f'i{config_index}' not in loaded.files:
            continue
        idx = loaded[f'i{config_index}']
        if len(idx) == 0:
            continue
        covered += 1
        dates.append(idx)
        xs.append(loaded[f'x{config_index}'])
        y15.append(loaded[f'y{config_index}'])
        y10.append(loaded[f't{config_index}'])
        quiet.append(loaded[f'q{config_index}'])
        codes.append(np.full(len(idx), code, dtype=np.int32))
    if not dates:
        return None
    return dict(
        dates=np.concatenate(dates), x=np.vstack(xs), y15=np.vstack(y15),
        y10=np.concatenate(y10), quiet=np.concatenate(quiet),
        symbol=np.concatenate(codes), tickers=covered,
    )


def _folds(dates: np.ndarray):
    years = np.array([date.fromordinal(int(day)).year for day in dates])
    holdout_cut = HOLDOUT_START.toordinal()
    folds = []
    for year in range(FIRST_TEST_YEAR, HOLDOUT_START.year + 1):
        test = (years == year) & (dates < holdout_cut)
        train = dates < date(year, 1, 1).toordinal()
        if test.any() and train.sum() >= 500:
            folds.append((train, test, False))
    folds.append((dates < holdout_cut, dates >= holdout_cut, True))
    return folds


def run_config(panel: dict, window: int, baseline: int) -> dict:
    dates, x = panel['dates'], panel['x']
    print(f'config {window}d/{baseline} rows {len(dates)} tickers {panel["tickers"]}', flush=True)
    store = {kind: np.full(len(dates), np.nan, dtype=np.float32) for kind in METHODS}
    flags = {kind: {str(percent): np.zeros(len(dates), dtype=bool) for percent in TOP_PERCENTS} for kind in METHODS}
    for train_mask, test_mask, is_holdout in _folds(dates):
        train_idx = np.flatnonzero(train_mask)
        test_idx = np.flatnonzero(test_mask)
        if len(test_idx) == 0 or len(train_idx) < 500:
            continue
        ref_idx = _cap_sample(train_idx, 20000, 19)
        label = 'holdout' if is_holdout else str(date.fromordinal(int(dates[test_idx[0]])).year)
        for kind in METHODS:
            print(f'  fit {kind} {label} train {len(train_idx)} test {len(test_idx)}', flush=True)
            scored, cuts = _score_pair(kind, x[train_idx], x[test_idx], x[ref_idx], seed=len(train_idx) % 10000 + window)
            if scored is None:
                continue
            store[kind][test_idx] = scored
            for percent, cut in cuts.items():
                flags[kind][percent][test_idx] = scored >= cut
    return summarize_config(panel, store, flags, window, baseline)


def summarize_config(panel, store, flags, window, baseline):
    dates = panel['dates']
    holdout = dates >= HOLDOUT_START.toordinal()
    walk = (dates < HOLDOUT_START.toordinal()) & (np.array([date.fromordinal(int(day)).year for day in dates]) >= FIRST_TEST_YEAR)
    cells = []
    for kind in METHODS:
        for percent in TOP_PERCENTS:
            anomaly = flags[kind][str(percent)]
            for sample_name, mask in (('walk', walk), ('holdout', holdout)):
                if mask.sum() < 100:
                    continue
                for h_i, horizon in enumerate(JUMP_HORIZONS):
                    stats = lift_stats(anomaly[mask], panel['y15'][mask, h_i])
                    ci = clustered_lift(panel['symbol'][mask], anomaly[mask], panel['y15'][mask, h_i])
                    cell = dict(
                        method=kind, percent=percent, horizon=horizon, jump=0.15,
                        sample=sample_name, lift=stats['lift'], cond=stats['cond'], base=stats['base'],
                        cond_n=stats['cond_n'], ci=ci, wilson=list(wilson(stats['cond_hit'], stats['cond_n'])),
                    )
                    if horizon in (5, 20):
                        top = date_hit_rate(dates[mask], store[kind][mask], panel['y15'][mask, h_i], 4)
                        cell['top4'] = top
                    cells.append(cell)
                ten = lift_stats(anomaly[mask], panel['y10'][mask])
                cells.append(dict(
                    method=kind, percent=percent, horizon=5, jump=0.10, sample=sample_name,
                    lift=ten['lift'], cond=ten['cond'], base=ten['base'], cond_n=ten['cond_n'],
                    ci=clustered_lift(panel['symbol'][mask], anomaly[mask], panel['y10'][mask]),
                    wilson=list(wilson(ten['cond_hit'], ten['cond_n'])),
                ))
                quiet = mask & (panel['quiet'] == 1)
                if quiet.sum() >= 100:
                    qstats = lift_stats(anomaly[quiet], panel['y15'][quiet, JUMP_HORIZONS.index(20)])
                    cells.append(dict(
                        method=kind, percent=percent, horizon=20, jump=0.15, sample=sample_name + '-quiet',
                        lift=qstats['lift'], cond=qstats['cond'], base=qstats['base'], cond_n=qstats['cond_n'],
                        ci=(None, None), wilson=(None, None),
                    ))
    buckets = bucket_profile(panel, flags['mahalanobis']['0.01'], walk)
    if window == 5 and baseline == 50:
        np.savez_compressed(
            CACHE / 'sec_mahalanobis_w5_b50.npz',
            dates=dates, symbol=panel['symbol'], scores=store['mahalanobis'])
    return dict(
        window=window, baseline=baseline, rows=int(len(dates)), tickers=int(panel['tickers']),
        cells=cells, buckets=buckets,
        event=event_study(panel, store['mahalanobis'], walk, holdout),
    )


def bucket_profile(panel, anomaly, walk):
    mask = walk & anomaly & (panel['y15'][:, JUMP_HORIZONS.index(20)] == 1)
    base = walk & np.isfinite(panel['y15'][:, JUMP_HORIZONS.index(20)])
    if mask.sum() < 30 or base.sum() < 30:
        return []
    jump_mean = np.nanmean(panel['x'][mask][:, :N_BUCKET], axis=0)
    all_mean = np.nanmean(panel['x'][base][:, :N_BUCKET], axis=0)
    gap = jump_mean - all_mean
    order = np.argsort(-np.nan_to_num(gap, nan=-1e9))[:8]
    return [dict(feature=FEATURES[int(i)], jump=float(jump_mean[int(i)]), other=float(all_mean[int(i)])) for i in order]


def event_study(panel, scores, walk, holdout):
    """Mean Mahalanobis score on the jump day and 5, 10, and 20 sessions earlier, versus other names."""
    out = []
    horizon = JUMP_HORIZONS.index(20)
    dates, symbols = panel['dates'], panel['symbol']
    for name, mask in (('walk', walk), ('holdout', holdout)):
        known = mask & np.isfinite(scores) & np.isfinite(panel['y15'][:, horizon])
        if known.sum() < 50:
            continue
        jump = known & (panel['y15'][:, horizon] == 1)
        rest = known & (panel['y15'][:, horizon] == 0)
        path = {lag: [] for lag in (0, 5, 10, 20)}
        order = np.argsort(symbols, kind='mergesort')
        sym = symbols[order]
        cuts = np.r_[0, np.flatnonzero(np.diff(sym)) + 1, len(sym)]
        for a, b in zip(cuts[:-1], cuts[1:]):
            rows = order[a:b]
            row_dates = dates[rows]
            seq = np.argsort(row_dates, kind='mergesort')
            rows = rows[seq]
            is_jump = jump[rows]
            for pos in np.flatnonzero(is_jump):
                for lag in path:
                    if pos - lag >= 0:
                        path[lag].append(float(scores[rows[pos - lag]]))
        out.append(dict(
            sample=name,
            jump_score=float(np.mean(scores[jump])) if jump.any() else None,
            other_score=float(np.mean(scores[rest])) if rest.any() else None,
            jumps=int(jump.sum()),
            path={str(lag): float(np.mean(values)) if values else None for lag, values in path.items()},
        ))
    return out


def sec_overlap(panel, scores, cases):
    """Cross-sectional percentile of the score on each case's trade dates."""
    dates = panel['dates']
    symbols = panel['symbol']
    found = []
    by_symbol = {}
    for case in cases:
        by_symbol.setdefault(case['symbol'].upper(), []).append(case)
    # The panel stores codes, not tickers. Caller passes a map via panel['names'].
    names = panel.get('names')
    if names is None:
        return []
    code = {name.upper(): i for i, name in enumerate(names)}
    for symbol, group in by_symbol.items():
        if symbol not in code:
            for case in group:
                found.append(dict(symbol=symbol, case=case['id'], days=0, in_top=None, median_pct=None))
            continue
        rows = symbols == code[symbol]
        if not rows.any():
            for case in group:
                found.append(dict(symbol=symbol, case=case['id'], days=0, in_top=None, median_pct=None))
            continue
        day_rows = {int(day): i for i, day in enumerate(dates) if False}
        del day_rows
        for case in group:
            start = date.fromisoformat(case['trade_start']).toordinal()
            end = date.fromisoformat(case['trade_end']).toordinal()
            mine = np.flatnonzero(rows & (dates >= start) & (dates <= end) & np.isfinite(scores))
            percentiles = []
            for row in mine:
                day = dates[row]
                peers = scores[(dates == day) & np.isfinite(scores)]
                if len(peers) < 20:
                    continue
                percentiles.append(float(np.mean(peers <= scores[row])))
            found.append(dict(
                symbol=symbol, case=case['id'], days=len(percentiles),
                median_pct=None if not percentiles else float(np.median(percentiles)),
                in_top=None if not percentiles else float(np.mean(np.array(percentiles) >= 0.99)),
            ))
    return found


def render(report: dict) -> str:
    lines = [
        '# Options-flow anomalies before price jumps',
        '',
        'Each score uses a 1, 3, or 5 session window ending at that close. The baseline is the 50 or 100 sessions before that window, so the window itself is not in the average. A name is kept only when the split-adjusted close is at least $10, it has a listed chain that day, average daily option volume over the baseline is at least 100 contracts, and at least 40 baseline sessions are usable. The chain scan itself keeps symbols whose average volume since 2017 is at least 100, so a name that is usually quieter is not pulled. Earnings reaction sessions, and the two sessions before them, are not scored. A forward jump that lands on an earnings reaction is not counted.',
        '',
        'PyOD is not installed, so the histogram method is a direct HBOS. The autoencoder is an 8-component reconstruction. Isolation forest, local outlier factor, and a one-class SVM are the other detectors, plus a Ledoit-Wolf Mahalanobis distance. Thresholds are the training-score quantiles. The holdout from 2025-11-13 is fit only on earlier rows.',
        '',
        'Earnings dates come from `erdate` through 2022-01-04 and from 8-K Item 2.02 reaction sessions after that. Names missing from both calendars are not earnings-filtered. Earnings are not inferred from the price jump itself. Open interest enters as today minus yesterday, never tomorrow. Dollar premium is the bid-ask midpoint times volume times 100. Delta-weighted notional uses absolute delta when delta is present; otherwise the bucket is assigned from strike over spot.',
        '',
        f"Symbols on a calendar with no earnings date: {report['uncovered_earnings']}. Detected split steps: {report['splits']}.",
        '',
        '## Universe',
        '',
        '| Window | Baseline | Tickers | Ticker-days |',
        '| ---: | ---: | ---: | ---: |',
    ]
    for block in report['configs']:
        lines.append(f"| {block['window']} | {block['baseline']} | {block['tickers']} | {block['rows']} |")
    lines += [
        '',
        '## Lift at the top 1 percent, 20-session 15 percent jump',
        '',
        'Lift is the jump rate inside the anomaly over the jump rate of the whole universe. The interval resamples tickers.',
        '',
        '| Method | Window | Baseline | Walk-forward lift | Interval | Holdout lift | Interval |',
        '| --- | ---: | ---: | ---: | --- | ---: | --- |',
    ]
    for block in report['configs']:
        for method in METHODS:
            walk = _cell(block, method, 0.01, 20, 0.15, 'walk')
            held = _cell(block, method, 0.01, 20, 0.15, 'holdout')
            lines.append(
                f"| {method} | {block['window']} | {block['baseline']} | {_n(walk, 'lift')} | {_span(walk)} | {_n(held, 'lift')} | {_span(held)} |"
            )
    lines += ['', '## Other thresholds and horizons, 5-session window, 50-session baseline', '']
    lines.append('| Method | Sample | Threshold | Horizon | Jump | Lift | Conditional rate | Base rate |')
    lines.append('| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |')
    focus = next((block for block in report['configs'] if block['window'] == 5 and block['baseline'] == 50), None)
    if focus:
        for cell in focus['cells']:
            if cell['sample'] not in ('walk', 'holdout'):
                continue
            if cell['percent'] == 0.01 and cell['horizon'] == 20 and cell['jump'] == 0.15:
                continue
            lines.append(
                f"| {cell['method']} | {cell['sample']} | {cell['percent']:.1%} | {cell['horizon']} | {cell['jump']:.0%} | {_n(cell, 'lift')} | {_n(cell, 'cond')} | {_n(cell, 'base')} |"
            )
    lines += ['', '## Daily top 4, 20-session 15 percent jump', '', '| Method | Window | Baseline | Sample | Date hit rate | Random top 4 |', '| --- | ---: | ---: | --- | ---: | ---: |']
    for block in report['configs']:
        for method in METHODS:
            for sample in ('walk', 'holdout'):
                cell = _cell(block, method, 0.01, 20, 0.15, sample)
                top = (cell or {}).get('top4') or {}
                lines.append(
                    f"| {method} | {block['window']} | {block['baseline']} | {sample} | {_fmt(top.get('hit'))} | {_fmt(top.get('random'))} |"
                )
    lines += ['', '## Buckets elevated on Mahalanobis anomalies that later jump', '']
    for block in report['configs']:
        if not block.get('buckets'):
            continue
        lines.append(f"Window {block['window']}, baseline {block['baseline']}: " + ', '.join(
            f"{item['feature']} {item['jump']:.2f} vs {item['other']:.2f}" for item in block['buckets'][:5]))
    lines += ['', '## Quiet names', '', 'Quiet means the 10-session return is inside 5 percent and the session return is inside 3 percent, both known at the close. The table is the 20-session jump at the top 1 percent.', '']
    lines.append('| Method | Window | Baseline | Sample | Lift |')
    lines.append('| --- | ---: | ---: | --- | ---: |')
    for block in report['configs']:
        for method in ('mahalanobis', 'iforest'):
            for sample in ('walk-quiet', 'holdout-quiet'):
                cell = _cell(block, method, 0.01, 20, 0.15, sample)
                if cell:
                    lines.append(f"| {method} | {block['window']} | {block['baseline']} | {sample} | {_n(cell, 'lift')} |")
    lines += ['', '## Score before a 20-session jump, Mahalanobis', '']
    for block in report['configs']:
        for item in block.get('event') or []:
            path = item.get('path') or {}
            lines.append(
                f"Window {block['window']}, baseline {block['baseline']}, {item['sample']}: "
                f"jump day {_fmt(item.get('jump_score'))}, other names {_fmt(item.get('other_score'))}, "
                f"5 sessions earlier {_fmt(path.get('5'))}, 20 sessions earlier {_fmt(path.get('20'))}."
            )
    lines += ['', '## Known SEC cases', '', 'Percentile is within that session\'s cross section, for the Mahalanobis score on the 5-session window and 50-session baseline. A case with no chain days in the kept universe is absent from the score.', '']
    if report.get('sec'):
        lines.append('| Case | Symbol | Trade days scored | Median percentile | Share in top 1 percent |')
        lines.append('| --- | --- | ---: | ---: | ---: |')
        for row in report['sec']:
            lines.append(
                f"| {row.get('case', '')} | {row['symbol']} | {row['days']} | {_fmt(row.get('median_pct'))} | {_fmt(row.get('in_top'))} |"
            )
    lines += ['', '## Verdict', '', report['verdict'], '']
    return '\n'.join(lines)


def _cell(block, method, percent, horizon, jump, sample):
    for cell in block['cells']:
        if (cell['method'] == method and cell['percent'] == percent and cell['horizon'] == horizon
                and cell['jump'] == jump and cell['sample'] == sample):
            return cell
    return None


def _n(cell, key):
    if not cell or cell.get(key) is None:
        return 'n/a'
    return f"{cell[key]:.2f}"


def _fmt(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.3f}'


def _span(cell):
    if not cell or not cell.get('ci') or cell['ci'][0] is None:
        return 'n/a'
    return f"{cell['ci'][0]:.2f} to {cell['ci'][1]:.2f}"


def verdict_text(configs) -> str:
    clears = []
    for block in configs:
        for method in METHODS:
            walk = _cell(block, method, 0.01, 20, 0.15, 'walk')
            held = _cell(block, method, 0.01, 20, 0.15, 'holdout')
            top_w = (walk or {}).get('top4') or {}
            top_h = (held or {}).get('top4') or {}
            if not walk or not held or walk.get('lift') is None or held.get('lift') is None:
                continue
            interval_ok = walk.get('ci') and walk['ci'][0] is not None and walk['ci'][0] > 1
            if interval_ok and held['lift'] > 1 and (top_w.get('hit') or 0) > (top_w.get('random') or 1) and (top_h.get('hit') or 0) > (top_h.get('random') or 1):
                clears.append(f"{method} on a {block['window']}-day window against a {block['baseline']}-day baseline")
    if not clears:
        return ('No detector clears the bar set before the run. That bar is a walk-forward lift above 1 at the top 1 percent for a 20-session 15 percent jump, with the ticker-bootstrap interval also above 1, a holdout lift above 1, and a daily top-4 hit rate above the random top-4 in both samples.')
    return ('These detectors clear the bar set before the run, on a 20-session 15 percent jump at the top 1 percent: ' + '; '.join(clears) + '.')


def run(root: Path):
    symbols = [line.strip() for line in Path('/tmp/anomaly_symbol_list.txt').read_text().splitlines() if line.strip()]
    build_cache(root, symbols)
    earnings = load_earnings(root)
    uncovered = sum(1 for symbol in symbols if symbol.upper() not in earnings)
    cases = json.loads((root / 'data' / 'sec_cases.json').read_text())['cases']
    configs = []
    for i, (window, baseline) in enumerate(CONFIGS):
        panel = load_config(symbols, i)
        if panel is None:
            continue
        panel['names'] = symbols
        block = run_config(panel, window, baseline)
        configs.append(block)
        del panel
    report = dict(
        configs=configs, uncovered_earnings=uncovered, splits='see build log',
        sec=sec_case_pass(symbols, cases), verdict='',
    )
    report['verdict'] = verdict_text(configs)
    report['splits'] = 'applied inside each price series before the $10 filter and the jump labels'
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'anomaly_test.json').write_text(json.dumps(report, indent=2) + '\n')
    text = render(report)
    (folder / 'ANOMALY_TEST.md').write_text(text)
    print(text, flush=True)
    return report


def sec_case_pass(symbols, cases):
    """Score SEC trade dates on the saved 5-day / 50-day Mahalanobis file if the pass stored it."""
    path = CACHE / 'sec_mahalanobis_w5_b50.npz'
    if not path.exists():
        return []
    loaded = np.load(path)
    panel = dict(
        dates=loaded['dates'], symbol=loaded['symbol'], names=symbols,
    )
    return sec_overlap(panel, loaded['scores'], cases)


def _score_pair(kind: str, train_x: np.ndarray, score_x: np.ndarray, ref_x: np.ndarray, seed: int):
    """Fit once on the past. Higher scores are more anomalous. Thresholds use the training rows only."""
    if len(train_x) < 500 or len(score_x) == 0:
        return None, None
    train_x, both = _impute(train_x, np.vstack([score_x, ref_x]))
    scored, reference = _apply_model(kind, train_x, both[:len(score_x)], both[len(score_x):], seed)
    if scored is None:
        return None, None
    cuts = {str(percent): robust_threshold(reference, percent) for percent in TOP_PERCENTS}
    return scored, cuts


def _apply_model(kind, train_x, score_x, ref_x, seed):
    def pack(values_score, values_ref):
        return values_score.astype(np.float32), values_ref.astype(np.float32)

    if kind == 'hbos':
        return pack(hbos_scores(train_x, score_x), hbos_scores(train_x, ref_x))
    if kind == 'mahalanobis':
        sample = _cap_sample(np.arange(len(train_x)), 80_000, seed)
        fitted = train_x[sample]
        return pack(mahalanobis_scores(fitted, score_x), mahalanobis_scores(fitted, ref_x))
    if kind == 'pca':
        from sklearn.decomposition import PCA
        center = train_x.mean(axis=0)
        spread = train_x.std(axis=0)
        spread[spread < 1e-8] = 1.0
        sample = _cap_sample(np.arange(len(train_x)), 80_000, seed)
        model = PCA(n_components=min(8, train_x.shape[1] - 1), random_state=seed)
        model.fit((train_x[sample] - center) / spread)

        def error(rows):
            scaled = (rows - center) / spread
            rebuilt = model.inverse_transform(model.transform(scaled))
            return np.mean((scaled - rebuilt) ** 2, axis=1)

        return pack(error(score_x), error(ref_x))
    if kind == 'iforest':
        from sklearn.ensemble import IsolationForest
        sample = _cap_sample(np.arange(len(train_x)), 80_000, seed)
        model = IsolationForest(
            n_estimators=80, max_samples=2048, random_state=seed, n_jobs=2, contamination='auto')
        model.fit(train_x[sample])
        return pack(-model.score_samples(score_x), -model.score_samples(ref_x))
    if kind == 'lof':
        from sklearn.neighbors import LocalOutlierFactor
        sample = _cap_sample(np.arange(len(train_x)), 2500, seed)
        model = LocalOutlierFactor(n_neighbors=20, novelty=True, n_jobs=2)
        model.fit(train_x[sample])
        return pack(-model.decision_function(score_x), -model.decision_function(ref_x))
    if kind == 'ocsvm':
        from sklearn.svm import OneClassSVM
        sample = _cap_sample(np.arange(len(train_x)), 4000, seed)
        model = OneClassSVM(kernel='rbf', gamma='scale', nu=0.02)
        model.fit(train_x[sample])
        return pack(-model.decision_function(score_x), -model.decision_function(ref_x))
    raise ValueError(kind)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
