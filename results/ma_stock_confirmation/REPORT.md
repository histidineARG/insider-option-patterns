# M&A target stock reaction confirmation

Screened 88 dated target candidates from local maevent records, extracted SEC cases and reviewed M&A examples. This does not cover all 9,465 merger filing documents: those filing dates are not verified announcement dates.

**44 candidates pass the market screen; 28 also have reviewed announcement dates and session timing.**

Rules: reaction-session close / immediately preceding market-session close − 1 ≥ 15%; reaction-session volume / average volume of the preceding 20 calendar trading sessions ≥ 2.0×. The reaction session is the announcement trading date for pre-open/intraday releases, the next session for after-close releases, and the next session for nontrading-day releases. Current-session volume is excluded from the baseline.

Missing previous quotes or any of the required 20 baseline sessions prevent price/volume confirmation. No missing sessions are filled or silently skipped. The calendar is the versioned NYSE snapshot in data/calendar, including the January 9, 2025 closure. Prices are raw stockquote closes; corporate-action adjustment quality is not independently verified.

## Source and timing reviewed passes

| Target | Announcement date | Reaction session | Close return | Volume / prior 20-session mean |
|---|---|---|---:|---:|
| HNZ | 2013-02-14 | 2013-02-14 | 19.87% | 43.06× |
| SFD | 2013-05-29 | 2013-05-29 | 28.42% | 36.00× |
| ONXX | 2013-06-30 | 2013-07-01 | 51.27% | 17.92× |
| BEAM | 2014-01-13 | 2014-01-13 | 24.56% | 63.43× |
| CNQR | 2014-09-18 | 2014-09-19 | 17.64% | 41.84× |
| FMI | 2015-01-12 | 2015-01-12 | 95.32% | 30.41× |
| KRFT | 2015-03-25 | 2015-03-25 | 35.58% | 37.12× |
| PCP | 2015-08-10 | 2015-08-10 | 19.10% | 12.31× |
| ARG | 2015-11-17 | 2015-11-17 | 29.36% | 11.98× |
| AFFX | 2016-01-08 | 2016-01-11 | 51.57% | 147.52× |
| ADT | 2016-02-16 | 2016-02-16 | 47.53% | 22.49× |
| AFOP | 2016-04-07 | 2016-04-08 | 19.34% | 45.92× |
| LNKD | 2016-06-13 | 2016-06-13 | 46.64% | 15.37× |
| JOY | 2016-07-21 | 2016-07-21 | 19.75% | 9.06× |
| SWC | 2016-12-09 | 2016-12-09 | 17.98% | 21.82× |
| CEB | 2017-01-05 | 2017-01-05 | 20.92% | 24.71× |
| BIVV | 2018-01-22 | 2018-01-22 | 61.89% | 35.96× |
| AVXS | 2018-04-09 | 2018-04-09 | 81.57% | 38.00× |
| EFII | 2019-04-15 | 2019-04-15 | 29.25% | 33.79× |
| BOLD | 2019-12-02 | 2019-12-03 | 105.98% | 79.25× |
| VRTU | 2020-09-10 | 2020-09-10 | 24.49% | 35.57× |
| COHR | 2021-01-19 | 2021-01-19 | 29.65% | 25.12× |
| GSKY | 2021-09-15 | 2021-09-15 | 53.15% | 22.66× |
| ZGNX | 2022-01-19 | 2022-01-19 | 65.73% | 47.52× |
| MAXR | 2022-12-16 | 2022-12-16 | 124.81% | 34.99× |
| PRVB | 2023-03-13 | 2023-03-13 | 259.70% | 29.60× |
| RETA | 2023-07-28 | 2023-07-28 | 54.02% | 23.21× |
| IMGN | 2023-11-30 | 2023-11-30 | 82.63% | 13.01× |

## Market passes awaiting date or timing review

| Target | Candidate announcement date | Reaction session | Close return | Volume multiple |
|---|---|---|---:|---:|
| XRTX | 2013-12-23 | 2013-12-23 | 27.27% | 53.56× |
| ZLC | 2014-02-19 | 2014-02-19 | 40.31% | 60.41× |
| SUSS | 2014-04-28 | 2014-04-28 | 36.28% | 17.20× |
| POZN | 2015-06-08 | 2015-06-08 | 18.94% | 13.85× |
| KLAC | 2015-10-21 | 2015-10-21 | 18.79% | 13.27× |
| RSE | 2016-01-19 | 2016-01-19 | 29.73% | 24.70× |
| ALR | 2016-02-01 | 2016-02-01 | 45.46% | 24.01× |
| CSCD | 2016-02-04 | 2016-02-04 | 32.26% | 24.28× |
| LF | 2016-02-05 | 2016-02-05 | 70.18% | 39.73× |
| CKP | 2016-03-02 | 2016-03-02 | 29.28% | 72.10× |
| TUMI | 2016-03-03 | 2016-03-03 | 30.15% | 13.98× |
| VAL | 2016-03-21 | 2016-03-21 | 23.17% | 21.35× |
| RKUS | 2016-04-04 | 2016-04-04 | 32.40% | 59.56× |
| VA | 2016-04-04 | 2016-04-04 | 41.67% | 14.71× |
| GNCMA | 2017-04-04 | 2017-04-04 | 62.40% | 42.25× |
| ODP | 2021-01-11 | 2021-01-11 | 19.43% | 5.59× |

## Data issues and exclusions

Some local maevent symbols identify a seller, divested business parent, minority investment or unverified event. Their exclusion reasons are retained in all_candidates.csv. Mathematical threshold agreement does not establish that the M&A announcement caused the move, and does not establish insider trading.

TUMI passes the price/volume screen on March 3, 2016; SEC proxy materials describe public takeover rumors on that date. It remains pending as a definitive-announcement label. Source: https://www.sec.gov/Archives/edgar/data/1535031/000119312516517061/d166077dprem14a.htm

KAMN on January 19, 2024 rises about 100.85%, but January 8 is missing from its required baseline. CALT on May 28, 2024 rises about 69.27%, but May 1 is missing. Both remain unconfirmed under the strict 20-session volume rule.

AFOP was announced after close April 7, 2016, so its reaction session is April 8. Audentes/BOLD was announced at 6:01pm EST on December 2, 2019, so its reaction session is December 3. The underlying CSVs preserve timing-source links.

Outputs: confirmed_targets.csv (strict confirmations); price_volume_passes.csv (all market passes, including unverified timing); all_candidates.csv (all records, failures, exclusions and missing-data diagnostics).
