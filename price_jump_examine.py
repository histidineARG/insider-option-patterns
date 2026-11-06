"""Examine ≥15% NYSE-calendar jumps and drop earnings using the EDGAR 8-K 2.02 calendar.

Policy: keep 2 (M&A), 3 (biotech trial), 4 (tech breakthrough); drop 1 (earnings).
Earnings drops are assigned when a jump's reaction session is the first NYSE session
at/after an EDGAR Item 2.02 acceptance datetime (same calendar day before open counts
as that session; after-close acceptance maps to the next session).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import pymysql

from edgar_earnings_calendar import pad_cik, run as build_earnings_calendar


def sessions(root: Path) -> list[date]:
    rows = json.loads((root / 'data/calendar/nyse_sessions.json').read_text())
    return [date.fromisoformat(r['session']) for r in rows]


def db_connect():
    password = os.environ.get('OPTIONDB_PASSWORD')
    if password is None:
        raise RuntimeError('OPTIONDB_PASSWORD is required')
    config = dict(
        user=os.environ.get('OPTIONDB_USER') or 'optiondb',
        password=password,
        database=os.environ.get('OPTIONDB_DATABASE', 'optiondb'),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=120,
        autocommit=False,
    )
    if os.environ.get('OPTIONDB_HOST'):
        config['host'] = os.environ['OPTIONDB_HOST']
        config['port'] = int(os.environ.get('OPTIONDB_PORT', '3306'))
    else:
        config['unix_socket'] = os.environ.get('OPTIONDB_SOCKET', '/run/mysqld/mysqld.sock')
    return pymysql.connect(**config)


def load_cik2symbol(connection) -> dict[str, str]:
    with connection.cursor() as q:
        q.execute('SELECT symbol, cik FROM cik2symbol WHERE cik IS NOT NULL')
        out = {}
        for r in q.fetchall():
            sym = (r['symbol'] or '').strip().upper()
            if sym:
                out[sym] = pad_cik(r['cik'])
        return out


def extract_jumps(connection, calendar: list[date], start: date, end: date,
                  min_return: float = 0.15, min_vol_ratio: float = 2.0) -> list[dict]:
    """NYSE-calendar consecutive close-to-close jumps with volume confirmation."""
    idx = {d: i for i, d in enumerate(calendar)}
    days = [d for d in calendar if start <= d <= end]
    jumps = []
    with connection.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=0')
        q.execute('START TRANSACTION READ ONLY')
        for d in days:
            i = idx[d]
            if i == 0:
                continue
            prev = calendar[i - 1]
            q.execute(
                'SELECT a.symbol AS symbol, a.qdate AS qdate, a.close AS close, a.volume AS volume, '
                'b.close AS prev_close, b.volume AS prev_volume, b.qdate AS prev_qdate '
                'FROM stockquote a '
                'JOIN stockquote b ON a.symbol=b.symbol AND b.qdate=%s '
                'WHERE a.qdate=%s AND a.close>0 AND b.close>0 AND b.volume>0 '
                'AND a.close >= b.close * %s AND a.volume >= b.volume * %s',
                (prev, d, 1.0 + min_return, min_vol_ratio),
            )
            for r in q.fetchall():
                prev_close = float(r['prev_close'])
                close = float(r['close'])
                prev_vol = float(r['prev_volume'])
                vol = float(r['volume'])
                jumps.append(dict(
                    symbol=str(r['symbol']).strip().upper(),
                    qdate=r['qdate'].isoformat() if hasattr(r['qdate'], 'isoformat') else str(r['qdate']),
                    prev_qdate=prev.isoformat(),
                    close=close,
                    prev_close=prev_close,
                    close_return=(close / prev_close) - 1.0,
                    volume=vol,
                    prev_volume=prev_vol,
                    vol_ratio=vol / prev_vol if prev_vol else None,
                ))
        connection.rollback()
    return jumps


def parse_acceptance(ts: str) -> datetime:
    # EDGAR stamps look like 2021-01-27T21:30:35.000Z
    text = ts.replace('Z', '+00:00')
    return datetime.fromisoformat(text).astimezone(timezone.utc)


def reaction_session_with_meta(acceptance: datetime, session_meta: dict[date, dict]) -> date | None:
    calendar = sorted(session_meta)
    day = acceptance.date()
    # candidate: same calendar day if session exists and acceptance <= market_close_utc
    if day in session_meta:
        close = datetime.fromisoformat(session_meta[day]['market_close_utc'])
        if acceptance <= close:
            return day
    # else next session strictly after acceptance date, or after close on session day
    for d in calendar:
        if d > day:
            return d
        if d == day:
            continue
    return None


def load_session_meta(root: Path) -> dict[date, dict]:
    rows = json.loads((root / 'data/calendar/nyse_sessions.json').read_text())
    return {date.fromisoformat(r['session']): r for r in rows}


def load_earnings(root: Path) -> list[dict]:
    path = root / 'results/edgar_earnings_calendar/earnings_8k_202.json'
    if not path.exists():
        return []
    return json.loads(path.read_text()).get('filings') or []


def match_earnings(jumps: list[dict], earnings: list[dict], session_meta: dict[date, dict],
                   cik_by_symbol: dict[str, str]) -> list[dict]:
    # map cik -> list of (reaction_session, filing)
    by_cik = defaultdict(list)
    for er in earnings:
        try:
            acc = parse_acceptance(er['acceptance_datetime'])
        except ValueError:
            continue
        react = reaction_session_with_meta(acc, session_meta)
        if react is None:
            continue
        by_cik[er['cik']].append((react, er))

    er_sessions = {cik: {d for d, _ in rows} for cik, rows in by_cik.items()}
    er_detail = {cik: {d: er for d, er in rows} for cik, rows in by_cik.items()}

    out = []
    for jump in jumps:
        row = dict(jump)
        cik = cik_by_symbol.get(jump['symbol'])
        row['cik'] = cik
        q = date.fromisoformat(jump['qdate'])
        if cik and q in er_sessions.get(cik, ()):
            er = er_detail[cik][q]
            row.update(
                jump_cause='earnings',
                cause_class='1_earnings',
                news_filter='drop_earnings',
                earnings_filing_date=er['filing_date'],
                earnings_acceptance_datetime=er['acceptance_datetime'],
                earnings_accession=er['accession'],
                earnings_locator=er['locator'],
                earnings_source=er['source'],
            )
        else:
            row.update(
                jump_cause=None,
                cause_class='unclassified',
                news_filter='pending_news_review',
                earnings_filing_date=None,
                earnings_acceptance_datetime=None,
                earnings_accession=None,
                earnings_locator=None,
                earnings_source=None,
            )
        out.append(row)
    return out


def write_outputs(root: Path, rows: list[dict], start: date, end: date) -> dict:
    out = root / 'results/price_jump_examine'
    out.mkdir(parents=True, exist_ok=True)
    stamp = f'{start.isoformat()}_{end.isoformat()}'
    (out / f'jumps_{stamp}.json').write_text(json.dumps(rows, indent=2) + '\n')
    fields = [
        'symbol', 'cik', 'qdate', 'prev_qdate', 'close_return', 'vol_ratio',
        'cause_class', 'jump_cause', 'news_filter',
        'earnings_filing_date', 'earnings_acceptance_datetime', 'earnings_accession',
        'earnings_locator', 'close', 'prev_close', 'volume', 'prev_volume',
    ]
    with (out / f'jumps_{stamp}.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    counts = dict(Counter(r['cause_class'] for r in rows))
    filter_counts = dict(Counter(r['news_filter'] for r in rows))
    with_cik = sum(1 for r in rows if r.get('cik'))
    manifest = dict(
        start=start.isoformat(),
        end=end.isoformat(),
        n_jumps=len(rows),
        n_with_cik=with_cik,
        cause_class_counts=counts,
        news_filter_counts=filter_counts,
        policy='keep 2,3,4; drop 1 (earnings via EDGAR 8-K Item 2.02)',
        notes=[
            'Jumps are NYSE-calendar consecutive close-to-close with volume ≥2× prior session.',
            'drop_earnings requires a mapped CIK and an Item 2.02 acceptance whose reaction session equals qdate.',
            'Unclassified jumps still need news review for classes 2/3/4; absence of Item 2.02 is not proof of non-earnings.',
        ],
    )
    (out / f'manifest_{stamp}.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = [
        f'# Price-jump examine {start} → {end}',
        '',
        'Policy: **keep 2/3/4**, **drop 1** using EDGAR 8-K Item 2.02 earnings calendar.',
        '',
        f"Jumps (≥15%, vol≥2×): **{len(rows)}**. With CIK map: **{with_cik}**.",
        f"Cause counts: {counts}.",
        f"Filter counts: {filter_counts}.",
        '',
        'Unclassified rows are pending news review (not automatic keeps).',
        '',
    ]
    (out / f'REPORT_{stamp}.md').write_text('\n'.join(lines))
    # also refresh rolling latest pointers
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (out / 'REPORT.md').write_text('\n'.join(lines))
    return manifest


def ensure_earnings_for_ciks(root: Path, ciks: list[str], pause: float) -> None:
    existing = {p.stem for p in (root / 'results/edgar_earnings_calendar/by_cik').glob('*.json')} if (
        root / 'results/edgar_earnings_calendar/by_cik').exists() else set()
    missing = [int(c) for c in ciks if pad_cik(c) not in existing]
    if missing:
        print(f'fetching EDGAR Item 2.02 for {len(missing)} CIKs', flush=True)
        build_earnings_calendar(missing, root=root, pause=pause)
    else:
        # rebuild aggregate from cache
        build_earnings_calendar([int(c) for c in ciks], root=root, pause=pause)


def run(root: Path, start: date, end: date, pause: float = 0.12,
        fetch_earnings: bool = True) -> dict:
    calendar = sessions(root)
    session_meta = load_session_meta(root)
    with db_connect() as connection:
        cik_by_symbol = load_cik2symbol(connection)
        jumps = extract_jumps(connection, calendar, start, end)
    # CIKs for jumped symbols
    ciks = sorted({cik_by_symbol[j['symbol']] for j in jumps if j['symbol'] in cik_by_symbol})
    if fetch_earnings and ciks:
        ensure_earnings_for_ciks(root, ciks, pause=pause)
    earnings = load_earnings(root)
    # If aggregate file is stale relative to cache, rebuild from cache only
    if not earnings and (root / 'results/edgar_earnings_calendar/by_cik').exists():
        ensure_earnings_for_ciks(root, ciks, pause=pause)
        earnings = load_earnings(root)
    rows = match_earnings(jumps, earnings, session_meta, cik_by_symbol)
    return write_outputs(root, rows, start, end)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start', required=True, help='YYYY-MM-DD')
    p.add_argument('--end', required=True, help='YYYY-MM-DD')
    p.add_argument('--pause', type=float, default=0.12)
    p.add_argument('--skip-earnings-fetch', action='store_true')
    args = p.parse_args(argv)
    manifest = run(
        Path('.'),
        date.fromisoformat(args.start),
        date.fromisoformat(args.end),
        pause=args.pause,
        fetch_earnings=not args.skip_earnings_fetch,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
