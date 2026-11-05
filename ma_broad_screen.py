"""Find price-action leads across every mapped issuer in the SEC merger inventory."""
from bisect import bisect_left, bisect_right
import csv
from datetime import date, timedelta
import json
from pathlib import Path
import re
import statistics

from sec_match import connection


def scan(c, root=Path('.'), minimum_return=0.10, filing_lag_days=180):
    source=root/'data/m_and_a/sec_filing_search/merger_filings_2013_2026.csv'
    filings=list(csv.DictReader(source.open()))
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        q.execute('SELECT symbol,cik FROM cik2symbol')
        mapping={}
        for r in q.fetchall():mapping.setdefault(int(r['cik']),set()).add(r['symbol'].strip().upper())
        q.execute("SELECT tradingday FROM tradingday WHERE tradingday BETWEEN '2012-01-01' AND '2026-11-05' ORDER BY tradingday")
        calendar=[r['tradingday'] for r in q.fetchall()]
        previous={b:a for a,b in zip(calendar,calendar[1:])}
        by_symbol={}
        for f in filings:
            if f['form'].endswith('/A'):continue
            symbols=set(mapping.get(int(f['cik']),set()))
            for text in re.findall(r'\(([^()]+)\)',f['display_names']):
                for token in re.split(r'[,; ]+',text):
                    if re.fullmatch(r'[A-Z][A-Z0-9.\-]{0,9}',token) and token!='CIK':symbols.add(token)
            for symbol in symbols:by_symbol.setdefault(symbol,[]).append(f)
        output=[];symbols_with_quotes=0
        for i,(symbol,docs) in enumerate(sorted(by_symbol.items())):
            docs=sorted(docs,key=lambda f:f['filing_date'])
            dates=[date.fromisoformat(f['filing_date']) for f in docs]
            start=max(date(2013,1,1),dates[0]-timedelta(days=filing_lag_days+35))
            q.execute('SELECT qdate,close,volume FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s ORDER BY qdate',
                      (symbol,start,dates[-1]))
            quotes=q.fetchall()
            if quotes:symbols_with_quotes+=1
            for j,current in enumerate(quotes[1:],start=1):
                prior=quotes[j-1]
                if prior['close']<=0 or current['close']<=0:continue
                change=float(current['close']/prior['close']-1)
                if change<minimum_return:continue
                if previous.get(current['qdate'])!=prior['qdate']:continue
                lo=bisect_left(dates,current['qdate'])
                hi=bisect_right(dates,current['qdate']+timedelta(days=filing_lag_days))
                relevant=docs[lo:hi]
                if not relevant:continue
                # Group a symbol/date once; all source references remain attached.
                distinct={f['source_url']:f for f in relevant}
                relevant=list(distinct.values())
                history=quotes[max(0,j-20):j]
                mean=statistics.mean(int(r['volume']) for r in history) if len(history)==20 else None
                output.append(dict(symbol=symbol,reaction_date=str(current['qdate']),
                    previous_date=str(prior['qdate']),close_return_pct=change*100,
                    close=float(current['close']),previous_close=float(prior['close']),
                    volume=int(current['volume']),volume_ratio20=int(current['volume'])/mean if mean and mean>0 else None,
                    ciks=sorted(set(f['cik'] for f in relevant)),
                    filer_names=sorted(set(f['display_names'] for f in relevant)),
                    filings=[dict(source_url=f['source_url'],filing_date=f['filing_date'],form=f['form'],cik=f['cik'],accession=f['accession']) for f in relevant],
                    event_confirmation='unverified_price_action_lead',target_public_at_announcement=None,
                    target_was_acquired=None))
            if (i+1)%100==0:print('Symbols checked',i+1,'/',len(by_symbol),'price-action leads',len(output),flush=True)
    c.rollback()
    folder=root/'results/ma_broad_screen';folder.mkdir(parents=True,exist_ok=True)
    (folder/'price_action_leads.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    fields=['symbol','reaction_date','previous_date','close_return_pct','close','previous_close','volume','volume_ratio20','ciks','filer_names','event_confirmation','target_public_at_announcement','target_was_acquired']
    with (folder/'price_action_leads.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader()
        for row in output:
            row=dict(row,ciks=';'.join(row['ciks']),filer_names=';'.join(row['filer_names']))
            writer.writerow(row)
    manifest=dict(symbols_considered=len(by_symbol),symbols_with_quotes=symbols_with_quotes,
                  price_action_leads=len(output),at_least_15pct=sum(r['close_return_pct']>=15 for r in output),
                  minimum_return_pct=minimum_return*100,maximum_filing_lag_days=filing_lag_days,
                  volume_filter=False,notes=[
                    'These are discovery leads, not confirmed M&A events.',
                    'CIK-symbol mapping is an undated local snapshot supplemented by SEC display tickers.',
                    'Only mapped issuers and observed consecutive-session stockquote rows are screened.',
                    'The price threshold chooses documents to verify; it must not define the complete event registry.',
                    'A merger filing after a price jump does not establish the jump was caused by that transaction.'
                  ])
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2),flush=True)
    return output


if __name__=='__main__':
    with connection() as c:scan(c)
