# Options-flow anomalies before price jumps

Each score uses a 1, 3, or 5 session window ending at that close. The baseline is the 50 or 100 sessions before that window, so the window itself is not in the average. A name is kept only when the split-adjusted close is at least $10, it has a listed chain that day, average daily option volume over the baseline is at least 100 contracts, and at least 40 baseline sessions are usable. The chain scan itself keeps symbols whose average volume since 2017 is at least 100, so a name that is usually quieter is not pulled. Earnings reaction sessions, and the two sessions before them, are not scored. A forward jump that lands on an earnings reaction is not counted.

PyOD is not installed, so the histogram method is a direct HBOS. The autoencoder is an 8-component reconstruction. Isolation forest, local outlier factor, and a one-class SVM are the other detectors, plus a Ledoit-Wolf Mahalanobis distance. Thresholds are the training-score quantiles. The holdout from 2025-11-13 is fit only on earlier rows.

Earnings dates come from `erdate` through 2022-01-04 and from 8-K Item 2.02 reaction sessions after that. Names missing from both calendars are not earnings-filtered. Earnings are not inferred from the price jump itself. Open interest enters as today minus yesterday, never tomorrow. Dollar premium is the bid-ask midpoint times volume times 100. Delta-weighted notional uses absolute delta when delta is present; otherwise the bucket is assigned from strike over spot.

Symbols on a calendar with no earnings date: 1201. Detected split steps: applied inside each price series before the $10 filter and the jump labels.

## Universe

| Window | Baseline | Tickers | Ticker-days |
| ---: | ---: | ---: | ---: |
| 1 | 50 | 4436 | 4452446 |
| 1 | 100 | 4376 | 4405817 |
| 3 | 50 | 4430 | 4362710 |
| 3 | 100 | 4372 | 4317483 |
| 5 | 50 | 4427 | 4273549 |
| 5 | 100 | 4367 | 4229678 |

## Lift at the top 1 percent, 20-session 15 percent jump

Lift is the jump rate inside the anomaly over the jump rate of the whole universe. The interval resamples tickers.

| Method | Window | Baseline | Walk-forward lift | Interval | Holdout lift | Interval |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| mahalanobis | 1 | 50 | 1.21 | 1.17 to 1.26 | 0.97 | 0.90 to 1.03 |
| hbos | 1 | 50 | 1.62 | 1.57 to 1.68 | 1.45 | 1.34 to 1.53 |
| iforest | 1 | 50 | 1.44 | 1.40 to 1.49 | 1.25 | 1.17 to 1.32 |
| lof | 1 | 50 | 1.15 | 1.11 to 1.19 | 1.02 | 0.95 to 1.11 |
| ocsvm | 1 | 50 | 1.24 | 1.20 to 1.28 | 1.06 | 0.99 to 1.13 |
| pca | 1 | 50 | 1.13 | 1.09 to 1.18 | 0.91 | 0.84 to 0.97 |
| mahalanobis | 1 | 100 | 1.33 | 1.28 to 1.39 | 1.10 | 1.01 to 1.19 |
| hbos | 1 | 100 | 1.79 | 1.72 to 1.85 | 1.64 | 1.51 to 1.77 |
| iforest | 1 | 100 | 1.58 | 1.53 to 1.64 | 1.34 | 1.24 to 1.45 |
| lof | 1 | 100 | 1.29 | 1.24 to 1.34 | 1.15 | 1.05 to 1.23 |
| ocsvm | 1 | 100 | 1.34 | 1.30 to 1.39 | 1.11 | 1.03 to 1.19 |
| pca | 1 | 100 | 1.24 | 1.19 to 1.29 | 0.97 | 0.89 to 1.04 |
| mahalanobis | 3 | 50 | 1.18 | 1.12 to 1.24 | 0.95 | 0.87 to 1.02 |
| hbos | 3 | 50 | 1.49 | 1.43 to 1.54 | 1.40 | 1.30 to 1.52 |
| iforest | 3 | 50 | 1.38 | 1.33 to 1.43 | 1.21 | 1.10 to 1.32 |
| lof | 3 | 50 | 1.13 | 1.08 to 1.18 | 0.95 | 0.87 to 1.05 |
| ocsvm | 3 | 50 | 1.21 | 1.16 to 1.27 | 0.99 | 0.90 to 1.08 |
| pca | 3 | 50 | 1.10 | 1.05 to 1.16 | 0.85 | 0.77 to 0.92 |
| mahalanobis | 3 | 100 | 1.30 | 1.24 to 1.36 | 1.00 | 0.91 to 1.11 |
| hbos | 3 | 100 | 1.73 | 1.65 to 1.80 | 1.63 | 1.50 to 1.79 |
| iforest | 3 | 100 | 1.56 | 1.50 to 1.62 | 1.32 | 1.20 to 1.46 |
| lof | 3 | 100 | 1.26 | 1.20 to 1.32 | 1.07 | 0.96 to 1.17 |
| ocsvm | 3 | 100 | 1.32 | 1.26 to 1.38 | 1.02 | 0.93 to 1.12 |
| pca | 3 | 100 | 1.23 | 1.16 to 1.29 | 0.94 | 0.84 to 1.04 |
| mahalanobis | 5 | 50 | 1.23 | 1.16 to 1.29 | 1.00 | 0.90 to 1.12 |
| hbos | 5 | 50 | 1.53 | 1.47 to 1.61 | 1.46 | 1.30 to 1.61 |
| iforest | 5 | 50 | 1.43 | 1.37 to 1.49 | 1.26 | 1.13 to 1.39 |
| lof | 5 | 50 | 1.17 | 1.12 to 1.23 | 1.08 | 0.96 to 1.18 |
| ocsvm | 5 | 50 | 1.22 | 1.15 to 1.29 | 0.96 | 0.86 to 1.08 |
| pca | 5 | 50 | 1.11 | 1.04 to 1.17 | 0.84 | 0.75 to 0.94 |
| mahalanobis | 5 | 100 | 1.33 | 1.27 to 1.41 | 1.09 | 0.99 to 1.22 |
| hbos | 5 | 100 | 1.76 | 1.68 to 1.84 | 1.68 | 1.51 to 1.84 |
| iforest | 5 | 100 | 1.57 | 1.51 to 1.65 | 1.33 | 1.19 to 1.46 |
| lof | 5 | 100 | 1.21 | 1.15 to 1.28 | 0.99 | 0.87 to 1.12 |
| ocsvm | 5 | 100 | 1.32 | 1.26 to 1.40 | 1.09 | 0.97 to 1.20 |
| pca | 5 | 100 | 1.21 | 1.15 to 1.28 | 0.99 | 0.88 to 1.09 |

## Other thresholds and horizons, 5-session window, 50-session baseline

| Method | Sample | Threshold | Horizon | Jump | Lift | Conditional rate | Base rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| mahalanobis | walk | 1.0% | 1 | 15% | 5.55 | 0.01 | 0.00 |
| mahalanobis | walk | 1.0% | 5 | 15% | 2.18 | 0.06 | 0.03 |
| mahalanobis | walk | 1.0% | 10 | 15% | 1.53 | 0.10 | 0.07 |
| mahalanobis | walk | 1.0% | 5 | 10% | 1.64 | 0.11 | 0.07 |
| mahalanobis | holdout | 1.0% | 1 | 15% | 2.79 | 0.01 | 0.00 |
| mahalanobis | holdout | 1.0% | 5 | 15% | 1.48 | 0.06 | 0.04 |
| mahalanobis | holdout | 1.0% | 10 | 15% | 1.08 | 0.11 | 0.10 |
| mahalanobis | holdout | 1.0% | 5 | 10% | 1.21 | 0.11 | 0.09 |
| mahalanobis | walk | 0.5% | 1 | 15% | 6.85 | 0.02 | 0.00 |
| mahalanobis | walk | 0.5% | 5 | 15% | 2.44 | 0.07 | 0.03 |
| mahalanobis | walk | 0.5% | 10 | 15% | 1.64 | 0.11 | 0.07 |
| mahalanobis | walk | 0.5% | 20 | 15% | 1.27 | 0.18 | 0.14 |
| mahalanobis | walk | 0.5% | 5 | 10% | 1.78 | 0.12 | 0.07 |
| mahalanobis | holdout | 0.5% | 1 | 15% | 2.71 | 0.01 | 0.00 |
| mahalanobis | holdout | 0.5% | 5 | 15% | 1.61 | 0.07 | 0.04 |
| mahalanobis | holdout | 0.5% | 10 | 15% | 1.05 | 0.11 | 0.10 |
| mahalanobis | holdout | 0.5% | 20 | 15% | 0.94 | 0.19 | 0.20 |
| mahalanobis | holdout | 0.5% | 5 | 10% | 1.19 | 0.11 | 0.09 |
| mahalanobis | walk | 0.1% | 1 | 15% | 9.80 | 0.02 | 0.00 |
| mahalanobis | walk | 0.1% | 5 | 15% | 3.10 | 0.09 | 0.03 |
| mahalanobis | walk | 0.1% | 10 | 15% | 2.00 | 0.13 | 0.07 |
| mahalanobis | walk | 0.1% | 20 | 15% | 1.40 | 0.20 | 0.14 |
| mahalanobis | walk | 0.1% | 5 | 10% | 2.06 | 0.14 | 0.07 |
| mahalanobis | holdout | 0.1% | 1 | 15% | 4.01 | 0.02 | 0.00 |
| mahalanobis | holdout | 0.1% | 5 | 15% | 3.09 | 0.13 | 0.04 |
| mahalanobis | holdout | 0.1% | 10 | 15% | 1.83 | 0.18 | 0.10 |
| mahalanobis | holdout | 0.1% | 20 | 15% | 1.24 | 0.25 | 0.20 |
| mahalanobis | holdout | 0.1% | 5 | 10% | 1.91 | 0.18 | 0.09 |
| hbos | walk | 1.0% | 1 | 15% | 6.77 | 0.02 | 0.00 |
| hbos | walk | 1.0% | 5 | 15% | 2.85 | 0.08 | 0.03 |
| hbos | walk | 1.0% | 10 | 15% | 2.01 | 0.14 | 0.07 |
| hbos | walk | 1.0% | 5 | 10% | 2.11 | 0.14 | 0.07 |
| hbos | holdout | 1.0% | 1 | 15% | 4.58 | 0.02 | 0.00 |
| hbos | holdout | 1.0% | 5 | 15% | 2.20 | 0.09 | 0.04 |
| hbos | holdout | 1.0% | 10 | 15% | 1.66 | 0.17 | 0.10 |
| hbos | holdout | 1.0% | 5 | 10% | 1.88 | 0.18 | 0.09 |
| hbos | walk | 0.5% | 1 | 15% | 7.48 | 0.02 | 0.00 |
| hbos | walk | 0.5% | 5 | 15% | 3.04 | 0.08 | 0.03 |
| hbos | walk | 0.5% | 10 | 15% | 2.13 | 0.14 | 0.07 |
| hbos | walk | 0.5% | 20 | 15% | 1.58 | 0.23 | 0.14 |
| hbos | walk | 0.5% | 5 | 10% | 2.24 | 0.15 | 0.07 |
| hbos | holdout | 0.5% | 1 | 15% | 5.10 | 0.02 | 0.00 |
| hbos | holdout | 0.5% | 5 | 15% | 2.30 | 0.10 | 0.04 |
| hbos | holdout | 0.5% | 10 | 15% | 1.66 | 0.17 | 0.10 |
| hbos | holdout | 0.5% | 20 | 15% | 1.42 | 0.29 | 0.20 |
| hbos | holdout | 0.5% | 5 | 10% | 1.95 | 0.18 | 0.09 |
| hbos | walk | 0.1% | 1 | 15% | 9.55 | 0.02 | 0.00 |
| hbos | walk | 0.1% | 5 | 15% | 3.35 | 0.09 | 0.03 |
| hbos | walk | 0.1% | 10 | 15% | 2.20 | 0.15 | 0.07 |
| hbos | walk | 0.1% | 20 | 15% | 1.59 | 0.23 | 0.14 |
| hbos | walk | 0.1% | 5 | 10% | 2.38 | 0.16 | 0.07 |
| hbos | holdout | 0.1% | 1 | 15% | 6.39 | 0.03 | 0.00 |
| hbos | holdout | 0.1% | 5 | 15% | 2.91 | 0.12 | 0.04 |
| hbos | holdout | 0.1% | 10 | 15% | 1.99 | 0.20 | 0.10 |
| hbos | holdout | 0.1% | 20 | 15% | 1.57 | 0.32 | 0.20 |
| hbos | holdout | 0.1% | 5 | 10% | 2.40 | 0.23 | 0.09 |
| iforest | walk | 1.0% | 1 | 15% | 6.37 | 0.02 | 0.00 |
| iforest | walk | 1.0% | 5 | 15% | 2.60 | 0.07 | 0.03 |
| iforest | walk | 1.0% | 10 | 15% | 1.82 | 0.12 | 0.07 |
| iforest | walk | 1.0% | 5 | 10% | 1.94 | 0.13 | 0.07 |
| iforest | holdout | 1.0% | 1 | 15% | 3.93 | 0.02 | 0.00 |
| iforest | holdout | 1.0% | 5 | 15% | 1.75 | 0.08 | 0.04 |
| iforest | holdout | 1.0% | 10 | 15% | 1.40 | 0.14 | 0.10 |
| iforest | holdout | 1.0% | 5 | 10% | 1.57 | 0.15 | 0.09 |
| iforest | walk | 0.5% | 1 | 15% | 7.74 | 0.02 | 0.00 |
| iforest | walk | 0.5% | 5 | 15% | 3.02 | 0.08 | 0.03 |
| iforest | walk | 0.5% | 10 | 15% | 2.02 | 0.14 | 0.07 |
| iforest | walk | 0.5% | 20 | 15% | 1.52 | 0.22 | 0.14 |
| iforest | walk | 0.5% | 5 | 10% | 2.17 | 0.14 | 0.07 |
| iforest | holdout | 0.5% | 1 | 15% | 4.66 | 0.02 | 0.00 |
| iforest | holdout | 0.5% | 5 | 15% | 1.95 | 0.08 | 0.04 |
| iforest | holdout | 0.5% | 10 | 15% | 1.53 | 0.15 | 0.10 |
| iforest | holdout | 0.5% | 20 | 15% | 1.31 | 0.26 | 0.20 |
| iforest | holdout | 0.5% | 5 | 10% | 1.72 | 0.16 | 0.09 |
| iforest | walk | 0.1% | 1 | 15% | 12.08 | 0.03 | 0.00 |
| iforest | walk | 0.1% | 5 | 15% | 3.95 | 0.11 | 0.03 |
| iforest | walk | 0.1% | 10 | 15% | 2.37 | 0.16 | 0.07 |
| iforest | walk | 0.1% | 20 | 15% | 1.68 | 0.24 | 0.14 |
| iforest | walk | 0.1% | 5 | 10% | 2.60 | 0.17 | 0.07 |
| iforest | holdout | 0.1% | 1 | 15% | 3.85 | 0.02 | 0.00 |
| iforest | holdout | 0.1% | 5 | 15% | 2.02 | 0.09 | 0.04 |
| iforest | holdout | 0.1% | 10 | 15% | 1.30 | 0.13 | 0.10 |
| iforest | holdout | 0.1% | 20 | 15% | 1.05 | 0.21 | 0.20 |
| iforest | holdout | 0.1% | 5 | 10% | 1.68 | 0.16 | 0.09 |
| lof | walk | 1.0% | 1 | 15% | 3.61 | 0.01 | 0.00 |
| lof | walk | 1.0% | 5 | 15% | 1.77 | 0.05 | 0.03 |
| lof | walk | 1.0% | 10 | 15% | 1.39 | 0.09 | 0.07 |
| lof | walk | 1.0% | 5 | 10% | 1.45 | 0.10 | 0.07 |
| lof | holdout | 1.0% | 1 | 15% | 2.35 | 0.01 | 0.00 |
| lof | holdout | 1.0% | 5 | 15% | 1.28 | 0.05 | 0.04 |
| lof | holdout | 1.0% | 10 | 15% | 1.06 | 0.11 | 0.10 |
| lof | holdout | 1.0% | 5 | 10% | 1.12 | 0.11 | 0.09 |
| lof | walk | 0.5% | 1 | 15% | 4.32 | 0.01 | 0.00 |
| lof | walk | 0.5% | 5 | 15% | 1.92 | 0.05 | 0.03 |
| lof | walk | 0.5% | 10 | 15% | 1.46 | 0.10 | 0.07 |
| lof | walk | 0.5% | 20 | 15% | 1.18 | 0.17 | 0.14 |
| lof | walk | 0.5% | 5 | 10% | 1.52 | 0.10 | 0.07 |
| lof | holdout | 0.5% | 1 | 15% | 2.87 | 0.01 | 0.00 |
| lof | holdout | 0.5% | 5 | 15% | 1.38 | 0.06 | 0.04 |
| lof | holdout | 0.5% | 10 | 15% | 1.12 | 0.11 | 0.10 |
| lof | holdout | 0.5% | 20 | 15% | 1.06 | 0.21 | 0.20 |
| lof | holdout | 0.5% | 5 | 10% | 1.15 | 0.11 | 0.09 |
| lof | walk | 0.1% | 1 | 15% | 4.29 | 0.01 | 0.00 |
| lof | walk | 0.1% | 5 | 15% | 2.25 | 0.06 | 0.03 |
| lof | walk | 0.1% | 10 | 15% | 1.71 | 0.12 | 0.07 |
| lof | walk | 0.1% | 20 | 15% | 1.30 | 0.19 | 0.14 |
| lof | walk | 0.1% | 5 | 10% | 1.72 | 0.11 | 0.07 |
| lof | holdout | 0.1% | 1 | 15% | 1.25 | 0.01 | 0.00 |
| lof | holdout | 0.1% | 5 | 15% | 1.30 | 0.06 | 0.04 |
| lof | holdout | 0.1% | 10 | 15% | 1.04 | 0.10 | 0.10 |
| lof | holdout | 0.1% | 20 | 15% | 0.97 | 0.20 | 0.20 |
| lof | holdout | 0.1% | 5 | 10% | 1.12 | 0.11 | 0.09 |
| ocsvm | walk | 1.0% | 1 | 15% | 5.10 | 0.01 | 0.00 |
| ocsvm | walk | 1.0% | 5 | 15% | 2.15 | 0.06 | 0.03 |
| ocsvm | walk | 1.0% | 10 | 15% | 1.50 | 0.10 | 0.07 |
| ocsvm | walk | 1.0% | 5 | 10% | 1.65 | 0.11 | 0.07 |
| ocsvm | holdout | 1.0% | 1 | 15% | 2.11 | 0.01 | 0.00 |
| ocsvm | holdout | 1.0% | 5 | 15% | 1.16 | 0.05 | 0.04 |
| ocsvm | holdout | 1.0% | 10 | 15% | 0.99 | 0.10 | 0.10 |
| ocsvm | holdout | 1.0% | 5 | 10% | 1.11 | 0.11 | 0.09 |
| ocsvm | walk | 0.5% | 1 | 15% | 6.47 | 0.02 | 0.00 |
| ocsvm | walk | 0.5% | 5 | 15% | 2.45 | 0.07 | 0.03 |
| ocsvm | walk | 0.5% | 10 | 15% | 1.63 | 0.11 | 0.07 |
| ocsvm | walk | 0.5% | 20 | 15% | 1.27 | 0.18 | 0.14 |
| ocsvm | walk | 0.5% | 5 | 10% | 1.84 | 0.12 | 0.07 |
| ocsvm | holdout | 0.5% | 1 | 15% | 1.96 | 0.01 | 0.00 |
| ocsvm | holdout | 0.5% | 5 | 15% | 1.15 | 0.05 | 0.04 |
| ocsvm | holdout | 0.5% | 10 | 15% | 0.96 | 0.10 | 0.10 |
| ocsvm | holdout | 0.5% | 20 | 15% | 0.92 | 0.19 | 0.20 |
| ocsvm | holdout | 0.5% | 5 | 10% | 1.13 | 0.11 | 0.09 |
| ocsvm | walk | 0.1% | 1 | 15% | 5.28 | 0.01 | 0.00 |
| ocsvm | walk | 0.1% | 5 | 15% | 2.56 | 0.07 | 0.03 |
| ocsvm | walk | 0.1% | 10 | 15% | 1.71 | 0.12 | 0.07 |
| ocsvm | walk | 0.1% | 20 | 15% | 1.33 | 0.19 | 0.14 |
| ocsvm | walk | 0.1% | 5 | 10% | 1.78 | 0.12 | 0.07 |
| ocsvm | holdout | 0.1% | 1 | 15% | 1.37 | 0.01 | 0.00 |
| ocsvm | holdout | 0.1% | 5 | 15% | 0.94 | 0.04 | 0.04 |
| ocsvm | holdout | 0.1% | 10 | 15% | 0.85 | 0.09 | 0.10 |
| ocsvm | holdout | 0.1% | 20 | 15% | 0.85 | 0.17 | 0.20 |
| ocsvm | holdout | 0.1% | 5 | 10% | 0.88 | 0.08 | 0.09 |
| pca | walk | 1.0% | 1 | 15% | 4.22 | 0.01 | 0.00 |
| pca | walk | 1.0% | 5 | 15% | 1.81 | 0.05 | 0.03 |
| pca | walk | 1.0% | 10 | 15% | 1.33 | 0.09 | 0.07 |
| pca | walk | 1.0% | 5 | 10% | 1.42 | 0.09 | 0.07 |
| pca | holdout | 1.0% | 1 | 15% | 2.13 | 0.01 | 0.00 |
| pca | holdout | 1.0% | 5 | 15% | 1.09 | 0.05 | 0.04 |
| pca | holdout | 1.0% | 10 | 15% | 0.83 | 0.08 | 0.10 |
| pca | holdout | 1.0% | 5 | 10% | 0.92 | 0.09 | 0.09 |
| pca | walk | 0.5% | 1 | 15% | 5.18 | 0.01 | 0.00 |
| pca | walk | 0.5% | 5 | 15% | 1.99 | 0.05 | 0.03 |
| pca | walk | 0.5% | 10 | 15% | 1.41 | 0.10 | 0.07 |
| pca | walk | 0.5% | 20 | 15% | 1.15 | 0.16 | 0.14 |
| pca | walk | 0.5% | 5 | 10% | 1.51 | 0.10 | 0.07 |
| pca | holdout | 0.5% | 1 | 15% | 1.88 | 0.01 | 0.00 |
| pca | holdout | 0.5% | 5 | 15% | 1.04 | 0.04 | 0.04 |
| pca | holdout | 0.5% | 10 | 15% | 0.74 | 0.07 | 0.10 |
| pca | holdout | 0.5% | 20 | 15% | 0.75 | 0.15 | 0.20 |
| pca | holdout | 0.5% | 5 | 10% | 0.87 | 0.08 | 0.09 |
| pca | walk | 0.1% | 1 | 15% | 7.00 | 0.02 | 0.00 |
| pca | walk | 0.1% | 5 | 15% | 2.25 | 0.06 | 0.03 |
| pca | walk | 0.1% | 10 | 15% | 1.56 | 0.11 | 0.07 |
| pca | walk | 0.1% | 20 | 15% | 1.21 | 0.17 | 0.14 |
| pca | walk | 0.1% | 5 | 10% | 1.63 | 0.11 | 0.07 |
| pca | holdout | 0.1% | 1 | 15% | 1.66 | 0.01 | 0.00 |
| pca | holdout | 0.1% | 5 | 15% | 0.70 | 0.03 | 0.04 |
| pca | holdout | 0.1% | 10 | 15% | 0.52 | 0.05 | 0.10 |
| pca | holdout | 0.1% | 20 | 15% | 0.54 | 0.11 | 0.20 |
| pca | holdout | 0.1% | 5 | 10% | 0.50 | 0.05 | 0.09 |

## Daily top 4, 20-session 15 percent jump

| Method | Window | Baseline | Sample | Date hit rate | Random top 4 |
| --- | ---: | ---: | --- | ---: | ---: |
| mahalanobis | 1 | 50 | walk | 0.550 | 0.422 |
| mahalanobis | 1 | 50 | holdout | 0.583 | 0.579 |
| hbos | 1 | 50 | walk | 0.583 | 0.422 |
| hbos | 1 | 50 | holdout | 0.739 | 0.579 |
| iforest | 1 | 50 | walk | 0.590 | 0.422 |
| iforest | 1 | 50 | holdout | 0.656 | 0.579 |
| lof | 1 | 50 | walk | 0.505 | 0.422 |
| lof | 1 | 50 | holdout | 0.610 | 0.579 |
| ocsvm | 1 | 50 | walk | 0.526 | 0.422 |
| ocsvm | 1 | 50 | holdout | 0.615 | 0.579 |
| pca | 1 | 50 | walk | 0.497 | 0.422 |
| pca | 1 | 50 | holdout | 0.550 | 0.579 |
| mahalanobis | 1 | 100 | walk | 0.582 | 0.418 |
| mahalanobis | 1 | 100 | holdout | 0.606 | 0.576 |
| hbos | 1 | 100 | walk | 0.609 | 0.418 |
| hbos | 1 | 100 | holdout | 0.775 | 0.576 |
| iforest | 1 | 100 | walk | 0.613 | 0.418 |
| iforest | 1 | 100 | holdout | 0.683 | 0.576 |
| lof | 1 | 100 | walk | 0.554 | 0.418 |
| lof | 1 | 100 | holdout | 0.592 | 0.576 |
| ocsvm | 1 | 100 | walk | 0.572 | 0.418 |
| ocsvm | 1 | 100 | holdout | 0.578 | 0.576 |
| pca | 1 | 100 | walk | 0.542 | 0.418 |
| pca | 1 | 100 | holdout | 0.509 | 0.576 |
| mahalanobis | 3 | 50 | walk | 0.516 | 0.423 |
| mahalanobis | 3 | 50 | holdout | 0.505 | 0.579 |
| hbos | 3 | 50 | walk | 0.581 | 0.423 |
| hbos | 3 | 50 | holdout | 0.748 | 0.579 |
| iforest | 3 | 50 | walk | 0.577 | 0.423 |
| iforest | 3 | 50 | holdout | 0.628 | 0.579 |
| lof | 3 | 50 | walk | 0.495 | 0.423 |
| lof | 3 | 50 | holdout | 0.509 | 0.579 |
| ocsvm | 3 | 50 | walk | 0.516 | 0.423 |
| ocsvm | 3 | 50 | holdout | 0.564 | 0.579 |
| pca | 3 | 50 | walk | 0.474 | 0.423 |
| pca | 3 | 50 | holdout | 0.472 | 0.579 |
| mahalanobis | 3 | 100 | walk | 0.547 | 0.418 |
| mahalanobis | 3 | 100 | holdout | 0.486 | 0.576 |
| hbos | 3 | 100 | walk | 0.622 | 0.418 |
| hbos | 3 | 100 | holdout | 0.775 | 0.576 |
| iforest | 3 | 100 | walk | 0.620 | 0.418 |
| iforest | 3 | 100 | holdout | 0.661 | 0.576 |
| lof | 3 | 100 | walk | 0.520 | 0.418 |
| lof | 3 | 100 | holdout | 0.537 | 0.576 |
| ocsvm | 3 | 100 | walk | 0.547 | 0.418 |
| ocsvm | 3 | 100 | holdout | 0.500 | 0.576 |
| pca | 3 | 100 | walk | 0.536 | 0.418 |
| pca | 3 | 100 | holdout | 0.459 | 0.576 |
| mahalanobis | 5 | 50 | walk | 0.514 | 0.423 |
| mahalanobis | 5 | 50 | holdout | 0.537 | 0.580 |
| hbos | 5 | 50 | walk | 0.604 | 0.423 |
| hbos | 5 | 50 | holdout | 0.739 | 0.580 |
| iforest | 5 | 50 | walk | 0.581 | 0.423 |
| iforest | 5 | 50 | holdout | 0.702 | 0.580 |
| lof | 5 | 50 | walk | 0.496 | 0.423 |
| lof | 5 | 50 | holdout | 0.560 | 0.580 |
| ocsvm | 5 | 50 | walk | 0.513 | 0.423 |
| ocsvm | 5 | 50 | holdout | 0.546 | 0.580 |
| pca | 5 | 50 | walk | 0.475 | 0.423 |
| pca | 5 | 50 | holdout | 0.417 | 0.580 |
| mahalanobis | 5 | 100 | walk | 0.567 | 0.418 |
| mahalanobis | 5 | 100 | holdout | 0.587 | 0.576 |
| hbos | 5 | 100 | walk | 0.635 | 0.418 |
| hbos | 5 | 100 | holdout | 0.812 | 0.576 |
| iforest | 5 | 100 | walk | 0.612 | 0.418 |
| iforest | 5 | 100 | holdout | 0.670 | 0.576 |
| lof | 5 | 100 | walk | 0.502 | 0.418 |
| lof | 5 | 100 | holdout | 0.546 | 0.576 |
| ocsvm | 5 | 100 | walk | 0.544 | 0.418 |
| ocsvm | 5 | 100 | holdout | 0.523 | 0.576 |
| pca | 5 | 100 | walk | 0.535 | 0.418 |
| pca | 5 | 100 | holdout | 0.482 | 0.576 |

## Buckets elevated on Mahalanobis anomalies that later jump

Window 1, baseline 50: vol_call_atm_d45 9.23 vs 1.22, vol_call_itm_d45 9.02 vs 1.36, vol_put_atm_d45 8.60 vs 1.24, vol_put_otm_d45 8.42 vs 1.26, vol_call_itm_dlong 8.41 vs 1.30
Window 1, baseline 100: vol_call_atm_d45 9.34 vs 1.13, vol_call_itm_d45 8.82 vs 1.21, vol_put_otm_d45 8.73 vs 1.15, vol_put_atm_d45 8.72 vs 1.14, vol_call_itm_dlong 8.40 vs 1.22
Window 3, baseline 50: vol_call_otm_d21 10.85 vs 1.53, vol_put_otm_d21 10.83 vs 1.53, vol_call_atm_d45 9.99 vs 1.36, vol_put_dotm_d21 9.98 vs 1.55, vol_put_atm_d45 9.82 vs 1.42
Window 3, baseline 100: vol_call_atm_d45 10.27 vs 1.24, vol_put_otm_d45 10.16 vs 1.30, vol_put_otm_d21 10.18 vs 1.35, vol_call_otm_d21 10.16 vs 1.35, vol_put_atm_d45 10.08 vs 1.27
Window 5, baseline 50: vol_put_otm_d21 12.12 vs 1.67, vol_call_otm_d21 11.87 vs 1.67, vol_put_dotm_d21 11.56 vs 1.69, vol_call_atm_d21 11.04 vs 1.64, vol_put_otm_d45 10.56 vs 1.56
Window 5, baseline 100: vol_put_otm_d45 11.47 vs 1.37, vol_call_atm_d45 10.92 vs 1.29, vol_put_dotm_d45 11.07 vs 1.47, vol_put_otm_d21 10.99 vs 1.43, vol_put_atm_d45 10.88 vs 1.34

## Quiet names

Quiet means the 10-session return is inside 5 percent and the session return is inside 3 percent, both known at the close. The table is the 20-session jump at the top 1 percent.

| Method | Window | Baseline | Sample | Lift |
| --- | ---: | ---: | --- | ---: |
| mahalanobis | 1 | 50 | walk-quiet | 0.95 |
| mahalanobis | 1 | 50 | holdout-quiet | 0.68 |
| iforest | 1 | 50 | walk-quiet | 1.20 |
| iforest | 1 | 50 | holdout-quiet | 0.88 |
| mahalanobis | 1 | 100 | walk-quiet | 1.00 |
| mahalanobis | 1 | 100 | holdout-quiet | 0.68 |
| iforest | 1 | 100 | walk-quiet | 1.22 |
| iforest | 1 | 100 | holdout-quiet | 0.90 |
| mahalanobis | 3 | 50 | walk-quiet | 0.99 |
| mahalanobis | 3 | 50 | holdout-quiet | 0.85 |
| iforest | 3 | 50 | walk-quiet | 1.17 |
| iforest | 3 | 50 | holdout-quiet | 1.16 |
| mahalanobis | 3 | 100 | walk-quiet | 1.01 |
| mahalanobis | 3 | 100 | holdout-quiet | 0.84 |
| iforest | 3 | 100 | walk-quiet | 1.25 |
| iforest | 3 | 100 | holdout-quiet | 0.94 |
| mahalanobis | 5 | 50 | walk-quiet | 0.96 |
| mahalanobis | 5 | 50 | holdout-quiet | 0.90 |
| iforest | 5 | 50 | walk-quiet | 1.13 |
| iforest | 5 | 50 | holdout-quiet | 1.14 |
| mahalanobis | 5 | 100 | walk-quiet | 1.00 |
| mahalanobis | 5 | 100 | holdout-quiet | 0.99 |
| iforest | 5 | 100 | walk-quiet | 1.13 |
| iforest | 5 | 100 | holdout-quiet | 1.03 |

## Score before a 20-session jump, Mahalanobis

Window 1, baseline 50, walk: jump day 154.180, other names 47105.984, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 1, baseline 50, holdout: jump day 45.028, other names 271.520, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 1, baseline 100, walk: jump day 150.992, other names 35894.238, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 1, baseline 100, holdout: jump day 139.746, other names 91997.531, 5 sessions earlier 205.505, 20 sessions earlier n/a.
Window 3, baseline 50, walk: jump day 195.097, other names 36729.066, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 3, baseline 50, holdout: jump day 138.430, other names 92991.094, 5 sessions earlier 140.586, 20 sessions earlier n/a.
Window 3, baseline 100, walk: jump day 122.261, other names 28278.711, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 3, baseline 100, holdout: jump day 45.049, other names 51.288, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 50, walk: jump day 176.018, other names 64340.680, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 50, holdout: jump day 136.874, other names 86298.969, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 100, walk: jump day 361.632, other names 30786.650, 5 sessions earlier n/a, 20 sessions earlier n/a.
Window 5, baseline 100, holdout: jump day 53.797, other names 5073.667, 5 sessions earlier n/a, 20 sessions earlier n/a.

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
| bioverativ_2018 | BIVV | 5 | 0.822 | 0.000 |
| efii_2019 | EFII | 5 | 0.743 | 0.000 |
| audentes_2019 | BOLD | 0 | n/a | n/a |
| dicks_2019 | DKS | 10 | 0.357 | 0.000 |
| twilio_2020 | TWLO | 0 | n/a | n/a |
| virtusa_2020 | VRTU | 0 | n/a | n/a |
| odp_2021 | ODP | 1 | 0.653 | 0.000 |
| coherent_2021 | COHR | 9 | 0.794 | 0.000 |
| greensky_2021 | GSKY | 0 | n/a | n/a |
| pfizer_2021 | PFE | 1 | 0.810 | 0.000 |
| zogenix_2022 | ZGNX | 1 | 0.767 | 0.000 |
| lantheus_2022 | LNTH | 6 | 0.609 | 0.000 |
| maxar_2022 | MAXR | 4 | 0.574 | 0.000 |
| kaman_2024 | KAMN | 0 | n/a | n/a |
| calliditas_2024 | CALT | 0 | n/a | n/a |

## Verdict

These detectors clear the bar set before the run, on a 20-session 15 percent jump at the top 1 percent: hbos on a 1-day window against a 50-day baseline; iforest on a 1-day window against a 50-day baseline; lof on a 1-day window against a 50-day baseline; ocsvm on a 1-day window against a 50-day baseline; mahalanobis on a 1-day window against a 100-day baseline; hbos on a 1-day window against a 100-day baseline; iforest on a 1-day window against a 100-day baseline; lof on a 1-day window against a 100-day baseline; ocsvm on a 1-day window against a 100-day baseline; hbos on a 3-day window against a 50-day baseline; iforest on a 3-day window against a 50-day baseline; hbos on a 3-day window against a 100-day baseline; iforest on a 3-day window against a 100-day baseline; hbos on a 5-day window against a 50-day baseline; iforest on a 5-day window against a 50-day baseline; mahalanobis on a 5-day window against a 100-day baseline; hbos on a 5-day window against a 100-day baseline; iforest on a 5-day window against a 100-day baseline.
