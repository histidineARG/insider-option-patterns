"""Descriptive SEC event alignment. This is not a trained model or a backtest."""
import argparse
import csv
from datetime import date, timedelta
from decimal import Decimal
import getpass
import json
import os
from pathlib import Path
import statistics

import pymysql


def connection():
    password = os.environ.get('OPTIONDB_PASSWORD')
    if password is None:
        password = getpass.getpass('Local MySQL password: ')
    return pymysql.connect(
        unix_socket=os.environ.get('OPTIONDB_SOCKET', '/run/mysqld/mysqld.sock'),
        user=os.environ.get('OPTIONDB_USER', 'bill'), password=password,
        database=os.environ.get('OPTIONDB_DATABASE', 'optiondb'),
        cursorclass=pymysql.cursors.DictCursor, connect_timeout=5, read_timeout=65)


def daily_query(case):
    args = []
    series = []
    for contract in case['contracts']:
        series.append('(strike=%s AND edate=%s)')
        args.extend([contract['strike'], contract['expiry']])
    match = "`type`='call' AND (" + ' OR '.join(series) + ')' if series else 'FALSE'
    eligible = "`type`='call' AND underlying_last>0 AND strike>underlying_last AND DATEDIFF(edate,qdate) BETWEEN 1 AND 60"
    sql = f'''SELECT qdate, COUNT(*) AS chain_rows,
        SUM(CASE WHEN `type`='call' THEN GREATEST(volume,0) ELSE 0 END) AS call_volume,
        SUM(CASE WHEN `type`='put' THEN GREATEST(volume,0) ELSE 0 END) AS put_volume,
        SUM(CASE WHEN `type`='call' AND underlying_last>0 AND strike>underlying_last
            AND edate>=qdate THEN GREATEST(volume,0) ELSE 0 END) AS otm_all_expiries_volume,
        SUM(CASE WHEN {eligible} THEN GREATEST(volume,0) ELSE 0 END) AS otm_volume,
        SUM(CASE WHEN {eligible} THEN GREATEST(oi,0) ELSE 0 END) AS otm_oi,
        MAX(CASE WHEN {eligible} THEN GREATEST(volume,0) ELSE 0 END) AS top_otm_volume,
        SUM(CASE WHEN {match} THEN GREATEST(volume,0) ELSE 0 END) AS source_series_volume,
        SUM(CASE WHEN {match} THEN 1 ELSE 0 END) AS source_series_rows
        FROM optiondaily WHERE underlying=%s AND qdate BETWEEN %s AND %s
        GROUP BY qdate ORDER BY qdate'''
    args *= 2  # Two identical matched-series expressions, in SQL order.
    start = date.fromisoformat(case['trade_start']) - timedelta(days=120)
    end = date.fromisoformat(case['event_date']) + timedelta(days=7)
    args.extend([case['symbol'], start, end])
    return sql, args


def annotate(days, lookback=20):
    result = []
    for i, day in enumerate(days):
        row = {k: (float(v) if isinstance(v, Decimal) else v) for k,v in day.items()}
        history = days[max(0,i-lookback):i]
        row['baseline_sessions'] = len(history)
        row['otm_ratio20'] = None
        row['otm_z20'] = None
        row['zero_baseline'] = False
        row['diagnostic_alert'] = False
        if len(history) == lookback:
            values = [float(d['otm_volume']) for d in history]
            mean, std = statistics.mean(values), statistics.pstdev(values)
            row['baseline_mean20'] = mean
            row['zero_baseline'] = mean == 0
            row['otm_ratio20'] = row['otm_volume']/mean if mean else None
            row['otm_z20'] = (row['otm_volume']-mean)/std if std else None
            row['diagnostic_alert'] = row['otm_volume'] >= 100 and (mean == 0 or row['otm_ratio20'] >= 3)
        row['otm_volume_oi'] = row['otm_volume']/row['otm_oi'] if row['otm_oi'] else None
        row['top_otm_share'] = row['top_otm_volume']/row['otm_volume'] if row['otm_volume'] else None
        for field in ['otm_all_expiries_volume','source_series_volume']:
            mean = statistics.mean(float(d[field]) for d in history) if len(history)==lookback else None
            row[field+'_ratio20'] = row[field]/mean if mean else None
            row[field+'_zero_baseline'] = mean == 0 if mean is not None else None
        result.append(row)
    return result


def summarize(case, days, calendar):
    start, end, event = map(date.fromisoformat, [case['trade_start'],case['trade_end'],case['event_date']])
    # EOD on an after-close announcement date is not assumed observable before news.
    pre = [d for d in days if start <= d['qdate'] <= end and d['qdate'] < event]
    expected = [d for d in calendar if start <= d <= end and d < event]
    observed = {d['qdate'] for d in pre}
    alerts = [d for d in pre if d['diagnostic_alert']]
    peak = max((d for d in pre if d['otm_ratio20'] is not None),
               key=lambda d:d['otm_ratio20'],default=None)
    first = alerts[0]['qdate'] if alerts else None
    next_day = next((d for d in calendar if first and d>first), None)
    source_volume = sum(d['source_series_volume'] for d in days if start <= d['qdate'] <= end)
    return dict(case_id=case['id'],symbol=case['symbol'],event_date=event.isoformat(),
                evidence_status=case['evidence_status'],window_quality=case['window_quality'],
                match_status='pre_event_data' if pre else ('no_usable_pre_event_eod' if days else 'no_chain_data'),
                observed_pre_event_sessions=len(pre),expected_pre_event_sessions=len(expected),
                missing_pre_event_dates=';'.join(str(d) for d in expected if d not in observed),
                diagnostic_alert_days=len(alerts),first_diagnostic_alert=str(first) if first else None,
                next_session_close_proxy=str(next_day) if next_day else None,
                entry_proxy_precedes_event=bool(next_day and next_day < event),
                peak_otm_ratio20=peak['otm_ratio20'] if peak else None,
                peak_ratio_date=str(peak['qdate']) if peak else None,
                peak_all_expiries_ratio20=max((d['otm_all_expiries_volume_ratio20'] for d in pre
                    if d['otm_all_expiries_volume_ratio20'] is not None),default=None),
                peak_source_series_ratio20=max((d['source_series_volume_ratio20'] for d in pre
                    if d['source_series_volume_ratio20'] is not None),default=None) if case['contracts'] else None,
                source_series_volume=source_volume if case['contracts'] else None,
                source_series_rows=sum(d['source_series_rows'] for d in days if start <= d['qdate'] <= end) if case['contracts'] else None,
                documented_contracts=case.get('documented_contracts'),source_url=case['source_url'])


def run(c, registry, output):
    output.mkdir(parents=True, exist_ok=True)
    summaries, daily = [], []
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        q.execute("SELECT tradingday FROM tradingday WHERE tradingday BETWEEN '2012-01-01' AND '2026-11-05' ORDER BY tradingday")
        calendar = [r['tradingday'] for r in q.fetchall()]
        for case in registry['cases']:
            if not case['event_date_verified']:
                summaries.append(dict(case_id=case['id'],symbol=case['symbol'],match_status='event_date_review_pending',source_url=case['source_url']))
                print(case['id'], 'event date review pending',flush=True)
                continue
            sql,args = daily_query(case)
            try:
                q.execute(sql,args)
                days = annotate(q.fetchall())
                summary = summarize(case,days,calendar)
                summaries.append(summary)
                daily.extend(dict(case_id=case['id'],**day) for day in days)
                print(case['id'],summary['match_status'],'sessions',summary['observed_pre_event_sessions'],
                      'peak ratio',summary['peak_otm_ratio20'],flush=True)
            except pymysql.MySQLError as e:
                summaries.append(dict(case_id=case['id'],symbol=case['symbol'],match_status='query_failed',error=str(e)))
                print(case['id'],'query failed',e,flush=True)
    c.rollback()
    for name,rows in [('case_matches',summaries),('daily_features',daily)]:
        (output/(name+'.json')).write_text(json.dumps(rows,indent=2,default=str,allow_nan=False)+'\n')
        fields = list(dict.fromkeys(k for r in rows for k in r))
        with (output/(name+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    return summaries


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry',type=Path,default=Path('data/sec_cases.json'))
    p.add_argument('--output',type=Path,default=Path('results/sec_alignment'))
    args=p.parse_args()
    with connection() as c:
        run(c,json.loads(args.registry.read_text()),args.output)


if __name__=='__main__':
    main()
