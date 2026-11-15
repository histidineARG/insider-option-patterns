"""M&A-news pool for 2013–2026, confirmed by the stock path.

A headline enters only when that symbol's own close on the announcement,
divided by the close ten sessions earlier, is at least 15%, or the
announcement session itself is at least 15%. One close-to-close is not the
test. Same-symbol rows within 7 days are one event.

News coverage is not the same as price coverage. takeover ends 2021-08-21,
news ends 2022-07-25, and research_ma_events is sparse after that.
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

from insider_resolved import connect, load_sessions

MIN_RETURN = 0.15
LOOKBACK = 10
GAP_DAYS = 7
DEAL_SQL = '''
  (title LIKE '%to acquire%' OR title LIKE '%to be acquired%'
   OR title LIKE '%merger agreement%' OR title LIKE '%agreed to acquire%'
   OR title LIKE '%agrees to acquire%' OR title LIKE '%definitive agreement%'
   OR title LIKE '%takeover%' OR title LIKE '%buyout%'
   OR title LIKE '%acquire %')
  AND title NOT LIKE '%acquires % shares%'
  AND title NOT LIKE '%acquires new%'
  AND title NOT LIKE '%acquires stake%'
  AND title NOT LIKE '%buys new position%'
  AND title NOT LIKE '%shareholder alert%'
  AND title NOT LIKE '%law firm%'
  AND title NOT LIKE '%plaintiff%'
  AND title NOT LIKE '%investigation%'
'''


def path_return(stock, sessions, index, day):
    """Return (reaction, path). Path uses the close ten sessions before the day."""
    if day not in index or index[day] < LOOKBACK or day not in stock:
        return None, None
    previous = sessions[index[day] - 1]
    base = sessions[index[day] - LOOKBACK]
    if previous not in stock or base not in stock or not stock[previous] or not stock[base] or not stock[day]:
        return None, None
    reaction = stock[day] / stock[previous] - 1
    path = stock[day] / stock[base] - 1
    return reaction, path


def cluster(rows):
    rows = sorted(rows, key=lambda row: (row['symbol'], row['qdate']))
    kept = []
    for row in rows:
        if (kept and kept[-1]['symbol'] == row['symbol']
                and (row['qdate'] - kept[-1]['qdate']).days <= GAP_DAYS):
            kept[-1]['sources'] = sorted(set(kept[-1]['sources']) | set(row['sources']))
            if row['path'] > kept[-1]['path']:
                kept[-1]['path'] = row['path']
                kept[-1]['reaction'] = row['reaction']
                kept[-1]['title'] = row['title']
                kept[-1]['qdate'] = row['qdate']
            continue
        kept.append(dict(row))
    return kept


def fetch_table(connection, sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


def collect(connection, root: Path):
    rows = []
    for row in fetch_table(connection, f'''
          SELECT TRIM(symbol) symbol, pdate qdate, title FROM takeover
          WHERE pdate >= '2013-01-01' AND pdate < '2022-01-01'
            AND symbol IS NOT NULL AND TRIM(symbol) <> '' AND {DEAL_SQL}
        '''):
        rows.append(dict(symbol=row['symbol'].upper(), qdate=row['qdate'],
                         title=row['title'] or '', sources=['takeover']))
    for row in fetch_table(connection, f'''
          SELECT TRIM(symbol) symbol, pdate qdate, title FROM news
          WHERE pdate >= '2013-01-01' AND symbol IS NOT NULL AND TRIM(symbol) <> '' AND {DEAL_SQL}
        '''):
        rows.append(dict(symbol=row['symbol'].upper(), qdate=row['qdate'],
                         title=row['title'] or '', sources=['news']))
    for row in fetch_table(connection, '''
          SELECT TRIM(symbol) symbol, announcedate qdate,
                 CONCAT(acquirer, ' / ', acquiree) title
          FROM maevent
          WHERE announcedate >= '2013-01-01' AND symbol IS NOT NULL AND TRIM(symbol) <> ''
        '''):
        rows.append(dict(symbol=row['symbol'].upper(), qdate=row['qdate'],
                         title=row['title'] or '', sources=['maevent']))
    for row in fetch_table(connection, '''
          SELECT TRIM(target_symbol) symbol, announcement_date qdate,
                 CONCAT(IFNULL(acquirer_name,''), ' / ', IFNULL(target_name,'')) title
          FROM research_ma_events
          WHERE announcement_date >= '2013-01-01'
            AND target_symbol IS NOT NULL AND TRIM(target_symbol) <> ''
        '''):
        rows.append(dict(symbol=row['symbol'].upper(), qdate=row['qdate'],
                         title=row['title'] or '', sources=['research_ma']))
    payload = json.loads((root / 'data/price_jump_news_reviews.json').read_text())
    for row in payload['reviews']:
        if row.get('news_filter') == 'keep' and str(row.get('cause_class', '')).startswith('2_'):
            rows.append(dict(symbol=row['symbol'].upper(), qdate=date.fromisoformat(row['qdate']),
                             title=row.get('detail') or '', sources=['ledger_class2']))
    return [row for row in rows if isinstance(row['qdate'], date)]


def quotes_for(connection, symbol, start, end):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT qdate, close FROM stockquote WHERE symbol=%s AND qdate BETWEEN %s AND %s',
            (symbol, start, end),
        )
        return {row['qdate']: float(row['close']) for row in cursor.fetchall() if row['close']}


def run(root: Path) -> dict:
    sessions = load_sessions(root)
    index = {day: i for i, day in enumerate(sessions)}
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET SESSION MAX_EXECUTION_TIME=300000')
            cursor.execute('START TRANSACTION READ ONLY')
        raw = collect(connection, root)
        print(f'candidate rows {len(raw)}', flush=True)
        by_symbol = {}
        for row in raw:
            by_symbol.setdefault(row['symbol'], []).append(row)
        confirmed = []
        missing = 0
        for n, (symbol, items) in enumerate(by_symbol.items(), start=1):
            start = min(row['qdate'] for row in items) - timedelta(days=20)
            end = max(row['qdate'] for row in items)
            stock = quotes_for(connection, symbol, start, end)
            seen = set()
            for row in items:
                key = (symbol, row['qdate'])
                if key in seen:
                    continue
                seen.add(key)
                reaction, path = path_return(stock, sessions, index, row['qdate'])
                if reaction is None:
                    missing += 1
                    continue
                if path < MIN_RETURN and reaction < MIN_RETURN:
                    continue
                confirmed.append(dict(symbol=symbol, qdate=row['qdate'], title=row['title'],
                                      sources=list(row['sources']), reaction=reaction, path=path))
            if n % 1000 == 0:
                print(f'symbols {n} confirmed days {len(confirmed)}', flush=True)
    finally:
        connection.rollback()
        connection.close()
    merged = {}
    for row in confirmed:
        key = (row['symbol'], row['qdate'])
        current = merged.get(key)
        if current is None:
            merged[key] = row
            continue
        current['sources'] = sorted(set(current['sources']) | set(row['sources']))
        if row['path'] > current['path']:
            current['path'] = row['path']
            current['reaction'] = row['reaction']
            current['title'] = row['title']
    events = []
    for row in cluster(list(merged.values())):
        events.append(dict(
            symbol=row['symbol'], qdate=row['qdate'].isoformat(),
            reaction=round(row['reaction'], 4), path=round(row['path'], 4),
            title=row['title'][:240], sources=row['sources'],
        ))
    by_year = {}
    path_only = 0
    for row in events:
        by_year[row['qdate'][:4]] = by_year.get(row['qdate'][:4], 0) + 1
        if row['path'] >= MIN_RETURN and row['reaction'] < MIN_RETURN:
            path_only += 1
    summary = dict(
        price_coverage='2013-01-02 through 2026-11-12',
        news_coverage='takeover through 2021-08-21; news through 2022-07-25; research_ma sparse through 2024-05-28',
        candidate_rows=len(raw),
        missing_price=missing,
        confirmed_days=len(merged),
        events=len(events),
        path_only_events=path_only,
        by_year=dict(sorted(by_year.items())),
    )
    folder = root / 'results' / 'insider_footprint'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'ma_news_pool.json').write_text(json.dumps(dict(summary=summary, events=events), indent=2) + '\n')
    (folder / 'MA_NEWS_POOL.md').write_text(render(summary))
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def render(summary) -> str:
    lines = [
        '# M&A news pool, 2013–2026',
        '',
        'Prices and options on this machine run from 2013-01-02 through 2026-11-12. Deal headlines do not. `takeover` ends 2021-08-21, `news` ends 2022-07-25, and `research_ma_events` has only a handful of later dates. Years after the headline feeds cannot be screened for M&A news here.',
        '',
        'The 86 class-2 names are the 2013–2016 manual review of one-day jumps. They are included as headlines, not treated as the whole market.',
        '',
        'A headline is kept when that stock’s announcement close is at least 15% above the close ten sessions earlier, or the announcement session itself is at least 15%. The ten-session path is what admits a move that started before the headline. Same-symbol rows within 7 days are one event. `takeover.pct` is not used.',
        '',
        f"Candidate rows: {summary['candidate_rows']}. Dates with no usable close: {summary['missing_price']}. Jump days: {summary['confirmed_days']}. Events: {summary['events']}. Events admitted by the ten-session path whose announcement day itself was under 15%: {summary['path_only_events']}.",
        '',
        '| Year | Events |',
        '| --- | ---: |',
    ]
    for year in [str(y) for y in range(2013, 2027)]:
        lines.append(f"| {year} | {summary['by_year'].get(year, 0)} |")
    lines += [
        '',
        'An event is a deal headline on a symbol whose stock moved. It is not a verified target-only list and not an insider-trading label.',
        '',
    ]
    return '\n'.join(lines)


def main():
    run(Path(os.environ.get('FOOTPRINT_ROOT', '.')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
