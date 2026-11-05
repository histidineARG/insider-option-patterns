"""Persist the M&A inventory and evidence in dedicated research_ma_* tables."""
import csv
import hashlib
import json
from pathlib import Path

from ma_stock_confirmation import MA_CASES
from sec_match import connection

SCHEMA=[
'''CREATE TABLE IF NOT EXISTS research_ma_events (
 event_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 event_key VARCHAR(100) NOT NULL UNIQUE,
 target_name VARCHAR(255), acquirer_name VARCHAR(255),
 target_symbol VARCHAR(31), acquirer_symbol VARCHAR(31),
 announcement_date DATE, announcement_session VARCHAR(32),
 completion_date DATE, termination_date DATE,
 deal_status VARCHAR(32) NOT NULL DEFAULT 'candidate',
 target_public_at_announcement BOOLEAN NULL,
 target_was_acquired BOOLEAN NULL,
 event_verified BOOLEAN NOT NULL DEFAULT FALSE,
 review_status VARCHAR(32) NOT NULL DEFAULT 'needs_review',
 metadata JSON NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 INDEX ix_research_ma_symbol_date(target_symbol,announcement_date),
 INDEX ix_research_ma_status(deal_status,target_public_at_announcement)
) ENGINE=InnoDB''',
'''CREATE TABLE IF NOT EXISTS research_ma_sources (
 source_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
 event_id BIGINT UNSIGNED NOT NULL,
 evidence_key CHAR(64) NOT NULL UNIQUE,
 source_url TEXT NOT NULL, source_role VARCHAR(64) NOT NULL,
 evidence JSON NOT NULL,
 FOREIGN KEY(event_id) REFERENCES research_ma_events(event_id)
) ENGINE=InnoDB''',
'''CREATE TABLE IF NOT EXISTS research_ma_filings (
 filing_key CHAR(64) NOT NULL PRIMARY KEY,
 cik VARCHAR(10) NOT NULL, accession VARCHAR(31) NOT NULL,
 document_name VARCHAR(255), form VARCHAR(31), filing_date DATE,
 source_url TEXT NOT NULL, metadata JSON NOT NULL,
 event_id BIGINT UNSIGNED NULL,
 INDEX ix_research_ma_cik_date(cik,filing_date),
 FOREIGN KEY(event_id) REFERENCES research_ma_events(event_id)
) ENGINE=InnoDB''',
'''CREATE TABLE IF NOT EXISTS research_ma_discovery_records (
 record_key CHAR(64) NOT NULL PRIMARY KEY,
 source_dataset VARCHAR(100) NOT NULL, source_record_id VARCHAR(255) NOT NULL,
 metadata JSON NOT NULL, event_id BIGINT UNSIGNED NULL,
 FOREIGN KEY(event_id) REFERENCES research_ma_events(event_id)
) ENGINE=InnoDB''',
'''CREATE TABLE IF NOT EXISTS research_ma_price_leads (
 lead_key CHAR(64) NOT NULL PRIMARY KEY, symbol VARCHAR(31) NOT NULL,
 reaction_date DATE NOT NULL, close_return_pct DOUBLE,
 volume_ratio20 DOUBLE NULL, event_confirmation VARCHAR(64) NOT NULL,
 metadata JSON NOT NULL, event_id BIGINT UNSIGNED NULL,
 INDEX ix_research_ma_lead_symbol_date(symbol,reaction_date),
 FOREIGN KEY(event_id) REFERENCES research_ma_events(event_id)
) ENGINE=InnoDB''',
'''CREATE OR REPLACE VIEW research_ma_public_company_acquisitions AS
 SELECT *, CASE WHEN target_public_at_announcement=1 AND target_was_acquired=1
 THEN 1 WHEN target_public_at_announcement=0 OR target_was_acquired=0 THEN 0
 ELSE NULL END AS completed_public_company_acquisition
 FROM research_ma_events'''
]


def digest(text):return hashlib.sha256(text.encode()).hexdigest()


def dump(value):return json.dumps(value,default=str,allow_nan=False)


def add_source(q,event_id,url,role,evidence):
    key=digest(str(event_id)+'|'+role+'|'+url)
    q.execute('''INSERT INTO research_ma_sources(event_id,evidence_key,source_url,source_role,evidence)
                 VALUES(%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE evidence=VALUES(evidence)''',
              (event_id,key,url,role,dump(evidence)))


def upsert(q,key,row):
    fields=['event_key','target_name','acquirer_name','target_symbol','acquirer_symbol',
            'announcement_date','announcement_session','completion_date','termination_date',
            'deal_status','target_public_at_announcement','target_was_acquired','event_verified','review_status','metadata']
    row=dict(row,event_key=key,metadata=dump(row.get('metadata',{})))
    q.execute('''INSERT INTO research_ma_events ('''+','.join(fields)+''') VALUES ('''+','.join(['%s']*len(fields))+''')
                 ON DUPLICATE KEY UPDATE event_id=LAST_INSERT_ID(event_id)''',tuple(row.get(f) for f in fields))
    return q.lastrowid


def ingest(c,root=Path('.')):
    with c.cursor() as q:
        for statement in SCHEMA:q.execute(statement)
    c.commit()
    with c.cursor() as q:
        # Every local source row is retained, including missing dates and private/divisional deals.
        local=list(csv.DictReader((root/'data/m_and_a/local_maevent_all.csv').open()))
        for r in local:
            symbol=r['symbol'].strip().upper() or None
            event_id=upsert(q,'local_maevent:'+r['maid'],dict(target_name=r['acquiree'],
                acquirer_name=r['acquirer'],target_symbol=symbol,announcement_date=r['announcedate'] or None,
                announcement_session='unknown',deal_status='candidate',target_public_at_announcement=None,
                target_was_acquired=None,event_verified=False,review_status='needs_review',metadata=r))
            add_source(q,event_id,'optiondb.maevent/'+r['maid'],'local_discovery',r)
        reviewed=json.loads((root/'data/m_and_a/reviewed_event_examples.json').read_text())['events']
        additions=root/'data/m_and_a/additional_reviewed_events.json'
        if additions.exists():reviewed+=json.loads(additions.read_text())['events']
        for r in reviewed:
            status=r['outcome'] if r['outcome'] in ['completed','terminated'] else 'announced'
            event_id=upsert(q,'reviewed:'+r['id'],dict(target_name=r['target'],acquirer_name=r['acquirer'],
                target_symbol=r['target_symbol'],acquirer_symbol=r['acquirer_symbol'],
                announcement_date=r['definitive_announcement_date'],announcement_session=r.get('announcement_session','unknown'),
                completion_date=r.get('outcome_effective_date') if status=='completed' else None,
                termination_date=(r.get('outcome_effective_date') or r.get('outcome_announcement_date')) if status=='terminated' else None,
                deal_status=status,target_public_at_announcement=True,
                target_was_acquired=True if status=='completed' else (False if status=='terminated' else None),
                event_verified=True,review_status='source_reviewed',metadata=r))
            add_source(q,event_id,r['announcement_source'],'announcement',r)
            if r.get('outcome_source'):add_source(q,event_id,r['outcome_source'],'outcome',r)
        for r in json.loads((root/'data/sec_cases.json').read_text())['cases']:
            if r['id'] not in MA_CASES:continue
            event_id=upsert(q,'sec_case:'+r['id'],dict(target_name=r['issuer'],target_symbol=r['symbol'],
                announcement_date=r['event_date'],announcement_session=r['announcement_session'],
                deal_status='announced',target_public_at_announcement=True,target_was_acquired=None,
                event_verified=r['event_date_verified'],review_status='source_reviewed',metadata=r))
            add_source(q,event_id,r['source_url'],'case_event_evidence',r)
        timing=root/'data/m_and_a/announcement_timing_reviews.json'
        if timing.exists():
            for review in json.loads(timing.read_text())['reviews']:
                q.execute('''SELECT event_id FROM research_ma_events WHERE target_symbol=%s
                             AND announcement_date=%s AND event_verified=1''',
                          (review['symbol'],review['announcement_date']))
                for match in q.fetchall():
                    q.execute('''UPDATE research_ma_events SET announcement_session=%s
                                 WHERE event_id=%s AND (announcement_session IS NULL OR announcement_session='unknown')''',
                              (review['announcement_session'],match['event_id']))
                    add_source(q,match['event_id'],review['announcement_timing_source'],'announcement_timing',review)
        # Retain filing evidence separately; a filing is not automatically a distinct deal.
        for r in csv.DictReader((root/'data/m_and_a/sec_filing_search/merger_filings_2013_2026.csv').open()):
            key=digest(r['cik']+'|'+r['accession']+'|'+r['document'])
            q.execute('''INSERT INTO research_ma_filings(filing_key,cik,accession,document_name,form,filing_date,source_url,metadata)
                       VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE metadata=VALUES(metadata)''',
                      (key,r['cik'],r['accession'],r['document'],r['form'],r['filing_date'],r['source_url'],dump(r)))
        for r in csv.DictReader((root/'data/m_and_a/edgar_candidates_enriched_all.csv').open()):
            key=digest('open_edgar_candidates|'+r['cik'])
            q.execute('''INSERT INTO research_ma_discovery_records(record_key,source_dataset,source_record_id,metadata)
                       VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE metadata=VALUES(metadata)''',
                      (key,'open_edgar_candidates',r['cik'],dump(r)))
        leads=root/'results/ma_broad_screen/price_action_leads.json'
        if leads.exists():
            for r in json.loads(leads.read_text()):
                key=digest(r['symbol']+'|'+r['reaction_date'])
                q.execute('''INSERT INTO research_ma_price_leads(lead_key,symbol,reaction_date,close_return_pct,volume_ratio20,event_confirmation,metadata)
                           VALUES(%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE metadata=VALUES(metadata),
                           close_return_pct=VALUES(close_return_pct),volume_ratio20=VALUES(volume_ratio20)''',
                          (key,r['symbol'],r['reaction_date'],r['close_return_pct'],r['volume_ratio20'],r['event_confirmation'],dump(r)))
    c.commit()
    stats={}
    with c.cursor() as q:
        for t in ['research_ma_events','research_ma_sources','research_ma_filings','research_ma_discovery_records','research_ma_price_leads']:
            q.execute('SELECT COUNT(*) AS n FROM '+t);stats[t]=q.fetchone()['n']
        q.execute('SELECT deal_status,COUNT(*) AS n FROM research_ma_events GROUP BY deal_status');stats['event_statuses']=q.fetchall()
        q.execute('SELECT COUNT(*) AS n FROM research_ma_public_company_acquisitions WHERE completed_public_company_acquisition=1')
        stats['verified_completed_public_acquisitions']=q.fetchone()['n']
    output=root/'results/ma_registry';output.mkdir(parents=True,exist_ok=True)
    (output/'ingest_summary.json').write_text(dump(stats)+'\n')
    print(json.dumps(stats,indent=2),flush=True)
    return stats


if __name__=='__main__':
    with connection() as c:ingest(c)
