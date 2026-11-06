"""Audit saved background coverage by year without querying the database."""
from collections import defaultdict
import json
from pathlib import Path

from exploratory_patterns import valid
from research_cohort import write_rows


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[str(row['qdate'])[:4]].append(row)
    results = []
    for year, observations in sorted(groups.items()):
        observed = [r for r in observations if r.get('chain_observed')]
        results.append(dict(
            year=int(year), sampled_stock_days=len(observations),
            sampled_dates=len({r['qdate'] for r in observations}),
            observed_chains=len(observed),
            no_target_rows=sum(r.get('option_coverage_status') ==
                               'no_target_rows_listing_status_unknown' for r in observations),
            query_failures=sum(r.get('option_coverage_status') == 'query_failed'
                               for r in observations),
            incomplete_baselines=sum(not r.get('baseline_complete') for r in observed),
            invalid_volume=sum(not r.get('volume_data_valid') for r in observed),
            usable_observations=sum(valid(r) for r in observations)))
    return results


def run(root=Path('.')):
    folder = root / 'results/background_sample'
    rows = json.loads((folder / 'observations.json').read_text())
    summary = summarize(rows)
    write_rows(folder, 'yearly_coverage', summary)
    lines = ['# Background coverage audit', '',
             'Saved, outcome-independent stockquote sample. Counts describe source coverage, '
             'not a verified historical equity-option universe. Missing target rows do not '
             'establish that options were unlisted. No observations are presumed negative.', '',
             '| Year | Stock-days | Dates | Chains | No target rows | Query failures | Incomplete baseline | Invalid volume | Usable |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in summary:
        lines.append('| ' + ' | '.join(str(v) for v in row.values()) + ' |')
    lines += ['', 'Incomplete baseline and invalid volume counts apply to observed chains and '
              'can overlap. Usable requires an observed chain, a complete baseline, and valid '
              'volume data. Counts are unweighted and do not estimate population rates.', '',
              'Regenerate from saved observations with `python3 background_report.py`. '
              'Review issuer identity, historical instrument classification, and first public '
              'disclosures before assigning labels or choosing chronological splits.', '']
    (folder / 'REPORT.md').write_text('\n'.join(lines))
    return summary


if __name__ == '__main__':
    run()
