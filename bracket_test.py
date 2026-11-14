"""Long-stock brackets on the anomaly tail.

The signal rules and the walk-forward split match the anomaly test. The bracket
grid is scored on the walk-forward only. The holdout is read after that choice.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import numpy as np

from anomaly_flow import HOLDOUT_START, _as_date, _f, adjust_closes, load_earnings
from insider_footprint import load_sessions
from straddle_test import score_signals

STOPS = (0.03, 0.05, 0.08)
BREAKEVEN_TARGET = (0.85 / 0.15) * 0.05
TARGETS = (0.15, 0.20, 0.25, BREAKEVEN_TARGET, 0.30, 0.40)
HOLDS = (10, 20, 40)
ROUND_TRIP = 0.001
STOP_EXTRA = 0.001
MAX_POSITIONS = 20
SOURCES = (
    ('hbos', 1, 'p1'), ('hbos', 1, 'p05'), ('hbos', 1, 'top4'),
    ('hbos', 5, 'p1'), ('hbos', 5, 'p05'), ('hbos', 5, 'top4'),
    ('iforest', 1, 'p1'), ('iforest', 1, 'p05'), ('iforest', 1, 'top4'),
)


def scale_ohlc(open_, high, low, close):
    """Apply the same split scale to the whole bar. Ratios use the adjusted close."""
    adjusted, _factors, _breaks = adjust_closes(close)
    scale = np.ones_like(close)
    np.divide(adjusted, close, out=scale, where=close > 0)
    return open_ * scale, high * scale, low * scale, adjusted


def walk_bracket(opens, highs, lows, closes, entry, stop, target, hold, earnings, gap_on_first=False):
    """Stop, target, or time exit. A same-day stop and target counts as the stop. A gap fills at the open."""
    stop_px = entry * (1.0 - stop)
    target_px = entry * (1.0 + target)
    last = min(hold, len(opens)) - 1
    if last < 0 or entry <= 0:
        return None
    for i in range(last + 1):
        if earnings is not None and earnings[i]:
            return None
        check_gap = gap_on_first or i > 0
        if check_gap and opens[i] <= stop_px:
            return 'stop', float(opens[i]), i
        if check_gap and opens[i] >= target_px:
            return 'target', float(opens[i]), i
        hit_stop = lows[i] <= stop_px
        hit_target = highs[i] >= target_px
        if hit_stop:
            return 'stop', float(stop_px), i
        if hit_target:
            return 'target', float(target_px), i
    return 'time', float(closes[last]), last


def net_return(entry, exit_price, kind: str) -> float:
    ret = exit_price / entry - 1.0 - ROUND_TRIP
    if kind == 'stop':
        ret -= STOP_EXTRA
    return float(ret)


def kelly_terms(returns: np.ndarray) -> dict:
    if len(returns) == 0:
        return dict(p=None, b=None, expectancy=None, f=None, avg_win=None, avg_loss=None)
    wins = returns[returns > 0]
    losses = returns[returns <= 0]
    p = float(len(wins) / len(returns))
    avg_win = float(wins.mean()) if len(wins) else None
    avg_loss = float(losses.mean()) if len(losses) else None
    b = None if not avg_win or not avg_loss else avg_win / abs(avg_loss)
    f = None if not b else p - (1.0 - p) / b
    return dict(p=p, b=b, expectancy=float(returns.mean()), f=f, avg_win=avg_win, avg_loss=avg_loss)


def theoretical_b(target: float, stop: float) -> float:
    return target / stop


def dedupe(entries: np.ndarray, symbols: np.ndarray, index: dict, gap: int = 20) -> np.ndarray:
    keep = np.zeros(len(entries), dtype=bool)
    last = {}
    order = np.argsort(entries, kind='mergesort')
    for i in order:
        day = date.fromordinal(int(entries[i]))
        if day not in index:
            continue
        previous = last.get(int(symbols[i]))
        if previous is not None and index[day] < previous + gap:
            continue
        last[int(symbols[i])] = index[day]
        keep[i] = True
    return keep


def clustered_mean(symbols: np.ndarray, values: np.ndarray, reps: int = 300, seed: int = 11):
    if len(values) < 30:
        return None, None
    order = np.argsort(symbols, kind='mergesort')
    sym = symbols[order]
    vals = values[order]
    if sym.dtype.kind in ('U', 'S', 'O'):
        change = np.flatnonzero(sym[1:] != sym[:-1]) + 1 if len(sym) > 1 else np.array([], dtype=int)
    else:
        change = np.flatnonzero(np.diff(sym)) + 1
    cuts = np.r_[0, change, len(sym)]
    groups = [vals[a:b] for a, b in zip(cuts[:-1], cuts[1:])]
    rng = np.random.RandomState(seed)
    means = np.empty(reps)
    n = len(groups)
    for i in range(reps):
        draw = rng.randint(0, n, size=n)
        means[i] = np.mean(np.concatenate([groups[j] for j in draw]))
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def pack_stats(returns, outcomes, symbols) -> dict:
    finite = np.isfinite(returns)
    returns, outcomes, symbols = returns[finite], outcomes[finite], symbols[finite]
    if len(returns) == 0:
        empty = dict(n=0, target=None, stop=None, time=None, mean=None, median=None, ci=(None, None))
        empty.update(kelly_terms(returns))
        return empty
    terms = kelly_terms(returns)
    return dict(
        n=int(len(returns)),
        target=float(np.mean(outcomes == 1)),
        stop=float(np.mean(outcomes == 2)),
        time=float(np.mean(outcomes == 0)),
        mean=float(np.mean(returns)),
        median=float(np.median(returns)),
        ci=clustered_mean(symbols, returns),
        **terms,
    )


def simulate_path(opens, highs, lows, closes, entry, earnings_flags, gap_on_first=False):
    """All stop, target, and hold results for one entry. Outcome 1 is the target, 2 is the stop, 0 is time."""
    n_cfg = len(STOPS) * len(TARGETS) * len(HOLDS)
    rets = np.full(n_cfg, np.nan)
    outcomes = np.zeros(n_cfg, dtype=np.int8)
    elapsed = np.zeros(n_cfg, dtype=np.int16)
    for s_i, stop in enumerate(STOPS):
        for t_i, target in enumerate(TARGETS):
            for h_i, hold in enumerate(HOLDS):
                walked = walk_bracket(
                    opens, highs, lows, closes, entry, stop, target, hold, earnings_flags, gap_on_first)
                slot = (s_i * len(TARGETS) + t_i) * len(HOLDS) + h_i
                if walked is None:
                    continue
                kind, price, day = walked
                rets[slot] = net_return(entry, price, kind)
                outcomes[slot] = {'time': 0, 'target': 1, 'stop': 2}[kind]
                elapsed[slot] = day + 1
    return rets, outcomes, elapsed


def portfolio_curve(entry_i, exit_i, rets, scores, stop, risk, sessions_n):
    """Fixed fraction of equity risked at the stop. At most 20 names are open."""
    if len(rets) == 0 or risk <= 0:
        return dict(cagr=None, max_drawdown=None, sharpe=None, terminal=None)
    order = np.argsort(entry_i, kind='mergesort')
    equity = np.ones(sessions_n)
    open_until = []
    cash_events = []
    for i in order:
        if not np.isfinite(rets[i]):
            continue
        start = int(entry_i[i])
        stop_at = int(exit_i[i])
        open_until = [item for item in open_until if item > start]
        if len(open_until) >= MAX_POSITIONS:
            continue
        open_until.append(stop_at)
        frac = risk / stop
        cash_events.append((stop_at, frac * float(rets[i])))
    # Apply exits in order. Equity is flat between exits, then jumps.
    cash_events.sort()
    level = 1.0
    path = np.ones(sessions_n)
    cursor = 0
    for day, pnl in cash_events:
        day = min(max(day, 0), sessions_n - 1)
        path[cursor:day] = level
        level *= 1.0 + pnl
        path[day:] = level
        cursor = day
    path[cursor:] = level
    daily = np.diff(path) / path[:-1]
    daily = daily[np.isfinite(daily)]
    sharpe = None if len(daily) < 20 or daily.std() == 0 else float(daily.mean() / daily.std() * np.sqrt(252))
    peak = np.maximum.accumulate(path)
    drawdown = float(np.max(1.0 - path / peak))
    years = max(sessions_n / 252.0, 1 / 252)
    cagr = float(path[-1] ** (1.0 / years) - 1.0) if path[-1] > 0 else None
    return dict(cagr=cagr, max_drawdown=drawdown, sharpe=sharpe, terminal=float(path[-1]))


def run(root: Path):
    symbols = [line.strip() for line in Path('/tmp/anomaly_symbol_list.txt').read_text().splitlines() if line.strip()]
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    print('scoring', flush=True)
    panels, flags = score_signals(symbols)
    signals, universe = _collect_signals(symbols, panels, flags)
    print(f'signals {len(signals)} universe {len(universe)}', flush=True)
    del panels, flags
    rng = np.random.RandomState(20261113)
    matches = _match(signals, universe, rng)
    needed = {}
    for row, match in zip(signals, matches):
        needed.setdefault(row['symbol'], set()).add(row['date'])
        if match is not None:
            needed.setdefault(symbols[int(match[0])], set()).add(date.fromordinal(int(match[1])))
    print(f'loading prices for {len(needed)} names', flush=True)
    bars = _load_prices(sorted(needed))
    earnings = {symbol: {day.toordinal() for day in days} for symbol, days in load_earnings(root).items()}
    print('simulating', flush=True)
    report = _simulate(signals, matches, symbols, bars, earnings, sessions, index)
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'bracket_test.json').write_text(json.dumps(report, indent=2) + '\n')
    text = render(report)
    (folder / 'BRACKET_TEST.md').write_text(text)
    print(text, flush=True)
    return report


def _collect_signals(symbols, panels, flags):
    rows = []
    for (kind, window), pack in flags.items():
        panel = panels[window]
        rvol = panel['x'][:, -1]
        for rule, mask in (('p1', pack['p1']), ('p05', pack['p05']), ('top4', pack['top4'])):
            for i in np.flatnonzero(mask):
                rows.append(dict(
                    symbol=symbols[int(panel['symbol'][i])],
                    date=date.fromordinal(int(panel['dates'][i])),
                    source=kind, window=int(window), rule=rule,
                    score=float(pack['scores'][i]),
                    rvol=float(rvol[i]) if np.isfinite(rvol[i]) else None,
                ))
    panel = panels[1]
    finite = np.isfinite(flags[('hbos', 1)]['scores'])
    universe = dict(
        symbol=panel['symbol'][finite],
        date=panel['dates'][finite],
        rvol=panel['x'][finite, -1],
    )
    return rows, universe


def _match(signals, universe, rng):
    dates = universe['date']
    months = np.empty(len(dates), dtype=np.int32)
    for i, ordinal in enumerate(dates.tolist()):
        day = date.fromordinal(int(ordinal))
        months[i] = day.year * 12 + day.month
    decile = np.full(len(dates), -1, dtype=np.int8)
    rvol = universe['rvol']
    month_rows = {}
    for month in np.unique(months):
        idx = np.flatnonzero((months == month) & np.isfinite(rvol))
        month_rows[int(month)] = idx
        if len(idx) < 10:
            continue
        order = np.argsort(rvol[idx])
        ranks = np.empty(len(order), dtype=np.int8)
        ranks[order] = np.minimum(9, np.arange(len(order)) * 10 // len(order))
        decile[idx] = ranks
    buckets = {}
    for i in range(len(dates)):
        buckets.setdefault((int(months[i]), int(decile[i])), []).append(i)
    matched = []
    for row in signals:
        month = row['date'].year * 12 + row['date'].month
        bucket = -1
        idx = month_rows.get(month)
        if row['rvol'] is not None and idx is not None and len(idx):
            bucket = int(min(9, np.sum(rvol[idx] <= row['rvol']) * 10 / len(idx)))
        choices = buckets.get((month, bucket)) or buckets.get((month, -1)) or []
        if not choices:
            matched.append(None)
            continue
        pick = choices[int(rng.randint(0, len(choices)))]
        matched.append((int(universe['symbol'][pick]), int(universe['date'][pick])))
    return matched


def _load_prices(symbols):
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
            days, o, h, l, c = [], [], [], [], []
            for row in rows:
                day = _as_date(row['qdate'])
                if day is None:
                    continue
                days.append(day.toordinal())
                o.append(_f(row['open']))
                h.append(_f(row['high']))
                l.append(_f(row['low']))
                c.append(_f(row['close']))
            o, h, l, c = scale_ohlc(np.array(o), np.array(h), np.array(l), np.array(c))
            return symbol, (np.array(days, dtype=np.int32), o, h, l, c)
        except Exception as exc:  # noqa: BLE001
            print(f'skip {symbol} {type(exc).__name__}', flush=True)
            return symbol, None

    out = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch, symbol) for symbol in symbols]
        for done, future in enumerate(as_completed(futures), start=1):
            symbol, payload = future.result()
            out[symbol] = payload
            if done % 400 == 0 or done == len(symbols):
                print(f'prices {done}/{len(symbols)}', flush=True)
    return out


def _path(bars, symbol, signal_ordinal, entry_mode, earnings):
    payload = bars.get(symbol)
    if payload is None:
        return None
    days, opens, highs, lows, closes = payload
    pos = int(np.searchsorted(days, signal_ordinal))
    if pos >= len(days) or int(days[pos]) != signal_ordinal:
        return None
    if entry_mode == 'next':
        if pos + 1 >= len(days):
            return None
        start = pos + 1
        entry = float(opens[start])
    else:
        start = pos
        entry = float(closes[start])
        if start + 1 >= len(days):
            return None
        start = start + 1
    if entry <= 0:
        return None
    stop = min(len(days), start + 40)
    flags = np.array([int(days[i]) in earnings for i in range(start, stop)])
    return opens[start:stop], highs[start:stop], lows[start:stop], closes[start:stop], entry, flags, int(days[start]), entry_mode == 'close'


def _simulate(signals, matches, symbols, bars, earnings, sessions, index):
    # Materialize every signal path once, then summarize the grid.
    names = {i: name for i, name in enumerate(symbols)}
    records = []
    for row, match in zip(signals, matches):
        earn = earnings.get(row['symbol'].upper(), set())
        path = _path(bars, row['symbol'], row['date'].toordinal(), 'next', earn)
        close_path = _path(bars, row['symbol'], row['date'].toordinal(), 'close', earn)
        random_path = None
        if match is not None:
            random_path = _path(bars, names[match[0]], match[1], 'next', earnings.get(names[match[0]].upper(), set()))
        if path is None:
            continue
        rets, outcomes, elapsed = simulate_path(*path[:6], gap_on_first=path[7])
        random_rets = np.full_like(rets, np.nan)
        if random_path is not None:
            random_rets, _random_out, _random_elapsed = simulate_path(*random_path[:6], gap_on_first=random_path[7])
        close_rets = np.full_like(rets, np.nan)
        if close_path is not None:
            close_rets, _close_out, _close_elapsed = simulate_path(*close_path[:6], gap_on_first=close_path[7])
        records.append(dict(
            symbol=row['symbol'], source=row['source'], window=row['window'], rule=row['rule'],
            date=row['date'], score=row['score'], entry_ord=path[6], elapsed=elapsed,
            rets=rets, outcomes=outcomes, random_rets=random_rets, close_rets=close_rets,
        ))
    print(f'paths {len(records)}', flush=True)
    cells = []
    n_cfg = len(STOPS) * len(TARGETS) * len(HOLDS)
    for source, window, rule in SOURCES:
        chosen_rows = [row for row in records if row['source'] == source and row['window'] == window and row['rule'] == rule]
        if not chosen_rows:
            continue
        for slot in range(n_cfg):
            s_i, rem = divmod(slot, len(TARGETS) * len(HOLDS))
            t_i, h_i = divmod(rem, len(HOLDS))
            for sample in ('walk', 'holdout'):
                subset = [row for row in chosen_rows if (row['date'] >= HOLDOUT_START) == (sample == 'holdout')]
                if not subset:
                    continue
                returns = np.array([row['rets'][slot] for row in subset])
                outcomes = np.array([row['outcomes'][slot] for row in subset])
                sym = np.array([row['symbol'] for row in subset])
                entries = np.array([row['date'].toordinal() for row in subset])
                ids = {name: i for i, name in enumerate(dict.fromkeys(sym.tolist()))}
                codes = np.array([ids[name] for name in sym])
                keep = dedupe(entries, codes, index)
                random_returns = np.array([row['random_rets'][slot] for row in subset])
                close_returns = np.array([row['close_rets'][slot] for row in subset])
                cell = dict(
                    source=source, window=window, rule=rule, sample=sample,
                    stop=STOPS[s_i], target=TARGETS[t_i], hold=HOLDS[h_i],
                    theoretical_b=theoretical_b(TARGETS[t_i], STOPS[s_i]),
                    next=pack_stats(returns, outcomes, sym),
                    deduped=pack_stats(returns[keep], outcomes[keep], sym[keep]),
                    random=pack_stats(random_returns, np.zeros(len(subset), dtype=np.int8), sym),
                    close_entry=pack_stats(close_returns, np.zeros(len(subset), dtype=np.int8), sym),
                )
                cells.append(cell)
    chosen = _choose(cells)
    held = _twin(cells, chosen, 'holdout') if chosen else None
    curve = _curves(records, chosen, sessions, index) if chosen else {}
    return dict(
        cells=_compact(cells), chosen=_label(chosen), holdout=_label(held),
        portfolio=curve, verdict=verdict_text(chosen, held),
    )


def _choose(cells):
    pool = [cell for cell in cells if cell['sample'] == 'walk' and cell['deduped']['mean'] is not None]
    if not pool:
        return None
    return max(pool, key=lambda cell: cell['deduped']['mean'])


def _twin(cells, chosen, sample):
    for cell in cells:
        if (cell['sample'] == sample and cell['source'] == chosen['source'] and cell['window'] == chosen['window']
                and cell['rule'] == chosen['rule'] and cell['stop'] == chosen['stop']
                and cell['target'] == chosen['target'] and cell['hold'] == chosen['hold']):
            return cell
    return None


def _label(cell):
    if cell is None:
        return None
    keep = ('source', 'window', 'rule', 'stop', 'target', 'hold', 'sample', 'theoretical_b', 'next', 'deduped', 'random', 'close_entry')
    return {key: cell[key] for key in keep}


def _curves(records, chosen, sessions, index):
    subset = [row for row in records if row['source'] == chosen['source'] and row['window'] == chosen['window'] and row['rule'] == chosen['rule']]
    slot = (STOPS.index(chosen['stop']) * len(TARGETS) + TARGETS.index(chosen['target'])) * len(HOLDS) + HOLDS.index(chosen['hold'])
    entry_i, exit_i, rets, scores = [], [], [], []
    for row in subset:
        if row['date'] not in index or not np.isfinite(row['rets'][slot]):
            continue
        entry_i.append(index.get(date.fromordinal(int(row['entry_ord'])), index[row['date']]))
        exit_i.append(min(entry_i[-1] + int(row['elapsed'][slot]), len(sessions) - 1))
        rets.append(row['rets'][slot])
        scores.append(row['score'])
    terms = chosen['deduped']
    kelly = 0.25 * terms['f'] if terms.get('f') and terms['f'] > 0 else 0.0
    return dict(
        risk_1pct=portfolio_curve(np.array(entry_i), np.array(exit_i), np.array(rets), np.array(scores), chosen['stop'], 0.01, len(sessions)),
        quarter_kelly=portfolio_curve(np.array(entry_i), np.array(exit_i), np.array(rets), np.array(scores), chosen['stop'], kelly, len(sessions)),
        kelly_f=terms.get('f'), quarter=kelly,
    )


def _compact(cells):
    """Keep the Kelly slice and the best row of each signal so the file stays readable."""
    kept = []
    for cell in cells:
        interesting = (
            cell['stop'] == 0.05 and cell['hold'] == 20 and cell['source'] == 'hbos' and cell['window'] == 1 and cell['rule'] == 'p1'
        )
        if interesting:
            labeled = _label(cell)
            labeled['role'] = 'kelly'
            kept.append(labeled)
    best = {}
    for cell in cells:
        if cell['sample'] != 'walk':
            continue
        key = (cell['source'], cell['window'], cell['rule'])
        if cell['deduped']['mean'] is None:
            continue
        if key not in best or cell['deduped']['mean'] > best[key]['deduped']['mean']:
            best[key] = cell
    for cell in best.values():
        labeled = _label(cell)
        labeled['role'] = 'best'
        kept.append(labeled)
        twin = _twin(cells, cell, 'holdout')
        if twin:
            labeled = _label(twin)
            labeled['role'] = 'best'
            kept.append(labeled)
    return kept


def render(report: dict) -> str:
    lines = [
        '# Long-stock brackets on the anomaly tail',
        '',
        'Signals are the anomaly-test HBOS scores for the 1-day and 5-day windows and the isolation-forest scores for the 1-day window, against the 100-day baseline. Top 1% and top 0.5% use the training-score threshold. Top 4 is the four highest scores that day. The bracket is chosen by the highest deduped walk-forward mean. The holdout from 2025-11-13 is not part of that choice.',
        '',
        'The fill for the live book is the next session open. The signal-close fill is only a reference. Stops are 3%, 5%, and 8%. Targets are 15%, 20%, 25%, 28.33%, 30%, and 40%. A 5% stop needs a target above 28.33% before a 15% win rate has a positive expectancy, because the payoff ratio then exceeds 5.667. If the stop and the target are both touched in one session, the stop is filled. A gap through the stop is filled at the open. Time exits use that session\'s close. Costs are 10 bps round trip, plus 10 bps more on a stop. One name is kept once per 20 sessions in the deduped book. Random names are from the same month and the same volatility decile.',
        '',
        '## Five percent stop, 20 sessions, HBOS 1-day top 1%, next open',
        '',
        '| Target | Theoretical b | Sample | N | Target rate | Stop rate | Time exit | Realized p | Realized b | Mean | Median | Kelly f* | Random mean |',
        '| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for cell in report['cells']:
        if cell.get('role') != 'kelly':
            continue
        stats = cell['deduped']
        lines.append(
            f"| {cell['target']:.2%} | {cell['theoretical_b']:.2f} | {cell['sample']} | {stats['n']} | {_n(stats['target'])} | {_n(stats['stop'])} | {_n(stats['time'])} | {_n(stats['p'])} | {_n(stats['b'])} | {_n(stats['mean'])} | {_n(stats['median'])} | {_n(stats['f'])} | {_n(cell['random']['mean'])} |"
        )
    lines += ['', '## Best walk-forward bracket for each signal, and its holdout', '']
    lines.append('| Signal | Stop | Target | Hold | Sample | Deduped mean | Median | Realized p | Realized b | Kelly f* | Random mean | Close-entry mean |')
    lines.append('| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    seen = set()
    for cell in report['cells']:
        if cell.get('role') != 'best':
            continue
        key = (cell['source'], cell['window'], cell['rule'], cell['stop'], cell['target'], cell['hold'], cell['sample'])
        if key in seen:
            continue
        seen.add(key)
        stats = cell['deduped']
        lines.append(
            f"| {cell['source']} {cell['window']}d {cell['rule']} | {cell['stop']:.0%} | {cell['target']:.2%} | {cell['hold']} | {cell['sample']} | {_n(stats['mean'])} | {_n(stats['median'])} | {_n(stats['p'])} | {_n(stats['b'])} | {_n(stats['f'])} | {_n(cell['random']['mean'])} | {_n(cell['close_entry']['mean'])} |"
        )
    chosen = report.get('chosen') or {}
    port = report.get('portfolio') or {}
    lines += ['', '## Chosen rule', '']
    if chosen:
        lines.append(
            f"Walk-forward choice: {chosen['source']} {chosen['window']}-day {chosen['rule']}, stop {chosen['stop']:.0%}, target {chosen['target']:.2%}, hold {chosen['hold']} sessions."
        )
    one = port.get('risk_1pct') or {}
    quarter = port.get('quarter_kelly') or {}
    lines.append(
        f"One percent risk, 20 names at most: terminal {_n(one.get('terminal'))}, CAGR {_n(one.get('cagr'))}, max drawdown {_n(one.get('max_drawdown'))}, Sharpe {_n(one.get('sharpe'))}."
    )
    lines.append(
        f"Quarter-Kelly risk {_n(port.get('quarter'))}: terminal {_n(quarter.get('terminal'))}, CAGR {_n(quarter.get('cagr'))}, max drawdown {_n(quarter.get('max_drawdown'))}, Sharpe {_n(quarter.get('sharpe'))}."
    )
    lines += ['', '## Verdict', '', report['verdict'], '']
    return '\n'.join(lines)


def _n(value):
    if value is None or value != value:
        return 'n/a'
    return f'{value:.3f}'


def verdict_text(chosen, held) -> str:
    if chosen is None or held is None:
        return 'No bracket was priced, so there is no comparison with the random book.'
    signal = held['deduped']['mean']
    random = held['random']['mean']
    name = f"{chosen['source']} {chosen['window']}-day {chosen['rule']}, stop {chosen['stop']:.0%}, target {chosen['target']:.2%}, {chosen['hold']} sessions"
    edge = None if signal is None or random is None else signal - random
    beats = edge is not None and edge > 0 and signal is not None and signal > 0
    edge_text = 'n/a' if edge is None else f'{edge:.3f}'
    if beats:
        return (
            f'{name} is the walk-forward choice. In the holdout its deduped mean stays positive and ahead of the random bracket by {edge_text}. '
            'That is the only holdout comparison.'
        )
    return (
        f'{name} is the walk-forward choice. In the holdout the deduped mean is {_n(signal)} and the matched random mean is {_n(random)}, a difference of {edge_text}. '
        'The bracket does not beat the random book with a positive expectancy. Buying the stock on the anomaly and bracketing it is not an improvement on doing the same trade at random.'
    )


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
