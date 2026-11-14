"""Daily top-3 and top-4 scan with the frozen logistic.

A purchase can be one day or several days, as far as 40 calendar days before
the announcement. The score uses only sessions from that span through the
scoring close. The forward jump is the outcome. Coefficients are not refit.
"""
from __future__ import annotations

import json
import math
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

from insider_model import fit_ridge_logistic
from insider_resolved import connect, expiry_class, load_sessions
from ma_candidate_screen import covering
from ma_signal_model import (
    FEATURES, OPTION_FEATURES, RIDGE, design, features_for, fold_of, overlaps_earnings, window_features,
)

TRADE_DAYS = 40
HORIZONS = (5, 10, 20, '40d')
JUMP = 0.15
HAZARD_UP = 1.0
HAZARD_DOWN = -0.5
START = date(2022, 1, 1)
END = date(2026, 11, 12)
CHAIN_FROM = date(2021, 11, 1)

MONTHLY_SQL = '''
SELECT qdate, edate,
       SUM(CASE WHEN `type`='call' THEN volume ELSE 0 END) AS call_vol,
       SUM(CASE WHEN `type`='put' THEN volume ELSE 0 END) AS put_vol,
       SUM(CASE WHEN `type`='call' THEN oi ELSE 0 END) AS call_oi,
       SUM(CASE WHEN `type`='call' AND underlying_last > 0 AND strike > underlying_last
           THEN volume ELSE 0 END) AS otm_call_vol
FROM optiondaily
WHERE underlying = %s AND qdate BETWEEN %s AND %s AND edate IN ({marks})
GROUP BY qdate, edate
'''


def monthly_dates(start: date, end: date) -> list[date]:
    days = []
    day = start
    while day <= end:
        if expiry_class(day) == 'monthly':
            days.append(day)
        day += timedelta(days=1)
    return days


def feature_days(sessions, index, score_date, calendar_days: int = TRADE_DAYS) -> list[date]:
    """Sessions from 40 calendar days before the close through that close."""
    earliest = score_date - timedelta(days=calendar_days)
    end = index[score_date]
    start = end
    while start > 0 and sessions[start - 1] >= earliest:
        start -= 1
    return sessions[start:end + 1]


def horizon_end_index(sessions, index, score_date, horizon):
    """Last session index of a forward horizon. None when the horizon is incomplete."""
    start = index[score_date]
    if horizon == '40d':
        limit = score_date + timedelta(days=TRADE_DAYS)
        if sessions[-1] < limit:
            return None
        end = start
        while end + 1 < len(sessions) and sessions[end + 1] <= limit:
            end += 1
        return None if end == start else end
    if start + horizon >= len(sessions):
        return None
    return start + horizon


def causal_features(rows, closes, days, score_date):
    """Features for one name on score_date. days must end on score_date."""
    if not days or days[-1] != score_date:
        raise ValueError('the feature window has to end on the scoring date')
    expiries = {edate for day in days for edate in rows.get(day, {})}
    cover = covering(expiries, score_date, 'monthly')
    return window_features(rows, cover, days, closes)


def forward_flags(spot, future, split_in_window: bool) -> dict | None:
    if spot is None or spot <= 0 or not future or any(close is None or close <= 0 for close in future):
        return None
    bad = split_in_window
    prev = spot
    for close in future:
        move = close / prev - 1
        if move >= HAZARD_UP or move <= HAZARD_DOWN:
            bad = True
        prev = close
    terminal = future[-1] / spot - 1
    peak = max(future) / spot - 1
    return dict(
        valid=True,
        bad=bad,
        terminal=(terminal >= JUMP) and not bad,
        peak=(peak >= JUMP) and not bad,
    )


def random_hit_probability(eligible: int, jumpers: int, picks: int) -> float | None:
    if eligible < picks or picks <= 0:
        return None
    if jumpers <= 0:
        return 0.0
    safe = eligible - jumpers
    if safe < picks:
        return 1.0
    return 1 - math.comb(safe, picks) / math.comb(eligible, picks)


def slate_summary(records: list[dict], picks: int, horizon: int, kind: str) -> dict:
    """records are scoring dates with a ranked slate and universe counts."""
    dates = hits = pick_hits = pick_n = false_picks = 0
    base = []
    news = dict(ma=0, earnings=0, other=0)
    for row in records:
        slate = row['slate'][:picks]
        flags = [item['jumps'].get(str(horizon)) for item in slate]
        if any(flag is None for flag in flags):
            continue
        dates += 1
        jumped = [item for item, flag in zip(slate, flags) if flag[kind]]
        pick_n += len(slate)
        pick_hits += len(jumped)
        false_picks += len(slate) - len(jumped)
        if jumped:
            hits += 1
        for item in jumped:
            label = item['news'].get(str(horizon), 'other')
            news[label] = news.get(label, 0) + 1
        universe = row['universe'][horizon]
        probability = random_hit_probability(universe['eligible'], universe[kind], picks)
        if probability is not None:
            base.append(probability)
    return dict(
        dates=dates,
        date_hit_rate=(hits / dates) if dates else None,
        pick_hit_rate=(pick_hits / pick_n) if pick_n else None,
        false_picks_per_hit=(false_picks / pick_hits) if pick_hits else None,
        base_rate=(sum(base) / len(base)) if base else None,
        hits=dict(ma=news['ma'], earnings=news['earnings'], other=news['other'], total=pick_hits),
    )


def classify_news(symbol: str, start: date, end: date, sessions, index, ma_days, earn_days) -> str:
    if start not in index or end not in index:
        return 'other'
    window = set(sessions[index[start] + 1:index[end] + 1])
    if any(day in window for day in ma_days.get(symbol, ())):
        return 'ma'
    if any(day in window for day in earn_days.get(symbol, ())):
        return 'earnings'
    return 'other'


def _beta(block, names):
    coeff = block['coefficients']
    return [coeff['intercept']] + [coeff[name] for name in names]


def recover_standardization(root: Path, connection) -> dict:
    cache = root / 'results' / 'insider_footprint' / 'frozen_standardization.json'
    if cache.exists():
        return json.loads(cache.read_text())
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    screen = json.loads((root / 'results/insider_footprint/candidate_screen.json').read_text())
    events = [row for row in screen['events'] if row.get('admitted') and row['qdate'] < '2022-01-01']
    symbols = sorted({row['symbol'] for row in events})
    earnings = {symbol: [] for symbol in symbols}
    with connection.cursor() as cursor:
        cursor.execute('SET SESSION MAX_EXECUTION_TIME=300000')
        for start in range(0, len(symbols), 400):
            chunk = symbols[start:start + 400]
            marks = ','.join(['%s'] * len(chunk))
            cursor.execute(
                f'''SELECT symbol, COALESCE(rxdate, erdate) AS reaction
                    FROM erdate WHERE symbol IN ({marks})''',
                chunk,
            )
            for row in cursor.fetchall():
                if row['reaction']:
                    earnings.setdefault(row['symbol'].upper(), []).append(row['reaction'])
    from ma_signal_model import PLACEBO_SHIFT
    samples = []
    for n, event in enumerate(events, start=1):
        day = date.fromisoformat(event['qdate'])
        start = date.fromisoformat(event['t_start'])
        if day not in index or start not in index or index[start] >= index[day]:
            continue
        window = sessions[index[start]:index[day]]
        if overlaps_earnings(window, earnings.get(event['symbol'], [])):
            continue
        if fold_of(day) != 'train':
            continue
        deal = features_for(connection, sessions, index, event['symbol'], window, day)
        if deal is None:
            continue
        samples.append(dict(label=1, **deal))
        prior = [item for item in earnings.get(event['symbol'], [])
                 if item in index and index[item] + len(window) < index[start]]
        if prior:
            earn = max(prior)
            earn_window = sessions[index[earn] - len(window):index[earn]]
            feat = features_for(connection, sessions, index, event['symbol'], earn_window, earn)
            if feat:
                samples.append(dict(label=0, **feat))
        if index[day] > PLACEBO_SHIFT + len(window):
            placebo_end = sessions[index[day] - PLACEBO_SHIFT]
            ordinary = sessions[index[placebo_end] - len(window):index[placebo_end]]
            feat = features_for(connection, sessions, index, event['symbol'], ordinary, placebo_end)
            if feat:
                samples.append(dict(label=0, **feat))
        if n % 200 == 0:
            print(f'standardization events {n} samples {len(samples)}', flush=True)
    frozen = json.loads((root / 'results/insider_footprint/signal_model.json').read_text())
    matrix, means, sds = design(samples, FEATURES)
    beta = fit_ridge_logistic(matrix, [row['label'] for row in samples], ridge=RIDGE)
    stored = _beta(frozen, FEATURES)
    gap = max(abs(a - b) for a, b in zip(beta, stored))
    option_matrix, option_means, option_sds = design(samples, OPTION_FEATURES)
    option_beta = fit_ridge_logistic(option_matrix, [row['label'] for row in samples], ridge=RIDGE)
    option_stored = _beta(frozen['without_pre_return'], OPTION_FEATURES)
    option_gap = max(abs(a - b) for a, b in zip(option_beta, option_stored))
    payload = dict(
        n_train=len(samples), five_gap=gap, option_gap=option_gap,
        features=list(FEATURES), means=means, sds=sds,
        option_features=list(OPTION_FEATURES), option_means=option_means, option_sds=option_sds,
        beta=stored, option_beta=option_stored,
    )
    if gap > 1e-3 or option_gap > 1e-3:
        payload['ok'] = False
    else:
        payload['ok'] = True
        cache.write_text(json.dumps(payload) + '\n')
    return payload


def _group_chain(fetched) -> dict:
    grouped = {}
    for row in fetched:
        grouped.setdefault(row['qdate'], {})[row['edate']] = dict(
            call_vol=int(row['call_vol'] or 0),
            put_vol=int(row['put_vol'] or 0),
            call_oi=int(row['call_oi'] or 0),
            otm_call_vol=int(row['otm_call_vol'] or 0),
        )
    return grouped


def scan_symbol(symbol: str, sessions, index, monthlies, splits) -> list[dict]:
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
            marks = ','.join(['%s'] * len(monthlies))
            cursor.execute(
                MONTHLY_SQL.format(marks=marks),
                (symbol, CHAIN_FROM, END, *monthlies),
            )
            chain = _group_chain(cursor.fetchall())
            cursor.execute(
                'SELECT qdate, close FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s',
                (symbol, CHAIN_FROM, END),
            )
            closes = {row['qdate']: float(row['close']) for row in cursor.fetchall() if row['close']}
    finally:
        connection.close()
    if not chain or not closes:
        return []
    out = []
    for day in sessions:
        if day < START or day > END or day not in index:
            continue
        window = feature_days(sessions, index, day)
        if len(window) < 2 or window[0] not in closes or day not in closes:
            continue
        try:
            features = causal_features(chain, closes, window, day)
        except ValueError:
            continue
        if features is None:
            continue
        scaled, _, _ = design([features], FEATURES, scan_symbol.means, scan_symbol.sds)
        option_scaled, _, _ = design([features], OPTION_FEATURES, scan_symbol.option_means, scan_symbol.option_sds)
        # Rank on the linear score. The probability saturates near 1 when the
        # lookback return is large, and a saturated probability does not order those names.
        score = sum(weight * value for weight, value in zip(scan_symbol.beta, scaled[0]))
        option_score = sum(weight * value for weight, value in zip(scan_symbol.option_beta, option_scaled[0]))
        spot = closes.get(day)
        jumps = {}
        for horizon in HORIZONS:
            end_i = horizon_end_index(sessions, index, day, horizon)
            if end_i is None:
                jumps[str(horizon)] = None
                continue
            future_days = sessions[index[day] + 1:end_i + 1]
            future = [closes.get(item) for item in future_days]
            split_hit = any((symbol, item) in splits for item in future_days)
            jumps[str(horizon)] = forward_flags(spot, future, split_hit)
        out.append(dict(
            day=day.isoformat(), score=score, option_score=option_score,
            pre_return=features['pre_return'], jumps=jumps,
        ))
    return out


def _load_news(root: Path, sessions, index):
    ma = {}
    earn = {}
    table = root / 'data' / 'edgar_deals' / 'announcements.json'
    if table.exists():
        for row in json.loads(table.read_text()):
            if row.get('symbol') and row.get('qdate'):
                ma.setdefault(row['symbol'], set()).add(date.fromisoformat(row['qdate']))
    pool = root / 'results' / 'insider_footprint' / 'ma_news_pool.json'
    if pool.exists():
        for row in json.loads(pool.read_text())['events']:
            if row.get('qdate', '') >= '2022-01-01':
                ma.setdefault(row['symbol'], set()).add(date.fromisoformat(row['qdate']))
    earnings_path = root / 'data' / 'edgar_deals' / 'earnings_8k_2022_2026.json'
    if earnings_path.exists():
        for row in json.loads(earnings_path.read_text()):
            if row.get('symbol') and row.get('reaction_session'):
                earn.setdefault(row['symbol'], set()).add(date.fromisoformat(row['reaction_session']))
    return ma, earn


def _push(heap_for_day, item):
    if len(heap_for_day) < 4:
        heap_for_day.append(item)
        heap_for_day.sort(key=lambda rec: rec[0], reverse=True)
    elif item[0] > heap_for_day[-1][0]:
        heap_for_day[-1] = item
        heap_for_day.sort(key=lambda rec: rec[0], reverse=True)


def _merge(symbol, rows, heaps, counts):
    for row in rows:
        day = row['day']
        counts['eligible'][day] = counts['eligible'].get(day, 0) + 1
        for horizon in HORIZONS:
            flag = row['jumps'].get(str(horizon))
            bucket = counts['horizon'].setdefault(str(horizon), {}).setdefault(day, dict(eligible=0, terminal=0, peak=0))
            if not flag:
                continue
            bucket['eligible'] += 1
            if flag['terminal']:
                bucket['terminal'] += 1
            if flag['peak']:
                bucket['peak'] += 1
        jumps = row['jumps']
        _push(heaps['five'].setdefault(day, []), (row['score'], symbol, row['pre_return'], jumps))
        _push(heaps['option'].setdefault(day, []), (row['option_score'], symbol, row['pre_return'], jumps))


def render(report: dict) -> str:
    lines = [
        '## Daily top picks, 2026-11-13',
        '',
        'On each session the frozen logistic scores every optionable name from the sessions in the 40 calendar days ending at that close. A single day in that span sets the peak call volume and the largest open-interest build. Several days add up in the call/put total. Names are ordered by the linear score. The five-feature score still includes the stock’s own return over that span. The option-only score leaves that return out, so one call print can rank a name that has not already run up. It names the top 3 and the top 4. A hit is a later close at least 15% above the scoring close, either at 5, 10, or 20 sessions or inside the next 40 calendar days. A one-day move of +100% or −50%, or a split, is not counted as a jump. A session counts only when every name in the slate has a close at that horizon. The coefficients are the 2013–2019 fit. This test does not choose a new cutoff.',
        '',
        'The stock return stops at the scoring close. It does not use the path into a later headline.',
        '',
        f"Names scanned: {report.get('symbols', 0)}. Scoring sessions: {report.get('sessions', 0)}. Standardization check gap: {report.get('five_gap')}.",
        '',
    ]
    if report.get('reason'):
        lines.append(report['reason'])
        return '\n'.join(lines) + '\n'
    lines.append('| Score | Slate | Horizon | Jump | Dates | Date hit rate | Random slate | Hit rate per pick | False picks per hit | M&A | Earnings | Other |')
    lines.append('| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
    for model, title in (('five', 'five-feature'), ('option', 'option-only')):
        block_model = (report.get('models') or {}).get(model) or {}
        results = block_model.get('results') or {}
        for picks in (3, 4):
            for horizon in HORIZONS:
                for kind in ('terminal', 'peak'):
                    block = results.get(str(picks), {}).get(str(horizon), {}).get(kind)
                    if not block:
                        continue
                    lines.append(
                        f"| {title} | top {picks} | {horizon} | {kind} | {block['dates']} | {_fmt(block['date_hit_rate'])} | "
                        f"{_fmt(block['base_rate'])} | {_fmt(block['pick_hit_rate'])} | {_fmt(block['false_picks_per_hit'])} | "
                        f"{block['hits']['ma']} | {block['hits']['earnings']} | {block['hits']['other']} |"
                    )
        pre = block_model.get('top_pre_return')
        if pre:
            lines.append('')
            lines.append(
                f"Highest {title} name: median lookback return {pre['median']:.3f}, 10th percentile {pre['p10']:.3f}."
            )
    lines += [
        '',
        'Date hit rate is the share of sessions where at least one name in the slate jumps. Random slate is the average probability that a random draw of the same size, from that session’s optionable names, contains a jump. False picks per hit is the number of slate names that do not jump divided by the number that do.',
        '',
        'M&A uses the EDGAR announcement table and the earlier headline pool when the reaction session falls inside the forward window. Earnings uses 8-K Item 2.02 reaction sessions in that window. A jump with neither is other. A rank is a review tag, not an identification of a trader.',
        '',
        'No new high-precision rule is frozen from this table. A cutoff chosen after these rates would be a proposal for a later test.',
        '',
    ]
    return '\n'.join(lines)


def _fmt(value):
    return 'n/a' if value is None else f'{value:.3f}'


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    monthlies = monthly_dates(CHAIN_FROM, date(2027, 2, 1))
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=300000')
            cursor.execute('START TRANSACTION READ ONLY')
        standard = recover_standardization(root, connection)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT symbol FROM optionstat WHERE qdate BETWEEN %s AND %s",
                (START, END),
            )
            symbols = sorted(row['symbol'] for row in cursor.fetchall())
            cursor.execute(
                "SELECT symbol, splitdate FROM split WHERE splitdate BETWEEN %s AND %s",
                (CHAIN_FROM, END),
            )
            splits = {(row['symbol'], row['splitdate']) for row in cursor.fetchall()}
    finally:
        connection.rollback()
        connection.close()
    if not standard.get('ok'):
        report = dict(reason='recovered training coefficients do not match the frozen fit',
                      five_gap=standard.get('five_gap'), option_gap=standard.get('option_gap'), symbols=0, sessions=0)
        _write(root, report)
        return report
    scan_symbol.means = standard['means']
    scan_symbol.sds = standard['sds']
    scan_symbol.beta = standard['beta']
    scan_symbol.option_means = standard['option_means']
    scan_symbol.option_sds = standard['option_sds']
    scan_symbol.option_beta = standard['option_beta']
    checkpoint = root / 'results' / 'insider_footprint' / 'walk_checkpoint.json'
    saved = json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
    if saved.get('version') == 2:
        heaps = saved['heaps']
        counts = saved['counts']
        done = set(saved['done'])
    else:
        heaps = {'five': {}, 'option': {}}
        counts = dict(eligible={}, horizon={})
        done = set()
    pending = [symbol for symbol in symbols if symbol not in done]
    lock = threading.Lock()
    finished = len(done)

    def _checkpoint():
        checkpoint.write_text(json.dumps(dict(version=2, heaps=heaps, counts=counts, done=sorted(done))) + '\n')

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(scan_symbol, symbol, sessions, index, monthlies, splits): symbol for symbol in pending}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                rows = future.result()
            except Exception as exc:  # noqa: BLE001
                print(f'skip {symbol} {exc}', flush=True)
                rows = []
            with lock:
                _merge(symbol, rows, heaps, counts)
                done.add(symbol)
                finished += 1
                if finished % 100 == 0:
                    _checkpoint()
                    print(f'scanned {finished}/{len(symbols)}', flush=True)
    _checkpoint()
    ma, earn = _load_news(root, sessions, index)
    report = _finish(symbols, heaps, counts, standard, sessions, index, ma, earn)
    _write(root, report)
    return report


def _slate_for(heap, sessions, index, ma, earn):
    labeled = {}
    for day, items in heap.items():
        score_day = date.fromisoformat(day)
        slate = []
        for item in items:
            news = {}
            for span in HORIZONS:
                end_i = horizon_end_index(sessions, index, score_day, span)
                if end_i is None:
                    news[str(span)] = 'other'
                else:
                    news[str(span)] = classify_news(
                        item[1], score_day, sessions[end_i], sessions, index, ma, earn)
            slate.append(dict(score=item[0], symbol=item[1], pre_return=item[2], jumps=item[3], news=news))
        labeled[day] = slate
    return labeled


def _quantile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[int(fraction * (len(ordered) - 1))]


def _model_results(labeled, counts) -> dict:
    results = {}
    for picks in (3, 4):
        results[str(picks)] = {}
        for horizon in HORIZONS:
            results[str(picks)][str(horizon)] = {}
            for kind in ('terminal', 'peak'):
                records = []
                for day, slate in labeled.items():
                    universe = {
                        span: counts['horizon'].get(str(span), {}).get(
                            day, dict(eligible=0, terminal=0, peak=0))
                        for span in HORIZONS
                    }
                    records.append(dict(slate=slate, universe=universe))
                results[str(picks)][str(horizon)][kind] = slate_summary(records, picks, horizon, kind)
    return results


def _finish(symbols, heaps, counts, standard, sessions, index, ma, earn) -> dict:
    models = {}
    for name in ('five', 'option'):
        labeled = _slate_for(heaps.get(name) or {}, sessions, index, ma, earn)
        pres = [slate[0]['pre_return'] for slate in labeled.values() if slate]
        models[name] = dict(
            results=_model_results(labeled, counts),
            top_pre_return=dict(median=_quantile(pres, 0.5), p10=_quantile(pres, 0.1)),
        )
    return dict(
        symbols=len(symbols),
        sessions=len((heaps.get('five') or {})),
        trade_days=TRADE_DAYS,
        five_gap=standard.get('five_gap'),
        option_gap=standard.get('option_gap'),
        models=models,
    )


def _write(root: Path, report: dict) -> None:
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'walkforward_score.json').write_text(json.dumps(report, indent=2) + '\n')
    text = render(report)
    (folder / 'WALKFORWARD.md').write_text(text)
    for name in ('VALIDATION.md', 'SIGNAL_MODEL.md'):
        path = folder / name
        prior = path.read_text() if path.exists() else ''
        marker = '## Daily top picks, 2026-11-13'
        if marker in prior:
            prior = prior.split(marker)[0].rstrip() + '\n'
        path.write_text(prior.rstrip() + '\n\n' + text)
    print(text, flush=True)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
