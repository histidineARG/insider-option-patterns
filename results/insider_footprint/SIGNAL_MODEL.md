# Pre-news signal model

The five-feature logistic separates deal windows from the same stock’s earnings and ordinary windows because of the stock’s own return across the window. Deal windows in the training years are up about 17% from the first session of the window to the session before the headline. Earnings windows and ordinary windows are about flat. That return belongs in the model because the question includes the price path. It is also close to the rule that admitted the window: the ten-session path through the announcement had to be at least 15%. The announcement session itself stays out of every feature.

The four option features on the covering monthly expiry — peak call volume, open-interest build, out-of-the-money share, and call/put volume — are a weak separator once that return is set aside. On 2020–2021 the deal window scores above its earnings window 64% of the time. On 2022 through 2024-11-12 the share is 51%. The five-feature coefficients stay as fit. This second table is a reading of the same rows.

A positive is the window before a deal whose ten-session path is at least 15%. Negatives are that stock’s earnings window and a same-length window 60 sessions earlier. Volume and open interest stay on one expiry. Fit uses 2013–2019. 2020–2021 is the check. The holdout, 2024-11-13 onward, stays out of the fit.

| Fold | Rows | AUC | Deal scores above its earnings | Deal scores above its ordinary window |
| --- | ---: | ---: | ---: | ---: |
| 2013–2019 train | 971 deals in 2880 | 0.829 | 802/954 (84%) | 776/955 (81%) |
| 2020–2021 check | 379 deals in 1107 | 0.814 | 287/355 (81%) | 298/373 (80%) |
| 2022 through 2024-11-12 | 105 deals in 307 | 0.837 | 82/98 (84%) | 87/104 (84%) |

Standardized coefficients, fit on 2013–2019:

- intercept: -0.750
- log_peak_call: -0.319
- log_oi_build: 0.397
- otm_share: -0.088
- log_call_put: 0.134
- pre_return: 1.928

Mean feature value on the 2013–2019 rows:

| Window | Rows | Stock return across the window | Log peak call volume | Log OI build |
| --- | ---: | ---: | ---: | ---: |
| Deal | 971 | 0.169 | 5.409 | 4.605 |
| Earnings | 954 | -0.006 | 4.955 | 4.099 |
| Ordinary | 955 | -0.003 | 4.528 | 3.846 |

The same split and the same ridge, with the stock return removed, leaves the four option features. That check is a reading of the fit above. It is not a second model and it was not used to change the five-feature coefficients.

| Fold | AUC | Deal scores above its earnings | Deal scores above its ordinary window |
| --- | ---: | ---: | ---: |
| 2013–2019 train | 0.607 | 590/899 (66%) | 552/881 (63%) |
| 2020–2021 check | 0.587 | 225/352 (64%) | 225/371 (61%) |
| 2022 through 2024-11-12 | 0.564 | 51/98 (52%) | 64/103 (62%) |

Option-only coefficients:

- intercept: -0.696
- log_peak_call: 0.192
- log_oi_build: 0.166
- otm_share: -0.284
- log_call_put: 0.164

Holdout rows from 2024-11-13 onward: 0. That window was not used.

The earnings calendar ends on 2022-01-04, so the 2022–2024 earnings pairs are only the deals that still have an earlier earnings date on file.

A higher score means the window looks more like the pre-deal windows in the training years than like that stock’s earnings or ordinary windows. It is not an identification of a trader.

## Daily top picks, 2026-11-13

On each session the frozen logistic scores every optionable name from the ten sessions ending at that close. Names are ordered by the linear score, because the probability saturates near 1 when that ten-session return is very large. It names the top 3 and the top 4. A hit is a later close at least 15% above that close, either at the horizon or at the highest close inside it. A one-day move of +100% or −50%, or a split, is not counted as a jump. A session counts only when every name in the slate has a close at that horizon. The coefficients are the 2013–2019 fit. This test does not choose a new cutoff.

The stock return in the score is the change from ten sessions earlier through the scoring close. It does not use the path into a later headline. That return has the largest frozen weight, so the top of the list is the names that already rose the most. On this run the median ten-session return of the highest-ranked name was about 25 times, and the 10th percentile was still about 9 times.

Names scanned: 8616. Scoring sessions: 1221. Standardization check gap: 0.0.

| Slate | Horizon | Jump | Dates | Date hit rate | Random slate | Hit rate per pick | False picks per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| top 3 | 5 | terminal | 956 | 0.306 | 0.080 | 0.120 | 7.337 | 0 | 11 | 333 |
| top 3 | 5 | peak | 956 | 0.474 | 0.108 | 0.199 | 4.032 | 2 | 20 | 548 |
| top 3 | 10 | terminal | 777 | 0.413 | 0.148 | 0.177 | 4.658 | 1 | 32 | 379 |
| top 3 | 10 | peak | 777 | 0.644 | 0.221 | 0.311 | 2.211 | 7 | 48 | 671 |
| top 3 | 20 | terminal | 505 | 0.481 | 0.246 | 0.202 | 3.951 | 8 | 34 | 264 |
| top 3 | 20 | peak | 505 | 0.770 | 0.386 | 0.411 | 1.432 | 15 | 72 | 536 |
| top 4 | 5 | terminal | 934 | 0.401 | 0.104 | 0.127 | 6.899 | 1 | 13 | 459 |
| top 4 | 5 | peak | 934 | 0.584 | 0.141 | 0.204 | 3.896 | 3 | 22 | 738 |
| top 4 | 10 | terminal | 746 | 0.517 | 0.191 | 0.181 | 4.536 | 3 | 41 | 495 |
| top 4 | 10 | peak | 746 | 0.752 | 0.282 | 0.316 | 2.168 | 11 | 62 | 869 |
| top 4 | 20 | terminal | 472 | 0.568 | 0.311 | 0.209 | 3.792 | 11 | 38 | 345 |
| top 4 | 20 | peak | 472 | 0.852 | 0.473 | 0.412 | 1.430 | 18 | 84 | 675 |

Date hit rate is the share of sessions where at least one name in the slate jumps. Random slate is the average probability that a random draw of the same size, from that session’s optionable names, contains a jump. False picks per hit is the number of slate names that do not jump divided by the number that do.

M&A uses the EDGAR announcement table and the earlier headline pool when the reaction session falls inside the forward window. Earnings uses 8-K Item 2.02 reaction sessions in that window. A jump with neither is other. A rank is a review tag, not an identification of a trader.

No new high-precision rule is frozen from this table. A cutoff chosen after these rates would be a proposal for a later test.
