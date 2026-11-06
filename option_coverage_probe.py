"""Bounded read-only checks of saved samples in both option tables.

Control symbols diagnose date presence only; they do not establish completeness.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path

import pymysql

from research_cohort import write_rows
from sec_match import connection


TABLES = ('optiondaily', 'optiondaily3')
CONTROLS = ('AAPL', 'MSFT', 'SPY')


def probes(observations, start_year):
    requested = {}
    for row in observations:
        if int(row['qdate'][:4]) >= start_year:
            requested[row['symbol'], row['qdate']] = 'sample'
    for day in sorted({day for _, day in requested}):
        for symbol in CONTROLS:
            key = symbol, day
            requested[key] = 'sample_and_control' if key in requested else 'control'
    return requested


def run(c, root=Path('.'), start_year=2024):
    source = root / 'results/background_sample'
    observations = json.loads((source / 'observations.json').read_text())
    frames = {r['qdate']: r for r in json.loads((source / 'sampling_frames.json').read_text())}
    rows = []
    try:
        with c.cursor() as q:
            q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
            q.execute('START TRANSACTION READ ONLY')
            for (symbol, day), role in sorted(probes(observations, start_year).items()):
                row = dict(symbol=symbol, qdate=day, role=role)
                for table in TABLES:
                    try:
                        q.execute(f'SELECT 1 AS present FROM {table} '
                                  'WHERE underlying=%s AND qdate=%s LIMIT 1', (symbol, day))
                        row[table] = 'present' if q.fetchone() else 'absent'
                    except pymysql.MySQLError as exc:
                        row[table] = 'query_failed'
                        row[table + '_error'] = str(exc)
                rows.append(row)
    finally:
        c.rollback()
    groups = defaultdict(list)
    for row in rows:
        groups[row['qdate']].append(row)
    summary = []
    for day, group in sorted(groups.items()):
        sample = [r for r in group if r['role'] != 'control']
        controls = [r for r in group if r['role'] != 'sample']
        summary.append(dict(qdate=day, stockquote_symbols=frames[day]['stockquote_symbols'],
                            sampled_symbols=len(sample),
                            primary_present=sum(r['optiondaily'] == 'present' for r in sample),
                            alternate_present=sum(r['optiondaily3'] == 'present' for r in sample),
                            alternate_only=sum(r['optiondaily'] == 'absent' and
                                               r['optiondaily3'] == 'present' for r in sample),
                            absent_both=sum(all(r[t] == 'absent' for t in TABLES) for r in sample),
                            query_failures=sum(any(r[t] == 'query_failed' for t in TABLES) for r in group),
                            primary_controls_present=sum(r['optiondaily'] == 'present' for r in controls),
                            controls_checked=len(controls)))
    folder = root / 'results/option_coverage_probe'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'symbol_checks', rows)
    write_rows(folder, 'date_summary', summary)
    lines = ['# Option coverage probe', '',
             'Read-only exact-symbol/date presence checks in both option tables. '
             'Controls are AAPL, MSFT, and SPY. Presence does not prove a complete chain; '
             'absence does not establish unlisted options or resolve ticker aliases.', '',
             '| Date | Stockquote symbols | Sample | Primary | Alternate | Alternate only | Absent both | Query failures | Primary controls |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in summary:
        lines.append('| ' + ' | '.join(str(r[k]) for k in (
            'qdate', 'stockquote_symbols', 'sampled_symbols', 'primary_present',
            'alternate_present', 'alternate_only', 'absent_both', 'query_failures')) +
            f" | {r['primary_controls_present']}/{r['controls_checked']} |")
    lines += ['', 'These checks retain the original outcome-independent sample. '
              'They do not filter missing symbols out of the universe or assign negative labels. '
              'Historical listing and instrument classification remain separate review tasks.', '']
    if summary and all(r['primary_controls_present'] == r['controls_checked']
                       and not r['query_failures'] for r in summary):
        lines += ['All control checks found primary-table data on every probed date. '
                  'This rules out total primary-table absence on those dates, but not '
                  'partial ingestion or symbol-specific gaps. Compare the stockquote '
                  'frame sizes before interpreting cross-year option coverage.', '']
    (folder / 'REPORT.md').write_text('\n'.join(lines))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--start-year', type=int, default=2024)
    args = parser.parse_args()
    with connection() as c:
        print(json.dumps(run(c, start_year=args.start_year), indent=2))


if __name__ == '__main__':
    main()
