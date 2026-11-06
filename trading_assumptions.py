"""Conservative trading assumptions; never assert fills the EOD tape cannot support."""
import hashlib
import json
from pathlib import Path


ASSUMPTIONS = {
    'version': 1,
    'frozen_at': '2026-11-06',
    'signal_availability': (
        'Feature session close plus vendor delivery. Actual historical vendor delay is '
        'unverified, so no observation is marked execution-ready.'),
    'entry': (
        'Earliest considered entry is the next exchange-session close strictly before the '
        'earliest verified disclosure bound. This is a timing proxy, not a fill.'),
    'option_selection': (
        'Candidate contracts must satisfy the fixed research quote screen recorded in the '
        'reviewed-cohort manifest. Multipliers, deliverables, and adjusted contracts remain '
        'unverified; midpoint fills are not assumed.'),
    'cost_model': (
        'When usable bid/ask quotes exist, buy at ask and sell at bid. Absent a usable quote, '
        'the trade is non-executable rather than filled at last trade or midpoint.'),
    'holding_period': (
        'Hold until the earlier of the verified disclosure reaction session or the close of the '
        'tenth subsequent exchange session after the feature date. No intraday exit is claimed.'),
    'position_sizing': (
        'Unit notional per episode for diagnostics only. Capital limits and simultaneous '
        'position caps are unspecified until population evaluation is authorized.'),
    'exclusions': [
        'No fill when vendor delivery timing is unverified.',
        'No fill when quote eligibility or contract multiplier is unverified.',
        'No fill when disclosure chronology remains unresolved.',
        'No short premium strategies in this protocol version.',
    ],
}


def blocked_trading_gates(evaluation_manifest, dataset_manifest):
    blocked = []
    if not evaluation_manifest.get('population_evaluation_authorized'):
        blocked.append('population_evaluation_unauthorized')
    if dataset_manifest.get('research_eligible', 0) == 0:
        blocked.append('no_research_eligible_observations')
    if not dataset_manifest.get('known_positive_labels', 0):
        blocked.append('no_verified_executable_positives')
    blocked.append('vendor_delivery_timing_unverified')
    blocked.append('contract_deliverables_unverified')
    return blocked


def run(root=Path('.')):
    evaluation = json.loads((root/'results/evaluation/manifest.json').read_text())
    dataset = json.loads((root/'results/research_dataset/manifest.json').read_text())
    blocked = blocked_trading_gates(evaluation, dataset)
    folder = root/'results/trading_assumptions'
    folder.mkdir(parents=True, exist_ok=True)
    manifest = dict(assumptions=ASSUMPTIONS, blocked_gates=blocked,
                    trading_simulation_authorized=False,
                    simulated_trades=0, net_return=None,
                    source_sha256={
                        'results/evaluation/manifest.json':
                            hashlib.sha256((root/'results/evaluation/manifest.json').read_bytes()).hexdigest(),
                        'results/research_dataset/manifest.json':
                            hashlib.sha256((root/'results/research_dataset/manifest.json').read_bytes()).hexdigest(),
                    })
    (folder/'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (folder/'assumptions.json').write_text(json.dumps(ASSUMPTIONS, indent=2) + '\n')
    lines = ['# Conservative trading assumptions', '',
             'Trading simulation remains blocked. The assumptions below are frozen for later '
             'use and do not invent fills, returns, or executable historical quotes.', '',
             '## Assumptions', '']
    for key in ('signal_availability', 'entry', 'option_selection', 'cost_model',
                'holding_period', 'position_sizing'):
        lines += [f'- **{key.replace("_", " ").capitalize()}:** {ASSUMPTIONS[key]}']
    lines += ['', '## Explicit exclusions', '']
    lines += [f'- {item}' for item in ASSUMPTIONS['exclusions']]
    lines += ['', '## Blocked gates', '']
    lines += [f'- {g}' for g in blocked]
    lines += ['', 'No net trading performance is reported from this artifact.', '']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    return manifest


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
