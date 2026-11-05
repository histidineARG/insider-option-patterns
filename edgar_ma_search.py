"""Enumerate SEC merger-related filing metadata without treating filing dates as announcements."""
import argparse
import csv
from datetime import date
import hashlib
import json
from pathlib import Path
import time

import requests

FORMS=['PREM14A','DEFM14A','DEFM14C','SC 14D9']
ENDPOINT='https://efts.sec.gov/LATEST/search-index'


def collect(output, start_year=2013, through='2026-11-05'):
    output.mkdir(parents=True,exist_ok=True)
    session=requests.Session()
    session.headers['User-Agent']='InsiderOptionPatterns public SEC metadata research'
    coverage=[]; unique={}; queries=[]
    for year in range(start_year,int(through[:4])+1):
        end=min(f'{year}-12-31',through)
        offset=0; expected=None; yearly={}
        while expected is None or offset<expected:
            params=dict(dateRange='custom',startdt=f'{year}-01-01',enddt=end,
                        forms=','.join(FORMS),size=100,**{'from':offset})
            response=session.get(ENDPOINT,params=params,timeout=60)
            response.raise_for_status(); payload=response.json()
            if payload.get('timed_out') or payload.get('_shards',{}).get('failed',0):
                raise RuntimeError('Incomplete SEC search response')
            total=payload['hits']['total']
            if total['relation']!='eq':raise RuntimeError('SEC total is a lower bound; use smaller date windows')
            if expected is None:expected=total['value']
            elif expected!=total['value']:raise RuntimeError('SEC result count changed during pagination; retry snapshot')
            hits=payload['hits']['hits']
            if not hits and offset<expected:raise RuntimeError('Unexpected empty SEC results page')
            queries.append(dict(url=response.url,total=expected,returned=len(hits)))
            (output/f'page_{year}_{offset:05d}.json').write_text(json.dumps(payload)+'\n')
            for hit in hits:
                yearly[hit['_id']]=hit
            offset+=len(hits)
            time.sleep(0.2)
        if len(yearly)!=expected:raise RuntimeError(f'Duplicate/missing paginated records for {year}')
        unique.update(yearly)
        coverage.append(dict(year=year,expected=expected,retrieved=len(yearly),through=end))
        print(year,'filing documents:',len(yearly),flush=True)
    rows=[]
    for key,hit in unique.items():
        source=hit['_source']; accession=source.get('adsh','')
        name=key.split(':',1)[1] if ':' in key else ''
        for cik in source.get('ciks',[]):
            url=f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-", "")}/{name}'
            rows.append(dict(cik=cik,display_names='; '.join(source.get('display_names',[])),
                             filing_date=source.get('file_date'),form=source.get('form'),
                             accession=accession,document=name,source_url=url,
                             date_kind='filing_date',announcement_date_verified=False,
                             public_target_verified=False,deal_status='unknown'))
    fields=list(rows[0]) if rows else []
    target=output/'merger_filings_2013_2026.csv'
    with target.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    manifest=dict(retrieved_at=date.today().isoformat(),endpoint=ENDPOINT,
                  forms=FORMS,start_year=start_year,through=through,coverage=coverage,
                  documents=len(unique),issuer_document_rows=len(rows),
                  csv_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),queries=queries,
                  limitations=[
                      'Census of returned documents for these four forms and dates, not all public-company M&A deals.',
                      'Announcements may precede filings; abandoned approaches without merger forms are absent.',
                      'Multiple filings and amendments are not independent deals.',
                      'Public-target eligibility, announcement timestamp, acquirer, and outcome are unverified.',
                      'Tender offers, foreign issuers, SPACs, funds and non-M&A proxy matters require classification.',
                      'Additional 8-K/6-K, S-4/F-4, SC TO-T and SC 13E3 evidence is needed for broader coverage.'
                  ])
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('TOTAL',len(unique),'documents;',len(rows),'issuer-document rows',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=Path('data/m_and_a/sec_filing_search'))
    p.add_argument('--start-year',type=int,default=2013)
    p.add_argument('--through',default='2026-11-05')
    args=p.parse_args();collect(args.output,args.start_year,args.through)
