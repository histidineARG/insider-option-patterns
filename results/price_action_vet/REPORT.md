# Stock price-action vetting

26 events audited. 26 have consistent arithmetic and reaction-session mapping; 26 recompute to ≥15% close-to-close.

Deep mode requeries OHLCV around each event and reports pre-announcement drift, gap structure, volume context, earlier-public session moves, post-move fade, and cash-offer premium comparisons. Prices are not rewritten; labels stay unauthorized.

| Event | Close | Gap | 5d drift | 20d drift | Vol20 | Offer prem | Status | Path flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| HNZ:2013-02-14 | 19.87% | 19.81% | -0.48% | 2.14% | 43.06x | 19.87% | jump_ok | reaction_mostly_overnight_gap, reaction_close_at_or_above_cash_offer |
| ONXX:2013-06-30 | 51.27% | 52.76% | 6.10% | -9.04% | 17.92x | n/a | jump_ok_prior_close_may_reflect_earlier_public | reaction_mostly_overnight_gap |
| CNQR:2014-09-18 | 17.64% | 18.30% | -2.71% | 7.27% | 41.84x | n/a | jump_ok_earlier_public_before_measured_window | earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |
| KRFT:2015-03-25 | 35.58% | 32.81% | -0.60% | -4.29% | 37.12x | n/a | jump_ok | reaction_mostly_overnight_gap |
| ADT:2016-02-16 | 47.53% | 51.17% | -3.93% | -11.55% | 22.49x | n/a | jump_ok_price_source_conflict | ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| AFOP:2016-04-07 | 19.34% | 19.21% | 4.53% | 19.38% | 45.92x | 19.66% | jump_ok | reaction_mostly_overnight_gap |
| LNKD:2016-06-13 | 46.64% | 48.22% | -2.95% | 3.29% | 15.37x | 49.53% | jump_ok | reaction_mostly_overnight_gap |
| JOY:2016-07-21 | 19.75% | 17.45% | -0.04% | 8.08% | 9.06x | 20.17% | jump_ok | reaction_mostly_overnight_gap |
| SWC:2016-12-09 | 17.98% | 19.14% | -2.26% | -1.54% | 21.82x | n/a | jump_ok | reaction_mostly_overnight_gap |
| CEB:2017-01-05 | 20.92% | 24.39% | 2.06% | 7.47% | 24.71x | n/a | jump_ok | reaction_mostly_overnight_gap |
| BIVV:2018-01-22 | 61.89% | 62.55% | 2.23% | 19.52% | 35.96x | 63.78% | jump_ok | reaction_mostly_overnight_gap |
| AVXS:2018-04-09 | 81.57% | 81.00% | -6.21% | -13.44% | 38.00x | 88.08% | jump_ok_prior_process_unresolved | reaction_mostly_overnight_gap |
| EFII:2019-04-15 | 29.25% | 25.54% | 1.38% | 7.42% | 33.79x | n/a | jump_ok | reaction_mostly_overnight_gap |
| BOLD:2019-12-02 | 105.98% | 105.31% | 0.56% | n/a | 79.25x | n/a | jump_ok | reaction_mostly_overnight_gap |
| VRTU:2020-09-10 | 24.49% | 24.64% | 1.78% | 0.82% | 35.57x | n/a | jump_ok_prior_process_unresolved | reaction_mostly_overnight_gap |
| COHR:2021-01-19 | 29.65% | 30.73% | -12.58% | 8.06% | 25.12x | n/a | jump_ok | ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| GSKY:2021-09-15 | 53.15% | 51.99% | -3.60% | 1.04% | 22.66x | n/a | jump_ok_prior_process_unresolved | previous_session_abs_move_ge_5pct, ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| ZGNX:2022-01-19 | 65.73% | 66.82% | -0.57% | 11.87% | 47.52x | 66.24% | jump_ok | reaction_mostly_overnight_gap |
| MAXR:2022-12-16 | 124.81% | 120.09% | -5.64% | -8.04% | 34.99x | n/a | jump_ok_same_day_earlier_disclosure | ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| PRVB:2023-03-13 | 259.70% | 259.40% | -18.09% | -28.19% | 29.60x | 273.13% | jump_ok_prior_process_unresolved | previous_session_abs_move_ge_5pct, earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |
| RETA:2023-07-28 | 54.02% | 51.72% | -1.42% | 9.84% | 23.21x | n/a | jump_ok_prior_close_may_reflect_earlier_public | reaction_mostly_overnight_gap |
| IMGN:2023-11-30 | 82.63% | 81.82% | 5.59% | 8.08% | 13.01x | 94.65% | jump_ok | reaction_mostly_overnight_gap |
| KAMN:2024-01-19 | 100.85% | 100.94% | -2.86% | -3.82% | n/a | 105.08% | jump_ok | reaction_mostly_overnight_gap |
| CALT:2024-05-28 | 69.27% | 70.16% | 1.04% | 14.97% | n/a | n/a | jump_ok_ads_security | reaction_mostly_overnight_gap |
| ITCI:2025-01-13 | 34.07% | 34.87% | 12.62% | 14.15% | 52.46x | 39.14% | jump_ok | strong_5d_pre_drift_ge_10pct, previous_session_abs_move_ge_5pct, ge_10pct_single_day_move_in_pre20, reaction_mostly_overnight_gap |
| SAGE:2025-06-16 | 35.37% | 35.67% | -2.19% | 1.36% | 40.39x | n/a | jump_ok_earlier_public_before_measured_window | earlier_public_lower_session_abs_ge_5pct, earlier_public_upper_session_abs_ge_5pct, reaction_mostly_overnight_gap |

Contamination / hazard statuses describe disclosure and identity interpretation. Path flags are additional price-series diagnostics and do not invent training labels.

## Path findings

All 26 reaction sessions are overnight-gap dominated (≥85% of the close-to-close jump appears at the open). 24/26 clear a 2× volume surge vs the prior 20 sessions; KAMN and CALT lack a complete baseline. 11/26 have a parseable single USD cash offer.

### Highest-signal price-path observations

- **ITCI**: previous session 2025-01-10 already +14.9% before the Monday announcement jump; 5d drift +12.6%.
- **CNQR**: earlier-public upper bound 2014-09-03 moved +8.6% (largest pre-20 move), weeks before the Sep 18 after-close deal print.
- **ADT**: 2016-02-02 already −15.7%; complaint “prior close 26.40” matches that day’s low, not the 26.87 previous close used locally.
- **GSKY**: previous session 2021-09-14 −12.2% immediately before the +53% reaction.
- **PRVB**: 5d/20d drift −18%/−28% into a distressed print, then +260% gap to a $25 cash offer.
- **ONXX / RETA**: earlier-public dates on the previous session itself show only +1.9% / +2.3% that day — prior close is only mildly contaminated, with the bulk of the jump still on the reaction session.
- **SAGE**: 2025-01-10 Biogen-bid session −5.1%; months later Supernus jump is a separate episode.
- Cash-offer prints generally close at a small discount to offer (LNKD −1.9%, AVXS −3.5%, IMGN −6.2%); HNZ closed exactly at $72.50.

### Pre-announcement drift and earlier-public session moves

| Event | Prev-session ret | 5d drift | 20d drift | Largest pre20 move | Earlier-public session move |
| --- | ---: | ---: | ---: | --- | --- |
| HNZ:2013-02-14 | -0.66% | -0.48% | 2.14% | 0.89% on 2013-01-18 | none |
| ONXX:2013-06-30 | 1.90% | 6.10% | -9.04% | -3.82% on 2013-06-04 | 2013-06-28: 1.90%; 2013-06-28: 1.90% |
| CNQR:2014-09-18 | 0.31% | -2.71% | 7.27% | 8.57% on 2014-09-03 | 2014-09-02: 0.57%; 2014-09-03: 8.57% |
| KRFT:2015-03-25 | -1.27% | -0.60% | -4.29% | 1.72% on 2015-03-12 | none |
| ADT:2016-02-16 | 1.90% | -3.93% | -11.55% | -15.66% on 2016-02-02 | none |
| AFOP:2016-04-07 | 3.62% | 4.53% | 19.38% | 7.08% on 2016-03-16 | none |
| LNKD:2016-06-13 | -3.98% | -2.95% | 3.29% | -3.98% on 2016-06-10 | none |
| JOY:2016-07-21 | 1.07% | -0.04% | 8.08% | -9.27% on 2016-06-27 | none |
| SWC:2016-12-09 | -1.21% | -2.26% | -1.54% | -4.19% on 2016-11-23 | none |
| CEB:2017-01-05 | 1.14% | 2.06% | 7.47% | 2.21% on 2016-12-15 | none |
| BIVV:2018-01-22 | 2.17% | 2.23% | 19.52% | 7.07% on 2018-01-09 | none |
| AVXS:2018-04-09 | -3.09% | -6.21% | -13.44% | -4.60% on 2018-03-27 | 2018-02-26: 1.89% |
| EFII:2019-04-15 | 0.72% | 1.38% | 7.42% | -5.90% on 2019-03-22 | none |
| BOLD:2019-12-02 | -1.45% | 0.56% | n/a | 9.51% on 2019-11-19 | none |
| VRTU:2020-09-10 | 1.61% | 1.78% | 0.82% | 3.34% on 2020-09-02 | 2020-08-30: -2.66% |
| COHR:2021-01-19 | -2.22% | -12.58% | 8.06% | 11.80% on 2021-01-07 | none |
| GSKY:2021-09-15 | -12.20% | -3.60% | 1.04% | -12.20% on 2021-09-14 | 2020-08-10: 2.10% |
| ZGNX:2022-01-19 | -1.82% | -0.57% | 11.87% | 6.40% on 2022-01-03 | none |
| MAXR:2022-12-16 | -3.91% | -5.64% | -8.04% | -11.22% on 2022-11-23 | 2022-12-16=reaction session; 2022-12-16=reaction session |
| PRVB:2023-03-13 | -7.59% | -18.09% | -28.19% | -7.59% on 2023-03-10 | 2022-10-04: 5.31% |
| RETA:2023-07-28 | 2.32% | -1.42% | 9.84% | 3.84% on 2023-07-06 | 2023-07-27: 2.32%; 2023-07-27: 2.32% |
| IMGN:2023-11-30 | 0.50% | 5.59% | 8.08% | -7.26% on 2023-11-20 | none |
| KAMN:2024-01-19 | 1.59% | -2.86% | -3.82% | -3.94% on 2024-01-16 | none |
| CALT:2024-05-28 | -1.45% | 1.04% | 14.97% | 7.47% on 2024-05-14 | none |
| ITCI:2025-01-13 | 14.91% | 12.62% | 14.15% | 14.91% on 2025-01-10 | none |
| SAGE:2025-06-16 | 1.52% | -2.19% | 1.36% | -4.63% on 2025-05-21 | 2025-01-10: -5.13%; 2025-01-10: -5.13% |

### Offer premium vs reaction

| Event | Offer | Prev close | Offer premium | Jump | Reaction close vs offer |
| --- | ---: | ---: | ---: | ---: | ---: |
| HNZ:2013-02-14 | $72.50 | $60.48 | 19.87% | 19.87% | 0.00% |
| AFOP:2016-04-07 | $18.50 | $15.46 | 19.66% | 19.34% | -0.27% |
| LNKD:2016-06-13 | $196.00 | $131.08 | 49.53% | 46.64% | -1.93% |
| JOY:2016-07-21 | $28.30 | $23.55 | 20.17% | 19.75% | -0.35% |
| BIVV:2018-01-22 | $105.00 | $64.11 | 63.78% | 61.89% | -1.15% |
| AVXS:2018-04-09 | $218.00 | $115.91 | 88.08% | 81.57% | -3.46% |
| ZGNX:2022-01-19 | $26.00 | $15.64 | 66.24% | 65.73% | -0.31% |
| PRVB:2023-03-13 | $25.00 | $6.70 | 273.13% | 259.70% | -3.60% |
| IMGN:2023-11-30 | $31.26 | $16.06 | 94.65% | 82.63% | -6.17% |
| KAMN:2024-01-19 | $46.00 | $22.43 | 105.08% | 100.85% | -2.07% |
| ITCI:2025-01-13 | $132.00 | $94.87 | 39.14% | 34.07% | -3.64% |

Outputs: `checks.json` (metrics), `windows.json` (raw OHLCV paths), `REPORT.md`.
