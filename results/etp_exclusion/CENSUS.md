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

## Refits on 2026-11-15

These scans were rerun with the default exclusion. Headline before/after tables are at the top of each report.

| Script | Result |
| --- | --- |
| `gb30_trade_test.py` | Top-4 `tp40-t40` uncapped holdout mean 0.337 → 0.013. It no longer beats the volatility-matched random mean. Holdout portfolio CAGR 0.857 → 0.264, Sharpe 1.223 → 1.035, max drawdown -0.175 → -0.118. SPY holdout CAGR stayed 0.124, Sharpe 0.912, drawdown -0.092. |
| `jump30_test.py` | Prior choice (iforest 1-day p05, 10 sessions) holdout mean 0.002 → -0.001. New choice (boost 1-day top 4, 20 sessions) holdout mean 0.059 versus random 0.020. |
| `bracket_test.py` | New choice holdout deduped mean -0.013 versus random -0.013. No positive holdout edge. |
| `straddle_test.py` | Same choice. Holdout deduped ask/bid mean -0.224 → -0.227. Still negative, still ahead of the random straddle. |
| `anomaly_flow.py` | HBOS 1-day/50-day holdout lift 1.449 → 1.346. Isolation forest 1.246 → 1.164. Both still clear. LOF on that baseline does not: holdout lift 0.971. |
| `quiet_otm_screen.py` | Multi-day slate of 3, 20 sessions: date hit rate 0.309 → 0.330 versus quiet base 0.276 → 0.293. Call mean 1.815 → 1.709. |
| `quiet_otm_pnl_stress.py` | Deduped slate median 0.875 → 0.800 versus random 0.894 → 0.737. The stress cut still passes. |
| `walkforward_score.py` | Top 3, 20-session terminal date hit rate 0.481 → 0.442 versus random base 0.246 → 0.296. Still above the base. |
| `quiet_screen.py` | Multi-day top 3, 20-session call mean 1.632 → 1.560. Still above 1. |
| `direction_test.py` | Boosting top 10, 20 sessions: holdout hit rate 0.626 → 0.653 versus base 0.524 → 0.524. Compounded holdout book 1.13 → 0.91 versus SPY 1.14. Still behind SPY. |
| `background_sample.py` | Redrawn at the saved settings. 1,300 stock-days, 0 ETP symbols. Chain present on 1,218 days versus 1,219. Complete feature rows 1,178 versus 1,181. |

`research_dataset.py` rebuilt on that redraw: 2,650 stock-days, 0 further ETP rows, 0 certified negatives (the previous filtered table had 9, because that draw still contained the reviewed names). Exploratory event alerts stayed 10/23, 8/23, and 4/23. Background usable observations are 1,178, with alerts 51, 17, and 8.

`price_jump_examine.py` was not rerun. It joins the whole `stockquote` cross-section once per NYSE session and can fetch EDGAR calendars for every mapped CIK. That pass was not timed, so no runtime number is claimed here.

Reviewed-cohort events (45) and their feature rows contain no symbols from this snapshot. `insider_footprint.py`, `insider_accumulation.py`, and `insider_resolved.py` were not rerun.

