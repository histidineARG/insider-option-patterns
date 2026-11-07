"""Examine ≥15% NYSE-calendar jumps and drop earnings using the EDGAR 8-K 2.02 calendar.

Policy: keep 2 (M&A), 3 (biotech trial), 4 (tech breakthrough); drop 1 (earnings).
Earnings drops are assigned when a jump's reaction session is the first NYSE session
at/after an EDGAR Item 2.02 acceptance datetime (same calendar day before open counts
as that session; after-close acceptance maps to the next session).

Hard filters after earnings (before news): prev_close < $5, ETF/ETN denylist, and
no optiondaily/optiondaily3 presence on qdate.
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

MIN_PREV_CLOSE = 5.0
EXTREME_PRINT_RETURN = 1.0  # 100%+ tagged as mechanical hazard for first news batch
GE50_RETURN = 0.50


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


def load_etf_denylist(root: Path) -> set[str]:
    path = root / 'data/event_review_overrides.json'
    raw = json.loads(path.read_text())
    block = raw.get('etf_etn_denylist') or {}
    return {str(s).strip().upper() for s in (block.get('symbols') or []) if str(s).strip()}


def load_news_reviews(root: Path) -> dict[tuple[str, str], dict]:
    path = root / 'data/price_jump_news_reviews.json'
    if not path.exists():
        return {}
    reviews = json.loads(path.read_text()).get('reviews') or []
    out = {}
    for r in reviews:
        sym = str(r.get('symbol') or '').strip().upper()
        qdate = str(r.get('qdate') or '').strip()
        if sym and qdate:
            out[(sym, qdate)] = r
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


def option_presence_keys(connection, pairs: list[tuple[str, str]]) -> set[tuple[str, str]]:
    """Return (symbol, qdate) keys with at least one row in optiondaily or optiondaily3."""
    present: set[tuple[str, str]] = set()
    if not pairs:
        return present
    # group by date for fewer round-trips
    by_date: dict[str, set[str]] = defaultdict(set)
    for sym, qdate in pairs:
        by_date[qdate].add(sym)
    with connection.cursor() as q:
        q.execute('SET SESSION MAX_EXECUTION_TIME=0')
        q.execute('START TRANSACTION READ ONLY')
        for qdate, symbols in sorted(by_date.items()):
            syms = sorted(symbols)
            # chunk IN lists
            for i in range(0, len(syms), 400):
                chunk = syms[i:i + 400]
                placeholders = ','.join(['%s'] * len(chunk))
                params = list(chunk) + [qdate]
                for table in ('optiondaily', 'optiondaily3'):
                    q.execute(
                        f'SELECT DISTINCT underlying AS symbol FROM {table} '
                        f'WHERE underlying IN ({placeholders}) AND qdate=%s',
                        params,
                    )
                    for r in q.fetchall():
                        present.add((str(r['symbol']).strip().upper(), qdate))
        connection.rollback()
    return present


def apply_hard_filters(rows: list[dict], etf_denylist: set[str],
                       option_present: set[tuple[str, str]] | None = None) -> list[dict]:
    """Apply sub-$5 / ETF / no-option drops to non-earnings rows.

    If option_present is None, skip the no-option gate (used in unit tests).
    """
    out = []
    for row in rows:
        r = dict(row)
        if r.get('news_filter') == 'drop_earnings':
            r['has_option'] = None
            out.append(r)
            continue
        prev_close = float(r.get('prev_close') or 0)
        sym = str(r.get('symbol') or '').strip().upper()
        qdate = str(r.get('qdate') or '')
        if prev_close < MIN_PREV_CLOSE:
            r.update(
                jump_cause=None,
                cause_class='sub_5',
                news_filter='drop_sub_5',
                has_option=None,
            )
            out.append(r)
            continue
        if sym in etf_denylist:
            r.update(
                jump_cause=None,
                cause_class='etf',
                news_filter='drop_etf',
                has_option=None,
            )
            out.append(r)
            continue
        if option_present is not None:
            has_opt = (sym, qdate) in option_present
            r['has_option'] = has_opt
            if not has_opt:
                r.update(
                    jump_cause=None,
                    cause_class='no_option',
                    news_filter='drop_no_option',
                )
                out.append(r)
                continue
        else:
            r['has_option'] = None
        out.append(r)
    return out


def apply_news_reviews(rows: list[dict], reviews: dict[tuple[str, str], dict]) -> list[dict]:
    """Overlay manual news reviews. Earnings drops still win if both present."""
    out = []
    for row in rows:
        r = dict(row)
        if r.get('news_filter') == 'drop_earnings':
            out.append(r)
            continue
        key = (str(r.get('symbol') or '').strip().upper(), str(r.get('qdate') or ''))
        rev = reviews.get(key)
        if not rev:
            out.append(r)
            continue
        r['jump_cause'] = rev.get('jump_cause')
        r['cause_class'] = rev.get('cause_class') or r.get('cause_class')
        r['news_filter'] = rev.get('news_filter') or r.get('news_filter')
        if rev.get('locator'):
            r['news_locator'] = rev['locator']
        if rev.get('detail'):
            r['news_detail'] = rev['detail']
        out.append(r)
    return out


def cohort_symbols(root: Path) -> set[str]:
    path = root / 'results/reviewed_cohort/events.json'
    if not path.exists():
        return set()
    events = json.loads(path.read_text())
    if isinstance(events, dict):
        events = events.get('events') or []
    return {str(e.get('symbol') or '').strip().upper() for e in events if e.get('symbol')}


def build_news_queue(rows: list[dict], root: Path, min_return: float = GE50_RETURN) -> list[dict]:
    cohort = cohort_symbols(root)
    queue = []
    for r in rows:
        if r.get('news_filter') != 'pending_news_review':
            continue
        if not r.get('cik'):
            continue
        if float(r.get('close_return') or 0) < min_return:
            continue
        if r.get('has_option') is False:
            continue
        if float(r.get('prev_close') or 0) < MIN_PREV_CLOSE:
            continue
        hazards = []
        if float(r.get('close_return') or 0) >= EXTREME_PRINT_RETURN:
            hazards.append('hazard_extreme_print')
        queue.append(dict(
            symbol=r['symbol'],
            qdate=r['qdate'],
            cik=r['cik'],
            close_return=r['close_return'],
            prev_close=r['prev_close'],
            close=r['close'],
            has_option=r.get('has_option'),
            hazards=hazards,
            cohort_overlap=r['symbol'] in cohort,
            include_in_first_news_batch='hazard_extreme_print' not in hazards,
        ))
    queue.sort(key=lambda x: (-float(x['close_return']), x['symbol'], x['qdate']))
    return queue


def write_news_queue(root: Path, queue: list[dict], min_return: float = GE50_RETURN,
                     filename: str = 'news_queue_ge50.json') -> Path:
    out = root / 'results/price_jump_examine'
    out.mkdir(parents=True, exist_ok=True)
    first = [r for r in queue if r.get('include_in_first_news_batch')]
    payload = dict(
        as_of=date.today().isoformat(),
        min_close_return=min_return,
        min_prev_close=MIN_PREV_CLOSE,
        n_queue=len(queue),
        n_first_batch=len(first),
        notes=[
            f'Queue requires pending_news_review, mapped CIK, has_option, prev_close>=5, '
            f'close_return>={min_return:.0%}.',
            'hazard_extreme_print (>=100%) excluded from first news batch until EDGAR/news says otherwise.',
        ],
        queue=queue,
        first_batch=first,
    )
    path = out / filename
    path.write_text(json.dumps(payload, indent=2) + '\n')
    return path


def write_outputs(root: Path, rows: list[dict], start: date, end: date) -> dict:
    out = root / 'results/price_jump_examine'
    out.mkdir(parents=True, exist_ok=True)
    stamp = f'{start.isoformat()}_{end.isoformat()}'
    (out / f'jumps_{stamp}.json').write_text(json.dumps(rows, indent=2) + '\n')
    fields = [
        'symbol', 'cik', 'qdate', 'prev_qdate', 'close_return', 'vol_ratio',
        'cause_class', 'jump_cause', 'news_filter', 'has_option',
        'earnings_filing_date', 'earnings_acceptance_datetime', 'earnings_accession',
        'earnings_locator', 'news_locator', 'close', 'prev_close', 'volume', 'prev_volume',
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
        policy=(
            'keep 2,3,4; drop 1 (earnings via EDGAR 8-K Item 2.02); '
            'hard-drop sub_$5, ETF/ETN denylist, no_option'
        ),
        notes=[
            'Jumps are NYSE-calendar consecutive close-to-close with volume ≥2× prior session.',
            'drop_earnings requires a mapped CIK and an Item 2.02 acceptance whose reaction session equals qdate.',
            'drop_sub_5 uses prev_close < $5; drop_etf uses data/event_review_overrides.json etf_etn_denylist.',
            'drop_no_option requires absence from both optiondaily and optiondaily3 on qdate.',
            'Manual reviews in data/price_jump_news_reviews.json overlay pending rows; earnings still wins.',
            'Unclassified pending rows still need news review for classes 2/3/4.',
        ],
    )
    (out / f'manifest_{stamp}.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = [
        f'# Price-jump examine {start} → {end}',
        '',
        'Policy: **keep 2/3/4**, **drop 1** (EDGAR 8-K Item 2.02), plus hard drops '
        '**sub-$5 / ETF / no-option**.',
        '',
        f"Jumps (≥15%, vol≥2×): **{len(rows)}**. With CIK map: **{with_cik}**.",
        f"Cause counts: {counts}.",
        f"Filter counts: {filter_counts}.",
        '',
        'Pending rows still need news review for keep classes 2/3/4.',
        '',
    ]
    (out / f'REPORT_{stamp}.md').write_text('\n'.join(lines))
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


def classify_rows(root: Path, jumps: list[dict], cik_by_symbol: dict[str, str],
                  connection=None, fetch_earnings: bool = True, pause: float = 0.12) -> list[dict]:
    session_meta = load_session_meta(root)
    ciks = sorted({cik_by_symbol[j['symbol']] for j in jumps if j['symbol'] in cik_by_symbol})
    if fetch_earnings and ciks:
        ensure_earnings_for_ciks(root, ciks, pause=pause)
    earnings = load_earnings(root)
    if not earnings and (root / 'results/edgar_earnings_calendar/by_cik').exists():
        ensure_earnings_for_ciks(root, ciks, pause=pause)
        earnings = load_earnings(root)
    rows = match_earnings(jumps, earnings, session_meta, cik_by_symbol)
    etf = load_etf_denylist(root)
    # option presence only for rows that would otherwise stay pending after price/ETF gates
    need_opt = [
        (r['symbol'], r['qdate']) for r in rows
        if r.get('news_filter') == 'pending_news_review'
        and float(r.get('prev_close') or 0) >= MIN_PREV_CLOSE
        and r['symbol'] not in etf
    ]
    option_present = None
    if connection is not None:
        option_present = option_presence_keys(connection, need_opt)
    rows = apply_hard_filters(rows, etf, option_present)
    rows = apply_news_reviews(rows, load_news_reviews(root))
    return rows


def raw_jumps_from_classified(rows: list[dict]) -> list[dict]:
    keys = ('symbol', 'qdate', 'prev_qdate', 'close', 'prev_close', 'close_return',
            'volume', 'prev_volume', 'vol_ratio')
    return [{k: r[k] for k in keys if k in r} for r in rows]


def run(root: Path, start: date, end: date, pause: float = 0.12,
        fetch_earnings: bool = True) -> dict:
    calendar = sessions(root)
    with db_connect() as connection:
        cik_by_symbol = load_cik2symbol(connection)
        jumps = extract_jumps(connection, calendar, start, end)
        rows = classify_rows(
            root, jumps, cik_by_symbol, connection=connection,
            fetch_earnings=fetch_earnings, pause=pause,
        )
    return write_outputs(root, rows, start, end)


def refresh_windows(root: Path, windows: list[tuple[date, date]], pause: float = 0.12,
                    fetch_earnings: bool = False) -> dict:
    """Re-classify existing jump artifacts with hard filters + news overlay."""
    all_rows: list[dict] = []
    manifests = []
    with db_connect() as connection:
        cik_by_symbol = load_cik2symbol(connection)
        for start, end in windows:
            stamp = f'{start.isoformat()}_{end.isoformat()}'
            path = root / 'results/price_jump_examine' / f'jumps_{stamp}.json'
            if not path.exists():
                raise FileNotFoundError(path)
            existing = json.loads(path.read_text())
            jumps = raw_jumps_from_classified(existing)
            rows = classify_rows(
                root, jumps, cik_by_symbol, connection=connection,
                fetch_earnings=fetch_earnings, pause=pause,
            )
            manifests.append(write_outputs(root, rows, start, end))
            all_rows.extend(rows)
    queue50 = build_news_queue(all_rows, root, min_return=GE50_RETURN)
    write_news_queue(root, queue50, min_return=GE50_RETURN, filename='news_queue_ge50.json')
    queue30 = build_news_queue(all_rows, root, min_return=0.30)
    # ge30 first batch excludes rows already covered by ge50 reviews when pending cleared;
    # still include extreme hazards but flag them.
    write_news_queue(root, queue30, min_return=0.30, filename='news_queue_ge30.json')
    summary = dict(
        windows=[dict(start=s.isoformat(), end=e.isoformat()) for s, e in windows],
        n_jumps=len(all_rows),
        news_filter_counts=dict(Counter(r['news_filter'] for r in all_rows)),
        cause_class_counts=dict(Counter(r['cause_class'] for r in all_rows)),
        n_queue_ge50=len(queue50),
        n_first_batch_ge50=sum(1 for r in queue50 if r.get('include_in_first_news_batch')),
        n_queue_ge30=len(queue30),
        n_first_batch_ge30=sum(1 for r in queue30 if r.get('include_in_first_news_batch')),
        manifests=manifests,
    )
    (root / 'results/price_jump_examine/refresh_summary.json').write_text(
        json.dumps(summary, indent=2) + '\n')
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--start', help='YYYY-MM-DD')
    p.add_argument('--end', help='YYYY-MM-DD')
    p.add_argument('--pause', type=float, default=0.12)
    p.add_argument('--skip-earnings-fetch', action='store_true')
    p.add_argument(
        '--refresh-2013-2016',
        action='store_true',
        help='Re-classify existing 2013-2016 jump artifacts with hard filters + reviews',
    )
    args = p.parse_args(argv)
    root = Path('.')
    if args.refresh_2013_2016:
        windows = [
            (date(2013, 1, 2), date(2014, 12, 31)),
            (date(2015, 1, 2), date(2015, 12, 31)),
            (date(2016, 1, 4), date(2016, 12, 30)),
        ]
        summary = refresh_windows(
            root, windows, pause=args.pause,
            fetch_earnings=not args.skip_earnings_fetch,
        )
        print(json.dumps(summary, indent=2))
        return
    if not args.start or not args.end:
        p.error('--start/--end required unless --refresh-2013-2016')
    manifest = run(
        root,
        date.fromisoformat(args.start),
        date.fromisoformat(args.end),
        pause=args.pause,
        fetch_earnings=not args.skip_earnings_fetch,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
