"""M&A announcement table from EDGAR, 2022-01-01 through 2026-11-12.

Forms: 8-K Item 1.01 whose text matches a merger agreement, SC TO-T, SC TO-I,
SC 14D9, DEFM14A, PREM14A, and 425. The earliest filing for a symbol inside
seven calendar days is the deal. An acceptance after the close maps to the
next session.
"""
from __future__ import annotations

import csv
import json
import re
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import requests

from edgar_earnings_calendar import extract_item_202_rows, pad_cik, sec_user_agent
from price_jump_examine import parse_acceptance, reaction_session_with_meta

ENDPOINT = 'https://efts.sec.gov/LATEST/search-index'
SUBMISSIONS = 'https://data.sec.gov/submissions'
START = date(2022, 1, 1)
END = date(2026, 11, 12)
GAP_DAYS = 7
PAUSE = 0.15
EARNINGS_FROM = date(2022, 1, 4)

FAMILIES = (
    dict(name='proxy', forms='DEFM14A,PREM14A'),
    dict(name='sc14d9', forms='SC 14D9'),
    dict(name='tot', forms='SC TO-T'),
    dict(name='toi', forms='SC TO-I'),
    dict(name='form425', forms='425'),
    dict(name='eightk_merger', forms='8-K', q='"merger agreement"', items='1.01'),
    dict(name='eightk_plan', forms='8-K', q='"plan of merger"', items='1.01'),
    dict(name='eightk_bca', forms='8-K', q='"business combination agreement"', items='1.01'),
)

_CIK_TAIL = re.compile(r'\(CIK\s+(\d+)\)\s*$', re.I)
_TICKER_TAIL = re.compile(r'\(([^)]+)\)\s*$')
_TICKER = re.compile(r'^[A-Z][A-Z0-9.\-]{0,9}$')
_SUFFIXES = ('WS', 'RT', 'W', 'U', 'R')


def parse_display_name(text: str) -> dict | None:
    cik_match = _CIK_TAIL.search(text.strip())
    if not cik_match:
        return None
    head = text[:cik_match.start()].strip()
    tickers = []
    ticker_match = _TICKER_TAIL.search(head)
    if ticker_match:
        raw = ticker_match.group(1)
        parts = [part.strip() for part in raw.split(',')]
        if parts and all(_TICKER.match(part.strip().upper()) and part.strip() == part.strip().upper() for part in parts):
            tickers = [part.strip().upper() for part in parts]
            head = head[:ticker_match.start()].strip()
    return dict(name=head, cik=cik_match.group(1).zfill(10), tickers=tickers)


def base_form(form: str) -> str:
    text = (form or '').upper().strip()
    return text[:-2] if text.endswith('/A') else text


def has_item_101(items) -> bool:
    if items is None:
        return False
    if isinstance(items, str):
        items = [part.strip() for part in items.split(',')]
    return any(str(item).strip() == '1.01' for item in items)


def assign_parties(form: str, display_names: list[str]) -> dict:
    parties = [parsed for name in display_names or [] if (parsed := parse_display_name(name))]
    target = parties[0] if parties else None
    other = parties[1] if len(parties) > 1 else None
    kind = base_form(form)
    if kind == 'SC TO-T':
        role = 'tender_target'
    elif kind == 'SC TO-I':
        role = 'issuer_tender'
        other = None
    elif kind in ('DEFM14A', 'PREM14A'):
        role = 'proxy_target'
    elif kind == 'SC 14D9':
        role = 'recommendation_target'
    elif kind == '8-K':
        role = 'agreement_party'
    else:
        role = 'communication_party'
    return dict(target=target, acquirer=other, form_role=role)


def prefer_common(tickers: list[str]) -> list[str]:
    ordered = []
    for ticker in tickers:
        text = ticker.strip().upper()
        if text and text not in ordered:
            ordered.append(text)
    bases = set(ordered)
    drop = set()
    for ticker in ordered:
        for suffix in _SUFFIXES:
            if ticker.endswith(suffix) and ticker[: -len(suffix)] in bases:
                drop.add(ticker)
                break
    kept = [ticker for ticker in ordered if ticker not in drop]
    return kept or ordered


def choose_symbols(party: dict | None, ticker_by_cik: dict, local_by_cik: dict) -> list[str]:
    if not party:
        return []
    found = list(party.get('tickers') or [])
    cik = party.get('cik')
    if not found and cik in ticker_by_cik:
        found.append(ticker_by_cik[cik])
    if not found:
        found.extend(local_by_cik.get(cik, []))
    return prefer_common(found)


def keep_filing(source: dict, family: str) -> bool:
    form = base_form(source.get('form') or '')
    if family.startswith('eightk'):
        return form == '8-K' and has_item_101(source.get('items'))
    return True


def earliest_deals(rows: list[dict], gap_days: int = GAP_DAYS) -> list[dict]:
    usable = [row for row in rows if row.get('symbol') and row.get('qdate')]
    usable.sort(key=lambda row: (row['symbol'], row['qdate'], row.get('acceptance_datetime') or '', row.get('file_date') or ''))
    kept = []
    for row in usable:
        if (kept and kept[-1]['symbol'] == row['symbol']
                and (row['qdate'] - kept[-1]['qdate']).days <= gap_days):
            also = kept[-1].setdefault('also_accessions', [])
            if row['accession'] not in also and row['accession'] != kept[-1]['accession']:
                also.append(row['accession'])
            continue
        kept.append(dict(row, also_accessions=list(row.get('also_accessions') or [])))
    return kept


def announcement_session(acceptance: str | None, file_date: str, session_meta: dict) -> tuple[date | None, str]:
    if acceptance:
        try:
            day = reaction_session_with_meta(parse_acceptance(acceptance), session_meta)
        except ValueError:
            day = None
        if day:
            return day, 'acceptance'
    filed = date.fromisoformat(file_date[:10])
    if filed in session_meta:
        return filed, 'file_date_only'
    for day in sorted(session_meta):
        if day > filed:
            return day, 'file_date_only'
    return None, 'unmapped'


def filing_url(cik: str, accession: str) -> str:
    return (
        f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/'
        f'{accession.replace("-", "")}/{accession}-index.html'
    )


def hit_row(hit: dict, family: str, ticker_by_cik: dict, local_by_cik: dict) -> dict | None:
    source = hit.get('_source') or hit
    if not keep_filing(source, family):
        return None
    parties = assign_parties(source.get('form') or '', source.get('display_names') or [])
    target = parties['target']
    symbols = choose_symbols(target, ticker_by_cik, local_by_cik)
    acquirer = parties['acquirer']
    cik = (target or {}).get('cik') or ''
    accession = source.get('adsh') or ''
    return dict(
        symbol=symbols[0] if symbols else '',
        symbol_candidates=symbols,
        cik=cik,
        issuer_name=(target or {}).get('name') or '',
        acquirer_name=(acquirer or {}).get('name') or '',
        acquirer_cik=(acquirer or {}).get('cik') or '',
        acquirer_tickers=prefer_common((acquirer or {}).get('tickers') or []),
        form=source.get('form') or '',
        form_role=parties['form_role'],
        accession=accession,
        file_date=source.get('file_date') or '',
        items=source.get('items') or [],
        family=family,
        source_url=filing_url(cik, accession) if cik and accession else '',
    )


def _session() -> requests.Session:
    http = requests.Session()
    http.headers['User-Agent'] = sec_user_agent()
    http.headers['Accept'] = 'application/json'
    return http


def _get(http: requests.Session, url: str, params: dict | None = None) -> requests.Response:
    last = None
    for attempt in range(4):
        response = http.get(url, params=params, timeout=90)
        if response.status_code in (429, 500, 502, 503):
            last = response
            time.sleep(PAUSE * (attempt + 2))
            continue
        response.raise_for_status()
        time.sleep(PAUSE)
        return response
    last.raise_for_status()
    raise RuntimeError('unreachable')


def _year_windows(start: date, end: date) -> list[tuple[date, date]]:
    windows = []
    year = start.year
    while year <= end.year:
        lo = max(start, date(year, 1, 1))
        hi = min(end, date(year, 12, 31))
        windows.append((lo, hi))
        year += 1
    return windows


def fetch_search(root: Path, http: requests.Session | None = None) -> list[dict]:
    http = http or _session()
    raw_dir = root / 'data' / 'edgar_deals' / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)
    coverage = []
    pending = [(family, lo, hi) for family in FAMILIES for lo, hi in _year_windows(START, END)]
    while pending:
        family, lo, hi = pending.pop(0)
        name = f"{family['name']}_{lo.isoformat()}_{hi.isoformat()}"
        done = raw_dir / f'{name}.done'
        path = raw_dir / f'{name}.jsonl'
        if done.exists():
            coverage.append(json.loads(done.read_text()))
            continue
        params = dict(dateRange='custom', startdt=lo.isoformat(), enddt=hi.isoformat(),
                      forms=family['forms'], size=100)
        if family.get('q'):
            params['q'] = family['q']
        if family.get('items'):
            params['items'] = family['items']
        try:
            probe = _get(http, ENDPOINT, dict(params, size=1))
        except requests.HTTPError:
            if lo >= hi:
                raise
            mid = lo + timedelta(days=(hi - lo).days // 2)
            pending[:0] = [(family, lo, mid), (family, mid + timedelta(days=1), hi)]
            continue
        payload = probe.json()
        total = payload['hits']['total']
        if total['relation'] != 'eq':
            if lo >= hi:
                raise RuntimeError(f'SEC window cannot be split: {name} {total}')
            mid = lo + timedelta(days=(hi - lo).days // 2)
            pending[:0] = [(family, lo, mid), (family, mid + timedelta(days=1), hi)]
            continue
        expected = total['value']
        lines = []
        offset = 0
        while offset < expected:
            page = _get(http, ENDPOINT, dict(params, **{'from': offset}))
            body = page.json()
            if body.get('timed_out'):
                raise RuntimeError(f'timed out {name} offset {offset}')
            hits = body['hits']['hits']
            if not hits:
                raise RuntimeError(f'empty page {name} offset {offset}')
            for hit in hits:
                lines.append(json.dumps(dict(
                    family=family['name'], startdt=lo.isoformat(), enddt=hi.isoformat(),
                    hit_id=hit.get('_id'), source=hit.get('_source'),
                )))
            offset += len(hits)
        path.write_text('\n'.join(lines) + ('\n' if lines else ''))
        record = dict(family=family['name'], start=lo.isoformat(), end=hi.isoformat(),
                      expected=expected, retrieved=len(lines))
        done.write_text(json.dumps(record) + '\n')
        coverage.append(record)
        print(f"fetched {name} {len(lines)}", flush=True)
    return coverage


def load_hits(root: Path) -> list[dict]:
    rows = []
    for path in sorted((root / 'data' / 'edgar_deals' / 'raw').glob('*.jsonl')):
        for line in path.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_ticker_map(path: Path) -> dict:
    payload = json.loads(path.read_text())
    mapping = {}
    values = payload.values() if isinstance(payload, dict) else payload
    for row in values:
        if not isinstance(row, dict) or 'cik_str' not in row:
            continue
        mapping[str(int(row['cik_str'])).zfill(10)] = str(row['ticker']).upper()
    return mapping


def download_tickers(root: Path, http: requests.Session) -> dict:
    path = root / 'data' / 'edgar_deals' / 'company_tickers.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 1000:
        return load_ticker_map(path)
    try:
        response = _get(http, 'https://www.sec.gov/files/company_tickers.json')
    except requests.HTTPError as exc:
        print(f'company_tickers unavailable: {exc.response.status_code}', flush=True)
        return {}
    path.write_text(response.text if response.text.endswith('\n') else response.text + '\n')
    return load_ticker_map(path)


def _index_block(block: dict) -> dict:
    found = {}
    accessions = block.get('accessionNumber') or []
    for i, accession in enumerate(accessions):
        found[accession] = dict(
            accession=accession,
            form=(block.get('form') or [''])[i],
            filing_date=(block.get('filingDate') or [''])[i],
            acceptance_datetime=(block.get('acceptanceDateTime') or [''])[i],
            items=(block.get('items') or [''] * len(accessions))[i],
            report_date=((block.get('reportDate') or [None] * len(accessions))[i] or None),
            primary_document=((block.get('primaryDocument') or [None] * len(accessions))[i]),
        )
    return found


def fetch_submission(http: requests.Session, cik: str, cache: Path) -> dict:
    cache.mkdir(parents=True, exist_ok=True)
    root_path = cache / f'{cik}.json'
    if root_path.exists():
        payload = json.loads(root_path.read_text())
    else:
        response = _get(http, f'{SUBMISSIONS}/CIK{cik}.json')
        payload = response.json()
        root_path.write_text(json.dumps(payload) + '\n')
    indexed = _index_block(payload.get('filings', {}).get('recent', {}))
    oldest = min((row['filing_date'] for row in indexed.values() if row['filing_date']), default='')
    need_archive = (not oldest) or oldest > EARNINGS_FROM.isoformat()
    for archive in payload.get('filings', {}).get('files') or []:
        name = archive.get('name')
        if not name or not need_archive:
            continue
        archive_path = cache / name.replace('/', '_')
        if archive_path.exists():
            archived = json.loads(archive_path.read_text())
        else:
            try:
                archived = _get(http, f'{SUBMISSIONS}/{name}').json()
            except requests.HTTPError:
                continue
            archive_path.write_text(json.dumps(archived) + '\n')
        indexed.update(_index_block(archived))
        dates = [row['filing_date'] for row in indexed.values() if row['filing_date']]
        if dates and min(dates) <= EARNINGS_FROM.isoformat():
            need_archive = False
    payload['_indexed'] = indexed
    return payload


def earnings_from_index(cik: str, issuer: str, tickers: list[str], indexed: dict, session_meta: dict) -> list[dict]:
    block = dict(
        form=[row['form'] for row in indexed.values()],
        items=[row['items'] for row in indexed.values()],
        filingDate=[row['filing_date'] for row in indexed.values()],
        acceptanceDateTime=[row['acceptance_datetime'] for row in indexed.values()],
        reportDate=[row['report_date'] for row in indexed.values()],
        accessionNumber=[row['accession'] for row in indexed.values()],
        primaryDocument=[row['primary_document'] for row in indexed.values()],
    )
    rows = []
    for row in extract_item_202_rows(block):
        session, basis = announcement_session(row['acceptance_datetime'], row['filing_date'], session_meta)
        if session is None or session < EARNINGS_FROM or session > END:
            continue
        rows.append(dict(
            symbol=tickers[0] if tickers else '',
            symbol_candidates=tickers,
            cik=cik,
            issuer_name=issuer,
            form=row['form'],
            items=row['items'],
            accession=row['accession'],
            filing_date=row['filing_date'],
            acceptance_datetime=row['acceptance_datetime'],
            reaction_session=session.isoformat(),
            session_basis=basis,
            source=f'{SUBMISSIONS}/CIK{cik}.json',
        ))
    return rows


def build_table(root: Path, ticker_by_cik: dict, local_by_cik: dict, session_meta: dict,
                acceptance_by_accession: dict) -> list[dict]:
    seen = set()
    filings = []
    for hit in load_hits(root):
        row = hit_row(dict(_source=hit.get('source'), _id=hit.get('hit_id')), hit.get('family') or '',
                      ticker_by_cik, local_by_cik)
        if row is None or not row['accession'] or row['accession'] in seen:
            continue
        seen.add(row['accession'])
        stamp = acceptance_by_accession.get(row['accession'])
        row['acceptance_datetime'] = stamp or ''
        session, basis = announcement_session(stamp, row['file_date'], session_meta)
        row['qdate'] = session
        row['session_basis'] = basis
        filings.append(row)
    deals = earliest_deals(filings)
    for row in deals:
        row['qdate'] = row['qdate'].isoformat()
        row['also_accessions'] = row.get('also_accessions') or []
    return deals


def write_outputs(root: Path, deals: list[dict], earnings: list[dict], coverage: list[dict]) -> None:
    folder = root / 'data' / 'edgar_deals'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'announcements.json').write_text(json.dumps(deals, indent=2) + '\n')
    fields = ['symbol', 'cik', 'issuer_name', 'acquirer_name', 'acquirer_cik', 'form', 'form_role',
              'accession', 'file_date', 'acceptance_datetime', 'qdate', 'session_basis', 'family',
              'source_url', 'also_accessions']
    with (folder / 'announcements.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for row in deals:
            out = dict(row)
            out['also_accessions'] = ' '.join(row.get('also_accessions') or [])
            writer.writerow(out)
    (folder / 'earnings_8k_2022_2026.json').write_text(json.dumps(earnings, indent=2) + '\n')
    mapped = [row for row in deals if row.get('symbol')]
    target_roles = {'proxy_target', 'recommendation_target', 'tender_target'}
    target_rows = [row for row in mapped if row['form_role'] in target_roles]
    provenance = dict(
        retrieved_at=date.today().isoformat(),
        endpoint=ENDPOINT,
        through=END.isoformat(),
        user_agent_source='SEC_USER_AGENT or edgar_earnings_calendar.DEFAULT_SEC_USER_AGENT',
        forms=[family['forms'] for family in FAMILIES],
        coverage=coverage,
        deals=len(deals),
        with_symbol=len(mapped),
        target_side_with_symbol=len(target_rows),
        earnings_rows=len(earnings),
        limitations=[
            '8-K rows are Item 1.01 filings whose text matched a merger-agreement phrase. The filer may be the buyer or the target.',
            'SC TO-T uses the first display name as the subject company and the second as the bidder.',
            'SC TO-I is an issuer self-tender, kept because it was requested, and marked issuer_tender.',
            'Ticker mapping uses the EDGAR display ticker, then company_tickers.json, then the local cik2symbol snapshot.',
            'A display name with no ticker and no company_tickers entry stays unmapped. Private targets are expected to be unmapped.',
            'Acceptance time comes from the submissions API. file_date_only means that stamp was missing.',
            'Full submissions JSON stays in data/edgar_deals/submissions and is not the committed extract.',
        ],
    )
    (folder / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(json.dumps({key: provenance[key] for key in ('deals', 'with_symbol', 'target_side_with_symbol', 'earnings_rows')}, indent=2), flush=True)


def main():
    root = Path('.')
    http = _session()
    coverage = fetch_search(root, http)
    tickers = download_tickers(root, http)
    from price_jump_examine import load_session_meta
    from insider_resolved import connect
    session_meta = load_session_meta(root)
    local = {}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT symbol, cik FROM cik2symbol WHERE cik IS NOT NULL')
            for row in cursor.fetchall():
                local.setdefault(str(int(row['cik'])).zfill(10), []).append(row['symbol'].upper())
    finally:
        connection.close()
    # First pass on file dates so submissions are fetched for mapped CIKs only.
    provisional = []
    seen = set()
    for hit in load_hits(root):
        row = hit_row(dict(_source=hit.get('source')), hit.get('family') or '', tickers, local)
        if row is None or not row['accession'] or row['accession'] in seen or not row['symbol']:
            if row and row['accession']:
                seen.add(row['accession'])
            continue
        seen.add(row['accession'])
        row['qdate'] = date.fromisoformat(row['file_date'][:10]) if row['file_date'] else None
        row['acceptance_datetime'] = ''
        provisional.append(row)
    seeds = earliest_deals([row for row in provisional if row.get('qdate')])
    ciks = sorted({row['cik'] for row in seeds if row.get('cik')})
    cache = root / 'data' / 'edgar_deals' / 'submissions'
    acceptance = {}
    earnings = []
    for n, cik in enumerate(ciks, start=1):
        try:
            payload = fetch_submission(http, cik, cache)
        except requests.HTTPError as exc:
            print(f'submission failed {cik} {exc}', flush=True)
            continue
        indexed = payload.get('_indexed') or {}
        acceptance.update({key: value['acceptance_datetime'] for key, value in indexed.items()})
        party_tickers = []
        issuer = payload.get('name') or ''
        for ticker in payload.get('tickers') or []:
            party_tickers.append(str(ticker).upper())
        earnings.extend(earnings_from_index(cik, issuer, prefer_common(party_tickers) or party_tickers, indexed, session_meta))
        if n % 100 == 0:
            print(f'submissions {n}/{len(ciks)}', flush=True)
    deals = build_table(root, tickers, local, session_meta, acceptance)
    # Earnings symbols prefer the deal symbol when the CIK maps to one.
    by_cik = {}
    for row in deals:
        if row.get('cik') and row.get('symbol'):
            by_cik.setdefault(row['cik'], row['symbol'])
    for row in earnings:
        if row['cik'] in by_cik:
            row['symbol'] = by_cik[row['cik']]
    write_outputs(root, deals, earnings, coverage)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
