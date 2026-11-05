# Price-only M&A cohort and option coverage

From 88 dated candidates, 24 have reviewed target/event dates and session timing and a stock close increase of at least 15%. Volume is not an eligibility condition.

| Target | Announcement | Return | Observed pre-event sessions / 30 | Valid 20-session-baseline feature days |
| --- | --- | ---: | ---: | ---: |
| HNZ | 2013-02-14 | 19.87% | 30 | 10 |
| ONXX | 2013-06-30 | 51.27% | 30 | 30 |
| CNQR | 2014-09-18 | 17.64% | 30 | 30 |
| KRFT | 2015-03-25 | 35.58% | 30 | 30 |
| ADT | 2016-02-16 | 47.53% | 30 | 30 |
| AFOP | 2016-04-07 | 19.34% | 30 | 30 |
| LNKD | 2016-06-13 | 46.64% | 30 | 30 |
| JOY | 2016-07-21 | 19.75% | 30 | 30 |
| SWC | 2016-12-09 | 17.98% | 30 | 30 |
| CEB | 2017-01-05 | 20.92% | 30 | 30 |
| BIVV | 2018-01-22 | 61.89% | 30 | 30 |
| AVXS | 2018-04-09 | 81.57% | 30 | 30 |
| EFII | 2019-04-15 | 29.25% | 30 | 30 |
| BOLD | 2019-12-02 | 105.98% | 29 | 10 |
| VRTU | 2020-09-10 | 24.49% | 30 | 30 |
| COHR | 2021-01-19 | 29.65% | 30 | 29 |
| GSKY | 2021-09-15 | 53.15% | 30 | 30 |
| ZGNX | 2022-01-19 | 65.73% | 29 | 23 |
| MAXR | 2022-12-16 | 124.81% | 30 | 19 |
| PRVB | 2023-03-13 | 259.70% | 30 | 30 |
| RETA | 2023-07-28 | 54.02% | 30 | 30 |
| IMGN | 2023-11-30 | 82.63% | 30 | 30 |
| KAMN | 2024-01-19 | 100.85% | 29 | 22 |
| CALT | 2024-05-28 | 69.27% | 30 | 30 |

These are descriptive candidates, not final training labels. First public disclosure, corporate actions, historical security identity, and wider event coverage still require review. Missing volume-baseline stock sessions do not prevent price-only qualification when consecutive reaction prices exist.

Daily features use the immediately preceding 20 calendar trading sessions; gaps invalidate the baseline. Observed zero OTM volume is preserved. No event-day or future option rows are used. The next-session close is a conservative timing proxy, not an executable fill assumption.

The sample was selected using future outcomes and is enriched with SEC cases. It cannot estimate population false positives, false negatives, precision, or profitability. All training labels remain null.
