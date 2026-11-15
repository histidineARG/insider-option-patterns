# ETP exclusion census

Snapshot `2026-11-15+446029073ac3` has 6592 symbols and 91 CIKs.

Headline metrics in the experiment reports were not refit in this pass when the scan walks thousands of option chains. Counts below are membership counts, not new returns.

## Anomaly symbol list

`/tmp/anomaly_symbol_list.txt` has 5299 symbols, of which 550 are exchange-traded products.
anomaly_flow, straddle_test, bracket_test, jump30_test, and gb30_trade_test read this file.

## optionstat universes

| Query | Symbols | ETP symbols |
| --- | ---: | ---: |
| direction_test optionstat 2014-01-01..2026-11-13 | 11691 | 2532 |
| quiet_screen / walkforward optionstat 2022-01-01..2026-11-12 | 8616 | 2431 |
| all optionstat symbols | 12458 | 2547 |

## Recomputed reports

These three reports were rebuilt from saved files. No option-chain scan was repeated.

| Artifact | Before | After | Rows removed |
| --- | --- | --- | --- |
| `results/research_dataset` stock-days | 2650 | 2442 | 208 background rows (195 symbols, including VXZ, TQQQ, UVXY). Feature rows 1350 and events 45 were unchanged. Certified negatives stayed 9. Feature-coverage-ready rows went from 2461 to 2269. |
| `results/exploratory_patterns` background usable / alerts | 1181 usable; alerts 52, 25, and 8 | 989 usable; alerts 49, 24, and 7 | Event side stayed 10/23, 8/23, and 4/23 |
| `results/evaluation` | The committed manifest was 2080 observations from an older table, with eligible 1861 and alerts 113, 48, and 17. That file was not the pre-filter version of the 2650-row table. | Rebuilt on the filtered 2442-row table: eligible 2242; alerts 161, 74, and 29; episodes 106, 58, and 25. A further ETP pass on that table removed 0. Gates remain blocked. Logistic status remains `blocked_by_evidence_gates`. Recall remains null. Simulated trades remain 0. | Do not read the alert-count change as an ETP effect. The previous evaluation artifact and this table were already different. |

## Not refit

These scans walk option chains for thousands of symbols. They were not rerun. The saved headline numbers are the pre-exclusion runs. Membership counts below are from the symbol lists those scripts query, not from a new fit.

| Script | Universe | ETP symbols removed by the new default | Rerun |
| --- | --- | --- | --- |
| `anomaly_flow.py`, `straddle_test.py`, `bracket_test.py`, `jump30_test.py`, `gb30_trade_test.py` | `/tmp/anomaly_symbol_list.txt`, 5299 symbols | 550 | `python3 anomaly_flow.py` then the four books. Each `run()` now filters that file. |
| `direction_test.py` | `optionstat` 2014-01-01 through 2026-11-13, 11691 symbols | 2532 | `python3 direction_test.py`. That script is not in the committed tree on `main`. A local untracked copy was filtered the same way and was not added here. |
| `quiet_screen.py`, `quiet_otm_screen.py`, `quiet_otm_pnl_stress.py`, `walkforward_score.py` | `optionstat` 2022-01-01 through 2026-11-12, 8616 symbols | 2431 | `python3 quiet_screen.py`, `python3 quiet_otm_screen.py`, `python3 quiet_otm_pnl_stress.py`, `python3 walkforward_score.py` |
| `background_sample.py` | saved sample is 1300 stock-days, 208 of them ETPs | not redrawn | `python3 background_sample.py --start-year 2013 --end-year 2025 --dates-per-year 5 --symbols-per-date 20 --seed 1984` |

`walkforward_score.py` will not resume a checkpoint written before this filter. A default run starts a new checkpoint with `version` 3 and `etp_excluded` true. `--include-etp` still resumes a version 2 checkpoint.

Reviewed-cohort events (45) and pre-event feature rows (1350) contain no symbols from this snapshot. Insider footprint, accumulation, and resolved screens read those keeps, so a rerun would drop 0 of those rows. They were not rerun.

`python3 price_jump_examine.py` now uses this snapshot instead of the 50-symbol denylist. The historical jump artifacts were not reclassified.

