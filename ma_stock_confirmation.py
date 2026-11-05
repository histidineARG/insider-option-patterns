"""Confirm stock price/volume reactions for dated M&A target candidates."""
import argparse
import csv
from datetime import date, timedelta
import json
from pathlib import Path
import statistics

from sec_match import connection

MA_CASES={'heinz_2013','onyx_2013','concur_2014','kraft_2015','adt_2016',
          'joy_2016','stillwater_2016','ceb_2017','gci_2017','bioverativ_2018',
          'efii_2019','audentes_2019','virtusa_2020','odp_2021','coherent_2021',
          'greensky_2021','zogenix_2022','maxar_2022','kaman_2024','calliditas_2024'}
LOCAL_EXCLUSIONS={
    'KKR':'Symbol is associated with a seller/owner, not acquired Oriental Brewery.',
    'AAN':'Acquired RIMCO business unit, not the public parent.',
    'EME':'Local entry has questionable target identity; requires role verification.',
    'DE':'Landscapes business divestiture, not public parent acquisition.',
    'JEC':'Local entry has questionable target/acquirer roles.',
    'VRSK':'Interthinx business divestiture, not public parent acquisition.',
    'CTAS':'Document shredding business divestiture.',
    'TYC':'ADT Korea business divestiture.',
    'NWPX':'OCTG business divestiture.',
    'ADM':'Fertilizer distribution business divestiture.',
    'ENG':'Gulf Coast operations divestiture.',
    'AROS':'Historical public-target security identity unverified.',
    'WDC':'Minority investment candidate, not whole-company acquisition.',
    'GWPH':'No acquirer specified; event type requires verification.',
    'EW':'No acquirer specified; event type requires verification.'}


def candidates(root):
    rows=[]
    for r in csv.DictReader((root/'data/m_and_a/local_maevent_all.csv').open()):
        symbol=r['symbol'].strip().upper()
        if not symbol or not r['announcedate'] or r['announcedate']<'2013-01-01':continue
        rows.append(dict(symbol=symbol,announcement_date=r['announcedate'],
                         issuer=r['acquiree'],source='optiondb.maevent:'+r['maid'],
                         announcement_session='unknown',date_verified=False,
                         eligibility='excluded' if symbol in LOCAL_EXCLUSIONS else 'candidate',
                         exclusion_reason=LOCAL_EXCLUSIONS.get(symbol,'')))
    for r in json.loads((root/'data/sec_cases.json').read_text())['cases']:
        if r['id'] not in MA_CASES or not r['event_date_verified']:continue
        rows.append(dict(symbol=r['symbol'],announcement_date=r['event_date'],
                         issuer=r['issuer'],source=r['source_url'],
                         announcement_session=r['announcement_session'],date_verified=True,
                         timing_source=r.get('announcement_timing_source',''),
                         eligibility='target_evidence_reviewed',exclusion_reason=''))
    for r in json.loads((root/'data/m_and_a/reviewed_event_examples.json').read_text())['events']:
        rows.append(dict(symbol=r['target_symbol'],announcement_date=r['definitive_announcement_date'],
                         issuer=r['target'],source=r['announcement_source'],
                         announcement_session=r.get('announcement_session','unknown'),
                         timing_source=r.get('announcement_timing_source',''),
                         date_verified=True,eligibility='target_evidence_reviewed',exclusion_reason=''))
    # Prefer reviewed source metadata for the same symbol/date; retain all source references.
    merged={}
    for r in rows:
        key=r['symbol'],r['announcement_date']
        if key in merged:
            previous=merged[key]
            sources=previous['source']+'; '+r['source']
            if r['date_verified']:merged[key]=r
            merged[key]['source']=sources
        else:merged[key]=r
    return sorted(merged.values(),key=lambda r:(r['announcement_date'],r['symbol']))


def measure(quotes, reaction, previous_session, expected_baseline, volume_multiple):
    by_date={r['qdate']:r for r in quotes}
    current=by_date.get(reaction); previous=by_date.get(previous_session)
    result=dict(reaction_date=str(reaction),previous_session=str(previous_session),
                market_screen_pass=False,status='missing_reaction_quote')
    if current is None:return result
    if previous is None:return dict(result,status='missing_previous_session_quote')
    history=[by_date[d] for d in expected_baseline if d in by_date]
    result['baseline_sessions']=len(history)
    result['missing_baseline_dates']=';'.join(str(d) for d in expected_baseline if d not in by_date)
    result.update(previous_close=float(previous['close']),reaction_close=float(current['close']),
                  reaction_volume=int(current['volume']),previous_volume=int(previous['volume']))
    if previous['close']<=0 or current['close']<=0 or current['volume']<=0:
        return dict(result,status='invalid_price_or_volume')
    result['close_return_pct']=float((current['close']/previous['close']-1)*100)
    result['open_gap_pct']=float((current['open']/previous['close']-1)*100)
    result['high_return_pct']=float((current['high']/previous['close']-1)*100)
    result['price_jump_at_least_15pct']=current['close']*100 >= previous['close']*115
    result['volume_vs_previous']=int(current['volume'])/int(previous['volume']) if previous['volume']>0 else None
    if len(history)!=20 or len(expected_baseline)!=20:
        return dict(result,status='incomplete_20_session_baseline')
    if any(r['volume']<=0 for r in history):return dict(result,status='invalid_baseline_volume')
    average=statistics.mean(int(r['volume']) for r in history)
    ratio=int(current['volume'])/average
    result.update(volume_avg20=average,volume_ratio20=ratio,
                  above_max_volume20=int(current['volume'])>max(int(r['volume']) for r in history),
                  volume_surge=ratio>=volume_multiple,status='measured')
    result['market_screen_pass']=bool(result['price_jump_at_least_15pct'] and result['volume_surge'])
    return result


def run(c, root=Path('.'), volume_multiple=2.0):
    rows=candidates(root);results=[]
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        q.execute("SELECT tradingday FROM tradingday WHERE tradingday BETWEEN '2012-01-01' AND '2026-11-05' ORDER BY tradingday")
        calendar=[r['tradingday'] for r in q.fetchall()]
        for case in rows:
            if case['eligibility']=='excluded':
                results.append(dict(case,status='excluded_wrong_role_or_unverified_event',market_screen_pass=False));continue
            event=date.fromisoformat(case['announcement_date'])
            after=case['announcement_session']=='after_close'
            reaction=next((d for d in calendar if d>event or (d==event and not after)),None)
            if reaction is None:
                results.append(dict(case,status='no_calendar_reaction_session',market_screen_pass=False));continue
            index=calendar.index(reaction);baseline=calendar[max(0,index-20):index]
            q.execute('SELECT qdate,open,high,low,close,volume FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s ORDER BY qdate',
                      (case['symbol'],reaction-timedelta(days=75),reaction+timedelta(days=7)))
            quotes=q.fetchall()
            m=measure(quotes,reaction,calendar[index-1],baseline,volume_multiple)
            timed=case['announcement_session'] in ['before_open','intraday','after_close','nontrading_day']
            result=dict(case,**m,volume_threshold=volume_multiple,
                        confirmation='confirmed_price_volume_reaction' if m['market_screen_pass'] and case['date_verified'] and timed else
                            ('market_pass_date_or_timing_review_required' if m['market_screen_pass'] else 'not_confirmed'))
            # Unknown publication time: report next-session reaction separately, never choose the winner.
            if case['announcement_session']=='unknown' and event==reaction and index+1<len(calendar):
                next_reaction=calendar[index+1]
                alternative=measure(quotes,next_reaction,reaction,calendar[max(0,index-19):index+1],volume_multiple)
                result.update(next_session_date=str(next_reaction),
                              next_session_return_pct=alternative.get('close_return_pct'),
                              next_session_volume_ratio20=alternative.get('volume_ratio20'),
                              next_session_screen_pass=alternative['market_screen_pass'])
            results.append(result)
    c.rollback()
    output=root/'results/ma_stock_confirmation';output.mkdir(parents=True,exist_ok=True)
    for name,items in [('all_candidates',results),('price_volume_passes',[r for r in results if r['market_screen_pass']])]:
        (output/(name+'.json')).write_text(json.dumps(items,indent=2,default=str,allow_nan=False)+'\n')
        fields=list(dict.fromkeys(k for r in items for k in r))
        with (output/(name+'.csv')).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(items)
    confirmed=[r for r in results if r.get('confirmation')=='confirmed_price_volume_reaction']
    with (output/'confirmed_targets.csv').open('w',newline='') as f:
        fields=list(dict.fromkeys(k for r in confirmed for k in r))
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(confirmed)
    passed=[r for r in results if r['market_screen_pass']]
    report=['# M&A target stock reaction confirmation','',
            f'Screened {len(results)} dated target candidates from local maevent records, extracted SEC cases and reviewed M&A examples. This does not cover all 9,465 merger filing documents: those filing dates are not verified announcement dates.',
            '',f'**{len(passed)} candidates pass the market screen; {len(confirmed)} also have reviewed announcement dates and session timing.**',
            '', 'Rules: reaction-session close / immediately preceding market-session close − 1 ≥ 15%; reaction-session volume / average volume of the preceding 20 calendar trading sessions ≥ '+str(volume_multiple)+'×. The reaction session is the announcement trading date for pre-open/intraday releases, the next session for after-close releases, and the next session for nontrading-day releases. Current-session volume is excluded from the baseline.',
            '', 'Missing previous quotes or any of the required 20 baseline sessions prevent confirmation. No missing sessions are filled or silently skipped. The historical calendar is optiondb.tradingday. Prices are raw stockquote closes; corporate-action adjustment quality is not independently verified.',
            '', '## Source and timing reviewed passes','',
            '| Target | Announcement date | Reaction session | Close return | Volume / prior 20-session mean |',
            '|---|---|---|---:|---:|']
    for r in confirmed:
        report.append(f"| {r['symbol']} | {r['announcement_date']} | {r['reaction_date']} | {r['close_return_pct']:.2f}% | {r['volume_ratio20']:.2f}× |")
    report.extend(['','## Market passes awaiting date or timing review','',
                   '| Target | Candidate announcement date | Reaction session | Close return | Volume multiple |',
                   '|---|---|---|---:|---:|'])
    for r in passed:
        if r['confirmation']!='confirmed_price_volume_reaction':
            report.append(f"| {r['symbol']} | {r['announcement_date']} | {r['reaction_date']} | {r['close_return_pct']:.2f}% | {r['volume_ratio20']:.2f}× |")
    report.extend(['','## Data issues and exclusions','',
                   'Some local maevent symbols identify a seller, divested business parent, minority investment or unverified event. Their exclusion reasons are retained in all_candidates.csv. Mathematical threshold agreement does not establish that the M&A announcement caused the move, and does not establish insider trading.',
                   '', 'TUMI passes the price/volume screen on March 3, 2016; SEC proxy materials describe public takeover rumors on that date. It remains pending as a definitive-announcement label. Source: https://www.sec.gov/Archives/edgar/data/1535031/000119312516517061/d166077dprem14a.htm',
                   '', 'KAMN on January 19, 2024 rises about 100.85%, but January 8 is missing from its required baseline. CALT on May 28, 2024 rises about 69.27%, but May 1 is missing. Both remain unconfirmed under the strict 20-session volume rule.',
                   '', 'AFOP was announced after close April 7, 2016, so its reaction session is April 8. Audentes/BOLD was announced at 6:01pm EST on December 2, 2019, so its reaction session is December 3. The underlying CSVs preserve timing-source links.',
                   '', 'Outputs: confirmed_targets.csv (strict confirmations); price_volume_passes.csv (all market passes, including unverified timing); all_candidates.csv (all records, failures, exclusions and missing-data diagnostics).',''])
    (output/'REPORT.md').write_text('\n'.join(report))
    for r in results:
        if r['market_screen_pass']:
            print(r['symbol'],r['announcement_date'],f"{r['close_return_pct']:.2f}%",f"{r['volume_ratio20']:.2f}x",r['confirmation'],flush=True)
    print('TOTAL',len(results),'candidates;',sum(r['market_screen_pass'] for r in results),'market passes;',
          sum(r.get('confirmation')=='confirmed_price_volume_reaction' for r in results),'source/timing confirmed',flush=True)
    return results


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--volume-multiple',type=float,default=2.0)
    args=p.parse_args()
    if args.volume_multiple<=0:p.error('Volume multiple must be positive')
    with connection() as c:run(c,volume_multiple=args.volume_multiple)
