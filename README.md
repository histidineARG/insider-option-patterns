# Insider Option Patterns

This repository is Python research code for studying end-of-day option activity around documented SEC insider-trading matters and public merger events. It aligns a local case registry and SEC filing metadata with a local MySQL database of historical option chains and stock quotes, then builds review checklists, coverage audits, and time-safe observation tables. The baseline detector flags unusual out-of-the-money call volume for investigation. Nothing here identifies a trader, establishes that trading was illegal, or reports a validated trading strategy.

Design notes, which are study plans rather than fitted results, are in [RESEARCH.md](RESEARCH.md), [METHODOLOGY.md](METHODOLOGY.md), and [ROADMAP.md](ROADMAP.md). There are no notebooks.

## Analyses

- **Option-volume screen** (`detector.py`). For each symbol and session, aggregate calls that are 3–50% out of the money with 3–45 calendar days to expiration. Default alert gates are at least 500 contracts, 5× the prior mean, a population z-score of at least 3, and volume/open interest of at least 1, using up to 20 prior observed chain sessions and at least 10 of them. The target day and later days are excluded from the baseline. Thresholds are CLI flags; `python3 detector.py --help` lists them. Estimated premium uses the closing bid/ask midpoint when the quote is usable. The query is a read-only transaction.
- **SEC case alignment** (`sec_match.py`, `research_report.py`). Compare chain volume in windows from `data/sec_cases.json` with the complaint or release dates stored in that file. Output is descriptive. Discovery leads that are not fully extracted live in `data/sec_discovery_candidates.json`.
- **M&A inventory.** `edgar_ma_search.py` pages SEC full-text search for `PREM14A`, `DEFM14A`, `DEFM14C`, and `SC 14D9`. `ma_inventory.py` refreshes a Hugging Face EDGAR deal file and exports local `maevent` / `mafromnews` rows. Filing dates are not announcement times. `ma_stock_confirmation.py` measures a close-to-close jump of at least 15% and a volume multiple (default 2× the previous 20 sessions). `ma_broad_screen.py` screens mapped merger filers for price jumps. `ma_registry.py` is the script that **writes** database tables: it creates and fills `research_ma_*` tables and the `research_ma_public_company_acquisitions` view. Other database scripts read source tables.
- **Cohorts and labels.** `research_cohort.py` audits option coverage and pre-event features for price-qualified candidates. `reviewed_cohort.py` overlays `data/event_review_overrides.json` and keeps `training_label_ready` false until review gates pass. `research_dataset.py` builds a stock-day table with a ten-session outcome window and the partitions in `data/evaluation_protocol.json`. Unknown labels stay null. Negatives are recorded only from complete rows in `data/outcome_coverage_reviews.json`.
- **Evaluation gates.** `evaluation.py` builds fixed-rule alert episodes and can fit a logistic model, and it refuses population metrics while evidence gates fail. `trading_assumptions.py` records conservative fill rules and writes a blocked trading simulation (no fills and no return). `exploratory_patterns.py` counts fixed volume rules on the saved event and background samples; its report states that those counts are not precision, recall, or profitability.
- **Coverage, identity, and jump review.** `background_sample.py` draws an outcome-independent stock-day sample. `background_report.py` summarizes that saved sample by year. `stock_coverage.py`, `stock_frame_audit.py`, and `option_coverage_probe.py` audit `stockquote` and option-table presence. `cik_audit.py` compares stored CIKs with SEC submissions metadata. `corporate_action_review.py` scores an identity checklist and does not mark events complete by itself. `price_action_vet.py` checks stored jumps offline, or requeries OHLCV with `--deep`. `price_jump_examine.py` classifies large stock jumps and uses an EDGAR 8-K Item 2.02 calendar (`edgar_earnings_calendar.py`) to drop earnings. `edgar_jump_assist.py` only attaches non-earnings 8-K hints. It does not auto-keep a jump. `market_calendar.py` loads the checksummed NYSE session snapshot in `data/calendar/` (including the 2025-01-09 closure). `--refresh` rebuilds that snapshot and needs the optional `pandas_market_calendars` extra.

Saved JSON, CSV, and Markdown under `results/` are outputs from these steps. `results/news_jump_filter/` and `results/price_jump_population/` are checked-in snapshots. No current script writes those two directories.

## Repository structure

| Path | Role |
| --- | --- |
| `detector.py` | Read-only OTM call-volume screen. Console script `insider-option-patterns`. |
| `sec_match.py`, `research_report.py` | SEC case/chain alignment and the alignment report. |
| `edgar_ma_search.py`, `ma_inventory.py`, `ma_stock_confirmation.py`, `ma_broad_screen.py`, `ma_registry.py` | Merger-filing inventory, local M&A export, price/volume checks, price-jump leads, and the writing registry. |
| `research_cohort.py`, `reviewed_cohort.py`, `research_dataset.py`, `evaluation.py`, `trading_assumptions.py`, `exploratory_patterns.py` | Cohort features, review overlay, observation table, gated evaluation, trading assumptions, descriptive rules. |
| `background_sample.py`, `background_report.py`, `stock_coverage.py`, `stock_frame_audit.py`, `option_coverage_probe.py` | Sampling frame and option-coverage audits. |
| `cik_audit.py`, `corporate_action_review.py`, `price_action_vet.py`, `price_jump_examine.py`, `edgar_earnings_calendar.py`, `edgar_jump_assist.py`, `market_calendar.py` | Identity, corporate-action, price-path, earnings, and calendar checks. |
| `data/` | Registries, review ledgers, NYSE calendar snapshot, M&A extracts, evaluation protocol. |
| `data/m_and_a/` | SEC filing pages, local `maevent` / news exports, provenance. See `data/m_and_a/README.md`. |
| `results/` | Generated reports and tables. |
| `tests/` | Unit tests. They do not require the database. |
| `pyproject.toml` | Package metadata and dependencies. |
| `RESEARCH.md`, `METHODOLOGY.md`, `ROADMAP.md` | Research design and current gates. |

Run commands from the repository root so script imports and relative `data/` and `results/` paths resolve.

## Requirements and setup

Python 3.10 or newer. Direct dependencies are `PyMySQL` and `requests`. Regenerating the NYSE snapshot requires `pandas_market_calendars`.

```bash
python3 -m pip install -e .
python3 -m pip install -e '.[calendar]'   # only for market_calendar.py --refresh
```

The install was run in this environment with Python 3.12. The console script is `insider-option-patterns` (same CLI as `detector.py`).

Database scripts read connection settings from the environment:

- `OPTIONDB_PASSWORD`
- `OPTIONDB_USER` — MySQL user. If unset or empty, `detector.py`, `sec_match.py`, and `price_jump_examine.py` use `optiondb`.
- `OPTIONDB_DATABASE`
- `OPTIONDB_SOCKET`
- `OPTIONDB_HOST`
- `OPTIONDB_PORT`
- `SEC_USER_AGENT` — contact string sent to `data.sec.gov` by `edgar_earnings_calendar.py` (also used by `edgar_jump_assist.py`). SEC expects a User-Agent that identifies the caller. If unset or empty, the placeholder is `insider-option-patterns research (set SEC_USER_AGENT to a contact)`.

`detector.py` and `price_jump_examine.py` use TCP when `OPTIONDB_HOST` is set, and a Unix socket otherwise. `price_jump_examine.py` exits if `OPTIONDB_PASSWORD` is unset. `sec_match.connection()` (used by the other MySQL scripts) always uses a Unix socket; it does not read `OPTIONDB_HOST` or `OPTIONDB_PORT`. If `OPTIONDB_PASSWORD` is unset, `detector.py` and `sec_match.py` prompt on the terminal. No password is stored in the repository. `.gitignore` ignores `.env`.

## Running

### Verified without MySQL

These commands were run from the repository root after `python3 -m pip install -e .`. Each exited 0. `background_report.py` and `exploratory_patterns.py` rewrote their reports from saved JSON and matched the committed files. `research_report.py` rewrites `results/sec_alignment/REPORT.md` and updates its generated date.

```bash
python3 -m unittest discover -s tests -v
python3 detector.py --help
python3 background_report.py
python3 exploratory_patterns.py
python3 research_report.py
python3 -c "import market_calendar; print(len(market_calendar.sessions('2012-01-01', '2026-12-31')))"
```

The calendar call checks `data/calendar/manifest.json` against `data/calendar/nyse_sessions.json` and prints the session count. `market_calendar.py` with no arguments audits the database `tradingday` table and was not run. `market_calendar.py --refresh` was not run.

These also exited 0. They rewrite files under `results/`. `price_action_vet.py` without `--deep` replaces a previously saved deep OHLCV report with the offline close check, so do not run it if you need to keep that deep report.

```bash
python3 research_dataset.py
python3 evaluation.py
python3 trading_assumptions.py
python3 corporate_action_review.py
python3 reviewed_cohort.py --apply-reviews-only
python3 price_action_vet.py
```

`python3 -m unittest discover -s tests -v` completed 73 tests successfully.

### Requires the local MySQL database

No MySQL server was available here. `detector.py` was started against a closed port and exited 1 with a database error. Do not treat the invocations below as executed queries. They expect the tables listed under Data. `ma_registry.py` commits new `research_ma_*` tables; the others in this list use read-only transactions or read-only `SELECT`s.

```bash
python3 detector.py --symbols AAPL MSFT --date 2024-01-02
python3 detector.py --symbols AAPL --date 2024-01-02 --format csv
python3 sec_match.py
python3 ma_stock_confirmation.py
python3 ma_broad_screen.py
python3 research_cohort.py
python3 reviewed_cohort.py
python3 background_sample.py
python3 stock_coverage.py
python3 stock_frame_audit.py
python3 option_coverage_probe.py
python3 price_action_vet.py --deep
python3 price_jump_examine.py --start 2015-01-02 --end 2015-01-31
python3 ma_registry.py
```

`background_sample.py` accepts `--start-year`, `--end-year`, `--dates-per-year`, `--symbols-per-date`, and `--seed` (default 1984). `option_coverage_probe.py` accepts `--start-year` (default 2024). `ma_stock_confirmation.py` accepts `--volume-multiple` (default 2).

### Requires the network

These were not run here. They call SEC hosts and, for `ma_inventory.py`, Hugging Face, and the last one also opens MySQL.

```bash
python3 edgar_earnings_calendar.py --cik 320193
python3 edgar_jump_assist.py --help
python3 edgar_ma_search.py --help
python3 cik_audit.py
python3 ma_inventory.py
```

`edgar_earnings_calendar.py` exits unless `--cik` and/or `--ciks` is set. Cached per-CIK JSON under `results/edgar_earnings_calendar/by_cik/` is gitignored.

## Data, inputs, and outputs

**Local MySQL database** (name from `OPTIONDB_DATABASE`). Reads:

| Table | Used for |
| --- | --- |
| `optiondaily`, `optiondaily3` | EOD option chains (`underlying`, `underlying_last`, `type`, `strike`, `edate`, `qdate`, `volume`, `oi`, `bid`, `ask`). |
| `stockquote` | Equity OHLCV (`symbol`, `qdate`, `open`, `high`, `low`, `close`, `volume`). |
| `cik2symbol` | Local CIK-to-symbol map. |
| `maevent`, `mafromnews` | Local M&A and news-link rows exported by `ma_inventory.py`. |
| `tradingday` | Legacy session list audited by `market_calendar.py`. The script does not update it. |

Writes, only from `ma_registry.py`: `research_ma_events`, `research_ma_sources`, `research_ma_filings`, `research_ma_discovery_records`, `research_ma_price_leads`, and view `research_ma_public_company_acquisitions`.

**Files in `data/`.** Case text and contract windows in `sec_cases.json`. Review overlays, outcome reviews, jump-news reviews, and the frozen split protocol. NYSE sessions in `data/calendar/`. M&A CSV/JSON under `data/m_and_a/`, including `sec_filing_search/merger_filings_2013_2026.csv`.

**External sources.**

- SEC submissions JSON at `data.sec.gov` (`cik_audit.py`, `edgar_earnings_calendar.py`, `edgar_jump_assist.py`).
- SEC full-text search at `https://efts.sec.gov/LATEST/search-index` (`edgar_ma_search.py`).
- Hugging Face dataset `tcontorno/edgar-ma-deals` (`ma_inventory.py`).
- Optional `pandas_market_calendars` NYSE calendar when regenerating `data/calendar/`.

**Outputs.** Scripts write JSON, CSV, and `REPORT.md` files under `results/`. Examples: `results/sec_alignment/`, `results/ma_stock_confirmation/`, `results/research_cohort/`, `results/reviewed_cohort/`, `results/research_dataset/`, `results/evaluation/`, `results/trading_assumptions/`, `results/background_sample/`, `results/exploratory_patterns/`, `results/price_jump_examine/`, and `results/ma_registry/ingest_summary.json`. The detector prints JSON or CSV to stdout and diagnostics to stderr. Missing chain data is not the same as an empty alert list. Database failures exit 1.

Point-in-time vendor delivery, contract multipliers, and a complete historical option-listing universe are not established by these outputs. Read each `REPORT.md` for what that artifact claims.

## Disclaimer

This project is research and education. It is not financial, investment, legal, or trading advice. Alerts and descriptive counts are not a recommendation to buy or sell any security or option, and they are not a finding that any person traded on inside information. No script in this repository produces an authorized population-level accuracy estimate or a completed trading backtest.

## License

No license specified.
