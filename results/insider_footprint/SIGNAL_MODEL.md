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

On each session the frozen logistic scores every optionable name from the sessions in the 40 calendar days ending at that close. A single day in that span sets the peak call volume and the largest open-interest build. Several days add up in the call/put total. Names are ordered by the linear score. The five-feature score still includes the stock’s own return over that span. The option-only score leaves that return out, so one call print can rank a name that has not already run up. It names the top 3 and the top 4. A hit is a later close at least 15% above the scoring close, either at 5, 10, or 20 sessions or inside the next 40 calendar days. A one-day move of +100% or −50%, or a split, is not counted as a jump. A session counts only when every name in the slate has a close at that horizon. The coefficients are the 2013–2019 fit. This test does not choose a new cutoff.

The stock return stops at the scoring close. It does not use the path into a later headline.

Names scanned: 6185. Scoring sessions: 1182. Standardization check gap: 0.0.

| Score | Slate | Horizon | Jump | Dates | Date hit rate | Random slate | Hit rate per pick | False picks per hit | M&A | Earnings | Other |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| five-feature | top 3 | 5 | terminal | 927 | 0.303 | 0.097 | 0.118 | 7.453 | 6 | 27 | 296 |
| five-feature | top 3 | 5 | peak | 927 | 0.451 | 0.131 | 0.186 | 4.390 | 8 | 36 | 472 |
| five-feature | top 3 | 10 | terminal | 742 | 0.414 | 0.178 | 0.169 | 4.905 | 5 | 45 | 327 |
| five-feature | top 3 | 10 | peak | 742 | 0.636 | 0.264 | 0.296 | 2.373 | 12 | 67 | 581 |
| five-feature | top 3 | 20 | terminal | 446 | 0.442 | 0.296 | 0.207 | 3.830 | 7 | 46 | 224 |
| five-feature | top 3 | 20 | peak | 446 | 0.722 | 0.451 | 0.402 | 1.487 | 13 | 87 | 438 |
| five-feature | top 3 | 40d | terminal | 375 | 0.427 | 0.366 | 0.220 | 3.536 | 3 | 46 | 199 |
| five-feature | top 3 | 40d | peak | 375 | 0.765 | 0.547 | 0.445 | 1.246 | 11 | 94 | 396 |
| five-feature | top 4 | 5 | terminal | 919 | 0.366 | 0.126 | 0.118 | 7.470 | 6 | 31 | 397 |
| five-feature | top 4 | 5 | peak | 919 | 0.522 | 0.169 | 0.183 | 4.454 | 9 | 41 | 624 |
| five-feature | top 4 | 10 | terminal | 730 | 0.479 | 0.226 | 0.163 | 5.134 | 5 | 53 | 418 |
| five-feature | top 4 | 10 | peak | 730 | 0.690 | 0.329 | 0.287 | 2.484 | 14 | 80 | 744 |
| five-feature | top 4 | 20 | terminal | 435 | 0.510 | 0.367 | 0.206 | 3.847 | 9 | 57 | 293 |
| five-feature | top 4 | 20 | peak | 435 | 0.782 | 0.542 | 0.403 | 1.479 | 17 | 106 | 579 |
| five-feature | top 4 | 40d | terminal | 366 | 0.503 | 0.447 | 0.221 | 3.533 | 6 | 58 | 259 |
| five-feature | top 4 | 40d | peak | 366 | 0.820 | 0.642 | 0.441 | 1.270 | 16 | 114 | 515 |

Highest five-feature name: median lookback return 33.600, 10th percentile 15.659.
| option-only | top 3 | 5 | terminal | 1088 | 0.090 | 0.100 | 0.032 | 29.792 | 5 | 1 | 100 |
| option-only | top 3 | 5 | peak | 1088 | 0.114 | 0.134 | 0.041 | 23.358 | 5 | 3 | 126 |
| option-only | top 3 | 10 | terminal | 1000 | 0.185 | 0.180 | 0.065 | 14.306 | 7 | 4 | 185 |
| option-only | top 3 | 10 | peak | 1000 | 0.271 | 0.266 | 0.099 | 9.067 | 8 | 5 | 285 |
| option-only | top 3 | 20 | terminal | 852 | 0.311 | 0.293 | 0.119 | 7.380 | 18 | 17 | 270 |
| option-only | top 3 | 20 | peak | 852 | 0.477 | 0.446 | 0.192 | 4.195 | 24 | 32 | 436 |
| option-only | top 3 | 40d | terminal | 763 | 0.381 | 0.355 | 0.159 | 5.306 | 32 | 42 | 289 |
| option-only | top 3 | 40d | peak | 763 | 0.549 | 0.539 | 0.248 | 3.037 | 34 | 71 | 462 |
| option-only | top 4 | 5 | terminal | 1081 | 0.107 | 0.129 | 0.030 | 32.262 | 6 | 1 | 123 |
| option-only | top 4 | 5 | peak | 1081 | 0.137 | 0.172 | 0.038 | 25.048 | 6 | 3 | 157 |
| option-only | top 4 | 10 | terminal | 988 | 0.222 | 0.229 | 0.061 | 15.398 | 9 | 4 | 228 |
| option-only | top 4 | 10 | peak | 988 | 0.328 | 0.332 | 0.095 | 9.511 | 11 | 7 | 358 |
| option-only | top 4 | 20 | terminal | 825 | 0.366 | 0.362 | 0.114 | 7.753 | 25 | 23 | 329 |
| option-only | top 4 | 20 | peak | 825 | 0.554 | 0.533 | 0.185 | 4.392 | 34 | 41 | 537 |
| option-only | top 4 | 40d | terminal | 734 | 0.447 | 0.430 | 0.154 | 5.510 | 40 | 59 | 352 |
| option-only | top 4 | 40d | peak | 734 | 0.638 | 0.628 | 0.244 | 3.095 | 47 | 94 | 576 |

Highest option-only name: median lookback return 0.015, 10th percentile -0.116.

Date hit rate is the share of sessions where at least one name in the slate jumps. Random slate is the average probability that a random draw of the same size, from that session’s optionable names, contains a jump. False picks per hit is the number of slate names that do not jump divided by the number that do.

M&A uses the EDGAR announcement table and the earlier headline pool when the reaction session falls inside the forward window. Earnings uses 8-K Item 2.02 reaction sessions in that window. A jump with neither is other. A rank is a review tag, not an identification of a trader.

No new high-precision rule is frozen from this table. A cutoff chosen after these rates would be a proposal for a later test.
