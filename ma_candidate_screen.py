"""News-first M&A screen: ten-session path, own-volatility run start, earnings benchmark.

A statistical candidate is unusual versus that stock's own earnings windows.
It is not an identification of a trader.
"""
import json
import statistics
from datetime import date, timedelta
from pathlib import Path

from insider_resolved import connect, expiry_class, load_sessions

MIN_PATH = 0.15
HAZARD_UP = 1.0
HAZARD_DOWN = -0.5
CHAIN_SQL = '''
SELECT qdate, edate,
       SUM(CASE WHEN `type`='call' THEN volume ELSE 0 END) AS call_vol,
       SUM(CASE WHEN `type`='put' THEN volume ELSE 0 END) AS put_vol,
       SUM(CASE WHEN `type`='call' THEN oi ELSE 0 END) AS call_oi,
       SUM(CASE WHEN `type`='call' AND underlying_last > 0 AND strike > underlying_last
           THEN volume ELSE 0 END) AS otm_call_vol
FROM optiondaily
WHERE underlying = %s AND qdate BETWEEN %s AND %s
GROUP BY qdate, edate
'''


def beta(stock_returns, market_returns):
    paired = [(s, m) for s, m in zip(stock_returns, market_returns) if s is not None and m is not None]
    if len(paired) < 30:
        return 1.0
    stocks = [s for s, _ in paired]
    markets = [m for _, m in paired]
    mean_s = statistics.fmean(stocks)
    mean_m = statistics.fmean(markets)
    var_m = sum((m - mean_m) ** 2 for m in markets)
    if var_m == 0:
        return 1.0
    cov = sum((s - mean_s) * (m - mean_m) for s, m in paired)
    return cov / var_m


def detect_start(closes, volumes, market, event_index):
    """Return (start_offset, extended). Offset is negative, -10 when no earlier run qualifies.

    closes, volumes, and market are dicts of session index -> value, covering the lookback.
    """
    def ret(i):
        if closes.get(i) and closes.get(i - 1) and market.get(i) and market.get(i - 1):
            return closes[i] / closes[i - 1] - 1, market[i] / market[i - 1] - 1
        return None, None

    train = [ret(i) for i in range(event_index - 90, event_index - 30)]
    train = [(s, m) for s, m in train if s is not None]
    slope = beta([s for s, _ in train], [m for _, m in train])
    abnormal = []
    train_vol = []
    for i in range(event_index - 90, event_index - 30):
        stock_ret, market_ret = ret(i)
        if stock_ret is None:
            continue
        abnormal.append(stock_ret - slope * market_ret)
        if volumes.get(i):
            train_vol.append(volumes[i])
    sigma = statistics.pstdev(abnormal) if len(abnormal) >= 20 else None
    vol_med = statistics.median(train_vol) if train_vol else None
    base = closes.get(event_index - 10)
    end = closes.get(event_index)
    if not base or not end:
        return -10, False
    path = end / base - 1
    if sigma is None or not vol_med:
        return -10, False
    chosen = None
    for start in range(event_index - 30, event_index - 10):
        start_close = closes.get(start)
        if not start_close:
            continue
        longer = end / start_close - 1
        if longer < path + 0.05:
            continue
        shocks = 0
        for i in range(start, event_index - 10):
            stock_ret, market_ret = ret(i)
            if stock_ret is None or not volumes.get(i):
                continue
            if stock_ret - slope * market_ret > 2 * sigma and volumes[i] > 1.5 * vol_med:
                shocks += 1
        if shocks >= 2:
            chosen = start
            break
    if chosen is None:
        return -10, False
    return chosen - event_index, True


def hazard(closes, event_index, start_offset):
    for i in range(event_index + start_offset, event_index + 1):
        if not closes.get(i) or not closes.get(i - 1) or closes[i - 1] <= 0:
            return True
        move = closes[i] / closes[i - 1] - 1
        if move >= HAZARD_UP or move <= HAZARD_DOWN:
            return True
    return False


def series_metrics(rows, edate, days):
    """rows: qdate -> edate -> record. One expiry only."""
    call_volumes = []
    oi_changes = []
    otm = []
    previous_oi = None
    for day in days:
        rec = rows.get(day, {}).get(edate)
        if rec is None:
            previous_oi = None
            continue
        call_volumes.append(rec['call_vol'])
        if rec['call_vol']:
            otm.append(rec['otm_call_vol'] / rec['call_vol'])
        if previous_oi is not None and day != edate and day < edate:
            change = rec['call_oi'] - previous_oi
            if change > 0:
                oi_changes.append(change)
        previous_oi = None if day >= edate else rec['call_oi']
    if not call_volumes:
        return None
    return dict(
        peak_call=max(call_volumes),
        sum_call=sum(call_volumes),
        max_oi_build=max(oi_changes) if oi_changes else 0,
        otm_share=statistics.fmean(otm) if otm else None,
    )


def rank_against(value, baseline):
    if value is None or len(baseline) < 3:
        return None, None
    rank = sum(item <= value for item in baseline) / len(baseline)
    center = statistics.fmean(baseline)
    spread = statistics.pstdev(baseline)
    zed = None if spread == 0 else (value - center) / spread
    return rank, zed


def is_candidate(comparisons):
    usable = [row for row in comparisons if row.get('percentile') is not None]
    if len(usable) < 1:
        return 'baseline-missing'
    # At least one series must have three earnings windows. rank_against enforces that.
    flagged = any(
        (row['percentile'] is not None and row['percentile'] >= 0.75)
        or (row['z'] is not None and row['z'] >= 2)
        for row in usable
    )
    return 'statistical-candidate' if flagged else 'baseline-consistent'


def covering(expiries, event, kind):
    later = [edate for edate in expiries if edate > event and expiry_class(edate) == kind]
    return min(later) if later else None


def load_pool(root: Path):
    payload = json.loads((root / 'results/insider_footprint/ma_news_pool.json').read_text())
    return [row for row in payload['events'] if row['path'] >= MIN_PATH]


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    pool = load_pool(root)
    connection = connect()
    spy = {}
    results = []
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=300000')
            cursor.execute('START TRANSACTION READ ONLY')
            cursor.execute("SELECT qdate, close FROM stockquote WHERE symbol='SPY' AND qdate>='2012-06-01'")
            spy = {row['qdate']: float(row['close']) for row in cursor.fetchall() if row['close']}
        symbols = sorted({row['symbol'] for row in pool})
        earnings = {symbol: [] for symbol in symbols}
        with connection.cursor() as cursor:
            for chunk_start in range(0, len(symbols), 400):
                chunk = symbols[chunk_start:chunk_start + 400]
                marks = ','.join(['%s'] * len(chunk))
                cursor.execute(
                    f'''SELECT symbol, COALESCE(rxdate, erdate) AS reaction
                        FROM erdate WHERE symbol IN ({marks}) AND erdate >= '2012-01-01' ''',
                    chunk,
                )
                for row in cursor.fetchall():
                    if row['reaction']:
                        earnings.setdefault(row['symbol'].upper(), []).append(row['reaction'])
        for n, event in enumerate(pool, start=1):
            results.append(score_event(connection, sessions, index, spy, earnings, event))
            if n % 100 == 0:
                print(f'scored {n}', flush=True)
    finally:
        connection.rollback()
        connection.close()
    admitted = [row for row in results if row.get('admitted')]
    extended = [row for row in admitted if row.get('extended')]
    candidates = [row for row in admitted if row.get('status') == 'statistical-candidate']
    summary = dict(
        strict_path_events=len(pool),
        scored=len(results),
        admitted=len(admitted),
        extended=len(extended),
        extended_share=(len(extended) / len(admitted)) if admitted else None,
        statistical_candidates=len(candidates),
        baseline_consistent=sum(row.get('status') == 'baseline-consistent' for row in admitted),
        baseline_missing=sum(row.get('status') == 'baseline-missing' for row in admitted),
        by_year={},
    )
    for row in candidates:
        summary['by_year'][row['qdate'][:4]] = summary['by_year'].get(row['qdate'][:4], 0) + 1
    folder = root / 'results' / 'insider_footprint'
    (folder / 'candidate_screen.json').write_text(json.dumps(dict(summary=summary, events=results), indent=2, default=str) + '\n')
    (folder / 'CANDIDATE_SCREEN.md').write_text(render(summary, candidates[:40]))
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def score_event(connection, sessions, index, spy, earnings, event):
    symbol = event['symbol']
    day = date.fromisoformat(event['qdate'])
    record = dict(symbol=symbol, qdate=event['qdate'], title=event.get('title', '')[:180],
                  path=event['path'], reaction=event['reaction'], admitted=False)
    if day not in index or index[day] < 100:
        record['reason'] = 'short_history'
        return record
    anchor = index[day]
    start = sessions[anchor - 100]
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT qdate, close, volume FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s',
            (symbol, start, day),
        )
        quotes = {row['qdate']: row for row in cursor.fetchall()}
    closes = {}
    volumes = {}
    market = {}
    for i, session in enumerate(sessions):
        if session < start or session > day:
            continue
        row = quotes.get(session)
        if row and row['close']:
            closes[i] = float(row['close'])
            volumes[i] = float(row['volume'] or 0)
        if session in spy:
            market[i] = spy[session]
    offset, extended = detect_start(closes, volumes, market, anchor)
    if hazard(closes, anchor, offset):
        record['reason'] = 'corporate_action_hazard'
        return record
    start_index = anchor + offset
    record.update(t_start=sessions[start_index].isoformat(), extended=extended,
                  largest_day=_largest(closes, start_index, anchor, sessions))
    chain_start = sessions[max(0, start_index - 20)]
    rows = fetch_chain(connection, symbol, chain_start, day)
    if not _listed_before(rows, sessions[max(0, start_index - 20)]):
        record['reason'] = 'no_option_history'
        return record
    window = sessions[start_index:anchor]
    record['admitted'] = True
    record['comparisons'] = compare_earnings(
        connection, sessions, index, symbol, day, window, rows, earnings.get(symbol, []),
    )
    record['status'] = is_candidate(record['comparisons'])
    return record


def _largest(closes, start_index, anchor, sessions):
    best = None
    best_day = None
    for i in range(start_index + 1, anchor + 1):
        if closes.get(i) and closes.get(i - 1):
            move = closes[i] / closes[i - 1] - 1
            if best is None or move > best:
                best = move
                best_day = sessions[i].isoformat()
    return dict(return_=None if best is None else round(best, 4), qdate=best_day)


def fetch_chain(connection, symbol, start, end):
    with connection.cursor() as cursor:
        cursor.execute(CHAIN_SQL, (symbol, start, end))
        grouped = {}
        for row in cursor.fetchall():
            grouped.setdefault(row['qdate'], {})[row['edate']] = dict(
                call_vol=int(row['call_vol'] or 0),
                put_vol=int(row['put_vol'] or 0),
                call_oi=int(row['call_oi'] or 0),
                otm_call_vol=int(row['otm_call_vol'] or 0),
            )
        return grouped


def _listed_before(rows, cutoff):
    return any(day <= cutoff for day in rows)


def compare_earnings(connection, sessions, index, symbol, event, window, deal_rows, earnings_dates):
    comparisons = []
    length = len(window)
    prior = sorted(day for day in earnings_dates if day in index and index[day] < index[window[0]])[-8:]
    for kind in ('monthly', 'weekly'):
        expiries = {edate for day_rows in deal_rows.values() for edate in day_rows}
        cover = covering(expiries, event, kind)
        deal_metric = series_metrics(deal_rows, cover, window) if cover else None
        baseline = []
        for earn in prior:
            earn_window = sessions[index[earn] - length:index[earn]]
            if len(earn_window) < length:
                continue
            earn_rows = fetch_chain(connection, symbol, earn_window[0], earn)
            earn_cover = covering({edate for day_rows in earn_rows.values() for edate in day_rows}, earn, kind)
            metric = series_metrics(earn_rows, earn_cover, earn_window) if earn_cover else None
            if metric:
                baseline.append(metric['peak_call'])
        percentile, zed = rank_against(None if deal_metric is None else deal_metric['peak_call'], baseline)
        comparisons.append(dict(
            kind=kind, expiry=None if cover is None else cover.isoformat(),
            peak_call=None if deal_metric is None else deal_metric['peak_call'],
            max_oi_build=None if deal_metric is None else deal_metric['max_oi_build'],
            earnings_windows=len(baseline), percentile=percentile, z=zed,
        ))
    return comparisons


def render(summary, sample) -> str:
    share = summary['extended_share']
    share_txt = 'n/a' if share is None else f'{share:.0%}'
    lines = [
        '# Statistical candidates from M&A news',
        '',
        'Admission is a deal headline whose announcement close is at least 15% above the close ten sessions earlier, with an option chain at least 20 sessions before the path starts, and no one-day move of +100% or −50% in the path. The option score uses one expiry at a time and compares peak call volume with that stock’s own earnings windows. A statistical candidate is at or above its own 75th percentile, or at least 2 standard deviations above its own earnings mean. It is not an identification of a trader.',
        '',
        f"Strict ten-session path events: {summary['strict_path_events']}. Admitted: {summary['admitted']}. Path start before t = −10: {summary['extended']} ({share_txt}). Statistical candidates: {summary['statistical_candidates']}. Baseline-consistent: {summary['baseline_consistent']}. No earnings benchmark: {summary['baseline_missing']}.",
        '',
        'The extended-start share is the falsification check. A share above 30% would mean the early-run rule is firing on ordinary drift.',
        '',
        '| Year | Statistical candidates |',
        '| --- | ---: |',
    ]
    for year, count in sorted(summary['by_year'].items()):
        lines.append(f'| {year} | {count} |')
    lines += ['', 'First 40 candidates:', '']
    for row in sample:
        lines.append(f"- {row['symbol']} {row['qdate']} path {row['path']:.1%} start {row.get('t_start')}")
    lines.append('')
    return '\n'.join(lines)


def main():
    run(Path('.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
