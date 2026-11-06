# Confirmed M&A only — stockquote reaction jumps

Universe: `event_verified=1` and `target_public_at_announcement=1` in `research_ma_public_company_acquisitions`, plus any `reviewed_cohort` events absent from that table.

Reaction mapping uses announcement_session against the NYSE calendar. Unknown timing is not forced into a single reaction day.

| Year | Confirmed | Timed & measured | Timed ≥15% | Timed ≥20% | Unknown timing | Unknown any ≥20% | Missing quotes |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2013 | 2 | 2 | 2 | 1 | 0 | 0 | 0 |
| 2014 | 2 | 1 | 1 | 0 | 1 | 0 | 0 |
| 2015 | 2 | 1 | 1 | 1 | 1 | 0 | 0 |
| 2016 | 5 | 5 | 5 | 2 | 0 | 0 | 0 |
| 2017 | 2 | 1 | 1 | 1 | 1 | 1 | 0 |
| 2018 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| 2019 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| 2020 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
| 2021 | 3 | 2 | 2 | 2 | 1 | 0 | 0 |
| 2022 | 4 | 2 | 2 | 2 | 2 | 0 | 0 |
| 2023 | 3 | 3 | 3 | 3 | 0 | 0 | 0 |
| 2024 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |
| 2025 | 2 | 2 | 2 | 2 | 0 | 0 | 0 |

### Event detail

| Event | Session | Reaction | Close return | ≥15% | ≥20% | Status |
| --- | --- | --- | ---: | --- | --- | --- |
| HNZ:2013-02-14 | before_open | 2013-02-14 | 19.87% | True | False | measured |
| ONXX:2013-06-30 | nontrading_day | 2013-07-01 | 51.27% | True | True | measured |
| CNQR:2014-09-18 | after_close | 2014-09-19 | 17.64% | True | False | measured |
| BHI:2014-11-17 | unknown | 2014-11-17 | 8.92% | False | False | unknown_timing |
| KRFT:2015-03-25 | before_open | 2015-03-25 | 35.58% | True | True | measured |
| AGN:2015-11-23 | unknown | 2015-11-23 | -3.44% | False | False | unknown_timing |
| ADT:2016-02-16 | before_open | 2016-02-16 | 47.53% | True | True | measured |
| AFOP:2016-04-07 | after_close | 2016-04-08 | 19.34% | True | False | measured |
| LNKD:2016-06-13 | before_open | 2016-06-13 | 46.64% | True | True | measured |
| JOY:2016-07-21 | before_open | 2016-07-21 | 19.75% | True | False | measured |
| SWC:2016-12-09 | before_open | 2016-12-09 | 17.98% | True | False | measured |
| CEB:2017-01-05 | before_open | 2017-01-05 | 20.92% | True | True | measured |
| GNCMA:2017-04-04 | unknown | 2017-04-04 | 62.40% | True | True | unknown_timing |
| BIVV:2018-01-22 | before_open | 2018-01-22 | 61.89% | True | True | measured |
| AVXS:2018-04-09 | before_open | 2018-04-09 | 81.57% | True | True | measured |
| EFII:2019-04-15 | before_open | 2019-04-15 | 29.25% | True | True | measured |
| BOLD:2019-12-02 | after_close | 2019-12-03 | 105.98% | True | True | measured |
| VRTU:2020-09-10 | before_open | 2020-09-10 | 24.49% | True | True | measured |
| ODP:2021-01-11 | unknown | 2021-01-11 | 19.43% | True | False | unknown_timing |
| COHR:2021-01-19 | before_open | 2021-01-19 | 29.65% | True | True | measured |
| GSKY:2021-09-15 | before_open | 2021-09-15 | 53.15% | True | True | measured |
| ZGNX:2022-01-19 | before_open | 2022-01-19 | 65.73% | True | True | measured |
| SAVE:2022-07-28 | unknown | 2022-07-28 | 5.60% | False | False | unknown_timing |
| ACI:2022-10-14 | unknown | 2022-10-14 | -8.45% | False | False | unknown_timing |
| MAXR:2022-12-16 | before_open | 2022-12-16 | 124.81% | True | True | measured |
| PRVB:2023-03-13 | before_open | 2023-03-13 | 259.70% | True | True | measured |
| RETA:2023-07-28 | before_open | 2023-07-28 | 54.02% | True | True | measured |
| IMGN:2023-11-30 | before_open | 2023-11-30 | 82.63% | True | True | measured |
| KAMN:2024-01-19 | before_open | 2024-01-19 | 100.85% | True | True | measured |
| CALT:2024-05-28 | before_open | 2024-05-28 | 69.27% | True | True | measured |
| ITCI:2025-01-13 | before_open | 2025-01-13 | 34.07% | True | True | measured |
| SAGE:2025-06-16 | before_open | 2025-06-16 | 35.37% | True | True | measured |

Total confirmed events: 32. Timed ≥20%: 21.

