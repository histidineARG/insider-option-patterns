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
