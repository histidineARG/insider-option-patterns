"""Render the completed descriptive alignment and source-coverage findings."""
from datetime import date
import json
from pathlib import Path


def render(root=Path('.')):
    folder=root/'results/sec_alignment'
    rows=json.loads((folder/'case_matches.json').read_text())
    cases={r['id']:r for r in json.loads((root/'data/sec_cases.json').read_text())['cases']}
    def number(x):return f'{x:,.2f}' if x is not None else '—'
    lines=['# SEC case alignment: preliminary findings',
           '',f'Generated {date.today()}. Descriptive case study; no trained model, control sample, or trading backtest.',
           '',f'{len(rows)} case/event records processed; '+
           f"{sum(r.get('observed_pre_event_sessions',0)>0 for r in rows)} have EOD observations before their event within the extracted trade interval.",
           '', '## Important findings', '',
           '- Virtusa: 250 market contracts in the three documented series on the alleged purchase day, matching the complaint total. The next-open announcement precludes capturing its announcement move with a signal based on the previous final EOD volume.',
           '- EFII: 199 market contracts in the documented series over the purchase interval versus 187 alleged purchases. Its longer-dated calls are excluded by a 60-DTE screen. Exact-series ratios use contracts selected retrospectively from the complaint; they are diagnostic, not deployable predictions.',
           '- Heinz: the peak OTM ratio is about 0.12 with a 60-DTE ceiling versus 16.02 across expirations. Expiry filters can reverse the conclusion.',
           '- Kraft and Joy Global: aggregate volume does not show a large surge in the documented windows. Successful recovery of spectacular cases cannot establish general recall.',
           '- Kaman has no local chain rows for 2024-01-08 inside the examined interval. Historical data gaps need a full audit.',
           '', '## Comparison', '',
           'Ratios compare each observed session with its prior 20 observed chain sessions. Short-dated = OTM calls with 1–60 calendar DTE; all-expiry = all unexpired OTM calls. Case-selected exact series include ITM contracts where documented. Missing sessions are reported, not filled with zero.', '',
           '| Symbol | Event | Peak short-dated ratio | Peak all-expiry ratio | Documented series market volume | Alleged purchases |',
           '|---|---|---:|---:|---:|---:|']
    for r in rows:
        c=cases[r['case_id']]
        lines.append(f"| [{r['symbol']}]({c['source_url']}) | {r.get('event_date',c['event_date'])} | {number(r.get('peak_otm_ratio20'))} | {number(r.get('peak_all_expiries_ratio20'))} | {number(r.get('source_series_volume'))} | {number(r.get('documented_contracts'))} |")
    lines.extend(['','## Interpretation and limits','',
                  'Market volume belongs to all participants; agreement with a complaint does not reveal account identities. Alleged purchases may cover only a subset of defendants or series. Counts are not guaranteed to reconcile unless dates, contracts and source coverage are identical.',
                  '', 'The ad hoc diagnostic (at least 100 short-dated OTM calls and 3x lagged volume, or a zero baseline) fires in '+str(sum(r.get('diagnostic_alert_days',0)>0 for r in rows))+' extracted windows. Only '+str(sum(r.get('entry_proxy_precedes_event',False) for r in rows))+' have a subsequent trading-session close strictly before the event date. These counts are not a false-negative estimate, a profitability result or an executable opportunity count. The calendar is optiondb.tradingday and historical calendar completeness has not been independently audited.',
                  '', 'The registry deliberately separates complaint allegations, administrative settlements, reported civil verdicts and investigations. Charnas/ODP is investigation-only in the cited source and is not an adjudicated positive. Legal status strings describe the reviewed source, not necessarily the latest disposition.',
                  '', '## Search coverage','',
                  'The case inventory is **not exhaustive**. It contains 25 extracted case/event records plus 31 discovery records awaiting detailed review; multi-company and multi-event discovery records are not independent cases. Year-specific and named-case SEC searches were used. Local direct requests to the SEC enforcement archive returned HTTP 403. Search-engine recall is unknown; no denominator of all enforcement documents has been enumerated. The later successful EDGAR filing search concerns corporate M&A filings, not enforcement releases, and does not close this gap.',
                  '', 'Case-linked exact-series features must not be used as supervised input without reconstructing an ex ante contract selection rule. No false-positive or false-negative rates, predictive probabilities, expected returns, or live-trading performance have been estimated.',
                  '', '## Files','',
                  '- `data/sec_cases.json`: case evidence, dates, contract specifications and source locators.',
                  '- `data/sec_discovery_candidates.json`: pending and excluded records.',
                  '- `results/sec_alignment/daily_features.csv`: daily comparison series.',
                  '- `results/sec_alignment/case_matches.csv`: per-case summary and data gaps.',
                  '- `data/coverage_2026.json`: pre-backfill audit; `data/backfill_result_2026.json`: October 9 repair and remaining 14 missing dates.',
                  ''])
    (folder/'REPORT.md').write_text('\n'.join(lines))


if __name__=='__main__':render()
