"""Audit stockquote session counts before using it as a historical universe."""
from collections import Counter
from datetime import date
import json
from pathlib import Path
import statistics

from research_cohort import write_rows
from sec_match import connection
from market_calendar import sessions


def classify(calendar,counts):
    rows=[]
    for i,day in enumerate(calendar):
        count=counts.get(day,0)
        history=[counts.get(d,0) for d in calendar[max(0,i-20):i]]
        baseline=statistics.median(history) if len(history)==20 else None
        ratio=count/baseline if baseline else None
        rows.append(dict(qdate=day,stockquote_rows=count,prior20_median_rows=baseline,
                         count_ratio_to_prior20_median=ratio,
                         status='missing_session' if not count else
                           ('sparse_session' if count<100 or (ratio is not None and ratio<0.25) else 'present'),
                         # Screening diagnostic, not proof that other dates are complete.
                         diagnostic_minimum_symbols=100))
    return rows


def run(c,root=Path('.'),cutoff=date(2026,11,4)):
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        calendar=sessions('2013-01-01',cutoff,root=root)
        q.execute("SELECT qdate,COUNT(*) AS n FROM stockquote WHERE qdate BETWEEN '2013-01-01' AND %s GROUP BY qdate ORDER BY qdate",(cutoff,))
        counts={r['qdate']:r['n'] for r in q.fetchall()}
    c.rollback()
    rows=classify(calendar,counts)
    years=[]
    for year in sorted(set(d.year for d in calendar)):
        subset=[r for r in rows if r['qdate'].year==year]
        values=[r['stockquote_rows'] for r in subset]
        years.append(dict(year=year,expected_sessions=len(subset),
                          status_counts=dict(Counter(r['status'] for r in subset)),
                          min_rows=min(values),median_rows=statistics.median(values),max_rows=max(values)))
    folder=root/'results/stock_coverage';folder.mkdir(parents=True,exist_ok=True)
    write_rows(folder,'session_counts',rows)
    manifest=dict(cutoff=str(cutoff),calendar_source='data/calendar/manifest.json',years=years,
                  missing_dates=[str(r['qdate']) for r in rows if r['status']=='missing_session'],
                  sparse_dates=[str(r['qdate']) for r in rows if r['status']=='sparse_session'],
                  noncalendar_quote_dates=[str(d) for d in counts if d not in set(calendar)],
                  notes=['Counts measure source presence, not a verified list of public common stocks or listed options.',
                         'Sparse means fewer than 100 rows or below 25% of prior 20-session median; heuristic diagnostic only.',
                         'Do not silently remove sparse dates and claim full-period performance. Coverage regimes require investigation.'])
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lines=['# Historical stockquote coverage','',
           'Calendar-session counts through '+str(cutoff)+'. A present session is not necessarily complete. Sparse-session flags are diagnostics, not validated completeness thresholds.','',
           '| Year | Expected sessions | Missing | Sparse | Median rows | Minimum rows | Maximum rows |',
           '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in years:
        lines.append(f"| {r['year']} | {r['expected_sessions']} | {r['status_counts'].get('missing_session',0)} | {r['status_counts'].get('sparse_session',0)} | {r['median_rows']} | {r['min_rows']} | {r['max_rows']} |")
    lines+=['','The background sampling frame inherits these coverage defects. Its weights describe observed stockquote records and cannot repair omitted securities. Instrument classification, historical listings, and data-source changes remain unverified. Missing/sparse dates are listed in manifest.json; all counts are retained in session_counts.csv.','']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    print(json.dumps(years,indent=2),flush=True)
    return manifest


if __name__=='__main__':
    with connection() as c:run(c)
