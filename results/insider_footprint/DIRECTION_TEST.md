# Direction test

Exchange-traded products were removed before this refit (2,532 of 11,691 symbols; 7,012,933 scored rows versus 8,452,827). The headline is histogram boosting, top 10, 20 sessions.

| Metric | Before | After |
| --- | ---: | ---: |
| Walk-forward hit rate | 0.578 | 0.570 |
| Walk-forward base rate | 0.539 | 0.535 |
| Holdout hit rate | 0.626 | 0.653 |
| Holdout base rate | 0.524 | 0.524 |
| Walk-forward compounded book | 0.65 | 1.32 |
| Walk-forward SPY book | 3.30 | 3.30 |
| Walk-forward random book | 2.42 | 1.07 |
| Holdout compounded book | 1.13 | 0.91 |
| Holdout SPY book | 1.14 | 1.14 |
| Holdout random book | 1.07 | 0.96 |

Boosting still clears the absolute-direction bar: the holdout hit rate is above its own base rate. The compounded book still does not finish ahead of SPY in both samples.

The question is whether a stock is up over the next 5, 10, or 20 sessions, not whether it jumps 15%. Each score uses only the close and earlier data. The last twelve months, from 2025-11-13, were not used to choose a setting. Logistic regression and histogram gradient boosting use fixed settings and retrain once a year on earlier years only. The composite is an equal-weight signed z-score with no fit.

The universe is optionable names with a close of at least $5 and a 20-session median dollar volume of at least $5 million. A round trip costs 10 basis points. Prices that jump by a standard split ratio are put on one share count before the return is measured. A move larger than 70% that is not a split leaves the lookback feature blank.

## What is not in the data

- EDGAR Form 4 insider net buys: no table in optiondb.
- Earnings surprise versus a consensus estimate: not stored. The post-earnings feature is the reaction-session close-to-close return.
- stock_ta_daily is empty, so the 50- and 200-day averages are computed from stockquote.
- ivdaily ends on 2016-07-07. Implied volatility is optionstat mean, call, and put IV.
- daystat, the out-of-the-money call volume source, ends on 2025-12-30, so that feature is absent for most of the holdout.
- erdate ends on 2022-01-04. Later earnings reaction dates come from the 8-K Item 2.02 table already in the repo.

Panel rows: 7012933. Detected split days: 1557. Unexplained breaks: 13268.

## Hit rate

Hit rate is the share of the slate that finished up. The base rate is the same share for every liquid name that day. The interval is a block bootstrap of the daily hit rate, with the block as long as the horizon.

| Sample | Model | Horizon | Slate | Hit rate | Base rate | Random slate | Excess hit | Excess base | 95% interval |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Walk-forward | boost | 5 | 10 | 0.531 | 0.522 | 0.522 | 0.485 | 0.483 | 0.516 to 0.548 |
| Holdout | boost | 5 | 10 | 0.556 | 0.517 | 0.521 | 0.508 | 0.489 | 0.520 to 0.599 |
| Walk-forward | boost | 5 | 20 | 0.532 | 0.522 | 0.524 | 0.487 | 0.483 | 0.518 to 0.549 |
| Holdout | boost | 5 | 20 | 0.548 | 0.517 | 0.517 | 0.504 | 0.489 | 0.515 to 0.586 |
| Walk-forward | boost | 10 | 10 | 0.559 | 0.529 | 0.526 | 0.451 | 0.478 | 0.540 to 0.579 |
| Holdout | boost | 10 | 10 | 0.691 | 0.522 | 0.512 | 0.491 | 0.486 | 0.636 to 0.724 |
| Walk-forward | boost | 10 | 20 | 0.551 | 0.529 | 0.530 | 0.459 | 0.478 | 0.532 to 0.571 |
| Holdout | boost | 10 | 20 | 0.638 | 0.522 | 0.517 | 0.497 | 0.486 | 0.586 to 0.668 |
| Walk-forward | boost | 20 | 10 | 0.570 | 0.535 | 0.531 | 0.409 | 0.470 | 0.544 to 0.596 |
| Holdout | boost | 20 | 10 | 0.653 | 0.524 | 0.515 | 0.465 | 0.474 | 0.591 to 0.693 |
| Walk-forward | boost | 20 | 20 | 0.566 | 0.535 | 0.533 | 0.429 | 0.470 | 0.540 to 0.591 |
| Holdout | boost | 20 | 20 | 0.624 | 0.524 | 0.522 | 0.473 | 0.474 | 0.559 to 0.667 |
| Walk-forward | composite | 5 | 10 | 0.523 | 0.522 | 0.522 | 0.471 | 0.483 | 0.509 to 0.538 |
| Holdout | composite | 5 | 10 | 0.539 | 0.517 | 0.521 | 0.492 | 0.489 | 0.497 to 0.578 |
| Walk-forward | composite | 5 | 20 | 0.526 | 0.522 | 0.524 | 0.477 | 0.483 | 0.513 to 0.541 |
| Holdout | composite | 5 | 20 | 0.540 | 0.517 | 0.517 | 0.500 | 0.489 | 0.504 to 0.573 |
| Walk-forward | composite | 10 | 10 | 0.532 | 0.529 | 0.527 | 0.453 | 0.478 | 0.515 to 0.549 |
| Holdout | composite | 10 | 10 | 0.553 | 0.522 | 0.525 | 0.476 | 0.486 | 0.501 to 0.589 |
| Walk-forward | composite | 10 | 20 | 0.532 | 0.529 | 0.526 | 0.463 | 0.478 | 0.515 to 0.551 |
| Holdout | composite | 10 | 20 | 0.550 | 0.522 | 0.525 | 0.484 | 0.486 | 0.502 to 0.586 |
| Walk-forward | composite | 20 | 10 | 0.541 | 0.535 | 0.533 | 0.444 | 0.470 | 0.515 to 0.565 |
| Holdout | composite | 20 | 10 | 0.514 | 0.524 | 0.540 | 0.433 | 0.474 | 0.408 to 0.594 |
| Walk-forward | composite | 20 | 20 | 0.541 | 0.535 | 0.534 | 0.452 | 0.470 | 0.515 to 0.566 |
| Holdout | composite | 20 | 20 | 0.523 | 0.524 | 0.530 | 0.456 | 0.474 | 0.420 to 0.604 |
| Walk-forward | logistic | 5 | 10 | 0.511 | 0.522 | 0.522 | 0.471 | 0.483 | 0.498 to 0.527 |
| Holdout | logistic | 5 | 10 | 0.530 | 0.517 | 0.521 | 0.512 | 0.489 | 0.485 to 0.574 |
| Walk-forward | logistic | 5 | 20 | 0.515 | 0.522 | 0.524 | 0.475 | 0.483 | 0.503 to 0.532 |
| Holdout | logistic | 5 | 20 | 0.531 | 0.517 | 0.517 | 0.506 | 0.489 | 0.490 to 0.573 |
| Walk-forward | logistic | 10 | 10 | 0.504 | 0.529 | 0.526 | 0.456 | 0.478 | 0.486 to 0.526 |
| Holdout | logistic | 10 | 10 | 0.512 | 0.522 | 0.512 | 0.493 | 0.486 | 0.449 to 0.561 |
| Walk-forward | logistic | 10 | 20 | 0.506 | 0.529 | 0.530 | 0.457 | 0.478 | 0.486 to 0.526 |
| Holdout | logistic | 10 | 20 | 0.535 | 0.522 | 0.517 | 0.512 | 0.486 | 0.481 to 0.585 |
| Walk-forward | logistic | 20 | 10 | 0.516 | 0.535 | 0.531 | 0.442 | 0.470 | 0.486 to 0.546 |
| Holdout | logistic | 20 | 10 | 0.553 | 0.524 | 0.515 | 0.486 | 0.474 | 0.452 to 0.622 |
| Walk-forward | logistic | 20 | 20 | 0.512 | 0.535 | 0.533 | 0.440 | 0.470 | 0.484 to 0.542 |
| Holdout | logistic | 20 | 20 | 0.556 | 0.524 | 0.522 | 0.500 | 0.474 | 0.472 to 0.620 |

## Net return

Average and median forward return after the 10-basis-point cost. The terminal column compounds a non-overlapping book: one slate every horizon, so a 20-session pick is not reopened while it is still held.

| Sample | Model | Horizon | Slate | Mean net | Median net | Random mean net | Basket | SPY | Random basket |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Walk-forward | boost | 5 | 10 | 0.001 | 0.001 | 0.002 | 0.735 | 3.297 | 1.859 |
| Holdout | boost | 5 | 10 | -0.000 | 0.001 | 0.002 | 1.054 | 1.113 | 1.274 |
| Walk-forward | boost | 5 | 20 | 0.001 | 0.001 | 0.001 | 1.020 | 3.297 | 0.917 |
| Holdout | boost | 5 | 20 | 0.001 | 0.001 | 0.006 | 1.080 | 1.113 | 1.112 |
| Walk-forward | boost | 10 | 10 | 0.024 | 0.002 | 0.004 | 0.290 | 3.297 | 1.886 |
| Holdout | boost | 10 | 10 | -0.003 | 0.005 | 0.005 | 0.816 | 1.120 | 1.120 |
| Walk-forward | boost | 10 | 20 | 0.025 | 0.002 | 0.003 | 17.100 | 3.297 | 1.252 |
| Holdout | boost | 10 | 20 | 0.004 | 0.004 | 0.007 | 0.925 | 1.120 | 0.999 |
| Walk-forward | boost | 20 | 10 | 0.035 | 0.001 | 0.007 | 1.322 | 3.297 | 1.074 |
| Holdout | boost | 20 | 10 | 0.002 | 0.008 | 0.451 | 0.911 | 1.142 | 0.961 |
| Walk-forward | boost | 20 | 20 | 0.022 | 0.002 | 0.007 | 1.911 | 3.297 | 2.197 |
| Holdout | boost | 20 | 20 | 0.004 | 0.006 | 0.011 | 0.919 | 1.142 | 1.062 |
| Walk-forward | composite | 5 | 10 | 0.013 | -0.001 | 0.002 | 0.099 | 3.297 | 1.859 |
| Holdout | composite | 5 | 10 | -0.001 | 0.000 | 0.002 | 0.993 | 1.113 | 1.274 |
| Walk-forward | composite | 5 | 20 | 0.015 | -0.000 | 0.001 | 2.939 | 3.297 | 0.917 |
| Holdout | composite | 5 | 20 | 0.001 | 0.001 | 0.006 | 1.049 | 1.113 | 1.112 |
| Walk-forward | composite | 10 | 10 | 0.036 | -0.001 | 0.004 | 0.344 | 3.297 | 2.097 |
| Holdout | composite | 10 | 10 | 0.001 | 0.000 | 0.005 | 0.920 | 1.120 | 1.133 |
| Walk-forward | composite | 10 | 20 | 0.027 | -0.001 | 0.003 | 0.614 | 3.297 | 1.539 |
| Holdout | composite | 10 | 20 | 0.004 | 0.002 | 0.010 | 1.067 | 1.120 | 1.116 |
| Walk-forward | composite | 20 | 10 | 0.056 | 0.001 | 0.009 | 8.321 | 3.297 | 2.200 |
| Holdout | composite | 20 | 10 | 0.002 | -0.007 | 0.013 | 1.243 | 1.142 | 1.280 |
| Walk-forward | composite | 20 | 20 | 0.053 | 0.001 | 0.007 | 86.504 | 3.297 | 1.865 |
| Holdout | composite | 20 | 20 | 0.006 | -0.003 | 0.014 | 1.571 | 1.142 | 1.248 |
| Walk-forward | logistic | 5 | 10 | 0.005 | -0.001 | 0.002 | 0.326 | 3.297 | 1.859 |
| Holdout | logistic | 5 | 10 | 0.002 | 0.004 | 0.002 | 1.243 | 1.113 | 1.274 |
| Walk-forward | logistic | 5 | 20 | 0.002 | -0.001 | 0.001 | 0.911 | 3.297 | 0.917 |
| Holdout | logistic | 5 | 20 | 0.004 | 0.004 | 0.006 | 1.260 | 1.113 | 1.112 |
| Walk-forward | logistic | 10 | 10 | 0.001 | -0.002 | 0.004 | 0.444 | 3.297 | 1.886 |
| Holdout | logistic | 10 | 10 | 0.007 | 0.004 | 0.005 | 1.447 | 1.120 | 1.120 |
| Walk-forward | logistic | 10 | 20 | 0.001 | -0.002 | 0.003 | 0.948 | 3.297 | 1.252 |
| Holdout | logistic | 10 | 20 | 0.010 | 0.006 | 0.007 | 1.426 | 1.120 | 0.999 |
| Walk-forward | logistic | 20 | 10 | 0.003 | -0.001 | 0.007 | 0.519 | 3.297 | 1.074 |
| Holdout | logistic | 20 | 10 | 0.012 | 0.009 | 0.451 | 0.983 | 1.142 | 0.961 |
| Walk-forward | logistic | 20 | 20 | 0.002 | -0.003 | 0.007 | 1.037 | 3.297 | 2.197 |
| Holdout | logistic | 20 | 20 | 0.020 | 0.013 | 0.011 | 1.178 | 1.142 | 1.062 |

## Walk-forward by year, top 10, 20 sessions

| Model | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| composite | -0.020 | 0.016 | 0.016 | -0.035 | -0.009 | 0.002 | 0.017 | 0.011 | 0.052 | 0.007 |
| logistic | -0.016 | -0.062 | 0.015 | -0.022 | 0.018 | -0.095 | 0.043 | -0.043 | -0.031 | 0.011 |
| boost | 0.028 | 0.022 | 0.076 | 0.075 | -0.046 | 0.050 | 0.013 | -0.004 | 0.033 | 0.111 |

The year cells are hit rate minus that year's universe base rate.

## Regime, top 10, 20 sessions

| Sample | Model | SPY vs 200-day average | Dates | Hit rate | Base rate | Mean net |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Walk-forward | boost | above | 2004 | 0.569 | 0.526 | 0.040 |
| Walk-forward | boost | below | 472 | 0.572 | 0.575 | 0.016 |
| Holdout | boost | above | 207 | 0.650 | 0.511 | -0.007 |
| Holdout | boost | below | 12 | 0.700 | 0.759 | 0.143 |
| Walk-forward | composite | above | 2004 | 0.540 | 0.526 | 0.050 |
| Walk-forward | composite | below | 472 | 0.544 | 0.575 | 0.084 |
| Holdout | composite | above | 207 | 0.499 | 0.511 | -0.002 |
| Holdout | composite | below | 12 | 0.766 | 0.759 | 0.067 |
| Walk-forward | logistic | above | 2004 | 0.502 | 0.526 | -0.002 |
| Walk-forward | logistic | below | 472 | 0.577 | 0.575 | 0.025 |
| Holdout | logistic | above | 207 | 0.536 | 0.511 | 0.007 |
| Holdout | logistic | below | 12 | 0.833 | 0.759 | 0.092 |

## Feature weight on the 20-session model

- logistic: dist_ma50 0.095, spy_above_ma200 0.060, dist_ma200 0.053, iv_level 0.051, mom_12_1 0.037, pead 0.021
- boost: spy_above_ma200 0.003, dist_ma50 0.003, dist_ma200 0.003, iv_level 0.003, iv_change 0.003, rvol_20 0.003

## Signed composite

Higher 12-1 momentum, a positive earnings-reaction gap, and a close above the 50- and 200-day averages raise the score. So does an out-of-the-money call-volume surge. The last month's return, realized volatility, the implied-volatility level and its 20-session change, put-minus-call implied volatility, and the put/call volume ratio lower it. SPY versus its 200-day average is a regime flag and a model input. It is the same for every name, so it is not in the cross-sectional composite.

## Verdict

Histogram boosting clears the absolute-direction bar set before the run. On the 20-session top 10 its walk-forward interval sits above the share of liquid names that were up, the holdout is above its own base rate, and at least seven walk-forward years agree. The equal-weight composite and the logistic do not clear that bar. The same boosting slate beats SPY on 40.9% of walk-forward picks against a 47.0% universe rate, and on 46.5% of holdout picks against 47.4%. A non-overlapping 20-session top-10 book finishes at 1.32 times capital over the walk-forward, against 3.30 for SPY and 1.07 for random slates. The holdout book finishes at 0.91, against 1.14 for SPY. There is not a robust edge over SPY. Being up more often than the average stock is not the same as beating the market, and the compounded book does not finish ahead of SPY in both samples. The average net return is also much larger than the median, so a few very large winners carry the mean.
