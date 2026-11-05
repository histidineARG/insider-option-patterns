"""Collect M&A discovery candidates, preserving unverified dates and provenance."""
import argparse
import csv
from datetime import date, timedelta
import hashlib
import io
import json
from pathlib import Path

import requests

from sec_match import connection

DATASET = 'https://huggingface.co/datasets/tcontorno/edgar-ma-deals'


def write_csv(path, rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def collect(c, output):
    output.mkdir(parents=True,exist_ok=True)
    r=requests.get('https://huggingface.co/api/datasets/tcontorno/edgar-ma-deals',timeout=30)
    r.raise_for_status(); revision=r.json()['sha']
    url=f'{DATASET}/resolve/{revision}/edgar_ma_deals_2010_2024.csv'
    r=requests.get(url,timeout=60);r.raise_for_status()
    raw=r.content
    (output/'edgar_candidates_original_2010_2024.csv').write_bytes(raw)
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    metadata=dict(retrieved_at=date.today().isoformat(),dataset_url=DATASET,
                  revision=revision,source_csv=url,sha256=hashlib.sha256(raw).hexdigest(),
                  license='MIT; credit Tyler Contorno, EDGAR M&A Deal Events (2010–2024)',
                  limitations=[
                      'One earliest merger-related filing per CIK, not one row per deal.',
                      'Filing-date proxies can lag actual announcements by weeks.',
                      'Issuer public status, acquirer, deal outcome and actual announcement timestamps need verification.',
                      'Filtering earliest proxy dates at 2013 can omit later deals of issuers first present before 2013.',
                      'Open dataset ends in 2024; no 2025/2026 coverage is implied.',
                      'CIK mapping is a local undated snapshot; ticker reuse and historical validity require review.',
                  ])
    with c.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
        q.execute('START TRANSACTION READ ONLY')
        q.execute('SELECT symbol,cik FROM cik2symbol')
        mapping={}
        for item in q.fetchall():
            mapping.setdefault(int(item['cik']),[]).append(item['symbol'].upper())
        for i,row in enumerate(rows):
            proxy=date.fromisoformat(row['announcement_date_proxy'][:10])
            symbols=sorted(set(mapping.get(int(row['cik']),[])))
            row.update(candidate_symbols=';'.join(symbols),announcement_date_verified=False,
                       public_target_verified=False,deal_status='unknown',source_url=DATASET,
                       candidate_date_kind='earliest_merger_filing_proxy',
                       proxy_since_2013=proxy>=date(2013,1,1),
                       option_data_near_proxy=False,option_symbols_near_proxy='')
            found=[]
            if row['proxy_since_2013']:
                for symbol in symbols:
                    q.execute('SELECT 1 FROM optiondaily WHERE underlying=%s AND qdate BETWEEN %s AND %s LIMIT 1',
                              (symbol,proxy-timedelta(days=180),proxy+timedelta(days=30)))
                    if q.fetchone():found.append(symbol)
            row['option_data_near_proxy']=bool(found)
            row['option_symbols_near_proxy']=';'.join(found)
            if (i+1)%500==0:print('EDGAR candidates checked:',i+1,flush=True)
        # Keep all rows for source audit, including those without dates or symbols.
        q.execute('SELECT * FROM maevent ORDER BY maid')
        local=q.fetchall()
        for row in local:
            row.update(source_table='optiondb.maevent',announcement_date_verified=False,
                       public_target_verified=False,deal_status='unknown',option_data_near_local_date=False)
            day=row['announcedate']
            if day and day>=date(2013,1,1) and row['symbol']:
                q.execute('SELECT 1 FROM optiondaily WHERE underlying=%s AND qdate BETWEEN %s AND %s LIMIT 1',
                          (row['symbol'].upper(),day-timedelta(days=90),day))
                row['option_data_near_local_date']=bool(q.fetchone())
        q.execute("SELECT * FROM mafromnews WHERE qdate>='2013-01-01' ORDER BY qdate,id")
        news=q.fetchall()
    c.rollback()
    subset=[r for r in rows if r['proxy_since_2013']]
    write_csv(output/'edgar_candidates_enriched_all.csv',rows)
    write_csv(output/'edgar_candidates_proxy_since_2013.csv',subset)
    write_csv(output/'local_maevent_all.csv',local)
    write_csv(output/'local_mafromnews_since_2013.csv',news)
    metadata.update(original_rows=len(rows),proxy_since_2013_rows=len(subset),
                    provider_review_flag_true_since_2013=sum(r['passed_review'].lower()=='true' for r in subset),
                    option_coverage_near_proxy=sum(r['option_data_near_proxy'] for r in subset),
                    local_maevent_rows=len(local),local_news_rows=len(news),
                    local_dated_since_2013=sum(bool(r['announcedate'] and r['announcedate']>=date(2013,1,1)) for r in local),
                    local_dated_with_symbol_since_2013=sum(bool(r['announcedate'] and r['announcedate']>=date(2013,1,1) and r['symbol']) for r in local),
                    local_rows_with_option_data=sum(r['option_data_near_local_date'] for r in local))
    (output/'provenance.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata,indent=2),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path('data/m_and_a'))
    args=p.parse_args()
    with connection() as c:collect(c,args.output)


if __name__=='__main__':main()
