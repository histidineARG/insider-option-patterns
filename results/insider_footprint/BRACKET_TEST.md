# Long-stock brackets on the anomaly tail

Exchange-traded products were removed before this refit (550 of 5,299 symbols). Deduped means use the next open. The walk-forward choice changed. Neither holdout has a positive mean that beats its matched random book.

| Book | Walk mean | Holdout mean | Holdout random mean | Holdout n |
| --- | ---: | ---: | ---: | ---: |
| Before: iforest 1-day p05, stop 3%, target 15%, 20 sessions | 0.036 | -0.028 | -0.016 | 1269 |
| After: hbos 1-day top 4, stop 3%, target 15%, 10 sessions | -0.004 | -0.013 | -0.013 | 619 |

The bracket still does not beat the random book with a positive expectancy.

Signals are the anomaly-test HBOS scores for the 1-day and 5-day windows and the isolation-forest scores for the 1-day window, against the 100-day baseline. Top 1% and top 0.5% use the training-score threshold. Top 4 is the four highest scores that day. The bracket is chosen by the highest deduped walk-forward mean. The holdout from 2025-11-13 is not part of that choice.

The fill for the live book is the next session open. The signal-close fill is only a reference. Stops are 3%, 5%, and 8%. Targets are 15%, 20%, 25%, 28.33%, 30%, and 40%. A 5% stop needs a target above 28.33% before a 15% win rate has a positive expectancy, because the payoff ratio then exceeds 5.667. If the stop and the target are both touched in one session, the stop is filled. A gap through the stop is filled at the open. Time exits use that session's close. Costs are 10 bps round trip, plus 10 bps more on a stop. One name is kept once per 20 sessions in the deduped book. Random names are from the same month and the same volatility decile.

## Five percent stop, 20 sessions, HBOS 1-day top 1%, next open

| Target | Theoretical b | Sample | N | Target rate | Stop rate | Time exit | Realized p | Realized b | Mean | Median | Kelly f* | Random mean |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 15.00% | 3.00 | walk | 17596 | 0.147 | 0.657 | 0.195 | 0.302 | 1.856 | -0.008 | -0.052 | -0.074 | -0.005 |
| 15.00% | 3.00 | holdout | 1929 | 0.176 | 0.684 | 0.140 | 0.287 | 1.404 | -0.025 | -0.052 | -0.220 | -0.023 |
| 20.00% | 4.00 | walk | 17502 | 0.093 | 0.674 | 0.233 | 0.284 | 1.981 | -0.009 | -0.052 | -0.078 | -0.006 |
| 20.00% | 4.00 | holdout | 1924 | 0.120 | 0.709 | 0.172 | 0.262 | 1.549 | -0.027 | -0.052 | -0.214 | -0.023 |
| 25.00% | 5.00 | walk | 17446 | 0.061 | 0.682 | 0.257 | 0.275 | 2.041 | -0.009 | -0.052 | -0.080 | -0.007 |
| 25.00% | 5.00 | holdout | 1923 | 0.085 | 0.719 | 0.196 | 0.251 | 1.638 | -0.027 | -0.052 | -0.206 | -0.024 |
| 28.33% | 5.67 | walk | 17428 | 0.048 | 0.685 | 0.267 | 0.273 | 2.065 | -0.009 | -0.052 | -0.080 | -0.007 |
| 28.33% | 5.67 | holdout | 1921 | 0.068 | 0.723 | 0.209 | 0.247 | 1.658 | -0.028 | -0.052 | -0.207 | -0.025 |
| 30.00% | 6.00 | walk | 17419 | 0.044 | 0.686 | 0.271 | 0.271 | 2.078 | -0.009 | -0.052 | -0.079 | -0.007 |
| 30.00% | 6.00 | holdout | 1921 | 0.060 | 0.723 | 0.217 | 0.246 | 1.673 | -0.028 | -0.052 | -0.205 | -0.024 |
| 40.00% | 8.00 | walk | 17385 | 0.023 | 0.690 | 0.287 | 0.267 | 2.100 | -0.010 | -0.052 | -0.082 | -0.008 |
| 40.00% | 8.00 | holdout | 1916 | 0.033 | 0.729 | 0.239 | 0.240 | 1.698 | -0.029 | -0.052 | -0.207 | -0.026 |

## Best walk-forward bracket for each signal, and its holdout

| Signal | Stop | Target | Hold | Sample | Deduped mean | Median | Realized p | Realized b | Kelly f* | Random mean | Close-entry mean |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hbos 1d p1 | 3% | 15.00% | 10 | walk | -0.005 | -0.032 | 0.255 | 2.355 | -0.062 | -0.003 | -0.004 |
| hbos 1d p1 | 3% | 15.00% | 10 | holdout | -0.017 | -0.032 | 0.240 | 1.781 | -0.187 | -0.016 | -0.016 |
| hbos 1d p05 | 3% | 15.00% | 10 | walk | -0.005 | -0.032 | 0.250 | 2.426 | -0.059 | -0.003 | -0.003 |
| hbos 1d p05 | 3% | 15.00% | 10 | holdout | -0.016 | -0.032 | 0.231 | 1.906 | -0.173 | -0.018 | -0.017 |
| hbos 1d top4 | 3% | 15.00% | 10 | walk | -0.004 | -0.032 | 0.258 | 2.446 | -0.046 | -0.005 | -0.004 |
| hbos 1d top4 | 3% | 15.00% | 10 | holdout | -0.013 | -0.032 | 0.258 | 1.849 | -0.142 | -0.013 | -0.016 |
| hbos 5d p1 | 3% | 15.00% | 10 | walk | -0.006 | -0.032 | 0.246 | 2.363 | -0.073 | -0.003 | -0.004 |
| hbos 5d p1 | 3% | 15.00% | 10 | holdout | -0.021 | -0.032 | 0.220 | 1.758 | -0.224 | -0.020 | -0.026 |
| hbos 5d p05 | 3% | 15.00% | 10 | walk | -0.004 | -0.032 | 0.241 | 2.619 | -0.049 | -0.004 | -0.003 |
| hbos 5d p05 | 3% | 15.00% | 10 | holdout | -0.022 | -0.032 | 0.246 | 1.625 | -0.218 | -0.015 | -0.035 |
| hbos 5d top4 | 3% | 15.00% | 10 | walk | -0.004 | -0.032 | 0.245 | 2.612 | -0.044 | -0.005 | -0.003 |
| hbos 5d top4 | 3% | 15.00% | 10 | holdout | -0.021 | -0.032 | 0.262 | 1.483 | -0.236 | -0.010 | -0.022 |
| iforest 1d p1 | 3% | 15.00% | 10 | walk | -0.006 | -0.032 | 0.262 | 2.133 | -0.084 | -0.004 | -0.006 |
| iforest 1d p1 | 3% | 15.00% | 10 | holdout | 0.541 | -0.032 | 0.231 | 45.098 | 0.214 | -0.017 | -0.022 |
| iforest 1d p05 | 3% | 15.00% | 10 | walk | -0.006 | -0.032 | 0.251 | 2.269 | -0.079 | -0.005 | -0.005 |
| iforest 1d p05 | 3% | 15.00% | 10 | holdout | -0.024 | -0.032 | 0.207 | 1.673 | -0.267 | -0.012 | -0.019 |
| iforest 1d top4 | 3% | 15.00% | 10 | walk | -0.006 | -0.032 | 0.248 | 2.362 | -0.071 | -0.005 | -0.003 |
| iforest 1d top4 | 3% | 15.00% | 10 | holdout | -0.020 | -0.032 | 0.236 | 1.686 | -0.217 | -0.018 | -0.013 |

## Chosen rule

Walk-forward choice: hbos 1-day top4, stop 3%, target 15.00%, hold 10 sessions.
One percent risk, 20 names at most: terminal 0.000, CAGR -0.718, max drawdown 1.000, Sharpe -1.309.
Quarter-Kelly risk 0.000: terminal n/a, CAGR n/a, max drawdown n/a, Sharpe n/a.

## Verdict

hbos 1-day top4, stop 3%, target 15.00%, 10 sessions is the walk-forward choice. In the holdout the deduped mean is -0.013 and the matched random mean is -0.013, a difference of 0.000. The bracket does not beat the random book with a positive expectancy. Buying the stock on the anomaly and bracketing it is not an improvement on doing the same trade at random.
