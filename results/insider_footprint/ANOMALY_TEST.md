# Options-flow anomalies before price jumps

Exchange-traded products were removed before this refit (550 of 5,299 symbols; 4,749 names were already cached). Lift is the 20-session 15% jump rate in the top 1% divided by the universe rate.

| Method | Window | Baseline | Walk lift before | Walk lift after | Holdout lift before | Holdout lift after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hbos | 1 | 50 | 1.621 | 1.549 | 1.449 | 1.346 |
| iforest | 1 | 50 | 1.442 | 1.419 | 1.246 | 1.164 |
| lof | 1 | 50 | 1.154 | 1.172 | 1.022 | 0.971 |
| ocsvm | 1 | 50 | 1.239 | 1.234 | 1.058 | 1.010 |
| mahalanobis | 1 | 50 | 1.210 | 1.234 | 0.969 | 0.981 |
| pca | 1 | 50 | 1.130 | 1.165 | 0.909 | 0.896 |
| hbos | 1 | 100 | 1.792 | 1.692 | 1.639 | 1.487 |
| iforest | 1 | 100 | 1.582 | 1.557 | 1.340 | 1.287 |
| lof | 1 | 100 | 1.291 | 1.324 | 1.146 | 1.009 |
| ocsvm | 1 | 100 | 1.342 | 1.371 | 1.110 | 1.087 |
| mahalanobis | 1 | 100 | 1.334 | 1.331 | 1.099 | 1.004 |

HBOS and isolation forest still clear the pre-set bar on the 1-day window at both baselines. LOF on the 50-day baseline no longer does: its holdout lift is 0.971. The full clear list is in the verdict.

Each score uses a 1, 3, or 5 session window ending at that close. The baseline is the 50 or 100 sessions before that window, so the window itself is not in the average. A name is kept only when the split-adjusted close is at least $10, it has a listed chain that day, average daily option volume over the baseline is at least 100 contracts, and at least 40 baseline sessions are usable. The chain scan itself keeps symbols whose average volume since 2017 is at least 100, so a name that is usually quieter is not pulled. Earnings reaction sessions, and the two sessions before them, are not scored. A forward jump that lands on an earnings reaction is not counted.

PyOD is not installed, so the histogram method is a direct HBOS. The autoencoder is an 8-component reconstruction. Isolation forest, local outlier factor, and a one-class SVM are the other detectors, plus a Ledoit-Wolf Mahalanobis distance. Thresholds are the training-score quantiles. The holdout from 2025-11-13 is fit only on earlier rows.

Earnings dates come from `erdate` through 2022-01-04 and from 8-K Item 2.02 reaction sessions after that. Names missing from both calendars are not earnings-filtered. Earnings are not inferred from the price jump itself. Open interest enters as today minus yesterday, never tomorrow. Dollar premium is the bid-ask midpoint times volume times 100. Delta-weighted notional uses absolute delta when delta is present; otherwise the bucket is assigned from strike over spot.

Symbols on a calendar with no earnings date: 713. Detected split steps: applied inside each price series before the $10 filter and the jump labels.

## Universe

| Window | Baseline | Tickers | Ticker-days |
| ---: | ---: | ---: | ---: |
| 1 | 50 | 3935 | 3860964 |
| 1 | 100 | 3877 | 3817236 |
| 3 | 50 | 3929 | 3772830 |
| 3 | 100 | 3873 | 3730511 |
| 5 | 50 | 3926 | 3685256 |
| 5 | 100 | 3868 | 3644322 |

## Lift at the top 1 percent, 20-session 15 percent jump

Lift is the jump rate inside the anomaly over the jump rate of the whole universe. The interval resamples tickers.

| Method | Window | Baseline | Walk-forward lift | Interval | Holdout lift | Interval |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| mahalanobis | 1 | 50 | 1.23 | 1.19 to 1.28 | 0.98 | 0.91 to 1.05 |
| hbos | 1 | 50 | 1.55 | 1.49 to 1.60 | 1.35 | 1.25 to 1.43 |
| iforest | 1 | 50 | 1.42 | 1.38 to 1.46 | 1.16 | 1.09 to 1.24 |
| lof | 1 | 50 | 1.17 | 1.14 to 1.21 | 0.97 | 0.90 to 1.05 |
| ocsvm | 1 | 50 | 1.23 | 1.20 to 1.27 | 1.01 | 0.95 to 1.08 |
| pca | 1 | 50 | 1.16 | 1.13 to 1.20 | 0.90 | 0.84 to 0.96 |
| mahalanobis | 1 | 100 | 1.33 | 1.27 to 1.39 | 1.00 | 0.92 to 1.09 |
| hbos | 1 | 100 | 1.69 | 1.62 to 1.77 | 1.49 | 1.36 to 1.62 |
| iforest | 1 | 100 | 1.56 | 1.51 to 1.61 | 1.29 | 1.19 to 1.40 |
| lof | 1 | 100 | 1.32 | 1.27 to 1.38 | 1.01 | 0.93 to 1.09 |
| ocsvm | 1 | 100 | 1.37 | 1.32 to 1.42 | 1.09 | 0.99 to 1.18 |
| pca | 1 | 100 | 1.26 | 1.21 to 1.32 | 0.97 | 0.88 to 1.06 |
| mahalanobis | 3 | 50 | 1.25 | 1.19 to 1.30 | 0.92 | 0.82 to 1.01 |
| hbos | 3 | 50 | 1.45 | 1.39 to 1.50 | 1.35 | 1.25 to 1.47 |
| iforest | 3 | 50 | 1.36 | 1.31 to 1.41 | 1.14 | 1.05 to 1.26 |
| lof | 3 | 50 | 1.18 | 1.13 to 1.24 | 0.94 | 0.86 to 1.03 |
| ocsvm | 3 | 50 | 1.24 | 1.18 to 1.29 | 1.01 | 0.92 to 1.10 |
| pca | 3 | 50 | 1.21 | 1.15 to 1.27 | 0.87 | 0.78 to 0.95 |
| mahalanobis | 3 | 100 | 1.37 | 1.31 to 1.44 | 1.01 | 0.89 to 1.12 |
| hbos | 3 | 100 | 1.65 | 1.58 to 1.71 | 1.51 | 1.33 to 1.65 |
| iforest | 3 | 100 | 1.54 | 1.48 to 1.61 | 1.29 | 1.16 to 1.40 |
| lof | 3 | 100 | 1.27 | 1.19 to 1.33 | 1.01 | 0.91 to 1.10 |
| ocsvm | 3 | 100 | 1.35 | 1.29 to 1.41 | 1.01 | 0.88 to 1.12 |
| pca | 3 | 100 | 1.32 | 1.25 to 1.38 | 0.93 | 0.82 to 1.04 |
| mahalanobis | 5 | 50 | 1.26 | 1.20 to 1.33 | 0.92 | 0.82 to 1.02 |
| hbos | 5 | 50 | 1.49 | 1.43 to 1.56 | 1.39 | 1.27 to 1.53 |
| iforest | 5 | 50 | 1.40 | 1.33 to 1.47 | 1.18 | 1.05 to 1.30 |
| lof | 5 | 50 | 1.22 | 1.16 to 1.28 | 0.93 | 0.82 to 1.03 |
| ocsvm | 5 | 50 | 1.28 | 1.21 to 1.34 | 1.02 | 0.91 to 1.13 |
| pca | 5 | 50 | 1.19 | 1.13 to 1.26 | 0.85 | 0.76 to 0.95 |
| mahalanobis | 5 | 100 | 1.37 | 1.31 to 1.45 | 1.05 | 0.93 to 1.20 |
| hbos | 5 | 100 | 1.69 | 1.62 to 1.77 | 1.57 | 1.38 to 1.75 |
| iforest | 5 | 100 | 1.60 | 1.53 to 1.67 | 1.29 | 1.11 to 1.45 |
| lof | 5 | 100 | 1.29 | 1.22 to 1.36 | 0.98 | 0.86 to 1.07 |
| ocsvm | 5 | 100 | 1.37 | 1.30 to 1.45 | 1.04 | 0.91 to 1.19 |
| pca | 5 | 100 | 1.29 | 1.22 to 1.37 | 0.98 | 0.87 to 1.10 |

## Other thresholds and horizons, 5-session window, 50-session baseline

| Method | Sample | Threshold | Horizon | Jump | Lift | Conditional rate | Base rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mahalanobis | walk | 1.0% | 1 | 15% | 5.58 | 0.01 | 0.00 |
| mahalanobis | walk | 1.0% | 5 | 15% | 2.24 | 0.06 | 0.03 |
| mahalanobis | walk | 1.0% | 10 | 15% | 1.57 | 0.11 | 0.07 |
| mahalanobis | walk | 1.0% | 5 | 10% | 1.69 | 0.11 | 0.07 |
| mahalanobis | holdout | 1.0% | 1 | 15% | 2.65 | 0.01 | 0.00 |
| mahalanobis | holdout | 1.0% | 5 | 15% | 1.29 | 0.05 | 0.04 |
| mahalanobis | holdout | 1.0% | 10 | 15% | 0.95 | 0.09 | 0.10 |
| mahalanobis | holdout | 1.0% | 5 | 10% | 1.11 | 0.10 | 0.09 |
| mahalanobis | walk | 0.5% | 1 | 15% | 6.77 | 0.02 | 0.00 |
| mahalanobis | walk | 0.5% | 5 | 15% | 2.51 | 0.07 | 0.03 |
| mahalanobis | walk | 0.5% | 10 | 15% | 1.68 | 0.12 | 0.07 |
| mahalanobis | walk | 0.5% | 20 | 15% | 1.32 | 0.20 | 0.15 |
| mahalanobis | walk | 0.5% | 5 | 10% | 1.83 | 0.12 | 0.07 |
| mahalanobis | holdout | 0.5% | 1 | 15% | 2.08 | 0.01 | 0.00 |
| mahalanobis | holdout | 0.5% | 5 | 15% | 1.26 | 0.05 | 0.04 |
| mahalanobis | holdout | 0.5% | 10 | 15% | 0.84 | 0.08 | 0.10 |
| mahalanobis | holdout | 0.5% | 20 | 15% | 0.80 | 0.16 | 0.21 |
| mahalanobis | holdout | 0.5% | 5 | 10% | 1.03 | 0.09 | 0.09 |
| mahalanobis | walk | 0.1% | 1 | 15% | 10.35 | 0.03 | 0.00 |
| mahalanobis | walk | 0.1% | 5 | 15% | 3.38 | 0.09 | 0.03 |
| mahalanobis | walk | 0.1% | 10 | 15% | 2.10 | 0.14 | 0.07 |
| mahalanobis | walk | 0.1% | 20 | 15% | 1.46 | 0.22 | 0.15 |
| mahalanobis | walk | 0.1% | 5 | 10% | 2.18 | 0.15 | 0.07 |
| mahalanobis | holdout | 0.1% | 1 | 15% | 1.63 | 0.01 | 0.00 |
| mahalanobis | holdout | 0.1% | 5 | 15% | 1.23 | 0.05 | 0.04 |
| mahalanobis | holdout | 0.1% | 10 | 15% | 0.73 | 0.07 | 0.10 |
| mahalanobis | holdout | 0.1% | 20 | 15% | 0.67 | 0.14 | 0.21 |
| mahalanobis | holdout | 0.1% | 5 | 10% | 0.98 | 0.09 | 0.09 |
| hbos | walk | 1.0% | 1 | 15% | 6.88 | 0.02 | 0.00 |
| hbos | walk | 1.0% | 5 | 15% | 2.82 | 0.08 | 0.03 |
| hbos | walk | 1.0% | 10 | 15% | 1.97 | 0.14 | 0.07 |
| hbos | walk | 1.0% | 5 | 10% | 2.06 | 0.14 | 0.07 |
| hbos | holdout | 1.0% | 1 | 15% | 5.18 | 0.02 | 0.00 |
| hbos | holdout | 1.0% | 5 | 15% | 2.26 | 0.09 | 0.04 |
| hbos | holdout | 1.0% | 10 | 15% | 1.61 | 0.16 | 0.10 |
| hbos | holdout | 1.0% | 5 | 10% | 1.83 | 0.17 | 0.09 |
| hbos | walk | 0.5% | 1 | 15% | 7.60 | 0.02 | 0.00 |
| hbos | walk | 0.5% | 5 | 15% | 3.05 | 0.08 | 0.03 |
| hbos | walk | 0.5% | 10 | 15% | 2.08 | 0.14 | 0.07 |
| hbos | walk | 0.5% | 20 | 15% | 1.54 | 0.23 | 0.15 |
| hbos | walk | 0.5% | 5 | 10% | 2.21 | 0.15 | 0.07 |
| hbos | holdout | 0.5% | 1 | 15% | 5.90 | 0.02 | 0.00 |
| hbos | holdout | 0.5% | 5 | 15% | 2.35 | 0.09 | 0.04 |
| hbos | holdout | 0.5% | 10 | 15% | 1.66 | 0.16 | 0.10 |
| hbos | holdout | 0.5% | 20 | 15% | 1.41 | 0.29 | 0.21 |
| hbos | holdout | 0.5% | 5 | 10% | 1.93 | 0.18 | 0.09 |
| hbos | walk | 0.1% | 1 | 15% | 10.42 | 0.03 | 0.00 |
| hbos | walk | 0.1% | 5 | 15% | 3.48 | 0.10 | 0.03 |
| hbos | walk | 0.1% | 10 | 15% | 2.18 | 0.15 | 0.07 |
| hbos | walk | 0.1% | 20 | 15% | 1.55 | 0.23 | 0.15 |
| hbos | walk | 0.1% | 5 | 10% | 2.40 | 0.16 | 0.07 |
| hbos | holdout | 0.1% | 1 | 15% | 6.24 | 0.02 | 0.00 |
| hbos | holdout | 0.1% | 5 | 15% | 2.76 | 0.11 | 0.04 |
| hbos | holdout | 0.1% | 10 | 15% | 1.80 | 0.17 | 0.10 |
| hbos | holdout | 0.1% | 20 | 15% | 1.43 | 0.29 | 0.21 |
| hbos | holdout | 0.1% | 5 | 10% | 1.98 | 0.18 | 0.09 |
| iforest | walk | 1.0% | 1 | 15% | 6.65 | 0.02 | 0.00 |
| iforest | walk | 1.0% | 5 | 15% | 2.64 | 0.07 | 0.03 |
| iforest | walk | 1.0% | 10 | 15% | 1.82 | 0.13 | 0.07 |
| iforest | walk | 1.0% | 5 | 10% | 1.95 | 0.13 | 0.07 |
| iforest | holdout | 1.0% | 1 | 15% | 4.52 | 0.01 | 0.00 |
| iforest | holdout | 1.0% | 5 | 15% | 1.79 | 0.07 | 0.04 |
| iforest | holdout | 1.0% | 10 | 15% | 1.36 | 0.13 | 0.10 |
| iforest | holdout | 1.0% | 5 | 10% | 1.55 | 0.14 | 0.09 |
| iforest | walk | 0.5% | 1 | 15% | 8.30 | 0.02 | 0.00 |
| iforest | walk | 0.5% | 5 | 15% | 3.07 | 0.08 | 0.03 |
| iforest | walk | 0.5% | 10 | 15% | 2.04 | 0.14 | 0.07 |
| iforest | walk | 0.5% | 20 | 15% | 1.51 | 0.22 | 0.15 |
| iforest | walk | 0.5% | 5 | 10% | 2.23 | 0.15 | 0.07 |
| iforest | holdout | 0.5% | 1 | 15% | 4.86 | 0.02 | 0.00 |
| iforest | holdout | 0.5% | 5 | 15% | 2.06 | 0.08 | 0.04 |
| iforest | holdout | 0.5% | 10 | 15% | 1.50 | 0.15 | 0.10 |
| iforest | holdout | 0.5% | 20 | 15% | 1.28 | 0.26 | 0.21 |
| iforest | holdout | 0.5% | 5 | 10% | 1.70 | 0.16 | 0.09 |
| iforest | walk | 0.1% | 1 | 15% | 12.46 | 0.03 | 0.00 |
| iforest | walk | 0.1% | 5 | 15% | 3.91 | 0.11 | 0.03 |
| iforest | walk | 0.1% | 10 | 15% | 2.35 | 0.16 | 0.07 |
| iforest | walk | 0.1% | 20 | 15% | 1.65 | 0.25 | 0.15 |
| iforest | walk | 0.1% | 5 | 10% | 2.62 | 0.18 | 0.07 |
| iforest | holdout | 0.1% | 1 | 15% | 2.66 | 0.01 | 0.00 |
| iforest | holdout | 0.1% | 5 | 15% | 1.91 | 0.07 | 0.04 |
| iforest | holdout | 0.1% | 10 | 15% | 1.18 | 0.11 | 0.10 |
| iforest | holdout | 0.1% | 20 | 15% | 1.09 | 0.22 | 0.21 |
| iforest | holdout | 0.1% | 5 | 10% | 1.61 | 0.15 | 0.09 |
| lof | walk | 1.0% | 1 | 15% | 3.59 | 0.01 | 0.00 |
| lof | walk | 1.0% | 5 | 15% | 1.80 | 0.05 | 0.03 |
| lof | walk | 1.0% | 10 | 15% | 1.39 | 0.10 | 0.07 |
| lof | walk | 1.0% | 5 | 10% | 1.48 | 0.10 | 0.07 |
| lof | holdout | 1.0% | 1 | 15% | 1.59 | 0.01 | 0.00 |
| lof | holdout | 1.0% | 5 | 15% | 0.99 | 0.04 | 0.04 |
| lof | holdout | 1.0% | 10 | 15% | 0.87 | 0.08 | 0.10 |
| lof | holdout | 1.0% | 5 | 10% | 0.97 | 0.09 | 0.09 |
| lof | walk | 0.5% | 1 | 15% | 4.23 | 0.01 | 0.00 |
| lof | walk | 0.5% | 5 | 15% | 2.05 | 0.06 | 0.03 |
| lof | walk | 0.5% | 10 | 15% | 1.53 | 0.11 | 0.07 |
| lof | walk | 0.5% | 20 | 15% | 1.31 | 0.19 | 0.15 |
| lof | walk | 0.5% | 5 | 10% | 1.62 | 0.11 | 0.07 |
| lof | holdout | 0.5% | 1 | 15% | 1.56 | 0.00 | 0.00 |
| lof | holdout | 0.5% | 5 | 15% | 1.05 | 0.04 | 0.04 |
| lof | holdout | 0.5% | 10 | 15% | 0.85 | 0.08 | 0.10 |
| lof | holdout | 0.5% | 20 | 15% | 0.90 | 0.19 | 0.21 |
| lof | holdout | 0.5% | 5 | 10% | 0.96 | 0.09 | 0.09 |
| lof | walk | 0.1% | 1 | 15% | 5.27 | 0.01 | 0.00 |
| lof | walk | 0.1% | 5 | 15% | 2.43 | 0.07 | 0.03 |
| lof | walk | 0.1% | 10 | 15% | 1.96 | 0.13 | 0.07 |
| lof | walk | 0.1% | 20 | 15% | 1.46 | 0.22 | 0.15 |
| lof | walk | 0.1% | 5 | 10% | 1.94 | 0.13 | 0.07 |
| lof | holdout | 0.1% | 1 | 15% | 1.37 | 0.00 | 0.00 |
| lof | holdout | 0.1% | 5 | 15% | 1.06 | 0.04 | 0.04 |
| lof | holdout | 0.1% | 10 | 15% | 0.93 | 0.09 | 0.10 |
| lof | holdout | 0.1% | 20 | 15% | 0.91 | 0.19 | 0.21 |
| lof | holdout | 0.1% | 5 | 10% | 1.01 | 0.09 | 0.09 |
| ocsvm | walk | 1.0% | 1 | 15% | 5.47 | 0.01 | 0.00 |
| ocsvm | walk | 1.0% | 5 | 15% | 2.28 | 0.06 | 0.03 |
| ocsvm | walk | 1.0% | 10 | 15% | 1.58 | 0.11 | 0.07 |
| ocsvm | walk | 1.0% | 5 | 10% | 1.72 | 0.12 | 0.07 |
| ocsvm | holdout | 1.0% | 1 | 15% | 2.63 | 0.01 | 0.00 |
| ocsvm | holdout | 1.0% | 5 | 15% | 1.39 | 0.05 | 0.04 |
| ocsvm | holdout | 1.0% | 10 | 15% | 1.10 | 0.11 | 0.10 |
| ocsvm | holdout | 1.0% | 5 | 10% | 1.23 | 0.11 | 0.09 |
| ocsvm | walk | 0.5% | 1 | 15% | 6.49 | 0.02 | 0.00 |
| ocsvm | walk | 0.5% | 5 | 15% | 2.49 | 0.07 | 0.03 |
| ocsvm | walk | 0.5% | 10 | 15% | 1.67 | 0.12 | 0.07 |
| ocsvm | walk | 0.5% | 20 | 15% | 1.30 | 0.19 | 0.15 |
| ocsvm | walk | 0.5% | 5 | 10% | 1.87 | 0.13 | 0.07 |
| ocsvm | holdout | 0.5% | 1 | 15% | 2.55 | 0.01 | 0.00 |
| ocsvm | holdout | 0.5% | 5 | 15% | 1.52 | 0.06 | 0.04 |
| ocsvm | holdout | 0.5% | 10 | 15% | 1.10 | 0.11 | 0.10 |
| ocsvm | holdout | 0.5% | 20 | 15% | 0.99 | 0.20 | 0.21 |
| ocsvm | holdout | 0.5% | 5 | 10% | 1.27 | 0.12 | 0.09 |
| ocsvm | walk | 0.1% | 1 | 15% | 6.28 | 0.02 | 0.00 |
| ocsvm | walk | 0.1% | 5 | 15% | 2.52 | 0.07 | 0.03 |
| ocsvm | walk | 0.1% | 10 | 15% | 1.75 | 0.12 | 0.07 |
| ocsvm | walk | 0.1% | 20 | 15% | 1.33 | 0.20 | 0.15 |
| ocsvm | walk | 0.1% | 5 | 10% | 1.81 | 0.12 | 0.07 |
| ocsvm | holdout | 0.1% | 1 | 15% | 2.24 | 0.01 | 0.00 |
| ocsvm | holdout | 0.1% | 5 | 15% | 1.30 | 0.05 | 0.04 |
| ocsvm | holdout | 0.1% | 10 | 15% | 0.96 | 0.09 | 0.10 |
| ocsvm | holdout | 0.1% | 20 | 15% | 0.87 | 0.18 | 0.21 |
| ocsvm | holdout | 0.1% | 5 | 10% | 1.11 | 0.10 | 0.09 |
| pca | walk | 1.0% | 1 | 15% | 4.51 | 0.01 | 0.00 |
| pca | walk | 1.0% | 5 | 15% | 1.97 | 0.05 | 0.03 |
| pca | walk | 1.0% | 10 | 15% | 1.43 | 0.10 | 0.07 |
| pca | walk | 1.0% | 5 | 10% | 1.53 | 0.10 | 0.07 |
| pca | holdout | 1.0% | 1 | 15% | 2.15 | 0.01 | 0.00 |
| pca | holdout | 1.0% | 5 | 15% | 1.20 | 0.05 | 0.04 |
| pca | holdout | 1.0% | 10 | 15% | 0.89 | 0.09 | 0.10 |
| pca | holdout | 1.0% | 5 | 10% | 0.97 | 0.09 | 0.09 |
| pca | walk | 0.5% | 1 | 15% | 5.36 | 0.01 | 0.00 |
| pca | walk | 0.5% | 5 | 15% | 2.18 | 0.06 | 0.03 |
| pca | walk | 0.5% | 10 | 15% | 1.50 | 0.10 | 0.07 |
| pca | walk | 0.5% | 20 | 15% | 1.23 | 0.18 | 0.15 |
| pca | walk | 0.5% | 5 | 10% | 1.64 | 0.11 | 0.07 |
| pca | holdout | 0.5% | 1 | 15% | 2.25 | 0.01 | 0.00 |
| pca | holdout | 0.5% | 5 | 15% | 1.12 | 0.04 | 0.04 |
| pca | holdout | 0.5% | 10 | 15% | 0.77 | 0.08 | 0.10 |
| pca | holdout | 0.5% | 20 | 15% | 0.74 | 0.15 | 0.21 |
| pca | holdout | 0.5% | 5 | 10% | 0.87 | 0.08 | 0.09 |
| pca | walk | 0.1% | 1 | 15% | 6.87 | 0.02 | 0.00 |
| pca | walk | 0.1% | 5 | 15% | 2.52 | 0.07 | 0.03 |
| pca | walk | 0.1% | 10 | 15% | 1.74 | 0.12 | 0.07 |
| pca | walk | 0.1% | 20 | 15% | 1.29 | 0.19 | 0.15 |
| pca | walk | 0.1% | 5 | 10% | 1.76 | 0.12 | 0.07 |
| pca | holdout | 0.1% | 1 | 15% | 0.94 | 0.00 | 0.00 |
| pca | holdout | 0.1% | 5 | 15% | 1.14 | 0.04 | 0.04 |
| pca | holdout | 0.1% | 10 | 15% | 0.75 | 0.07 | 0.10 |
| pca | holdout | 0.1% | 20 | 15% | 0.65 | 0.13 | 0.21 |
| pca | holdout | 0.1% | 5 | 10% | 0.93 | 0.09 | 0.09 |

## Daily top 4, 20-session 15 percent jump

| Method | Window | Baseline | Sample | Date hit rate | Random top 4 |
| --- | ---: | ---: | --- | ---: | ---: |
| mahalanobis | 1 | 50 | walk | 0.556 | 0.430 |
| mahalanobis | 1 | 50 | holdout | 0.601 | 0.583 |
| hbos | 1 | 50 | walk | 0.580 | 0.430 |
| hbos | 1 | 50 | holdout | 0.748 | 0.583 |
| iforest | 1 | 50 | walk | 0.597 | 0.430 |
| iforest | 1 | 50 | holdout | 0.697 | 0.583 |
| lof | 1 | 50 | walk | 0.522 | 0.430 |
| lof | 1 | 50 | holdout | 0.583 | 0.583 |
| ocsvm | 1 | 50 | walk | 0.545 | 0.430 |
| ocsvm | 1 | 50 | holdout | 0.619 | 0.583 |
| pca | 1 | 50 | walk | 0.518 | 0.430 |
| pca | 1 | 50 | holdout | 0.573 | 0.583 |
| mahalanobis | 1 | 100 | walk | 0.593 | 0.426 |
| mahalanobis | 1 | 100 | holdout | 0.569 | 0.581 |
| hbos | 1 | 100 | walk | 0.598 | 0.426 |
| hbos | 1 | 100 | holdout | 0.725 | 0.581 |
| iforest | 1 | 100 | walk | 0.614 | 0.426 |
| iforest | 1 | 100 | holdout | 0.716 | 0.581 |
| lof | 1 | 100 | walk | 0.575 | 0.426 |
| lof | 1 | 100 | holdout | 0.656 | 0.581 |
| ocsvm | 1 | 100 | walk | 0.586 | 0.426 |
| ocsvm | 1 | 100 | holdout | 0.615 | 0.581 |
| pca | 1 | 100 | walk | 0.557 | 0.426 |
| pca | 1 | 100 | holdout | 0.518 | 0.581 |
| mahalanobis | 3 | 50 | walk | 0.525 | 0.431 |
| mahalanobis | 3 | 50 | holdout | 0.528 | 0.583 |
| hbos | 3 | 50 | walk | 0.581 | 0.431 |
| hbos | 3 | 50 | holdout | 0.761 | 0.583 |
| iforest | 3 | 50 | walk | 0.592 | 0.431 |
| iforest | 3 | 50 | holdout | 0.665 | 0.583 |
| lof | 3 | 50 | walk | 0.530 | 0.431 |
| lof | 3 | 50 | holdout | 0.541 | 0.583 |
| ocsvm | 3 | 50 | walk | 0.536 | 0.431 |
| ocsvm | 3 | 50 | holdout | 0.587 | 0.583 |
| pca | 3 | 50 | walk | 0.495 | 0.431 |
| pca | 3 | 50 | holdout | 0.514 | 0.583 |
| mahalanobis | 3 | 100 | walk | 0.584 | 0.427 |
| mahalanobis | 3 | 100 | holdout | 0.482 | 0.582 |
| hbos | 3 | 100 | walk | 0.622 | 0.427 |
| hbos | 3 | 100 | holdout | 0.757 | 0.582 |
| iforest | 3 | 100 | walk | 0.636 | 0.427 |
| iforest | 3 | 100 | holdout | 0.688 | 0.582 |
| lof | 3 | 100 | walk | 0.544 | 0.427 |
| lof | 3 | 100 | holdout | 0.541 | 0.582 |
| ocsvm | 3 | 100 | walk | 0.582 | 0.427 |
| ocsvm | 3 | 100 | holdout | 0.587 | 0.582 |
| pca | 3 | 100 | walk | 0.573 | 0.427 |
| pca | 3 | 100 | holdout | 0.491 | 0.582 |
| mahalanobis | 5 | 50 | walk | 0.533 | 0.432 |
| mahalanobis | 5 | 50 | holdout | 0.477 | 0.584 |
| hbos | 5 | 50 | walk | 0.610 | 0.432 |
| hbos | 5 | 50 | holdout | 0.729 | 0.584 |
| iforest | 5 | 50 | walk | 0.584 | 0.432 |
| iforest | 5 | 50 | holdout | 0.679 | 0.584 |
| lof | 5 | 50 | walk | 0.526 | 0.432 |
| lof | 5 | 50 | holdout | 0.528 | 0.584 |
| ocsvm | 5 | 50 | walk | 0.541 | 0.432 |
| ocsvm | 5 | 50 | holdout | 0.583 | 0.584 |
| pca | 5 | 50 | walk | 0.517 | 0.432 |
| pca | 5 | 50 | holdout | 0.491 | 0.584 |
| mahalanobis | 5 | 100 | walk | 0.596 | 0.428 |
| mahalanobis | 5 | 100 | holdout | 0.541 | 0.582 |
| hbos | 5 | 100 | walk | 0.629 | 0.428 |
| hbos | 5 | 100 | holdout | 0.807 | 0.582 |
| iforest | 5 | 100 | walk | 0.636 | 0.428 |
| iforest | 5 | 100 | holdout | 0.716 | 0.582 |
| lof | 5 | 100 | walk | 0.547 | 0.428 |
| lof | 5 | 100 | holdout | 0.564 | 0.582 |
| ocsvm | 5 | 100 | walk | 0.564 | 0.428 |
| ocsvm | 5 | 100 | holdout | 0.592 | 0.582 |
| pca | 5 | 100 | walk | 0.573 | 0.428 |
| pca | 5 | 100 | holdout | 0.468 | 0.582 |

## Buckets elevated on Mahalanobis anomalies that later jump

Window 1, baseline 50: vol_call_atm_d45 9.49 vs 1.22, vol_call_itm_d45 9.17 vs 1.37, vol_put_atm_d45 8.82 vs 1.24, vol_put_otm_d45 8.56 vs 1.26, vol_put_dotm_d45 8.46 vs 1.31
Window 1, baseline 100: vol_call_atm_d45 9.86 vs 1.13, vol_put_otm_d45 9.29 vs 1.15, vol_put_atm_d45 9.28 vs 1.14, vol_call_itm_d45 9.20 vs 1.21, vol_put_dotm_d45 8.93 vs 1.19
Window 3, baseline 50: vol_put_otm_d21 11.19 vs 1.54, vol_call_otm_d21 10.74 vs 1.54, vol_put_dotm_d21 10.31 vs 1.56, vol_call_atm_d45 10.05 vs 1.37, vol_put_atm_d45 10.00 vs 1.42
Window 3, baseline 100: vol_put_otm_d45 10.43 vs 1.30, vol_put_otm_d21 10.45 vs 1.35, vol_call_atm_d45 10.29 vs 1.24, vol_put_atm_d45 10.27 vs 1.27, vol_call_otm_d21 10.14 vs 1.35
Window 5, baseline 50: vol_put_otm_d21 12.52 vs 1.69, vol_call_otm_d21 12.20 vs 1.69, vol_put_dotm_d21 11.93 vs 1.70, vol_call_atm_d21 11.42 vs 1.67, vol_put_otm_d45 11.13 vs 1.56
Window 5, baseline 100: vol_put_otm_d45 11.58 vs 1.37, vol_put_otm_d21 11.18 vs 1.43, vol_call_atm_d45 10.98 vs 1.29, vol_put_dotm_d45 11.16 vs 1.47, vol_call_otm_d21 11.11 vs 1.43

## Quiet names

Quiet means the 10-session return is inside 5 percent and the session return is inside 3 percent, both known at the close. The table is the 20-session jump at the top 1 percent.

| Method | Window | Baseline | Sample | Lift |
| --- | ---: | ---: | --- | ---: |
| mahalanobis | 1 | 50 | walk-quiet | 1.02 |
| mahalanobis | 1 | 50 | holdout-quiet | 0.76 |
| iforest | 1 | 50 | walk-quiet | 1.27 |
| iforest | 1 | 50 | holdout-quiet | 1.05 |
| mahalanobis | 1 | 100 | walk-quiet | 1.02 |
| mahalanobis | 1 | 100 | holdout-quiet | 0.79 |
| iforest | 1 | 100 | walk-quiet | 1.26 |
| iforest | 1 | 100 | holdout-quiet | 1.07 |
| mahalanobis | 3 | 50 | walk-quiet | 1.04 |
| mahalanobis | 3 | 50 | holdout-quiet | 0.86 |
| iforest | 3 | 50 | walk-quiet | 1.17 |
| iforest | 3 | 50 | holdout-quiet | 1.09 |
| mahalanobis | 3 | 100 | walk-quiet | 1.12 |
| mahalanobis | 3 | 100 | holdout-quiet | 0.89 |
| iforest | 3 | 100 | walk-quiet | 1.32 |
| iforest | 3 | 100 | holdout-quiet | 1.11 |
| mahalanobis | 5 | 50 | walk-quiet | 1.09 |
| mahalanobis | 5 | 50 | holdout-quiet | 0.90 |
| iforest | 5 | 50 | walk-quiet | 1.17 |
| iforest | 5 | 50 | holdout-quiet | 1.20 |
| mahalanobis | 5 | 100 | walk-quiet | 1.12 |
| mahalanobis | 5 | 100 | holdout-quiet | 1.03 |
| iforest | 5 | 100 | walk-quiet | 1.26 |
| iforest | 5 | 100 | holdout-quiet | 1.17 |

## Score before a 20-session jump, Mahalanobis

Window 1, baseline 50, walk: jump day 167.960, other names 75700.453, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 1, baseline 50, holdout: jump day 92.584, other names 56888.703, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 1, baseline 100, walk: jump day 159.508, other names 46248.727, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 1, baseline 100, holdout: jump day 53.956, other names 1665.223, 5 sessions earlier 51.169, 20 sessions earlier n/a.
Window 3, baseline 50, walk: jump day 238.970, other names 36947.699, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 3, baseline 50, holdout: jump day 95.697, other names 62479.469, 5 sessions earlier 129.224, 20 sessions earlier n/a.
Window 3, baseline 100, walk: jump day 321.328, other names 31964.527, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 3, baseline 100, holdout: jump day 65.301, other names 23767.854, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 50, walk: jump day 902.181, other names 9492.783, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 50, holdout: jump day 151.468, other names 127887.602, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 100, walk: jump day 302.817, other names 32562.295, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 100, holdout: jump day 48.493, other names 2381.814, 5 sessions earlier n/a, 20 sessions earlier n/a.

## Known SEC cases

Percentile is within that session's cross section, for the Mahalanobis score on the 5-session window and 50-session baseline. A case with no chain days in the kept universe is absent from the score.

| Case | Symbol | Trade days scored | Median percentile | Share in top 1 percent |
| --- | --- | ---: | ---: | ---: |
| heinz_2013 | HNZ | 0 | n/a | n/a |
| onyx_2013 | ONXX | 0 | n/a | n/a |
| concur_2014 | CNQR | 0 | n/a | n/a |
| kraft_2015 | KRFT | 0 | n/a | n/a |
| adt_2016 | ADT | 0 | n/a | n/a |
| afop_2016 | AFOP | 0 | n/a | n/a |
| joy_2016 | JOY | 0 | n/a | n/a |
| incy_2016 | INCY | 0 | n/a | n/a |
| stillwater_2016 | SWC | 0 | n/a | n/a |
| ceb_2017 | CEB | 0 | n/a | n/a |
| gci_2017 | GNCMA | 0 | n/a | n/a |
| bioverativ_2018 | BIVV | 5 | 0.817 | 0.000 |
| efii_2019 | EFII | 5 | 0.747 | 0.000 |
| audentes_2019 | BOLD | 0 | n/a | n/a |
| dicks_2019 | DKS | 10 | 0.357 | 0.000 |
| twilio_2020 | TWLO | 0 | n/a | n/a |
| virtusa_2020 | VRTU | 0 | n/a | n/a |
| odp_2021 | ODP | 1 | 0.667 | 0.000 |
| coherent_2021 | COHR | 9 | 0.785 | 0.000 |
| greensky_2021 | GSKY | 0 | n/a | n/a |
| pfizer_2021 | PFE | 1 | 0.801 | 0.000 |
| zogenix_2022 | ZGNX | 1 | 0.774 | 0.000 |
| lantheus_2022 | LNTH | 6 | 0.603 | 0.000 |
| maxar_2022 | MAXR | 4 | 0.566 | 0.000 |
| kaman_2024 | KAMN | 0 | n/a | n/a |
| calliditas_2024 | CALT | 0 | n/a | n/a |

## Verdict

These detectors clear the bar set before the run, on a 20-session 15 percent jump at the top 1 percent: hbos on a 1-day window against a 50-day baseline; iforest on a 1-day window against a 50-day baseline; ocsvm on a 1-day window against a 50-day baseline; hbos on a 1-day window against a 100-day baseline; iforest on a 1-day window against a 100-day baseline; lof on a 1-day window against a 100-day baseline; ocsvm on a 1-day window against a 100-day baseline; hbos on a 3-day window against a 50-day baseline; iforest on a 3-day window against a 50-day baseline; ocsvm on a 3-day window against a 50-day baseline; hbos on a 3-day window against a 100-day baseline; iforest on a 3-day window against a 100-day baseline; ocsvm on a 3-day window against a 100-day baseline; hbos on a 5-day window against a 50-day baseline; iforest on a 5-day window against a 50-day baseline; hbos on a 5-day window against a 100-day baseline; iforest on a 5-day window against a 100-day baseline; ocsvm on a 5-day window against a 100-day baseline.
