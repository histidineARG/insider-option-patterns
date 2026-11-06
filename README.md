# Insider Option Patterns

Research option trading patterns associated with documented insider-trading cases
by aligning SEC evidence with historical EOD data in local `optiondb`.
The project includes a baseline OTM call-volume detector and an SEC case alignment
workflow. Signals prioritize investigation; they do not establish insider trading
or identify traders.

Research design: [RESEARCH.md](RESEARCH.md).
Current task, evidence gaps, and next target: [ROADMAP.md](ROADMAP.md).
Agreed event selection, background population, validation, and trading evaluation:
[METHODOLOGY.md](METHODOLOGY.md).
The source-backed case registry is `data/sec_cases.json`; additional discovery
candidates are in `data/sec_discovery_candidates.json`. The inventory is not exhaustive.
Run `python3 sec_match.py` to regenerate `results/sec_alignment/` with read-only
queries (password prompt). These results describe historical patterns, not validated
predictive performance or executable trading returns.

The preliminary findings are in [the SEC alignment report](results/sec_alignment/REPORT.md).
M&A discovery files are under `data/m_and_a/`. Run `python3 ma_inventory.py` to
refresh the open candidate dataset and local mappings; `python3 edgar_ma_search.py`
enumerates four SEC merger-related forms by year through the configured cutoff.
Filing dates and completion dates must not be substituted for first public
announcement timestamps. These inventories require event and issuer review before
they can supply training labels.
See [M&A inventory coverage](data/m_and_a/README.md) for the official SEC search
counts, source files, reviewed examples and remaining validation work.

Run `python3 ma_stock_confirmation.py` to check dated M&A targets in `stockquote`:
at least a 15% close-to-close price jump and 2× the previous 20 sessions' average
volume, with announcement-session alignment and explicit missing-data handling.
See [stock reaction confirmations](results/ma_stock_confirmation/REPORT.md).

The agreed price-only research cohort is separate from that older price-and-volume
screen. Run `python3 research_cohort.py` to audit option coverage and extract
calendar-aware pre-event features. See the [cohort report](results/research_cohort/REPORT.md).
It includes 24 price-qualified, source/timing-reviewed candidates; corporate-action
and first-public-disclosure checks remain pending. Missing volume baselines do
not disqualify otherwise measurable price jumps. Labels remain unset.

The newer [evidence-overlay cohort](results/reviewed_cohort/REPORT.md) preserves
that snapshot and adds ITCI and SAGE from 2025 acquirer releases: 26 price-qualified
candidates and 780 pre-event observations. `python3 reviewed_cohort.py` regenerates
it using read-only queries; `python3 reviewed_cohort.py --apply-reviews-only`
refreshes review fields offline from `data/event_review_overrides.json` without
requerying prices. Source findings record earlier takeover reports, conflicting
disclosure dates, price-source disagreements, ADS terms, and announcement-session
or press-time evidence for every candidate. Quote-candidate counts are diagnostics;
zero events are training-ready until first-disclosure and corporate-action reviews
pass.

Run `python3 cik_audit.py` to compare stored issuer CIKs with `data.sec.gov`
submissions metadata; see [CIK audit](results/cik_audit/REPORT.md). Suspicious
name mismatches are diagnostics for review overrides, not automatic label changes.
`python3 corporate_action_review.py` scores the identity/share-class/reincarnation
checklist without auto-marking any event complete:
[corporate-action checklist](results/corporate_action_review/REPORT.md).
`python3 price_action_vet.py` recomputes stored close-to-close jumps, checks
reaction-session calendar mapping, and flags earlier-public contamination plus
ADS/price-source hazards without rewriting prices:
[price-action vetting](results/price_action_vet/REPORT.md).

Run `python3 research_dataset.py` for the time-safe observation table with
ten-session outcome boundaries, disclosure diagnostics, and purged chronological
partitions frozen in `data/evaluation_protocol.json`. See the
[observation audit](results/research_dataset/REPORT.md). Unknown labels stay null;
empty `data/outcome_coverage_reviews.json` intentionally certifies no negatives.
`python3 evaluation.py` builds fixed-rule alert episodes and logistic interfaces
but blocks population metrics while evidence gates fail:
[evaluation report](results/evaluation/REPORT.md).
`python3 trading_assumptions.py` freezes conservative fill rules and reports
blocked trading simulation: [trading assumptions](results/trading_assumptions/REPORT.md).

Run `python3 background_sample.py` for a reproducible historical coverage pilot
whose dates and symbols are selected independently of M&A outcomes. Its unlabeled
observations are not assumed negative. `python3 stock_coverage.py` audits the
historical stockquote sampling frame; see [coverage diagnostics](results/stock_coverage/REPORT.md).
`python3 exploratory_patterns.py` describes fixed volume rules in the saved event
and background samples; see [exploratory counts](results/exploratory_patterns/REPORT.md).
These outputs do not estimate population accuracy or trading returns.

Run `python3 background_report.py` to audit saved background coverage by year
without database access; see the [background audit](results/background_sample/REPORT.md).
The expanded pilot contains 1,300 stock-days across 65 dates, with 1,181 usable
observations.

Run `python3 option_coverage_probe.py` for bounded, read-only checks of sampled
symbols and three control symbols in both option tables (2024 onward by default).
The [saved probe](results/option_coverage_probe/REPORT.md) finds all controls on
every sampled date, while the stockquote frame expands from roughly 6,000 to
22,000–24,000 symbols in 2025. None of the missing sampled chains were recovered
from `optiondaily3`. This supports investigating the broader sampling frame;
it does not rule out partial ingestion gaps or establish historical option listings.

The [frame expansion audit](results/stock_frame_audit/REPORT.md) locates the large
stockquote expansion on November 4, 2024: positive-price symbols rise from 5,960
to 22,991. Of the 2025 sampled stock-days, chains are present for 24/25 whose
symbols appeared in the preceding frame and 1/75 whose symbols did not. This
describes a change in the sampling population; the older frame is not an
eligibility filter for future listings. Run `python3 stock_frame_audit.py` to
repeat the read-only boundary symbol queries and saved-sample comparison.

The current descriptive rules surfaced alerts in 10/23 event windows and 52/1181
sampled background stock-days at 100 calls and 3× baseline; at 500 calls and 5×,
8/23 and 25/1181. These are not recall or false-positive estimates: event labels
remain under review, the background pilot is small, and its universe is unverified.

Research session alignment uses the versioned NYSE snapshot in `data/calendar/`,
including exchange holidays, early closes, and the January 9, 2025 closure.
The source database's `tradingday` table is not changed. Its audit records missing
sessions and incorrect holiday entries. Regenerating the snapshot requires
`pandas_market_calendars`; normal use reads the saved JSON. Run research scripts
from this checkout so their source inventories and outputs are available.

Run `python3 ma_broad_screen.py` to discover price jumps among mapped SEC merger
filers. The saved scan contains 3,303 unverified leads, including 1,809 jumps of
at least 15%. These require primary-source announcement and issuer confirmation;
they are not confirmed M&A events or model labels.

Run `python3 ma_registry.py` to create and populate dedicated `research_ma_*`
tables in `optiondb`. This command writes research tables; the detector and
screening commands read source tables. The registry retains event candidates,
filing evidence, discovery records, and price leads independently of price or
volume thresholds. Public-target status and acquisition completion remain unknown
until reviewed. The `research_ma_public_company_acquisitions` view marks completed
public-company acquisitions only when both flags are true. Source candidates
are not yet deduplicated into a canonical deal universe. See the saved
[ingest summary](results/ma_registry/ingest_summary.json) for counts.

## Run

Python 3.10+ and PyMySQL are required. Install with `python3 -m pip install -e .`
(or use an environment that already has PyMySQL).

```bash
python3 detector.py --symbols AAPL MSFT --date 2026-11-04
python3 detector.py --symbols AAPL --date 2026-11-04 --format csv
python3 -m unittest discover -s tests -v
```

The CLI prompts for the MySQL password. Credentials are never stored in this repo.
For unattended use, supply `OPTIONDB_PASSWORD` through your environment/secret manager.
Defaults: user `bill`, database `optiondb`, socket `/run/mysqld/mysqld.sock`.
Override with `OPTIONDB_USER`, `OPTIONDB_DATABASE`, `OPTIONDB_SOCKET`, or
`OPTIONDB_HOST` and `OPTIONDB_PORT` for TCP.

## Signal

For each requested symbol and date, aggregate calls 3–50% above the underlying
price with 3–45 calendar days to expiration. Require at least 500 contracts,
5x prior average volume, a population z-score of at least 3, and aggregate
volume/open-interest of at least 1. Thresholds are CLI options; see `--help`.
Use the prior 20 observed chain sessions, requiring at least 10. The target date
and future dates are excluded from the baseline. Observed sessions with no
qualifying calls count as zero; absent chain sessions are not fabricated.
A bounded history query spans max(90, lookback*4) calendar days.

Flat baselines qualify only if current volume exceeds their mean. Zero means
and zero OI are explicitly flagged, with undefined ratios emitted as JSON null.
Premium is an estimate using closing bid/ask midpoint, 100 shares per contract,
and reported volume; it is not observed transaction value. Invalid/crossed quotes
contribute no estimated premium. Adjusted contracts can use other multipliers.

JSON includes settings and ranked alerts. CSV includes headers even with no alerts.
Missing target data or insufficient history generates stderr diagnostics.
No alert is distinct from no data. Database failures exit with status 1.

## Data and performance

Uses the verified `optiondaily` schema: underlying, underlying_last, type, strike,
edate, qdate, volume, oi, bid, ask. `--table optiondaily3` selects the alternate
compatible table. Explicit symbols constrain the leading underlying/qdate index;
the source table has billions of rows, so start with a small watchlist.
Queries run in a read-only transaction with a 60-second server execution limit.
The detector creates no tables and changes no source data.

Coverage depends on source completeness. Contract eligibility changes as price
and DTE change. Daily aggregates cannot determine trade aggressor, opening versus
closing volume, intraday timing, or coordination. Earnings, public news, hedging,
rolls, and corporate actions can cause alerts. Review those explanations and
validate against subsequent data before drawing conclusions. This version has
no earnings calendar, intraday feed, or backtested predictive performance.
