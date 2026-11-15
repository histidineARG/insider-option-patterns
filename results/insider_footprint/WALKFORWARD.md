## Daily top picks, 2026-11-13

Exchange-traded products were removed before this rerun (2,431 of 8,616 symbols; 6,185 scanned). Date hit rate is the share of sessions where at least one slate name jumps. The base rate is the random slate of the same size. These rows are the five-feature score, which includes the stock's own return.

| Slate | Horizon | Jump | Date hit rate before | After | Random base before | After |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| top 3 | 20 | terminal | 0.481 | 0.442 | 0.246 | 0.296 |
| top 3 | 20 | peak | 0.770 | 0.722 | 0.386 | 0.451 |
| top 4 | 20 | terminal | 0.568 | 0.510 | 0.311 | 0.367 |
| top 4 | 20 | peak | 0.852 | 0.782 | 0.473 | 0.542 |

The slates still beat a random slate of the same size. The gap is smaller. Top 3, 20 sessions, terminal: 0.481 versus 0.246 before, 0.442 versus 0.296 after.


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

## Quiet stock, loud options, 2026-11-13

The stock is quiet and call volume rises on one day or across several days. A single day is call volume at least 5 times the prior 20-session mean and at least 500 contracts, without a second elevated day. A multi-day build is two or more of the last five sessions at least 3 times that mean, or a five-session total at least 5 times a normal five-session total spread over two or more days. The prior 20 sessions sit before that five-session window and average at least 100 contracts. Out-of-the-money calls (delta 0.10–0.35, 5–45 days) are at least 40% of call volume. The 10-session absolute return is under 5% (a second cut uses 3%), the scoring day is under 3%, and stock volume is under twice its prior 20-session median. Price is at least $5 and median dollar volume is at least $5 million. Names are ordered by the call-volume ratio times the out-of-the-money share. Open-interest confirmation and the earnings blackout are reported beside the main screen. Downside hit rates are not part of this test.

An earlier request for company_tickers.json returned 403. The retry succeeded and was used with display tickers and cik2symbol.

### Single day, call baseline, 10-session move under 5%

Days with a qualifying name: 1041. Mean qualifiers on those days: 8.322. Share of those days with at least 3: 0.945.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 945 | 0.022 | 0.070 | 0.034 | 0.007 | 134.000 | 1 | 4 | 16 |
| 3 | 5 | peak | 945 | 0.034 | 0.090 | 0.042 | 0.011 | 87.594 | 1 | 5 | 26 |
| 3 | 10 | terminal | 907 | 0.078 | 0.145 | 0.085 | 0.026 | 36.792 | 6 | 10 | 56 |
| 3 | 10 | peak | 907 | 0.107 | 0.208 | 0.119 | 0.037 | 25.941 | 10 | 15 | 76 |
| 3 | 20 | terminal | 831 | 0.189 | 0.268 | 0.189 | 0.071 | 13.006 | 26 | 32 | 120 |
| 3 | 20 | peak | 831 | 0.260 | 0.398 | 0.279 | 0.101 | 8.932 | 30 | 47 | 174 |
| 4 | 5 | terminal | 896 | 0.033 | 0.091 | 0.045 | 0.008 | 118.467 | 2 | 6 | 22 |
| 4 | 5 | peak | 896 | 0.047 | 0.117 | 0.056 | 0.012 | 80.455 | 2 | 7 | 35 |
| 4 | 10 | terminal | 862 | 0.103 | 0.187 | 0.112 | 0.028 | 35.295 | 8 | 15 | 72 |
| 4 | 10 | peak | 862 | 0.148 | 0.264 | 0.155 | 0.041 | 23.454 | 12 | 21 | 108 |
| 4 | 20 | terminal | 787 | 0.250 | 0.335 | 0.242 | 0.077 | 12.062 | 36 | 44 | 161 |
| 4 | 20 | peak | 787 | 0.343 | 0.484 | 0.350 | 0.110 | 8.125 | 41 | 64 | 240 |

### Multi-day build, call baseline, 10-session move under 5%

Days with a qualifying name: 1012. Mean qualifiers on those days: 4.934. Share of those days with at least 3: 0.790.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 770 | 0.045 | 0.069 | 0.034 | 0.016 | 63.167 | 2 | 9 | 25 |
| 3 | 5 | peak | 770 | 0.061 | 0.090 | 0.043 | 0.021 | 46.143 | 2 | 11 | 36 |
| 3 | 10 | terminal | 741 | 0.077 | 0.145 | 0.086 | 0.027 | 35.443 | 1 | 13 | 47 |
| 3 | 10 | peak | 741 | 0.138 | 0.209 | 0.121 | 0.049 | 19.394 | 3 | 21 | 85 |
| 3 | 20 | terminal | 679 | 0.171 | 0.264 | 0.187 | 0.064 | 14.669 | 10 | 25 | 95 |
| 3 | 20 | peak | 679 | 0.271 | 0.397 | 0.278 | 0.105 | 8.519 | 13 | 46 | 155 |
| 4 | 5 | terminal | 628 | 0.054 | 0.089 | 0.044 | 0.015 | 66.892 | 3 | 8 | 26 |
| 4 | 5 | peak | 628 | 0.072 | 0.116 | 0.056 | 0.020 | 50.265 | 3 | 9 | 37 |
| 4 | 10 | terminal | 598 | 0.117 | 0.185 | 0.112 | 0.032 | 30.065 | 2 | 19 | 56 |
| 4 | 10 | peak | 598 | 0.189 | 0.265 | 0.158 | 0.053 | 17.835 | 5 | 27 | 95 |
| 4 | 20 | terminal | 545 | 0.226 | 0.330 | 0.239 | 0.065 | 14.461 | 12 | 26 | 103 |
| 4 | 20 | peak | 545 | 0.347 | 0.484 | 0.350 | 0.109 | 8.198 | 15 | 51 | 171 |

### Single day, next-morning open-interest confirmation

Days with a qualifying name: 1014. Mean qualifiers on those days: 4.420. Share of those days with at least 3: 0.777.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 760 | 0.030 | 0.071 | 0.035 | 0.010 | 98.130 | 2 | 5 | 16 |
| 3 | 5 | peak | 760 | 0.045 | 0.091 | 0.043 | 0.015 | 64.143 | 2 | 6 | 27 |
| 3 | 10 | terminal | 729 | 0.102 | 0.148 | 0.088 | 0.034 | 28.160 | 6 | 12 | 57 |
| 3 | 10 | peak | 729 | 0.140 | 0.212 | 0.122 | 0.049 | 19.250 | 10 | 18 | 80 |
| 3 | 20 | terminal | 668 | 0.244 | 0.276 | 0.197 | 0.092 | 9.832 | 26 | 37 | 122 |
| 3 | 20 | peak | 668 | 0.308 | 0.406 | 0.287 | 0.127 | 6.859 | 27 | 57 | 171 |
| 4 | 5 | terminal | 582 | 0.053 | 0.096 | 0.048 | 0.014 | 71.750 | 3 | 7 | 22 |
| 4 | 5 | peak | 582 | 0.069 | 0.122 | 0.059 | 0.018 | 54.429 | 3 | 8 | 31 |
| 4 | 10 | terminal | 561 | 0.130 | 0.193 | 0.117 | 0.036 | 27.050 | 7 | 15 | 58 |
| 4 | 10 | peak | 561 | 0.185 | 0.272 | 0.163 | 0.053 | 17.700 | 10 | 23 | 87 |
| 4 | 20 | terminal | 512 | 0.291 | 0.345 | 0.252 | 0.089 | 10.253 | 24 | 45 | 113 |
| 4 | 20 | peak | 512 | 0.365 | 0.492 | 0.359 | 0.121 | 7.258 | 25 | 67 | 156 |

### Multi-day, next-morning open-interest confirmation

Days with a qualifying name: 986. Mean qualifiers on those days: 4.017. Share of those days with at least 3: 0.689.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 653 | 0.060 | 0.068 | 0.035 | 0.021 | 46.780 | 4 | 10 | 27 |
| 3 | 5 | peak | 653 | 0.078 | 0.089 | 0.043 | 0.028 | 35.278 | 4 | 12 | 38 |
| 3 | 10 | terminal | 629 | 0.084 | 0.144 | 0.086 | 0.030 | 32.105 | 3 | 13 | 41 |
| 3 | 10 | peak | 629 | 0.157 | 0.208 | 0.122 | 0.058 | 16.312 | 6 | 23 | 80 |
| 3 | 20 | terminal | 572 | 0.173 | 0.261 | 0.185 | 0.064 | 14.743 | 11 | 23 | 75 |
| 3 | 20 | peak | 572 | 0.278 | 0.394 | 0.277 | 0.110 | 8.079 | 13 | 41 | 135 |
| 4 | 5 | terminal | 478 | 0.054 | 0.086 | 0.044 | 0.014 | 72.538 | 2 | 6 | 18 |
| 4 | 5 | peak | 478 | 0.071 | 0.114 | 0.056 | 0.018 | 53.629 | 2 | 7 | 26 |
| 4 | 10 | terminal | 458 | 0.116 | 0.182 | 0.112 | 0.032 | 30.586 | 4 | 13 | 41 |
| 4 | 10 | peak | 458 | 0.190 | 0.261 | 0.157 | 0.053 | 17.887 | 5 | 20 | 72 |
| 4 | 20 | terminal | 414 | 0.222 | 0.325 | 0.236 | 0.061 | 15.396 | 9 | 20 | 72 |
| 4 | 20 | peak | 414 | 0.326 | 0.475 | 0.344 | 0.100 | 8.976 | 11 | 35 | 120 |

### Single day, no earnings filing in the next 5 sessions

Days with a qualifying name: 1040. Mean qualifiers on those days: 7.913. Share of those days with at least 3: 0.939.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 938 | 0.021 | 0.069 | 0.033 | 0.007 | 139.700 | 2 | 0 | 18 |
| 3 | 5 | peak | 938 | 0.032 | 0.090 | 0.042 | 0.011 | 92.800 | 2 | 0 | 28 |
| 3 | 10 | terminal | 899 | 0.080 | 0.145 | 0.085 | 0.027 | 35.945 | 6 | 4 | 63 |
| 3 | 10 | peak | 899 | 0.105 | 0.207 | 0.119 | 0.036 | 27.094 | 8 | 5 | 83 |
| 3 | 20 | terminal | 823 | 0.185 | 0.268 | 0.189 | 0.069 | 13.439 | 23 | 19 | 129 |
| 3 | 20 | peak | 823 | 0.254 | 0.398 | 0.279 | 0.098 | 9.245 | 27 | 30 | 184 |
| 4 | 5 | terminal | 875 | 0.027 | 0.090 | 0.044 | 0.007 | 144.833 | 1 | 0 | 23 |
| 4 | 5 | peak | 875 | 0.040 | 0.116 | 0.055 | 0.011 | 93.595 | 1 | 0 | 36 |
| 4 | 10 | terminal | 844 | 0.097 | 0.186 | 0.111 | 0.026 | 36.933 | 7 | 7 | 75 |
| 4 | 10 | peak | 844 | 0.142 | 0.263 | 0.154 | 0.039 | 24.576 | 9 | 9 | 114 |
| 4 | 20 | terminal | 770 | 0.244 | 0.335 | 0.242 | 0.075 | 12.333 | 33 | 27 | 171 |
| 4 | 20 | peak | 770 | 0.338 | 0.483 | 0.349 | 0.108 | 8.249 | 38 | 42 | 253 |

### Multi-day, no earnings filing in the next 5 sessions

Days with a qualifying name: 1010. Mean qualifiers on those days: 4.661. Share of those days with at least 3: 0.767.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 747 | 0.040 | 0.068 | 0.033 | 0.014 | 71.290 | 3 | 0 | 28 |
| 3 | 5 | peak | 747 | 0.054 | 0.089 | 0.042 | 0.019 | 52.357 | 3 | 0 | 39 |
| 3 | 10 | terminal | 718 | 0.071 | 0.143 | 0.085 | 0.026 | 38.164 | 2 | 4 | 49 |
| 3 | 10 | peak | 718 | 0.125 | 0.207 | 0.119 | 0.045 | 21.206 | 4 | 5 | 88 |
| 3 | 20 | terminal | 661 | 0.162 | 0.262 | 0.185 | 0.060 | 15.805 | 12 | 14 | 92 |
| 3 | 20 | peak | 661 | 0.257 | 0.395 | 0.276 | 0.099 | 9.117 | 15 | 27 | 154 |
| 4 | 5 | terminal | 593 | 0.046 | 0.086 | 0.043 | 0.012 | 83.714 | 3 | 0 | 25 |
| 4 | 5 | peak | 593 | 0.059 | 0.113 | 0.054 | 0.016 | 61.421 | 3 | 0 | 35 |
| 4 | 10 | terminal | 566 | 0.108 | 0.179 | 0.108 | 0.029 | 33.303 | 3 | 5 | 58 |
| 4 | 10 | peak | 566 | 0.168 | 0.258 | 0.152 | 0.046 | 20.562 | 5 | 6 | 94 |
| 4 | 20 | terminal | 518 | 0.220 | 0.324 | 0.234 | 0.065 | 14.463 | 12 | 15 | 107 |
| 4 | 20 | peak | 518 | 0.334 | 0.478 | 0.345 | 0.106 | 8.461 | 15 | 30 | 174 |

### Single day, 10-session move under 3%

Days with a qualifying name: 1025. Mean qualifiers on those days: 5.512. Share of those days with at least 3: 0.843.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 834 | 0.025 | 0.069 | 0.032 | 0.009 | 112.727 | 1 | 4 | 17 |
| 3 | 5 | peak | 834 | 0.034 | 0.089 | 0.039 | 0.012 | 85.276 | 1 | 5 | 23 |
| 3 | 10 | terminal | 802 | 0.081 | 0.147 | 0.082 | 0.028 | 34.382 | 4 | 10 | 54 |
| 3 | 10 | peak | 802 | 0.116 | 0.210 | 0.115 | 0.041 | 23.551 | 8 | 13 | 77 |
| 3 | 20 | terminal | 730 | 0.185 | 0.273 | 0.186 | 0.072 | 12.861 | 20 | 24 | 114 |
| 3 | 20 | peak | 730 | 0.266 | 0.404 | 0.273 | 0.105 | 8.563 | 23 | 39 | 167 |
| 4 | 5 | terminal | 711 | 0.039 | 0.090 | 0.041 | 0.011 | 93.800 | 4 | 6 | 20 |
| 4 | 5 | peak | 711 | 0.048 | 0.115 | 0.052 | 0.013 | 78.000 | 4 | 6 | 26 |
| 4 | 10 | terminal | 685 | 0.105 | 0.187 | 0.108 | 0.028 | 35.053 | 5 | 10 | 61 |
| 4 | 10 | peak | 685 | 0.146 | 0.264 | 0.148 | 0.039 | 24.370 | 7 | 14 | 87 |
| 4 | 20 | terminal | 629 | 0.242 | 0.342 | 0.237 | 0.074 | 12.455 | 22 | 27 | 138 |
| 4 | 20 | peak | 629 | 0.343 | 0.490 | 0.341 | 0.107 | 8.319 | 25 | 46 | 199 |

### Multi-day, 10-session move under 3%

Days with a qualifying name: 958. Mean qualifiers on those days: 3.301. Share of those days with at least 3: 0.579.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 528 | 0.027 | 0.066 | 0.032 | 0.009 | 104.600 | 1 | 4 | 10 |
| 3 | 5 | peak | 528 | 0.045 | 0.087 | 0.040 | 0.016 | 62.360 | 1 | 5 | 19 |
| 3 | 10 | terminal | 505 | 0.071 | 0.141 | 0.079 | 0.024 | 39.946 | 2 | 8 | 27 |
| 3 | 10 | peak | 505 | 0.123 | 0.205 | 0.113 | 0.044 | 21.612 | 2 | 14 | 51 |
| 3 | 20 | terminal | 459 | 0.161 | 0.257 | 0.173 | 0.060 | 15.590 | 8 | 20 | 55 |
| 3 | 20 | peak | 459 | 0.264 | 0.391 | 0.262 | 0.102 | 8.836 | 10 | 38 | 92 |
| 4 | 5 | terminal | 352 | 0.045 | 0.088 | 0.044 | 0.011 | 87.000 | 2 | 4 | 10 |
| 4 | 5 | peak | 352 | 0.071 | 0.115 | 0.054 | 0.018 | 53.154 | 2 | 6 | 18 |
| 4 | 10 | terminal | 335 | 0.116 | 0.183 | 0.106 | 0.031 | 30.905 | 3 | 7 | 32 |
| 4 | 10 | peak | 335 | 0.188 | 0.264 | 0.150 | 0.052 | 18.143 | 3 | 13 | 54 |
| 4 | 20 | terminal | 303 | 0.234 | 0.327 | 0.228 | 0.068 | 13.602 | 9 | 16 | 58 |
| 4 | 20 | peak | 303 | 0.350 | 0.483 | 0.339 | 0.109 | 8.182 | 10 | 30 | 92 |

### Single day, calls-plus-puts baseline at least 100

Days with a qualifying name: 1045. Mean qualifiers on those days: 9.467. Share of those days with at least 3: 0.960.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 964 | 0.024 | 0.067 | 0.034 | 0.008 | 124.739 | 1 | 4 | 18 |
| 3 | 5 | peak | 964 | 0.038 | 0.087 | 0.042 | 0.013 | 75.105 | 1 | 5 | 32 |
| 3 | 10 | terminal | 926 | 0.081 | 0.141 | 0.085 | 0.028 | 34.615 | 6 | 14 | 58 |
| 3 | 10 | peak | 926 | 0.114 | 0.202 | 0.119 | 0.040 | 23.804 | 10 | 21 | 81 |
| 3 | 20 | terminal | 844 | 0.192 | 0.262 | 0.189 | 0.070 | 13.386 | 25 | 38 | 113 |
| 3 | 20 | peak | 844 | 0.269 | 0.389 | 0.278 | 0.102 | 8.852 | 29 | 51 | 177 |
| 4 | 5 | terminal | 927 | 0.031 | 0.088 | 0.045 | 0.008 | 126.862 | 2 | 6 | 21 |
| 4 | 5 | peak | 927 | 0.045 | 0.112 | 0.056 | 0.012 | 79.609 | 2 | 7 | 37 |
| 4 | 10 | terminal | 889 | 0.109 | 0.181 | 0.112 | 0.029 | 33.524 | 8 | 17 | 78 |
| 4 | 10 | peak | 889 | 0.151 | 0.256 | 0.155 | 0.041 | 23.190 | 12 | 25 | 110 |
| 4 | 20 | terminal | 810 | 0.244 | 0.328 | 0.241 | 0.073 | 12.787 | 33 | 48 | 154 |
| 4 | 20 | peak | 810 | 0.328 | 0.474 | 0.349 | 0.104 | 8.586 | 37 | 67 | 234 |

### Multi-day, calls-plus-puts baseline at least 100

Days with a qualifying name: 1034. Mean qualifiers on those days: 6.467. Share of those days with at least 3: 0.898.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 894 | 0.048 | 0.066 | 0.034 | 0.017 | 58.600 | 2 | 13 | 30 |
| 3 | 5 | peak | 894 | 0.058 | 0.086 | 0.043 | 0.021 | 47.764 | 2 | 14 | 39 |
| 3 | 10 | terminal | 858 | 0.090 | 0.140 | 0.086 | 0.031 | 30.778 | 2 | 19 | 60 |
| 3 | 10 | peak | 858 | 0.136 | 0.202 | 0.120 | 0.050 | 19.109 | 4 | 24 | 100 |
| 3 | 20 | terminal | 788 | 0.188 | 0.261 | 0.188 | 0.069 | 13.503 | 12 | 35 | 116 |
| 3 | 20 | peak | 788 | 0.284 | 0.389 | 0.278 | 0.111 | 7.989 | 16 | 53 | 194 |
| 4 | 5 | terminal | 808 | 0.057 | 0.086 | 0.045 | 0.015 | 64.959 | 3 | 13 | 33 |
| 4 | 5 | peak | 808 | 0.072 | 0.112 | 0.056 | 0.019 | 50.302 | 3 | 15 | 45 |
| 4 | 10 | terminal | 775 | 0.119 | 0.179 | 0.112 | 0.031 | 30.959 | 5 | 25 | 67 |
| 4 | 10 | peak | 775 | 0.175 | 0.256 | 0.156 | 0.049 | 19.395 | 7 | 33 | 112 |
| 4 | 20 | terminal | 712 | 0.240 | 0.324 | 0.238 | 0.070 | 13.384 | 15 | 46 | 137 |
| 4 | 20 | peak | 712 | 0.351 | 0.473 | 0.348 | 0.109 | 8.158 | 19 | 69 | 223 |

### Equal-weight P&L

Stock is bought at the scoring close. The call is the nearest monthly contract whose delta is closest to 0.30 and between 0.20 and 0.40, bought at the ask and sold at the bid on the horizon or at expiry, whichever comes first. Each slate’s return is the average of the names that have a price. Hit rate is the share of those slate returns that are positive.

| Screen | Horizon | Leg | Slates | Mean | Median | Hit rate | Worst decile |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| single 3 | 5 | stock | 943 | 0.000 | 0.001 | 0.514 | -0.042 |
| single 3 | 5 | call | 669 | -0.161 | -0.455 | 0.253 | -0.876 |
| single 3 | 10 | stock | 906 | -0.001 | -0.001 | 0.489 | -0.059 |
| single 3 | 10 | call | 532 | 0.258 | -0.303 | 0.380 | -0.917 |
| single 3 | 20 | stock | 834 | -0.000 | -0.000 | 0.494 | -0.090 |
| single 3 | 20 | call | 344 | 1.335 | 0.717 | 0.657 | -0.800 |
| single 4 | 5 | stock | 894 | 0.000 | 0.001 | 0.519 | -0.042 |
| single 4 | 5 | call | 675 | -0.140 | -0.424 | 0.243 | -0.867 |
| single 4 | 10 | stock | 862 | 0.000 | -0.000 | 0.499 | -0.055 |
| single 4 | 10 | call | 556 | 0.342 | -0.151 | 0.424 | -0.897 |
| single 4 | 20 | stock | 792 | 0.003 | 0.002 | 0.524 | -0.080 |
| single 4 | 20 | call | 404 | 1.274 | 0.726 | 0.681 | -0.833 |
| multi 3 | 5 | stock | 770 | 0.002 | 0.003 | 0.529 | -0.043 |
| multi 3 | 5 | call | 560 | 0.008 | -0.404 | 0.291 | -0.866 |
| multi 3 | 10 | stock | 743 | 0.002 | 0.002 | 0.518 | -0.058 |
| multi 3 | 10 | call | 461 | 0.439 | -0.236 | 0.397 | -0.906 |
| multi 3 | 20 | stock | 681 | -0.003 | -0.001 | 0.489 | -0.087 |
| multi 3 | 20 | call | 270 | 1.560 | 0.667 | 0.626 | -0.857 |
| multi 4 | 5 | stock | 628 | 0.001 | 0.001 | 0.513 | -0.040 |
| multi 4 | 5 | call | 485 | -0.019 | -0.370 | 0.299 | -0.856 |
| multi 4 | 10 | stock | 603 | 0.001 | 0.001 | 0.506 | -0.059 |
| multi 4 | 10 | call | 409 | 0.384 | -0.283 | 0.406 | -0.900 |
| multi 4 | 20 | stock | 551 | -0.002 | -0.000 | 0.497 | -0.080 |
| multi 4 | 20 | call | 261 | 1.425 | 0.778 | 0.640 | -0.843 |

single top 3, 5 sessions, mean by year: 2021 stock -0.015 / call -0.406; 2022 stock -0.006 / call -0.283; 2023 stock 0.002 / call -0.143; 2024 stock 0.000 / call -0.027; 2025 stock 0.005 / call -0.107; 2026 stock 0.001 / call -0.305.
single top 3, 10 sessions, mean by year: 2021 stock -0.016 / call -0.229; 2022 stock -0.020 / call -0.209; 2023 stock -0.001 / call 0.256; 2024 stock 0.006 / call 0.774; 2025 stock 0.013 / call 0.343; 2026 stock -0.005 / call -0.024.
single top 3, 20 sessions, mean by year: 2021 stock -0.039 / call 1.242; 2022 stock -0.022 / call 0.641; 2023 stock 0.001 / call 2.041; 2024 stock 0.003 / call 1.683; 2025 stock 0.019 / call 1.201; 2026 stock 0.001 / call 0.459.
single top 4, 5 sessions, mean by year: 2021 stock -0.018 / call -0.309; 2022 stock -0.007 / call -0.236; 2023 stock 0.003 / call -0.116; 2024 stock -0.001 / call -0.093; 2025 stock 0.006 / call -0.060; 2026 stock 0.003 / call -0.268.
single top 4, 10 sessions, mean by year: 2021 stock -0.022 / call -0.061; 2022 stock -0.018 / call -0.109; 2023 stock -0.000 / call 0.411; 2024 stock 0.007 / call 0.696; 2025 stock 0.014 / call 0.438; 2026 stock -0.002 / call 0.083.
single top 4, 20 sessions, mean by year: 2021 stock -0.042 / call 1.217; 2022 stock -0.014 / call 0.862; 2023 stock 0.002 / call 1.839; 2024 stock 0.003 / call 1.398; 2025 stock 0.022 / call 1.180; 2026 stock 0.013 / call 0.545.
multi top 3, 5 sessions, mean by year: 2021 stock 0.002 / call 0.401; 2022 stock -0.004 / call -0.266; 2023 stock 0.001 / call 0.045; 2024 stock 0.003 / call -0.023; 2025 stock 0.006 / call 0.088; 2026 stock 0.004 / call 0.034.
multi top 3, 10 sessions, mean by year: 2021 stock 0.003 / call 1.450; 2022 stock -0.015 / call 0.062; 2023 stock -0.001 / call 0.464; 2024 stock 0.005 / call 0.305; 2025 stock 0.011 / call 0.528; 2026 stock 0.013 / call 0.565.
multi top 3, 20 sessions, mean by year: 2021 stock -0.031 / call 3.860; 2022 stock -0.021 / call 0.902; 2023 stock -0.007 / call 1.839; 2024 stock 0.005 / call 1.465; 2025 stock 0.005 / call 1.657; 2026 stock 0.019 / call 0.921.
multi top 4, 5 sessions, mean by year: 2021 stock 0.001 / call -0.355; 2022 stock -0.002 / call -0.048; 2023 stock -0.000 / call -0.018; 2024 stock -0.000 / call -0.114; 2025 stock 0.005 / call 0.185; 2026 stock 0.004 / call -0.088.
multi top 4, 10 sessions, mean by year: 2021 stock -0.003 / call 0.565; 2022 stock -0.014 / call 0.360; 2023 stock -0.004 / call 0.350; 2024 stock 0.005 / call 0.246; 2025 stock 0.009 / call 0.518; 2026 stock 0.009 / call 0.392.
multi top 4, 20 sessions, mean by year: 2021 stock -0.030 / call 2.435; 2022 stock -0.022 / call 1.486; 2023 stock -0.004 / call 1.590; 2024 stock 0.009 / call 0.876; 2025 stock 0.002 / call 1.965; 2026 stock 0.010 / call 0.879.

### Examples with a 15% rise within 20 sessions

- NLSN 2022-03-03 multi-day, call ratio 67.774, 10-session return -0.045, spike days 3 (2 consecutive), later ma.
- NLSN 2022-03-02 multi-day, call ratio 65.452, 10-session return -0.031, spike days 3 (2 consecutive), later ma.
- SGFY 2022-02-04 multi-day, call ratio 44.277, 10-session return 0.046, spike days 3 (2 consecutive), later ma.
- SGFY 2022-02-03 multi-day, call ratio 41.142, 10-session return 0.008, spike days 3 (2 consecutive), later ma.
- COMP 2026-01-02 multi-day, call ratio 35.272, 10-session return -0.003, spike days 2 (1 consecutive), later ma.
- COMP 2025-12-31 multi-day, call ratio 35.015, 10-session return -0.028, spike days 1 (1 consecutive), later ma.
- WNS 2025-06-18 single day, call ratio 34.962, 10-session return 0.007, spike days 1 (1 consecutive), later ma.
- WNS 2025-06-17 single day, call ratio 27.833, 10-session return 0.033, spike days 1 (1 consecutive), later ma.
- ADNT 2022-02-03 single day, call ratio 21.187, 10-session return -0.028, spike days 1 (1 consecutive), later ma.
- SMPL 2024-04-08 multi-day, call ratio 19.590, 10-session return -0.033, spike days 4 (4 consecutive), later ma.
- SILK 2024-06-10 single day, call ratio 18.931, 10-session return -0.040, spike days 1 (1 consecutive), later ma.
- PR 2023-07-27 single day, call ratio 18.319, 10-session return -0.044, spike days 1 (1 consecutive), later ma.
- SILK 2024-06-07 single day, call ratio 18.077, 10-session return -0.033, spike days 1 (1 consecutive), later ma.
- PR 2023-07-26 single day, call ratio 17.913, 10-session return -0.023, spike days 1 (1 consecutive), later ma.
- BKI 2023-06-28 single day, call ratio 16.965, 10-session return 0.040, spike days 1 (1 consecutive), later ma.
- BKI 2023-06-27 single day, call ratio 16.683, 10-session return 0.013, spike days 1 (1 consecutive), later ma.
- SAVE 2022-01-19 multi-day, call ratio 16.571, 10-session return -0.033, spike days 3 (2 consecutive), later ma.
- SAVE 2022-01-20 multi-day, call ratio 16.540, 10-session return 0.001, spike days 4 (2 consecutive), later ma.
- RDNT 2025-04-22 single day, call ratio 15.841, 10-session return -0.023, spike days 1 (1 consecutive), later ma.
- RDNT 2025-04-23 single day, call ratio 15.603, 10-session return 0.023, spike days 1 (1 consecutive), later ma.

### Resolved cases on this screen

These are loud call days inside the documented trade window. A day passes the stock gate only when the 10-session move is under 5%.
- lantheus_2022 LNTH 2022-02-24 ratio 20.822, 10-session return 0.434, spike days 1, stock already moved.
- maxar_2022 MAXR 2022-12-16 ratio 19.471, 10-session return 1.019, spike days 2, stock already moved.
- pfizer_2021 PFE 2021-11-04 ratio 11.460, 10-session return 0.023, spike days 2, stock quiet.
- zogenix_2022 ZGNX 2022-01-19 ratio 12.729, 10-session return 0.548, spike days 1, stock already moved.

A qualifying name is a review tag. It is not an identification of a trader.
