# Stock price-action vetting

45 events audited. 45 have consistent arithmetic and reaction-session mapping; 45 recompute to ≥15% close-to-close.

Deep mode requeries OHLCV around each event and reports pre-announcement drift, gap structure, volume context, earlier-public session moves, post-move fade, and cash-offer premium comparisons. Prices are not rewritten; labels stay unauthorized.

| Event | Close | Gap | 5d drift | 20d drift | Vol20 | Offer prem | Status | Path flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| HNZ:2013-02-14 | 19.87% | 19.81% | -0.48% | 2.14% | 43.06x | 19.87% | jump_ok | reaction_mostly_overnight_gap, reaction_close_at_or_above_cash_offer |
| SFD:2013-05-29 | 28.42% | 24.72% | 1.48% | 1.09% | 36.00x | n/a | jump_ok | reaction_mostly_overnight_gap |
| ONXX:2013-06-30 | 51.27% | 52.76% | 6.10% | -9.04% | 17.92x | n/a | jump_ok_prior_close_may_reflect_earlier_public | reaction_mostly_overnight_gap |
| XRTX:2013-12-23 | 27.27% | 26.89% | 0.00% | 3.16% | 53.56x | n/a | jump_ok | reaction_mostly_overnight_gap |
| BEAM:2014-01-13 | 24.56% | 24.59% | 0.48% | -0.61% | 63.43x | n/a | jump_ok | reaction_mostly_overnight_gap |
| ZLC:2014-02-19 | 40.31% | 39.97% | -0.13% | -0.40% | 60.41x | n/a | jump_ok | reaction_mostly_overnight_gap |
| SUSS:2014-04-28 | 36.28% | 37.30% | -1.23% | -4.81% | 17.20x | n/a | jump_ok | reaction_mostly_overnight_gap |
| CNQR:2014-09-18 | 17.64% | 18.30% | -2.71% | 7.27% | 41.84x | n/a | jump_ok_earlier_public_before_measured_window | earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |
| FMI:2015-01-12 | 95.32% | 126.45% | 7.89% | 7.70% | 30.41x | n/a | jump_ok | reaction_mostly_overnight_gap |
| KRFT:2015-03-25 | 35.58% | 32.81% | -0.60% | -4.29% | 37.12x | n/a | jump_ok_prior_close_may_reflect_earlier_public | reaction_mostly_overnight_gap |
| POZN:2015-06-08 | 18.94% | 16.42% | 17.05% | -4.91% | 13.85x | n/a | jump_ok | strong_5d_pre_drift_ge_10pct, reaction_mostly_overnight_gap |
| PCP:2015-08-10 | 19.10% | 19.23% | -0.53% | 1.58% | 12.31x | n/a | jump_ok_gap_may_include_earlier_public | reaction_mostly_overnight_gap |
| KLAC:2015-10-21 | 18.79% | 19.55% | 4.40% | 9.03% | 13.27x | n/a | jump_ok | reaction_mostly_overnight_gap |
| ARG:2015-11-17 | 29.36% | -0.84% | 10.72% | 16.51% | 11.98x | n/a | jump_ok_same_day_earlier_disclosure | strong_5d_pre_drift_ge_10pct |
| AFFX:2016-01-08 | 51.57% | 48.97% | -8.72% | -0.43% | 147.52x | n/a | jump_ok | reaction_mostly_overnight_gap |
| ALR:2016-02-01 | 45.46% | 45.46% | -4.22% | -6.18% | 24.01x | n/a | jump_ok | reaction_mostly_overnight_gap |
| CSCD:2016-02-04 | 32.26% | 29.78% | -1.67% | -2.05% | 24.28x | n/a | jump_ok | reaction_mostly_overnight_gap |
| LF:2016-02-05 | 70.18% | 66.67% | -10.94% | -19.72% | 39.73x | n/a | jump_ok | reaction_mostly_overnight_gap |
| ADT:2016-02-16 | 47.53% | 51.17% | -3.93% | -11.55% | 22.49x | n/a | jump_ok_price_source_conflict | ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| CKP:2016-03-02 | 29.28% | 27.12% | 19.36% | 23.47% | 72.10x | n/a | jump_ok | strong_5d_pre_drift_ge_10pct, strong_20d_pre_drift_ge_20pct, previous_session_abs_move_ge_5pct, reaction_mostly_overnight_gap |
| VAL:2016-03-20 | 23.17% | 25.24% | 2.43% | 8.79% | 21.35x | n/a | jump_ok | reaction_mostly_overnight_gap |
| RKUS:2016-04-04 | 32.40% | 32.00% | 6.50% | 0.20% | 59.56x | n/a | jump_ok | reaction_mostly_overnight_gap |
| VA:2016-04-04 | 41.67% | 40.08% | 13.84% | 27.92% | 14.71x | n/a | jump_ok | strong_5d_pre_drift_ge_10pct, strong_20d_pre_drift_ge_20pct, ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| AFOP:2016-04-07 | 19.34% | 19.21% | 4.53% | 19.38% | 45.92x | 19.66% | jump_ok | reaction_mostly_overnight_gap |
| LNKD:2016-06-13 | 46.64% | 48.22% | -2.95% | 3.29% | 15.37x | 49.53% | jump_ok | reaction_mostly_overnight_gap |
| JOY:2016-07-21 | 19.75% | 17.45% | -0.04% | 8.08% | 9.06x | 20.17% | jump_ok | reaction_mostly_overnight_gap |
| SWC:2016-12-09 | 17.98% | 19.14% | -2.26% | -1.54% | 21.82x | n/a | jump_ok | reaction_mostly_overnight_gap |
| CEB:2017-01-05 | 20.92% | 24.39% | 2.06% | 7.47% | 24.71x | n/a | jump_ok | reaction_mostly_overnight_gap |
| GNCMA:2017-04-04 | 62.40% | 50.78% | -2.65% | 15.05% | 42.25x | n/a | jump_ok | none |
| BIVV:2018-01-22 | 61.89% | 62.55% | 2.23% | 19.52% | 35.96x | 63.78% | jump_ok_gap_may_include_earlier_public | reaction_mostly_overnight_gap |
| AVXS:2018-04-09 | 81.57% | 81.00% | -6.21% | -13.44% | 38.00x | 88.08% | jump_ok_prior_process_unresolved | reaction_mostly_overnight_gap |
| EFII:2019-04-15 | 29.25% | 25.54% | 1.38% | 7.42% | 33.79x | n/a | jump_ok | reaction_mostly_overnight_gap |
| BOLD:2019-12-02 | 105.98% | 105.31% | 0.56% | n/a | 79.25x | n/a | jump_ok | reaction_mostly_overnight_gap |
| VRTU:2020-09-10 | 24.49% | 24.64% | 1.78% | 0.82% | 35.57x | n/a | jump_ok_prior_process_unresolved | reaction_mostly_overnight_gap |
| COHR:2021-01-19 | 29.65% | 30.73% | -12.58% | 8.06% | 25.12x | n/a | jump_ok_gap_may_include_earlier_public | ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| GSKY:2021-09-15 | 53.15% | 51.99% | -3.60% | 1.04% | 22.66x | n/a | jump_ok_prior_process_unresolved | previous_session_abs_move_ge_5pct, ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| ZGNX:2022-01-19 | 65.73% | 66.82% | -0.57% | 11.87% | 47.52x | 66.24% | jump_ok | reaction_mostly_overnight_gap |
| MAXR:2022-12-16 | 124.81% | 120.09% | -5.64% | -8.04% | 34.99x | n/a | jump_ok_same_day_earlier_disclosure | ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| PRVB:2023-03-13 | 259.70% | 259.40% | -18.09% | -28.19% | 29.60x | 273.13% | jump_ok_prior_process_unresolved | previous_session_abs_move_ge_5pct, earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |
| RETA:2023-07-28 | 54.02% | 51.72% | -1.42% | 9.84% | 23.21x | n/a | jump_ok_prior_close_may_reflect_earlier_public | reaction_mostly_overnight_gap |
| IMGN:2023-11-30 | 82.63% | 81.82% | 5.59% | 8.08% | 13.01x | 94.65% | jump_ok_earlier_public_before_measured_window | earlier_public_lower_session_abs_ge_5pct, earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |
| KAMN:2024-01-19 | 100.85% | 100.94% | -2.86% | -3.82% | n/a | 105.08% | jump_ok | reaction_mostly_overnight_gap |
| CALT:2024-05-28 | 69.27% | 70.16% | 1.04% | 14.97% | n/a | n/a | jump_ok_ads_security | reaction_mostly_overnight_gap |
| ITCI:2025-01-13 | 34.07% | 34.87% | 12.62% | 14.15% | 52.46x | 39.14% | jump_ok_gap_may_include_earlier_public | strong_5d_pre_drift_ge_10pct, previous_session_abs_move_ge_5pct, ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| SAGE:2025-06-16 | 35.37% | 35.67% | -2.19% | 1.36% | 40.39x | n/a | jump_ok_earlier_public_before_measured_window | earlier_public_lower_session_abs_ge_5pct, earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |

Contamination / hazard statuses describe disclosure and identity interpretation. Path flags are additional price-series diagnostics and do not invent training labels.
