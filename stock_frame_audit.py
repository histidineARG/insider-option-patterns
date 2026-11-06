"""Locate a large stockquote frame expansion and audit saved sample membership.

Membership is an exact ticker comparison, never a security classification or label.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from research_cohort import write_rows
from sec_match import connection


def transition(rows):
    ordered = sorted(rows, key=lambda r: r['qdate'])
    for i, row in enumerate(ordered):
        if (i and row['stockquote_rows'] >= 10000 and
                (row.get('prior20_median_rows') or 0) >= 1000 and
                (row.get('count_ratio_to_prior20_median') or 0) >= 2):
            return ordered[i-1]['qdate'], row['qdate']
    raise ValueError('No qualifying frame expansion in saved session counts')


def summarize(observations, baseline, start):
    details = []
    groups = defaultdict(list)
    for row in observations:
        if row['qdate'] < start:
            continue
        item = dict(symbol=row['symbol'], qdate=row['qdate'],
                    baseline_membership='present' if row['symbol'] in baseline else 'absent',
                    chain_observed=bool(row.get('chain_observed')),
                    option_coverage_status=row['option_coverage_status'])
        details.append(item)
        groups[row['qdate'][:4], item['baseline_membership']].append(item)
    summary = [dict(year=int(year), baseline_membership=membership,
                    sampled_stock_days=len(rows),
                    observed_chains=sum(r['chain_observed'] for r in rows),
                    no_target_rows=sum(r['option_coverage_status'] ==
                                       'no_target_rows_listing_status_unknown' for r in rows),
                    query_failures=sum(r['option_coverage_status'] == 'query_failed' for r in rows))
               for (year, membership), rows in sorted(groups.items())]
    return details, summary


def run(c, root=Path('.')):
    counts = json.loads((root / 'results/stock_coverage/session_counts.json').read_text())
    before, after = transition(counts)
    populations = {}
    try:
        with c.cursor() as q:
            q.execute('SET SESSION MAX_EXECUTION_TIME=60000')
            q.execute('START TRANSACTION READ ONLY')
            for day in (before, after):
                q.execute('SELECT symbol FROM stockquote WHERE qdate=%s AND close>0 ORDER BY symbol', (day,))
                populations[day] = {r['symbol'] for r in q.fetchall()}
    finally:
        c.rollback()
    baseline, expanded = populations[before], populations[after]
    observations = json.loads((root / 'results/background_sample/observations.json').read_text())
    details, summary = summarize(observations, baseline, after)
    manifest = dict(
        baseline_date=before, expansion_date=after,
        detection_rule='First session with >=10000 rows, prior20 median >=1000, and count/median >=2',
        baseline_positive_price_symbols=len(baseline), expansion_positive_price_symbols=len(expanded),
        retained_symbols=len(baseline & expanded), added_symbols=len(expanded - baseline),
        removed_symbols=len(baseline - expanded),
        symbol_set_sha256={day: hashlib.sha256('\n'.join(sorted(values)).encode()).hexdigest()
                           for day, values in populations.items()},
        notes=['Expansion date is a source-count diagnostic, not a verified vendor change date.',
               'Exact symbols do not resolve issuer identity, ticker reuse, or instrument type.',
               'Later symbols absent from the baseline may be new listings or renamed securities.',
               'Original samples and labels are unchanged. Membership strata are descriptive, not eligibility filters.'])
    folder = root / 'results/stock_frame_audit'
    folder.mkdir(parents=True, exist_ok=True)
    write_rows(folder, 'sample_membership', details)
    write_rows(folder, 'membership_summary', summary)
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = ['# Stockquote frame expansion', '',
             f'The first large expansion detected in saved session counts is {after}; '
             f'the preceding session is {before}. Detection requires at least 10,000 rows, '
             'a preceding 20-session median of at least 1,000, and at least twice that median.', '',
             f'Positive-price symbol sets increase from {len(baseline):,} to {len(expanded):,}: '
             f'{len(baseline & expanded):,} retained, {len(expanded - baseline):,} added, '
             f'and {len(baseline - expanded):,} removed.', '',
             'Saved post-expansion observations grouped by exact ticker presence in the '
             'preceding-session frame:', '',
             '| Year | Baseline membership | Stock-days | Observed chains | No target rows | Query failures |',
             '| --- | --- | ---: | ---: | ---: | ---: |']
    for row in summary:
        lines.append('| ' + ' | '.join(str(v) for v in row.values()) + ' |')
    lines += ['', *manifest['notes'], '',
              'Membership compares all later observations with one historical session. '
              'It cannot justify excluding subsequent listings from validation. '
              'Chain coverage uses the saved background extraction, not new chain queries. '
              'The source-count snapshot and current membership query may have different refresh times.', '']
    (folder / 'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    with connection() as c:
        print(json.dumps(run(c), indent=2))
