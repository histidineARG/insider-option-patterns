"""Load a versioned NYSE calendar snapshot; audit legacy database sessions."""
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
START='2012-01-01'
END='2026-12-31'
CARTER_SOURCE='https://ir.theice.com/press/news-details/2024/The-New-York-Stock-Exchange-Will-Close-Markets-on-January-9-to-Honor-the-Passing-of-Former-President-Jimmy-Carter-on-National-Day-of-Mourning/default.aspx'


def sessions(start='2012-01-01',end='2026-11-05',root=ROOT):
    first=date.fromisoformat(str(start));last=date.fromisoformat(str(end))
    manifest=json.loads((root/'data/calendar/manifest.json').read_text())
    if first<date.fromisoformat(manifest['start']) or last>date.fromisoformat(manifest['end']) or first>last:
        raise ValueError('Requested range is outside the versioned calendar snapshot')
    content=(root/'data/calendar/nyse_sessions.json').read_bytes()
    if hashlib.sha256(content).hexdigest()!=manifest['sha256']:
        raise ValueError('Calendar snapshot checksum mismatch')
    return [date.fromisoformat(r['session']) for r in json.loads(content) if first<=date.fromisoformat(r['session'])<=last]


def refresh(root=ROOT):
    # Optional regeneration dependency. Consumers use only the saved JSON.
    import pandas_market_calendars as mcal
    schedule=mcal.get_calendar('NYSE').schedule(start_date=START,end_date=END)
    rows=[dict(session=str(d.date()),market_open_utc=str(r['market_open']),market_close_utc=str(r['market_close']))
          for d,r in schedule.iterrows() if str(d.date())!='2025-01-09']
    folder=root/'data/calendar';folder.mkdir(parents=True,exist_ok=True)
    content=(json.dumps(rows,indent=2)+'\n').encode()
    (folder/'nyse_sessions.json').write_bytes(content)
    manifest=dict(calendar='NYSE',start=START,end=END,generator='pandas_market_calendars',
                  generator_version=mcal.__version__,session_count=len(rows),
                  sha256=hashlib.sha256(content).hexdigest(),
                  explicit_closures=[dict(date='2025-01-09',reason='Jimmy Carter national day of mourning',source=CARTER_SOURCE)],
                  sources=['https://www.nyse.com/trade/hours-calendars',
                           'https://pandas-market-calendars.readthedocs.io/en/latest/usage.html'],
                  generated_as_of='2026-11-05',
                  notes=['Versioned research calendar, not a guarantee against future unscheduled closures.',
                         'Generator 4.4.0 omits the January 9, 2025 closure; explicit removal is idempotent.'])
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def audit(c,root=ROOT):
    expected=set(sessions(root=root))
    with c.cursor() as q:
        q.execute("SELECT tradingday FROM tradingday WHERE tradingday BETWEEN %s AND %s ORDER BY tradingday",('2012-01-01','2026-11-05'))
        actual=set(r['tradingday'] for r in q.fetchall())
    c.rollback()
    output=dict(database_max_session=str(max(actual)),expected_session_counts_by_year=dict(Counter(d.year for d in expected)),
                database_dates_not_exchange_sessions=sorted(str(d) for d in actual-expected),
                exchange_sessions_missing_from_database=sorted(str(d) for d in expected-actual),
                database_table_modified=False)
    folder=root/'results/stock_coverage';folder.mkdir(parents=True,exist_ok=True)
    (folder/'legacy_calendar_audit.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2),flush=True)
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh',action='store_true')
    args=parser.parse_args()
    if args.refresh:print(json.dumps(refresh(),indent=2))
    else:
        from sec_match import connection
        with connection() as c:audit(c)
