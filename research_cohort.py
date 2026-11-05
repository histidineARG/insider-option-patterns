"""Read-only price-only M&A cohort and calendar-aware pre-event option audit.

This stage produces descriptive observations, not training labels or error rates.
It uses the saved stock-confirmation snapshot and does not promote price leads.
"""
import argparse
from collections import Counter
import csv
from datetime import date
import json
from pathlib import Path
import statistics

from sec_match import connection
from market_calendar import sessions


def cohort_decision(row):
    """Volume completeness and surge are deliberately absent from eligibility."""
    if row.get('eligibility') == 'excluded':
        return 'excluded_target_or_event_identity'
    if not row.get('date_verified') or row.get('eligibility') != 'target_evidence_reviewed':
        return 'announcement_or_target_review_pending'
    if row.get('announcement_session') not in {'before_open', 'after_close', 'intraday', 'nontrading_day'}:
        return 'announcement_timing_review_pending'
    if 'price_jump_at_least_15pct' not in row:
        return 'price_measurement_missing'
    return 'price_qualified' if row['price_jump_at_least_15pct'] else 'price_below_15pct'


def daily_sql():
    # Aggregate every observed chain day, preserving real zero OTM activity.
    eligible = "`type`='call' AND underlying_last>0 AND strike>underlying_last AND DATEDIFF(edate,qdate) BETWEEN 1 AND 60"
    return f'''SELECT qdate,COUNT(*) AS chain_rows,
      SUM(CASE WHEN `type`='call' THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS call_volume,
      SUM(CASE WHEN `type`='put' THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS put_volume,
      SUM(CASE WHEN {eligible} THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS otm_call_volume,
      SUM(CASE WHEN {eligible} THEN GREATEST(COALESCE(oi,0),0) ELSE 0 END) AS otm_call_oi_diagnostic,
      MAX(CASE WHEN {eligible} THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS top_otm_call_volume,
      SUM(CASE WHEN {eligible} AND DATEDIFF(edate,qdate)<=14 THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS otm_call_volume_dte1_14,
      SUM(CASE WHEN {eligible} AND DATEDIFF(edate,qdate) BETWEEN 15 AND 30 THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS otm_call_volume_dte15_30,
      SUM(CASE WHEN {eligible} AND DATEDIFF(edate,qdate) BETWEEN 31 AND 60 THEN GREATEST(COALESCE(volume,0),0) ELSE 0 END) AS otm_call_volume_dte31_60,
      SUM(CASE WHEN {eligible} AND (volume IS NULL OR volume<0) THEN 1 ELSE 0 END) AS invalid_otm_volume_rows
      FROM optiondaily WHERE underlying=%s AND qdate BETWEEN %s AND %s
      GROUP BY qdate ORDER BY qdate'''


def calendar_features(days, calendar, event_date, observation_sessions=30, lookback=20):
    """Missing sessions invalidate baselines; event-day/future rows are ignored."""
    before=[d for d in calendar if d < event_date]
    targets=before[-observation_sessions:]
    by_date={r['qdate']:r for r in days if r['qdate']<event_date}
    positions={d:i for i,d in enumerate(calendar)}
    output=[]
    for target in targets:
        index=positions[target]
        expected=calendar[max(0,index-lookback):index]
        observed=by_date.get(target)
        missing=[d for d in expected if d not in by_date]
        row=dict(qdate=target,chain_observed=observed is not None,
                 expected_baseline_sessions=len(expected),
                 observed_baseline_sessions=len(expected)-len(missing),
                 missing_baseline_dates=[str(d) for d in missing],
                 baseline_complete=len(expected)==lookback and not missing,
                 # Conservative next-session CLOSE proxy, not an asserted fill.
                 next_session_close_proxy=calendar[index+1] if index+1<len(calendar) else None,
                 next_close_strictly_before_announcement=(index+1<len(calendar) and calendar[index+1]<event_date),
                 training_label=None,
                 label_status='first_public_disclosure_and_universe_review_pending')
        # Horizon labels deliberately remain null: an announcement date is not
        # necessarily the first public disclosure, and the registry is incomplete.
        if observed is not None:
            row.update({k:int(v) for k,v in observed.items() if k!='qdate'})
            current=row['otm_call_volume']
            row['top_otm_call_share']=row['top_otm_call_volume']/current if current else None
            total=row['call_volume']+row['put_volume']
            row['call_share']=row['call_volume']/total if total else None
            if row['baseline_complete']:
                history=[by_date[d] for d in expected]
                invalid=sum(int(d['invalid_otm_volume_rows']) for d in history)+row['invalid_otm_volume_rows']
                row['volume_data_valid']=invalid==0
                if not invalid:
                    values=[int(d['otm_call_volume']) for d in history]
                    mean=statistics.mean(values);std=statistics.pstdev(values)
                    row.update(otm_mean20=mean,otm_std20=std,
                               otm_ratio20=current/mean if mean else None,
                               otm_z20=(current-mean)/std if std else None,
                               zero_volume_baseline=mean==0)
        output.append(row)
    return output


def write_rows(folder,name,rows):
    (folder/(name+'.json')).write_text(json.dumps(rows,indent=2,default=str,allow_nan=False)+'\n')
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with (folder/(name+'.csv')).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader()
        for row in rows:
            writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})


def run(c,root=Path('.')):
    source=root/'results/ma_stock_confirmation/all_candidates.json'
    inputs=json.loads(source.read_text())
    cohort=[];daily=[]
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        calendar=sessions(root=root)
        for candidate in inputs:
            row=dict(candidate,cohort_status=cohort_decision(candidate),
                     training_label_ready=False,first_public_disclosure_verified=False,
                     corporate_action_review_complete=False)
            if row['cohort_status']!='price_qualified':
                cohort.append(row);continue
            event=date.fromisoformat(row['announcement_date'])
            prior=[d for d in calendar if d<event][-50:]
            try:
                q.execute(daily_sql(),(row['symbol'],prior[0],prior[-1]))
                observed=q.fetchall()
                features=calendar_features(observed,calendar,event)
                valid=[r for r in features if r['chain_observed'] and r['baseline_complete'] and r.get('volume_data_valid')]
                row.update(option_coverage_status='observed_chain' if observed else 'no_rows_listing_status_unknown',
                           expected_observation_sessions=len(features),
                           observed_observation_sessions=sum(r['chain_observed'] for r in features),
                           complete_valid_feature_sessions=len(valid),
                           conservative_preannouncement_entry_sessions=sum(r['next_close_strictly_before_announcement'] for r in valid),
                           missing_observation_dates=[str(r['qdate']) for r in features if not r['chain_observed']],
                           peak_descriptive_otm_ratio20=max((r['otm_ratio20'] for r in valid if r.get('otm_ratio20') is not None),default=None))
                daily.extend(dict(symbol=row['symbol'],announcement_date=row['announcement_date'],**r) for r in features)
            except Exception as exc:
                # Surface individual query failures; never classify them as no options.
                import pymysql
                if not isinstance(exc,pymysql.MySQLError):raise
                row.update(option_coverage_status='query_failed',query_error=str(exc))
            cohort.append(row)
            print(row['symbol'],row.get('option_coverage_status'),row.get('complete_valid_feature_sessions'),flush=True)
    c.rollback()
    folder=root/'results/research_cohort';folder.mkdir(parents=True,exist_ok=True)
    write_rows(folder,'event_cohort',cohort);write_rows(folder,'pre_event_features',daily)
    qualified=[r for r in cohort if r['cohort_status']=='price_qualified']
    manifest=dict(source_snapshot=str(source.relative_to(root)),source_as_of='2026-11-05',
                  calendar_source='data/calendar/manifest.json',
                  candidate_count=len(cohort),cohort_status_counts=dict(Counter(r['cohort_status'] for r in cohort)),
                  price_qualified_count=len(qualified),volume_filter=False,
                  option_coverage_counts=dict(Counter(r['option_coverage_status'] for r in qualified)),
                  daily_observations=len(daily),training_ready_events=0,
                  notes=['Nonexhaustive, enforcement-enriched event sample; not a population estimate.',
                         'Price qualification does not imply completed corporate-action or first-public-disclosure review.',
                         'No source-series selection or future option activity enters features.',
                         'Open interest is diagnostic only until vendor publication timing is verified.',
                         'No rows does not prove no listed options. Background labels are not yet available.',
                         'No model, false-positive/false-negative rate, or trading return is estimated.'])
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lines=['# Price-only M&A cohort and option coverage','',
           f"From {len(cohort)} dated candidates, {len(qualified)} have reviewed target/event dates and session timing and a stock close increase of at least 15%. Volume is not an eligibility condition.",'',
           '| Target | Announcement | Return | Observed pre-event sessions / 30 | Valid 20-session-baseline feature days |',
           '| --- | --- | ---: | ---: | ---: |']
    for r in qualified:
        lines.append(f"| {r['symbol']} | {r['announcement_date']} | {r['close_return_pct']:.2f}% | {r.get('observed_observation_sessions','query failed')} | {r.get('complete_valid_feature_sessions','query failed')} |")
    lines+=['','These are descriptive candidates, not final training labels. First public disclosure, corporate actions, historical security identity, and wider event coverage still require review. Missing volume-baseline stock sessions do not prevent price-only qualification when consecutive reaction prices exist.',
            '', 'Daily features use the immediately preceding 20 calendar trading sessions; gaps invalidate the baseline. Observed zero OTM volume is preserved. No event-day or future option rows are used. The next-session close is a conservative timing proxy, not an executable fill assumption.',
            '', 'The sample was selected using future outcomes and is enriched with SEC cases. It cannot estimate population false positives, false negatives, precision, or profitability. All training labels remain null.','']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps(manifest,indent=2),flush=True)
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path('.'))
    args=parser.parse_args()
    with connection() as c:run(c,args.root)


if __name__=='__main__':main()
