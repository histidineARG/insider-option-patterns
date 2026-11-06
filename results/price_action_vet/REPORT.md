# Stock price-action vetting

26 events audited offline from stored closes and the NYSE calendar snapshot. 26 have consistent arithmetic and reaction-session mapping; 26 recompute to ≥15% close-to-close.

Contamination of the measured window and source/identity hazards are reported separately. They do not rewrite prices or authorize training labels.

| Event | Return | Status | Flags / hazards |
| --- | ---: | --- | --- |
| HNZ:2013-02-14 | 19.87% | jump_ok | none |
| ONXX:2013-06-30 | 51.27% | jump_ok_prior_close_may_reflect_earlier_public | earlier_public_on_previous_session |
| CNQR:2014-09-18 | 17.64% | jump_ok_earlier_public_before_measured_window | earlier_public_strictly_before_previous_session |
| KRFT:2015-03-25 | 35.58% | jump_ok | none |
| ADT:2016-02-16 | 47.53% | jump_ok_price_source_conflict | price_source_conflict |
| AFOP:2016-04-07 | 19.34% | jump_ok | none |
| LNKD:2016-06-13 | 46.64% | jump_ok | none |
| JOY:2016-07-21 | 19.75% | jump_ok | issuer_identity_was_corrected |
| SWC:2016-12-09 | 17.98% | jump_ok | issuer_identity_was_corrected |
| CEB:2017-01-05 | 20.92% | jump_ok | issuer_identity_was_corrected |
| BIVV:2018-01-22 | 61.89% | jump_ok | issuer_identity_was_corrected |
| AVXS:2018-04-09 | 81.57% | jump_ok_prior_process_unresolved | unresolved_earlier_process_on_or_before_previous_session |
| EFII:2019-04-15 | 29.25% | jump_ok | issuer_identity_was_corrected |
| BOLD:2019-12-02 | 105.98% | jump_ok | issuer_identity_was_corrected |
| VRTU:2020-09-10 | 24.49% | jump_ok_prior_process_unresolved | unresolved_earlier_process_on_or_before_previous_session |
| COHR:2021-01-19 | 29.65% | jump_ok | issuer_identity_was_corrected |
| GSKY:2021-09-15 | 53.15% | jump_ok_prior_process_unresolved | unresolved_earlier_process_on_or_before_previous_session |
| ZGNX:2022-01-19 | 65.73% | jump_ok | none |
| MAXR:2022-12-16 | 124.81% | jump_ok_same_day_earlier_disclosure | earlier_public_same_calendar_day_as_reaction |
| PRVB:2023-03-13 | 259.70% | jump_ok_prior_process_unresolved | unresolved_earlier_process_on_or_before_previous_session |
| RETA:2023-07-28 | 54.02% | jump_ok_prior_close_may_reflect_earlier_public | earlier_public_on_previous_session |
| IMGN:2023-11-30 | 82.63% | jump_ok | none |
| KAMN:2024-01-19 | 100.85% | jump_ok | none |
| CALT:2024-05-28 | 69.27% | jump_ok_ads_security | ads_or_ordinary_share_comparison_hazard |
| ITCI:2025-01-13 | 34.07% | jump_ok | none |
| SAGE:2025-06-16 | 35.37% | jump_ok_earlier_public_before_measured_window | earlier_public_strictly_before_previous_session |

Status meanings: `jump_ok` is clean measurement; `jump_ok_prior_close_may_reflect_earlier_public` means earlier public falls on the previous session used as the jump denominator; `jump_ok_earlier_public_before_measured_window` means an earlier episode before that previous close (announcement-day jump math can still hold); `jump_ok_same_day_earlier_disclosure` means an earlier report on the reaction date; `jump_ok_prior_process_unresolved` means an older public process/rumor upper bound only; `jump_ok_price_source_conflict` / `jump_ok_ads_security` preserve interpretation hazards without invalidating the local close-to-close math.
