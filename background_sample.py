"""Outcome-independent historical stock-day sample for option coverage preflight.

Unlabeled observations are never assumed negative. This pilot cannot estimate
false positives; it establishes reproducible background extraction and coverage.
"""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import random

from research_cohort import calendar_features, daily_sql, write_rows
from sec_match import connection
from market_calendar import sessions


def choose(items,count,seed):
    """Stable under input ordering; local RNG never depends on event outcomes."""
    values=sorted(items)
    return sorted(random.Random(seed).sample(values,min(count,len(values))))


def run(c,root=Path('.'),start_year=2013,end_year=2025,dates_per_year=1,symbols_per_date=5,seed=1984):
    if start_year>end_year or dates_per_year<1 or symbols_per_date<1:
        raise ValueError('Invalid year range or nonpositive sample size')
    rows=[];frames=[]
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        calendar=sessions(root=root)
        for year in range(start_year,end_year+1):
            dates=[d for d in calendar if d.year==year and calendar.index(d)>=20 and calendar.index(d)+10<len(calendar)]
            for target in choose(dates,dates_per_year,f'{seed}:dates:{year}'):
                q.execute('SELECT symbol FROM stockquote WHERE qdate=%s AND close>0 ORDER BY symbol',(target,))
                population=sorted(set(r['symbol'] for r in q.fetchall()))
                symbols=choose(population,symbols_per_date,f'{seed}:symbols:{target}')
                frames.append(dict(qdate=target,year_sessions=len(dates),sampled_year_sessions=min(dates_per_year,len(dates)),
                                   stockquote_symbols=len(population),sampled_symbols=len(symbols)))
                index=calendar.index(target)
                for symbol in symbols:
                    row=dict(symbol=symbol,qdate=target,training_label=None,
                             label_status='unlabeled_incomplete_event_registry',
                             selection='outcome_independent_stockquote_sample',
                             instrument_classification='unreviewed',
                             stockdate_sampling_weight=len(population)/len(symbols)*len(dates)/min(dates_per_year,len(dates)))
                    try:
                        q.execute('SELECT 1 AS present FROM optiondaily WHERE underlying=%s AND qdate=%s LIMIT 1',(symbol,target))
                        if not q.fetchone():
                            row['option_coverage_status']='no_target_rows_listing_status_unknown'
                        else:
                            q.execute(daily_sql(),(symbol,calendar[index-20],target))
                            days=q.fetchall()
                            features=calendar_features(days,calendar,calendar[index+1],observation_sessions=1)[0]
                            features.pop('next_close_strictly_before_announcement')
                            row.update(features)
                            row.update(label_status='unlabeled_incomplete_event_registry',option_coverage_status='observed_target_chain')
                    except Exception as exc:
                        import pymysql
                        if not isinstance(exc,pymysql.MySQLError):raise
                        row.update(option_coverage_status='query_failed',query_error=str(exc))
                    rows.append(row)
                print(target,'sampled',len(symbols),'of',len(population),'historical stockquote symbols',flush=True)
    c.rollback()
    folder=root/'results/background_sample';folder.mkdir(parents=True,exist_ok=True)
    write_rows(folder,'observations',rows);write_rows(folder,'sampling_frames',frames)
    counts=Counter(r['option_coverage_status'] for r in rows)
    summary=dict(seed=seed,start_year=start_year,end_year=end_year,dates_per_year=dates_per_year,
                 calendar_source='data/calendar/manifest.json',
                 symbols_per_date=symbols_per_date,sampled_stock_days=len(rows),sampled_dates=len(frames),
                 option_coverage_counts=dict(counts),
                 complete_valid_feature_observations=sum(bool(r.get('baseline_complete') and r.get('volume_data_valid')) for r in rows),
                 negative_labels_assigned=0,
                 notes=['Sampling uses historical stockquote presence and positive price, never M&A outcomes or current surviving tickers.',
                        'This is a small coverage pilot, not a complete optionable universe or performance test.',
                        'Source coverage, instrument type, ticker reuse, and first-disclosure labels still require validation.',
                        'Weights describe the two-stage stockquote sampling frame, not a validated equity-option universe.',
                        'Unlabeled observations may include real acquisition events; none are presumed negative.'])
    (folder/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
    return summary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start-year',type=int,default=2013)
    parser.add_argument('--end-year',type=int,default=2025)
    parser.add_argument('--dates-per-year',type=int,default=1)
    parser.add_argument('--symbols-per-date',type=int,default=5)
    parser.add_argument('--seed',type=int,default=1984)
    args=parser.parse_args()
    with connection() as c:run(c,**vars(args))


if __name__=='__main__':main()
