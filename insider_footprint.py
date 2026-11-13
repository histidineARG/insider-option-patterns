"""Pre-specified call-footprint screen for the 246 news-filter keeps.

The alert rule is frozen in the constants below. The database run compares
Tier A (class-2 M&A keeps) with a same-name date 60 sessions earlier and with
an earnings reaction on that name. Tier B (the other keeps) is reported as a
contrast. Nothing here refits a threshold or labels a person as an insider.
"""
import argparse
import json
import math
import os
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

from insider_model import evaluate_model, render_model_report, samples_from_records, window_features

WINDOW = 10
BASELINE = 20
MIN_OBSERVED_WINDOW = 8
MIN_BASELINE = 10
MIN_VOLUME = 100
VOLUME_RATIO = 3.0
BAND_SHARE_MIN = 0.40
BAND_SHARE_LIFT = 0.10
TOP_SHARE_MIN = 0.50
MIN_BAND_FOR_CONCENTRATION = 20
PLACEBO_SHIFT = 60
EARNINGS_GAP = 40
DELTA_LO = 0.10
DELTA_HI = 0.35
DTE_LO = 5
DTE_HI = 45
OTM_LO = 1.03
OTM_HI = 1.25

DAILY_SQL = '''
SELECT qdate,
       SUM(volume) AS call_vol,
       SUM(CASE WHEN delta BETWEEN %s AND %s
                 AND DATEDIFF(edate, qdate) BETWEEN %s AND %s
                 AND underlying_last > 0
                 AND strike > underlying_last * %s
                 AND strike <= underlying_last * %s
                 AND bid > 0 AND ask >= bid
            THEN volume ELSE 0 END) AS band_vol,
       SUM(CASE WHEN delta BETWEEN %s AND %s
                 AND DATEDIFF(edate, qdate) BETWEEN %s AND %s
                 AND underlying_last > 0
                 AND strike > underlying_last * %s
                 AND strike <= underlying_last * %s
                 AND bid > 0 AND ask >= bid
            THEN oi ELSE 0 END) AS band_oi
FROM optiondaily
WHERE underlying = %s AND `type` = 'call' AND qdate BETWEEN %s AND %s
GROUP BY qdate
'''

BAND_SQL = '''
SELECT qdate, strike, edate, SUM(volume) AS vol
FROM optiondaily
WHERE underlying = %s AND `type` = 'call' AND qdate BETWEEN %s AND %s
  AND delta BETWEEN %s AND %s
  AND DATEDIFF(edate, qdate) BETWEEN %s AND %s
  AND underlying_last > 0
  AND strike > underlying_last * %s
  AND strike <= underlying_last * %s
  AND bid > 0 AND ask >= bid
GROUP BY qdate, strike, edate
'''

PUT_SQL = '''
SELECT qdate, SUM(volume) AS put_vol
FROM optiondaily
WHERE underlying = %s AND `type` = 'put' AND qdate BETWEEN %s AND %s
GROUP BY qdate
'''


def load_sessions(root: Path) -> list[date]:
    rows = json.loads((root / 'data/calendar/nyse_sessions.json').read_text())
    return [date.fromisoformat(r['session']) for r in rows]


def load_keeps(root: Path) -> list[dict]:
    payload = json.loads((root / 'data/price_jump_news_reviews.json').read_text())
    keeps = []
    for row in payload['reviews']:
        if row.get('news_filter') != 'keep':
            continue
        keeps.append(dict(
            symbol=row['symbol'].upper(),
            qdate=date.fromisoformat(row['qdate']),
            cause_class=row.get('cause_class'),
            jump_cause=row.get('jump_cause'),
            tier='A' if str(row.get('cause_class', '')).startswith('2_') else 'B',
        ))
    return keeps


def span(sessions: list[date], index: dict, event: date, shift: int = 0):
    """Return (window dates, baseline dates) ending the session before event-shift."""
    if event not in index:
        return None
    end = index[event] - shift
    window_start = end - WINDOW
    baseline_start = window_start - BASELINE
    if baseline_start < 0 or end <= 0:
        return None
    return sessions[window_start:end], sessions[baseline_start:window_start]


def top_shares(band_rows) -> dict:
    totals = defaultdict(int)
    tops = defaultdict(int)
    for row in band_rows:
        volume = int(row['vol'] or 0)
        totals[row['qdate']] += volume
        if volume > tops[row['qdate']]:
            tops[row['qdate']] = volume
    return {day: tops[day] / totals[day] for day in totals if totals[day] > 0}


def chain_days(daily_rows, shares) -> dict:
    out = {}
    for row in daily_rows:
        call_vol = int(row['call_vol'] or 0)
        band_vol = int(row['band_vol'] or 0)
        out[row['qdate']] = dict(
            qdate=row['qdate'],
            call_vol=call_vol,
            band_vol=band_vol,
            band_oi=int(row.get('band_oi') or 0),
            put_vol=0,
            top_share=shares.get(row['qdate']),
        )
    return out


def _median_share(days) -> float:
    shares = [d['band_vol'] / d['call_vol'] for d in days if d['call_vol'] >= 20]
    if not shares:
        return 0.0
    return float(statistics.median(shares))


def score_window(window, baseline) -> dict:
    """Score already-selected observed chain days. Dates must be chronological."""
    if len(window) < MIN_OBSERVED_WINDOW or len(baseline) < MIN_BASELINE:
        return dict(eligible=False, hit=False, alert_dates=[], max_ratio=None, max_share=None,
                    observed_window=len(window), observed_baseline=len(baseline))
    mean = statistics.fmean(d['call_vol'] for d in baseline)
    median_share = _median_share(baseline)
    alerts = []
    ratios = []
    shares = []
    for day in window:
        volume = day['call_vol']
        share = (day['band_vol'] / volume) if volume else 0.0
        ratio = None if mean == 0 else volume / mean
        if volume:
            shares.append(share)
        if ratio is not None:
            ratios.append(ratio)
        surge = volume >= MIN_VOLUME if mean == 0 else volume >= VOLUME_RATIO * mean
        concentrated = True
        if day['band_vol'] >= MIN_BAND_FOR_CONCENTRATION:
            concentrated = day['top_share'] is not None and day['top_share'] >= TOP_SHARE_MIN
        if (volume >= MIN_VOLUME and surge and share >= BAND_SHARE_MIN
                and share >= median_share + BAND_SHARE_LIFT and concentrated):
            alerts.append(day['qdate'])
    return dict(
        eligible=True,
        hit=bool(alerts),
        alert_dates=[d.isoformat() for d in alerts],
        max_ratio=max(ratios) if ratios else None,
        max_share=max(shares) if shares else None,
        observed_window=len(window),
        observed_baseline=len(baseline),
        baseline_mean=mean,
        baseline_median_share=median_share,
    )


def select_days(by_date, wanted) -> list[dict]:
    return [by_date[d] for d in wanted if d in by_date]


def evaluate(by_date, window_dates, baseline_dates) -> dict:
    return score_window(select_days(by_date, window_dates), select_days(by_date, baseline_dates))


def mcnemar(pairs) -> dict:
    """Continuity-corrected McNemar on paired (case_hit, control_hit) booleans."""
    both = sum(a and b for a, b in pairs)
    case_only = sum(a and not b for a, b in pairs)
    control_only = sum(b and not a for a, b in pairs)
    neither = sum(not a and not b for a, b in pairs)
    discordant = case_only + control_only
    if discordant == 0:
        chi2 = None
        p_value = None
    else:
        chi2 = (abs(case_only - control_only) - 1) ** 2 / discordant
        p_value = math.erfc(math.sqrt(chi2 / 2.0))
    return dict(n=len(pairs), both=both, case_only=case_only, control_only=control_only,
                neither=neither, chi2=chi2, p_value=p_value)


def control_rows(records, key) -> list[dict]:
    rows = []
    for record in records:
        row = record.get(key)
        rows.append(row if row else dict(eligible=False, hit=False, reason='not_run'))
    return rows


def rate_row(records) -> dict:
    eligible = [r for r in records if r.get('eligible')]
    hits = [r for r in eligible if r.get('hit')]
    return dict(n=len(records), eligible=len(eligible), hits=len(hits),
                hit_rate=(len(hits) / len(eligible)) if eligible else None)


def hit_list(records, event_key='qdate') -> list[dict]:
    found = []
    for record in records:
        if record.get('eligible') and record.get('hit'):
            found.append(dict(symbol=record.get('symbol'), event=record.get(event_key),
                              alert_dates=record.get('alert_dates') or []))
    return found


def median_of(records, key):
    values = [r[key] for r in records if r.get('eligible') and r.get(key) is not None]
    if not values:
        return None
    return float(statistics.median(values))


def fetch_chain(connection, symbol, start, end):
    band_params = (DELTA_LO, DELTA_HI, DTE_LO, DTE_HI, OTM_LO, OTM_HI)
    daily_args = band_params + band_params + (symbol, start, end)
    band_args = (symbol, start, end) + band_params
    with connection.cursor() as cursor:
        cursor.execute(DAILY_SQL, daily_args)
        daily = cursor.fetchall()
        cursor.execute(BAND_SQL, band_args)
        band = cursor.fetchall()
        cursor.execute(PUT_SQL, (symbol, start, end))
        puts = cursor.fetchall()
    days = chain_days(daily, top_shares(band))
    for row in puts:
        volume = int(row['put_vol'] or 0)
        slot = days.get(row['qdate'])
        if slot is None:
            days[row['qdate']] = dict(qdate=row['qdate'], call_vol=0, band_vol=0, band_oi=0,
                                      put_vol=volume, top_share=None)
        else:
            slot['put_vol'] = volume
    return days


def connect():
    import pymysql
    password = os.environ.get('OPTIONDB_PASSWORD')
    if not password:
        raise RuntimeError('OPTIONDB_PASSWORD is required')
    config = dict(
        user=os.environ.get('OPTIONDB_USER') or 'optiondb',
        password=password,
        database=os.environ.get('OPTIONDB_DATABASE', 'optiondb'),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=180,
        autocommit=False,
    )
    if os.environ.get('OPTIONDB_HOST'):
        config['host'] = os.environ['OPTIONDB_HOST']
        config['port'] = int(os.environ.get('OPTIONDB_PORT', '3306'))
    else:
        config['unix_socket'] = os.environ.get('OPTIONDB_SOCKET', '/run/mysqld/mysqld.sock')
    connection = pymysql.connect(**config)
    with connection.cursor() as cursor:
        cursor.execute('SET SESSION MAX_EXECUTION_TIME=180000')
        cursor.execute('START TRANSACTION READ ONLY')
    return connection


def earnings_dates(connection, symbols):
    if not symbols:
        return defaultdict(list)
    placeholders = ','.join(['%s'] * len(symbols))
    sql = f'''SELECT symbol, erdate, rxdate FROM erdate
              WHERE symbol IN ({placeholders})
                AND erdate BETWEEN %s AND %s'''
    with connection.cursor() as cursor:
        cursor.execute(sql, (*symbols, date(2012, 6, 1), date(2017, 6, 1)))
        rows = cursor.fetchall()
    out = defaultdict(list)
    for row in rows:
        symbol = (row['symbol'] or '').upper()
        reaction = row['rxdate'] or row['erdate']
        if symbol and reaction:
            out[symbol].append(reaction)
    return out


def scored_span(days, dates) -> dict:
    window, baseline = dates
    scored = evaluate(days, window, baseline)
    features = window_features(select_days(days, window), select_days(days, baseline))
    if features:
        scored['features'] = features
    return scored


def choose_earnings(symbol, event, earnings, index, sessions, occupied):
    best = None
    best_distance = None
    event_i = index.get(event)
    if event_i is None:
        return None
    for raw in earnings.get(symbol, []):
        session = raw if raw in index else next((s for s in sessions if s >= raw), None)
        if session is None or session not in index:
            continue
        gaps = [abs(index[session] - index[other]) for other in occupied.get(symbol, []) if other in index]
        if not gaps or min(gaps) < EARNINGS_GAP:
            continue
        distance = abs(index[session] - event_i)
        if distance < EARNINGS_GAP:
            continue
        if best_distance is None or distance < best_distance:
            best = session
            best_distance = distance
    return best


def cover_range(window_dates, baseline_dates):
    days = list(window_dates) + list(baseline_dates)
    return min(days), max(days)


def run(root: Path, connection=None) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    keeps = load_keeps(root)
    own = close_connection = connection is None
    if own:
        connection = connect()
        close_connection = True
    cache = {}

    def chain(symbol, start, end):
        key = (symbol, start, end)
        if key not in cache:
            cache[key] = fetch_chain(connection, symbol, start, end)
        return cache[key]

    occupied = defaultdict(set)
    for row in keeps:
        occupied[row['symbol']].add(row['qdate'])
    symbols = sorted({row['symbol'] for row in keeps if row['tier'] == 'A'})
    earnings = earnings_dates(connection, symbols)
    records = []
    try:
        for n, row in enumerate(keeps, start=1):
            real = span(sessions, index, row['qdate'], 0)
            item = dict(symbol=row['symbol'], qdate=row['qdate'].isoformat(), tier=row['tier'],
                        cause_class=row['cause_class'], jump_cause=row['jump_cause'])
            if real is None:
                item.update(eligible=False, hit=False, reason='jump_not_on_calendar')
            else:
                start, end = cover_range(*real)
                item.update(scored_span(chain(row['symbol'], start, end), real))
            if row['tier'] == 'A':
                placebo = span(sessions, index, row['qdate'], PLACEBO_SHIFT)
                if placebo is None:
                    item['placebo'] = dict(eligible=False, hit=False, reason='no_prior_history')
                else:
                    start, end = cover_range(*placebo)
                    item['placebo'] = scored_span(chain(row['symbol'], start, end), placebo)
                    item['placebo_event'] = sessions[index[row['qdate']] - PLACEBO_SHIFT].isoformat()
                chosen = choose_earnings(row['symbol'], row['qdate'], earnings, index, sessions, occupied)
                if chosen is None:
                    item['earnings'] = dict(eligible=False, hit=False, reason='no_separated_earnings_date')
                else:
                    earnings_span = span(sessions, index, chosen, 0)
                    if earnings_span is None:
                        item['earnings'] = dict(eligible=False, hit=False, reason='earnings_span_unavailable')
                    else:
                        start, end = cover_range(*earnings_span)
                        item['earnings'] = scored_span(chain(row['symbol'], start, end), earnings_span)
                    item['earnings_event'] = chosen.isoformat()
            records.append(item)
            if n % 25 == 0:
                print(f'processed {n} of {len(keeps)}', flush=True)
    finally:
        if close_connection:
            connection.rollback()
            connection.close()

    tier_a = [r for r in records if r['tier'] == 'A']
    tier_b = [r for r in records if r['tier'] == 'B']
    placebo = control_rows(tier_a, 'placebo')
    earnings_rows = control_rows(tier_a, 'earnings')
    paired_placebo = [(r['hit'], r['placebo']['hit']) for r in tier_a
                      if r.get('eligible') and r.get('placebo', {}).get('eligible')]
    paired_earnings = [(r['hit'], r['earnings']['hit']) for r in tier_a
                       if r.get('eligible') and r.get('earnings', {}).get('eligible')]
    summary = dict(
        rule=dict(window=WINDOW, baseline=BASELINE, min_observed_window=MIN_OBSERVED_WINDOW,
                  min_baseline=MIN_BASELINE, min_volume=MIN_VOLUME, volume_ratio=VOLUME_RATIO,
                  band_share_min=BAND_SHARE_MIN, band_share_lift=BAND_SHARE_LIFT,
                  top_share_min=TOP_SHARE_MIN, delta=[DELTA_LO, DELTA_HI], dte=[DTE_LO, DTE_HI],
                  otm=[OTM_LO, OTM_HI], placebo_shift=PLACEBO_SHIFT, earnings_gap=EARNINGS_GAP),
        counts=dict(keeps=len(keeps), tier_a=len(tier_a), tier_b=len(tier_b)),
        tier_a=rate_row(tier_a),
        placebo=rate_row(placebo),
        earnings=rate_row(earnings_rows),
        tier_b=rate_row(tier_b),
        paired_placebo=mcnemar(paired_placebo),
        paired_earnings=mcnemar(paired_earnings),
        tier_a_hits=hit_list(tier_a),
        descriptive=dict(
            tier_a_median_max_ratio=median_of(tier_a, 'max_ratio'),
            tier_a_median_max_share=median_of(tier_a, 'max_share'),
            placebo_median_max_ratio=median_of(placebo, 'max_ratio'),
            placebo_median_max_share=median_of(placebo, 'max_share'),
            earnings_median_max_ratio=median_of(earnings_rows, 'max_ratio'),
            earnings_median_max_share=median_of(earnings_rows, 'max_share'),
            tier_b_median_max_ratio=median_of(tier_b, 'max_ratio'),
            tier_b_median_max_share=median_of(tier_b, 'max_share'),
        ),
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    model = evaluate_model(samples_from_records(records))
    summary['model'] = {key: model[key] for key in ('fit', 'n_train', 'volume_only_holdout_auc') if key in model}
    if model.get('fit'):
        summary['model']['holdout_2016'] = model['folds']['holdout_2016']
    (folder / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (folder / 'events.json').write_text(json.dumps(records, indent=2, default=str) + '\n')
    (folder / 'model.json').write_text(json.dumps(model, indent=2) + '\n')
    (folder / 'REPORT.md').write_text(render_report(summary))
    (folder / 'MODEL.md').write_text(render_model_report(model))
    print(json.dumps(model.get('folds', model), indent=2, default=str), flush=True)
    return summary


def fmt_rate(row) -> str:
    rate = 'n/a' if row['hit_rate'] is None else f"{row['hit_rate']:.1%}"
    return f"{row['hits']} / {row['eligible']} ({rate})"


def fmt_num(value, digits=2):
    if value is None:
        return 'n/a'
    return f'{value:.{digits}f}'


def render_report(summary) -> str:
    a = summary['tier_a']
    p = summary['placebo']
    e = summary['earnings']
    b = summary['tier_b']
    pp = summary['paired_placebo']
    pe = summary['paired_earnings']
    d = summary['descriptive']
    lines = [
        '# Call-footprint screen',
        '',
        'Frozen rule, applied once. A day alerts when call volume is at least 100 and at least 3× that name\'s prior-20-session mean, at least 40% of that volume sits in calls with delta 0.10–0.35, 5–45 days to expiry and 3–25% out of the money, that share is at least 0.10 above the name\'s baseline median, and one strike-expiry holds at least half of the band when the band has 20 contracts. An event hits when any of the 10 pre-event sessions alerts. The jump session itself is excluded.',
        '',
        'Tier A is the 86 class-2 M&A keeps. The placebo is the same name 60 trading sessions earlier. The earnings control is the nearest earnings reaction on that name at least 40 sessions away from every keep for the name. Tier B is the other 160 keeps. Vendor gamma is not a gate: stored gamma on this table is not on a per-dollar Black–Scholes scale.',
        '',
        'The jump date is the reaction session used by the news ledger. It is a proxy for first public disclosure, and an earlier rumor still contaminates that window. A hit is a cheap concentrated call print. It is not an identification of a trader.',
        '',
        '| Cohort | Hits / eligible |',
        '| --- | ---: |',
        f"| Tier A, 10 sessions before the jump | {fmt_rate(a)} |",
        f"| Same names, 60 sessions earlier | {fmt_rate(p)} |",
        f"| Same names, separated earnings reaction | {fmt_rate(e)} |",
        f"| Tier B, 10 sessions before the jump | {fmt_rate(b)} |",
        '',
        f"Paired Tier A versus placebo, among events eligible on both: {pp['n']} pairs, {pp['case_only']} hit only on the event, {pp['control_only']} hit only on the placebo, {pp['both']} hit on both. Continuity-corrected McNemar chi-square {fmt_num(pp['chi2'])}, p {fmt_num(pp['p_value'], 3)}.",
        '',
        f"Paired Tier A versus earnings: {pe['n']} pairs, {pe['case_only']} event only, {pe['control_only']} earnings only, {pe['both']} both. Chi-square {fmt_num(pe['chi2'])}, p {fmt_num(pe['p_value'], 3)}.",
        '',
        'Secondary description, not a second test. Median across eligible events of the largest single-day call-volume ratio and of the largest band share in the window:',
        '',
        '| Cohort | Median max volume ratio | Median max band share |',
        '| --- | ---: | ---: |',
        f"| Tier A | {fmt_num(d['tier_a_median_max_ratio'])} | {fmt_num(d['tier_a_median_max_share'])} |",
        f"| Placebo | {fmt_num(d['placebo_median_max_ratio'])} | {fmt_num(d['placebo_median_max_share'])} |",
        f"| Earnings | {fmt_num(d['earnings_median_max_ratio'])} | {fmt_num(d['earnings_median_max_share'])} |",
        f"| Tier B | {fmt_num(d['tier_b_median_max_ratio'])} | {fmt_num(d['tier_b_median_max_share'])} |",
        '',
        'Tier A events that hit:',
        '',
    ]
    hits = summary.get('tier_a_hits') or []
    if hits:
        for row in hits:
            dates = ', '.join(row['alert_dates'])
            lines.append(f"- {row['symbol']} {row['event']}: {dates}")
    else:
        lines.append('- None.')
    lines += [
        '',
        'Thresholds were not changed after seeing these counts. Population precision, training readiness, and trading results are not estimated.',
        '',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args()
    run(args.root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
