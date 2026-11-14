# Gradient-boosting +30% book

The model is a histogram gradient booster trained on a 20-session high of at least 30% above the signal close, refit each year on earlier years only. The holdout starts 2025-11-13 and is not used to choose an exit. Entry is the next open. A same-day stop and target counts as the stop. A gap fills at the open. The trail uses the highest close so far and cannot fire on the entry session. The cost is 10 bps round trip. A hold that reaches an earnings reaction is dropped. The exit is the close H sessions after the entry session when no stop or target hits. The top 0.5% and top 0.1% are ranks within each test year, not a cut taken from later years.

## Are the picks just high-volatility names?

Tails are measured from the entry open over the following 20 sessions. The random columns are names from the same month in the same trailing-volatility decile, and names from the same month in the same predicted-volatility decile. Predicted volatility is a ridge fit on trailing volatility and absolute return, trained only on earlier years, targeting the next 20 sessions of realized volatility.

| Book | N | +30% high | -20% low | -30% low | Median drawdown | Mean forward vol | Random +30% | Random -30% | Random vol |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| top4 | 8651 | 0.315 | 0.477 | 0.285 | -0.273 | 1.294 | 0.203 | 0.166 | 1.243 |
| p05 | 17099 | 0.319 | 0.476 | 0.281 | -0.270 | 1.295 | 0.200 | 0.162 | 1.229 |
| p01 | 3424 | 0.351 | 0.471 | 0.291 | -0.276 | 1.291 | 0.201 | 0.176 | 1.146 |

Drawdown percentiles from the running peak, top 4:

Median -0.273, 10th percentile -0.523, 90th percentile -0.126. Matched-random median -0.202.

## Overlap with a model trained on the -30% low

- top4: 1479 of 8760 upside picks are also downside picks, share 0.169, Jaccard 0.092.
- p05: 4099 of 17265 upside picks are also downside picks, share 0.237, Jaccard 0.135.
- p01: 304 of 3456 upside picks are also downside picks, share 0.088, Jaccard 0.046.

## Trailing volatility of the picks

- top4: median trailing vol 0.075 versus 0.022 for the filtered universe.
- p05: median trailing vol 0.075 versus 0.022 for the filtered universe.
- p01: median trailing vol 0.075 versus 0.022 for the filtered universe.

## Top 4 exits, deduped

| Rule | Sample | N | Mean | Median | Win | Target | Stop | P10 | P90 | Vol-match mean | Pred-vol mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hold-5 | walk | 3232 | -0.004 | -0.016 | 0.444 | 0.000 | 0.000 | -0.192 | 0.171 | 0.002 | 0.001 |
| hold-5 | holdout | 438 | 0.175 | -0.045 | 0.395 | 0.000 | 0.000 | -0.247 | 0.225 | -0.007 | 0.004 |
| hold-10 | walk | 3232 | -0.000 | -0.025 | 0.437 | 0.000 | 0.000 | -0.259 | 0.228 | 0.007 | 0.004 |
| hold-10 | holdout | 438 | 0.032 | -0.048 | 0.420 | 0.000 | 0.000 | -0.337 | 0.284 | 0.022 | 0.005 |
| hold-20 | walk | 3207 | 0.006 | -0.038 | 0.425 | 0.000 | 0.000 | -0.327 | 0.324 | 0.013 | 0.003 |
| hold-20 | holdout | 431 | 0.029 | -0.094 | 0.387 | 0.000 | 0.000 | -0.489 | 0.408 | 0.031 | -0.003 |
| hold-40 | walk | 2594 | 0.018 | -0.088 | 0.386 | 0.000 | 0.000 | -0.466 | 0.444 | 0.028 | 0.019 |
| hold-40 | holdout | 367 | -0.021 | -0.170 | 0.351 | 0.000 | 0.000 | -0.610 | 0.549 | 0.012 | -0.017 |
| tp15-t20 | walk | 3220 | 0.187 | 0.149 | 0.596 | 0.520 | 0.000 | -0.290 | 0.149 | 0.019 | 0.014 |
| tp15-t20 | holdout | 432 | 0.179 | 0.149 | 0.602 | 0.581 | 0.000 | -0.429 | 0.156 | 0.005 | 0.015 |
| tp20-t20 | walk | 3219 | 0.190 | 0.026 | 0.533 | 0.410 | 0.000 | -0.305 | 0.199 | 0.019 | 0.014 |
| tp20-t20 | holdout | 431 | 0.180 | 0.117 | 0.541 | 0.492 | 0.000 | -0.432 | 0.201 | 0.006 | 0.009 |
| tp25-t20 | walk | 3214 | 0.192 | -0.001 | 0.499 | 0.332 | 0.000 | -0.312 | 0.249 | 0.019 | 0.013 |
| tp25-t20 | holdout | 431 | 0.185 | 0.017 | 0.510 | 0.427 | 0.000 | -0.435 | 0.249 | 0.044 | 0.010 |
| tp30-t20 | walk | 3213 | 0.194 | -0.011 | 0.481 | 0.276 | 0.000 | -0.315 | 0.299 | 0.019 | 0.014 |
| tp30-t20 | holdout | 431 | 0.186 | -0.014 | 0.485 | 0.357 | 0.000 | -0.441 | 0.299 | 0.041 | 0.007 |
| tp40-t20 | walk | 3212 | 0.192 | -0.027 | 0.455 | 0.181 | 0.000 | -0.318 | 0.399 | 0.018 | 0.014 |
| tp40-t20 | holdout | 431 | 0.267 | -0.051 | 0.445 | 0.262 | 0.000 | -0.461 | 0.399 | 0.035 | 0.004 |
| tp15-t40 | walk | 2947 | 0.224 | 0.149 | 0.689 | 0.658 | 0.000 | -0.363 | 0.149 | 0.044 | 0.037 |
| tp15-t40 | holdout | 379 | 0.229 | 0.149 | 0.704 | 0.694 | 0.000 | -0.521 | 0.164 | 0.034 | 0.024 |
| tp20-t40 | walk | 2882 | 0.237 | 0.199 | 0.622 | 0.569 | 0.000 | -0.389 | 0.199 | 0.047 | 0.042 |
| tp20-t40 | holdout | 375 | 0.233 | 0.199 | 0.635 | 0.619 | 0.000 | -0.542 | 0.211 | 0.039 | 0.024 |
| tp25-t40 | walk | 2819 | 0.258 | 0.167 | 0.570 | 0.492 | 0.000 | -0.408 | 0.249 | 0.051 | 0.042 |
| tp25-t40 | holdout | 375 | 0.243 | 0.249 | 0.608 | 0.568 | 0.000 | -0.553 | 0.259 | 0.084 | 0.023 |
| tp30-t40 | walk | 2793 | 0.263 | 0.052 | 0.537 | 0.431 | 0.000 | -0.417 | 0.299 | 0.053 | 0.042 |
| tp30-t40 | holdout | 374 | 0.241 | 0.299 | 0.561 | 0.511 | 0.000 | -0.560 | 0.299 | 0.074 | 0.020 |
| tp40-t40 | walk | 2734 | 0.267 | -0.019 | 0.484 | 0.327 | 0.000 | -0.432 | 0.399 | 0.050 | 0.042 |
| tp40-t40 | holdout | 373 | 0.337 | 0.001 | 0.501 | 0.416 | 0.000 | -0.582 | 0.408 | 0.059 | 0.011 |
| trail10-40 | walk | 3188 | -0.012 | -0.055 | 0.331 | 0.000 | 0.986 | -0.154 | 0.172 | -0.006 | -0.010 |
| trail10-40 | holdout | 379 | -0.021 | -0.060 | 0.296 | 0.000 | 1.000 | -0.169 | 0.184 | -0.000 | -0.009 |
| trail15-40 | walk | 3109 | -0.013 | -0.080 | 0.314 | 0.000 | 0.942 | -0.193 | 0.232 | -0.014 | -0.012 |
| trail15-40 | holdout | 377 | -0.022 | -0.083 | 0.292 | 0.000 | 0.989 | -0.201 | 0.242 | -0.006 | -0.010 |
| trail20-40 | walk | 2998 | -0.009 | -0.107 | 0.306 | 0.000 | 0.858 | -0.236 | 0.297 | -0.015 | -0.013 |
| trail20-40 | holdout | 371 | -0.035 | -0.117 | 0.305 | 0.000 | 0.946 | -0.244 | 0.280 | -0.010 | -0.013 |
| stop10-tp30-40 | walk | 3136 | 0.177 | -0.101 | 0.247 | 0.215 | 0.740 | -0.101 | 0.299 | -0.009 | -0.007 |
| stop10-tp30-40 | holdout | 379 | 0.215 | -0.101 | 0.224 | 0.208 | 0.773 | -0.110 | 0.299 | -0.005 | -0.014 |
| stop15-tp30-40 | walk | 3081 | 0.188 | -0.151 | 0.333 | 0.283 | 0.630 | -0.151 | 0.299 | -0.005 | -0.002 |
| stop15-tp30-40 | holdout | 376 | 0.215 | -0.151 | 0.301 | 0.277 | 0.686 | -0.151 | 0.299 | -0.007 | -0.008 |
| stop20-tp30-40 | walk | 3029 | 0.193 | -0.201 | 0.391 | 0.326 | 0.537 | -0.201 | 0.299 | 0.002 | 0.002 |
| stop20-tp30-40 | holdout | 370 | 0.223 | -0.201 | 0.376 | 0.343 | 0.600 | -0.204 | 0.299 | -0.008 | -0.005 |

## Chosen on the walk-forward deduped mean

- top4: tp40-t40. Walk-forward mean 0.267. Holdout mean 0.337, median 0.001, volatility-match 0.059, predicted-vol match 0.011.
- p05: tp40-t40. Walk-forward mean 0.178. Holdout mean 0.158, median -0.001, volatility-match -0.011, predicted-vol match 0.023.
- p01: tp30-t40. Walk-forward mean 0.052. Holdout mean 0.029, median 0.299, volatility-match 0.034, predicted-vol match 7.619.

## Top 4 by year, chosen exit, deduped

Mean cap replaces any trade above +100% with +100%, so one bad print cannot set the year.

| Year | N | Mean | Mean cap | Median | Win | Vol-match mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2018 | 282 | 0.032 | 0.015 | -0.021 | 0.461 | 0.077 |
| 2019 | 327 | 1.769 | 0.033 | -0.022 | 0.474 | 0.025 |
| 2020 | 407 | 0.202 | 0.118 | 0.214 | 0.619 | 0.166 |
| 2021 | 323 | -0.002 | -0.002 | -0.063 | 0.446 | 0.039 |
| 2022 | 443 | -0.032 | -0.032 | -0.056 | 0.438 | -0.016 |
| 2023 | 278 | 0.152 | -0.055 | -0.107 | 0.421 | 0.030 |
| 2024 | 358 | 0.020 | -0.016 | -0.077 | 0.425 | 0.045 |
| 2025 | 351 | 0.072 | 0.055 | 0.100 | 0.561 | 0.069 |
| holdout | 373 | 0.337 | 0.009 | 0.001 | 0.501 | 0.059 |

## Largest top-4 trades, +40% target, 40-session cap

VXZ on 2019-07-22 is scored as a 566x gain. The raw quotes from 2019-07-01 through 2019-09-30 go from about 17.60 to 19.79. The split adjustment, not the market, produced that trade. FFIE, MULN, BFLY, KIDZ, and JDST are the same kind of print.

- VXZ 2019-07-22: 565.571
- BFLY 2026-04-13: 88.536
- KIDZ 2026-03-05: 45.428
- FFIE 2023-07-19: 35.516
- KIDZ 2026-02-26: 35.110
- KIDZ 2026-03-02: 35.110
- FFIE 2023-08-01: 32.093
- MULN 2023-10-27: 27.570
- MULN 2023-10-26: 23.999
- JDST 2020-04-13: 21.364
- JDST 2020-04-21: 21.015
- JDST 2020-04-17: 18.433

## Stock-only top 4, plain 20-session hold

- walk: mean 0.002, median -0.052, volatility-match 0.054, n 2802.
- holdout: mean -0.007, median -0.066, volatility-match -0.013, n 449.

## Portfolio, four names a day, equal slots, versus SPY

| Rule | Sample | CAGR | Max drawdown | Sharpe | SPY CAGR | SPY drawdown | SPY Sharpe |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hold-20 | walk | 0.010 | -0.895 | 0.312 | 0.127 | -0.342 | 0.719 |
| hold-20 | holdout | 0.054 | -0.647 | 0.731 | 0.124 | -0.092 | 0.912 |
| hold-40 | walk | 0.001 | -0.810 | 0.269 | 0.127 | -0.342 | 0.720 |
| hold-40 | holdout | -0.034 | -0.462 | 0.422 | 0.124 | -0.092 | 0.912 |
| tp30-t40 | walk | 0.321 | -0.210 | 0.430 | 0.127 | -0.342 | 0.720 |
| tp30-t40 | holdout | 0.964 | -0.160 | 1.284 | 0.124 | -0.092 | 0.912 |
| tp40-t40 | walk | 0.285 | -0.258 | 0.406 | 0.127 | -0.342 | 0.720 |
| tp40-t40 | holdout | 0.857 | -0.175 | 1.223 | 0.124 | -0.092 | 0.912 |

## Feature attribution

Exact Shapley values of the four feature groups, on the model trained before 2025 and scored on 2025 before the holdout. The value is the average change in predicted probability.
- option_volume: signed 0.003, mean absolute 0.005.
- option_flow: signed -0.001, mean absolute 0.002.
- persistence: signed -0.000, mean absolute 0.001.
- stock: signed 0.039, mean absolute 0.044.

Largest single-feature drops in average precision when that column is shuffled:
- rvol: 0.150
- vol_put_dotm_d45: 0.007
- ret_10: 0.003
- vol_call_atm_dlong: 0.003
- dnot_call: 0.003
- vol_put_itm_d45: 0.002
- vol_call_otm_d45: 0.002
- vol_put_atm_d21: 0.002
- vol_call_atm_d07: 0.001
- doi_z_put_otm_short: 0.001
- vol_put_otm_d21: 0.001
- vol_call_dotm_dlong: 0.001

## Ablation, stock return and trailing volatility only

| Model | Rule | Sample | Precision | Base | Lift | N |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| full | top4 | walk | 0.308 | 0.046 | 6.732 | 7888 |
| full | 0.5% | walk | 0.320 | 0.046 | 6.977 | 15224 |
| full | 0.1% | walk | 0.363 | 0.046 | 7.916 | 3045 |
| full | top4 | holdout | 0.364 | 0.073 | 4.970 | 872 |
| full | 0.5% | holdout | 0.382 | 0.073 | 5.229 | 2037 |
| full | 0.1% | holdout | 0.387 | 0.073 | 5.295 | 408 |
| stock | top4 | walk | 0.310 | 0.046 | 6.762 | 7888 |
| stock | 0.5% | walk | 0.312 | 0.046 | 6.823 | 15233 |
| stock | 0.1% | walk | 0.350 | 0.046 | 7.653 | 3050 |
| stock | top4 | holdout | 0.378 | 0.073 | 5.174 | 872 |
| stock | 0.5% | holdout | 0.409 | 0.073 | 5.596 | 2045 |
| stock | 0.1% | holdout | 0.447 | 0.073 | 6.116 | 427 |

## Verdict

The daily top 4, held with tp40-t40, is the walk-forward exit with the highest deduped mean (26.7%). On the holdout that mean is 33.7%, the median is 0.1%, the same-month same-volatility random mean is 5.9%, and the same predicted-volatility random mean is 1.1%. The holdout mean is 27.7% above that volatility-matched random stock. Capping every trade at +100% cuts the walk-forward mean from 26.7% to 1.7% and the holdout mean from 33.7% to 0.9%. The uncapped mean is a thin gap tail, not the typical trade. VXZ on 2019-07-22 is scored as a 566x gain, while the raw quotes over that window go from about 17.60 to 19.79. From the entry, 31.5% of top-4 names reach a +30% high within 20 sessions and 28.5% reach a -30% low, against 20.3% and 16.6% for the volatility-matched names. Forward volatility is 129.4% against 124.3%. Once volatility is matched, the upside and downside tails are close. The model is largely selecting high-volatility names. 16.9% of the upside top 4 are also top-4 picks of the mirror model trained on a -30% low. Holdout top-4 lift is 4.97 with the option features and 5.17 with trailing return and volatility only. Removing the option-flow features leaves most of the lift in place. A 15% target with a 40-session cap has a median of +14.9% on the picks and the same median on the volatility-matched random book. The target, not the model, sets that median. The four-name holdout portfolio has CAGR 85.7%, max drawdown -17.5%, and Sharpe 1.22, against SPY at 12.4%, -9.2%, and 0.91.
