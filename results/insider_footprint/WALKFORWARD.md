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

Days with a qualifying name: 1045. Mean qualifiers on those days: 9.650. Share of those days with at least 3: 0.962.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 961 | 0.021 | 0.069 | 0.031 | 0.007 | 143.150 | 1 | 3 | 16 |
| 3 | 5 | peak | 961 | 0.030 | 0.090 | 0.039 | 0.010 | 98.414 | 1 | 3 | 25 |
| 3 | 10 | terminal | 923 | 0.069 | 0.142 | 0.078 | 0.023 | 41.600 | 6 | 7 | 52 |
| 3 | 10 | peak | 923 | 0.093 | 0.205 | 0.110 | 0.031 | 30.828 | 8 | 11 | 68 |
| 3 | 20 | terminal | 844 | 0.161 | 0.260 | 0.174 | 0.061 | 15.335 | 24 | 27 | 104 |
| 3 | 20 | peak | 844 | 0.230 | 0.391 | 0.259 | 0.089 | 10.253 | 27 | 40 | 158 |
| 4 | 5 | terminal | 928 | 0.032 | 0.091 | 0.041 | 0.008 | 122.733 | 1 | 5 | 24 |
| 4 | 5 | peak | 928 | 0.040 | 0.117 | 0.051 | 0.010 | 96.684 | 1 | 5 | 32 |
| 4 | 10 | terminal | 891 | 0.094 | 0.183 | 0.102 | 0.024 | 40.442 | 7 | 10 | 69 |
| 4 | 10 | peak | 891 | 0.128 | 0.262 | 0.143 | 0.034 | 28.213 | 11 | 14 | 97 |
| 4 | 20 | terminal | 814 | 0.224 | 0.325 | 0.222 | 0.068 | 13.800 | 33 | 37 | 150 |
| 4 | 20 | peak | 814 | 0.306 | 0.476 | 0.326 | 0.096 | 9.436 | 36 | 54 | 222 |

### Multi-day build, call baseline, 10-session move under 5%

Days with a qualifying name: 1028. Mean qualifiers on those days: 5.596. Share of those days with at least 3: 0.870.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 856 | 0.039 | 0.068 | 0.031 | 0.013 | 74.529 | 1 | 9 | 24 |
| 3 | 5 | peak | 856 | 0.053 | 0.090 | 0.039 | 0.018 | 53.638 | 1 | 11 | 35 |
| 3 | 10 | terminal | 822 | 0.074 | 0.142 | 0.079 | 0.027 | 36.364 | 2 | 13 | 51 |
| 3 | 10 | peak | 822 | 0.127 | 0.206 | 0.111 | 0.045 | 21.018 | 3 | 21 | 88 |
| 3 | 20 | terminal | 753 | 0.154 | 0.258 | 0.173 | 0.056 | 16.929 | 10 | 22 | 94 |
| 3 | 20 | peak | 753 | 0.246 | 0.390 | 0.259 | 0.093 | 9.809 | 13 | 44 | 152 |
| 4 | 5 | terminal | 725 | 0.052 | 0.089 | 0.040 | 0.014 | 71.500 | 3 | 9 | 28 |
| 4 | 5 | peak | 725 | 0.070 | 0.117 | 0.051 | 0.019 | 52.704 | 3 | 11 | 40 |
| 4 | 10 | terminal | 691 | 0.110 | 0.184 | 0.104 | 0.030 | 32.707 | 2 | 19 | 61 |
| 4 | 10 | peak | 691 | 0.175 | 0.263 | 0.146 | 0.049 | 19.474 | 5 | 29 | 101 |
| 4 | 20 | terminal | 631 | 0.214 | 0.326 | 0.225 | 0.061 | 15.390 | 11 | 29 | 114 |
| 4 | 20 | peak | 631 | 0.330 | 0.480 | 0.330 | 0.100 | 8.976 | 14 | 54 | 185 |

### Single day, next-morning open-interest confirmation

Days with a qualifying name: 1025. Mean qualifiers on those days: 5.071. Share of those days with at least 3: 0.830.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 818 | 0.029 | 0.070 | 0.031 | 0.010 | 101.250 | 1 | 5 | 18 |
| 3 | 5 | peak | 818 | 0.038 | 0.091 | 0.039 | 0.013 | 75.688 | 1 | 5 | 26 |
| 3 | 10 | terminal | 785 | 0.084 | 0.143 | 0.079 | 0.028 | 34.149 | 4 | 9 | 54 |
| 3 | 10 | peak | 785 | 0.117 | 0.207 | 0.111 | 0.041 | 23.531 | 6 | 13 | 77 |
| 3 | 20 | terminal | 720 | 0.201 | 0.264 | 0.179 | 0.077 | 12.012 | 20 | 34 | 112 |
| 3 | 20 | peak | 720 | 0.263 | 0.395 | 0.264 | 0.107 | 8.310 | 21 | 51 | 160 |
| 4 | 5 | terminal | 683 | 0.045 | 0.094 | 0.043 | 0.012 | 84.375 | 2 | 6 | 24 |
| 4 | 5 | peak | 683 | 0.056 | 0.120 | 0.053 | 0.015 | 67.300 | 2 | 6 | 32 |
| 4 | 10 | terminal | 656 | 0.117 | 0.186 | 0.105 | 0.030 | 31.800 | 6 | 12 | 62 |
| 4 | 10 | peak | 656 | 0.160 | 0.266 | 0.147 | 0.043 | 22.018 | 9 | 17 | 88 |
| 4 | 20 | terminal | 599 | 0.265 | 0.332 | 0.229 | 0.080 | 11.545 | 25 | 41 | 125 |
| 4 | 20 | peak | 599 | 0.339 | 0.482 | 0.334 | 0.110 | 8.110 | 26 | 60 | 177 |

### Multi-day, next-morning open-interest confirmation

Days with a qualifying name: 1014. Mean qualifiers on those days: 4.509. Share of those days with at least 3: 0.772.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 749 | 0.053 | 0.068 | 0.031 | 0.019 | 52.500 | 3 | 10 | 29 |
| 3 | 5 | peak | 749 | 0.069 | 0.091 | 0.040 | 0.024 | 39.855 | 3 | 12 | 40 |
| 3 | 10 | terminal | 718 | 0.085 | 0.144 | 0.081 | 0.031 | 31.636 | 3 | 13 | 50 |
| 3 | 10 | peak | 718 | 0.149 | 0.208 | 0.114 | 0.055 | 17.254 | 6 | 23 | 89 |
| 3 | 20 | terminal | 656 | 0.157 | 0.259 | 0.175 | 0.058 | 16.263 | 11 | 23 | 80 |
| 3 | 20 | peak | 656 | 0.255 | 0.392 | 0.262 | 0.100 | 9.041 | 13 | 43 | 140 |
| 4 | 5 | terminal | 586 | 0.056 | 0.088 | 0.041 | 0.015 | 67.941 | 3 | 8 | 23 |
| 4 | 5 | peak | 586 | 0.073 | 0.115 | 0.051 | 0.019 | 51.089 | 3 | 10 | 32 |
| 4 | 10 | terminal | 565 | 0.108 | 0.180 | 0.103 | 0.030 | 32.731 | 3 | 16 | 48 |
| 4 | 10 | peak | 565 | 0.182 | 0.260 | 0.145 | 0.050 | 18.825 | 5 | 25 | 84 |
| 4 | 20 | terminal | 512 | 0.217 | 0.319 | 0.219 | 0.060 | 15.787 | 10 | 24 | 88 |
| 4 | 20 | peak | 512 | 0.320 | 0.472 | 0.324 | 0.097 | 9.343 | 13 | 43 | 142 |

### Single day, no earnings filing in the next 5 sessions

Days with a qualifying name: 1044. Mean qualifiers on those days: 9.244. Share of those days with at least 3: 0.959.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 957 | 0.019 | 0.069 | 0.031 | 0.006 | 158.500 | 1 | 0 | 17 |
| 3 | 5 | peak | 957 | 0.028 | 0.090 | 0.038 | 0.009 | 105.333 | 1 | 0 | 26 |
| 3 | 10 | terminal | 919 | 0.070 | 0.142 | 0.078 | 0.024 | 41.415 | 6 | 4 | 55 |
| 3 | 10 | peak | 919 | 0.091 | 0.205 | 0.110 | 0.031 | 31.435 | 8 | 5 | 72 |
| 3 | 20 | terminal | 841 | 0.159 | 0.260 | 0.174 | 0.060 | 15.599 | 23 | 18 | 111 |
| 3 | 20 | peak | 841 | 0.227 | 0.391 | 0.259 | 0.087 | 10.468 | 26 | 28 | 166 |
| 4 | 5 | terminal | 924 | 0.028 | 0.090 | 0.041 | 0.007 | 141.154 | 2 | 0 | 24 |
| 4 | 5 | peak | 924 | 0.036 | 0.117 | 0.051 | 0.009 | 107.706 | 2 | 0 | 32 |
| 4 | 10 | terminal | 886 | 0.093 | 0.183 | 0.103 | 0.024 | 40.694 | 7 | 6 | 72 |
| 4 | 10 | peak | 886 | 0.122 | 0.262 | 0.143 | 0.032 | 29.817 | 9 | 7 | 99 |
| 4 | 20 | terminal | 810 | 0.216 | 0.325 | 0.222 | 0.065 | 14.283 | 30 | 25 | 157 |
| 4 | 20 | peak | 810 | 0.296 | 0.476 | 0.326 | 0.093 | 9.728 | 33 | 39 | 230 |

### Multi-day, no earnings filing in the next 5 sessions

Days with a qualifying name: 1028. Mean qualifiers on those days: 5.319. Share of those days with at least 3: 0.857.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 843 | 0.033 | 0.067 | 0.030 | 0.011 | 89.321 | 2 | 0 | 26 |
| 3 | 5 | peak | 843 | 0.045 | 0.089 | 0.038 | 0.015 | 63.846 | 2 | 0 | 37 |
| 3 | 10 | terminal | 809 | 0.070 | 0.141 | 0.078 | 0.025 | 39.450 | 2 | 5 | 53 |
| 3 | 10 | peak | 809 | 0.117 | 0.205 | 0.110 | 0.042 | 23.030 | 3 | 7 | 91 |
| 3 | 20 | terminal | 741 | 0.148 | 0.257 | 0.172 | 0.054 | 17.681 | 10 | 13 | 96 |
| 3 | 20 | peak | 741 | 0.240 | 0.389 | 0.258 | 0.089 | 10.227 | 13 | 28 | 157 |
| 4 | 5 | terminal | 697 | 0.043 | 0.087 | 0.040 | 0.011 | 88.935 | 3 | 0 | 28 |
| 4 | 5 | peak | 697 | 0.057 | 0.115 | 0.050 | 0.015 | 63.837 | 3 | 0 | 40 |
| 4 | 10 | terminal | 667 | 0.100 | 0.181 | 0.102 | 0.027 | 35.548 | 3 | 6 | 64 |
| 4 | 10 | peak | 667 | 0.156 | 0.260 | 0.143 | 0.043 | 22.200 | 5 | 7 | 103 |
| 4 | 20 | terminal | 613 | 0.210 | 0.323 | 0.223 | 0.060 | 15.568 | 11 | 17 | 120 |
| 4 | 20 | peak | 613 | 0.315 | 0.477 | 0.328 | 0.096 | 9.390 | 14 | 31 | 191 |

### Single day, 10-session move under 3%

Days with a qualifying name: 1031. Mean qualifiers on those days: 6.468. Share of those days with at least 3: 0.887.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 882 | 0.022 | 0.069 | 0.029 | 0.008 | 131.300 | 0 | 3 | 17 |
| 3 | 5 | peak | 882 | 0.029 | 0.090 | 0.036 | 0.010 | 97.000 | 0 | 4 | 23 |
| 3 | 10 | terminal | 848 | 0.073 | 0.144 | 0.074 | 0.025 | 38.750 | 3 | 7 | 54 |
| 3 | 10 | peak | 848 | 0.103 | 0.208 | 0.104 | 0.036 | 26.956 | 6 | 9 | 76 |
| 3 | 20 | terminal | 771 | 0.161 | 0.264 | 0.167 | 0.063 | 14.952 | 19 | 20 | 106 |
| 3 | 20 | peak | 771 | 0.232 | 0.395 | 0.249 | 0.091 | 9.962 | 22 | 33 | 156 |
| 4 | 5 | terminal | 793 | 0.033 | 0.090 | 0.038 | 0.009 | 112.286 | 2 | 7 | 19 |
| 4 | 5 | peak | 793 | 0.043 | 0.117 | 0.048 | 0.011 | 87.111 | 2 | 8 | 26 |
| 4 | 10 | terminal | 763 | 0.092 | 0.186 | 0.098 | 0.025 | 39.693 | 4 | 12 | 59 |
| 4 | 10 | peak | 763 | 0.132 | 0.265 | 0.137 | 0.036 | 27.000 | 8 | 17 | 84 |
| 4 | 20 | terminal | 695 | 0.214 | 0.331 | 0.215 | 0.065 | 14.359 | 22 | 30 | 129 |
| 4 | 20 | peak | 695 | 0.309 | 0.482 | 0.315 | 0.095 | 9.530 | 25 | 48 | 191 |

### Multi-day, 10-session move under 3%

Days with a qualifying name: 992. Mean qualifiers on those days: 3.719. Share of those days with at least 3: 0.664.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 626 | 0.027 | 0.066 | 0.028 | 0.010 | 103.333 | 1 | 4 | 13 |
| 3 | 5 | peak | 626 | 0.043 | 0.087 | 0.035 | 0.015 | 66.071 | 1 | 5 | 22 |
| 3 | 10 | terminal | 598 | 0.069 | 0.139 | 0.073 | 0.023 | 41.714 | 2 | 9 | 31 |
| 3 | 10 | peak | 598 | 0.114 | 0.203 | 0.103 | 0.041 | 23.243 | 2 | 16 | 56 |
| 3 | 20 | terminal | 541 | 0.152 | 0.250 | 0.156 | 0.056 | 16.835 | 7 | 21 | 63 |
| 3 | 20 | peak | 541 | 0.248 | 0.382 | 0.239 | 0.094 | 9.678 | 9 | 41 | 102 |
| 4 | 5 | terminal | 433 | 0.044 | 0.089 | 0.038 | 0.011 | 90.158 | 2 | 4 | 13 |
| 4 | 5 | peak | 433 | 0.065 | 0.117 | 0.048 | 0.017 | 58.724 | 2 | 5 | 22 |
| 4 | 10 | terminal | 413 | 0.109 | 0.182 | 0.095 | 0.029 | 33.417 | 3 | 8 | 37 |
| 4 | 10 | peak | 413 | 0.174 | 0.262 | 0.135 | 0.048 | 19.650 | 3 | 13 | 64 |
| 4 | 20 | terminal | 373 | 0.212 | 0.317 | 0.204 | 0.060 | 15.764 | 8 | 19 | 62 |
| 4 | 20 | peak | 373 | 0.314 | 0.473 | 0.307 | 0.095 | 9.582 | 9 | 34 | 98 |

### Single day, calls-plus-puts baseline at least 100

Days with a qualifying name: 1047. Mean qualifiers on those days: 10.984. Share of those days with at least 3: 0.974.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 974 | 0.022 | 0.066 | 0.031 | 0.007 | 138.143 | 1 | 4 | 16 |
| 3 | 5 | peak | 974 | 0.034 | 0.086 | 0.038 | 0.012 | 84.941 | 1 | 4 | 29 |
| 3 | 10 | terminal | 935 | 0.073 | 0.137 | 0.078 | 0.025 | 39.652 | 6 | 11 | 52 |
| 3 | 10 | peak | 935 | 0.102 | 0.198 | 0.110 | 0.035 | 27.918 | 8 | 17 | 72 |
| 3 | 20 | terminal | 852 | 0.170 | 0.254 | 0.174 | 0.061 | 15.280 | 23 | 35 | 99 |
| 3 | 20 | peak | 852 | 0.239 | 0.381 | 0.259 | 0.090 | 10.113 | 25 | 46 | 159 |
| 4 | 5 | terminal | 941 | 0.031 | 0.086 | 0.041 | 0.008 | 128.793 | 1 | 5 | 23 |
| 4 | 5 | peak | 941 | 0.041 | 0.112 | 0.051 | 0.011 | 88.619 | 1 | 5 | 36 |
| 4 | 10 | terminal | 903 | 0.097 | 0.176 | 0.102 | 0.025 | 38.692 | 7 | 13 | 71 |
| 4 | 10 | peak | 903 | 0.131 | 0.251 | 0.143 | 0.035 | 27.441 | 11 | 19 | 97 |
| 4 | 20 | terminal | 824 | 0.215 | 0.315 | 0.221 | 0.063 | 14.770 | 30 | 39 | 140 |
| 4 | 20 | peak | 824 | 0.295 | 0.462 | 0.324 | 0.092 | 9.914 | 33 | 54 | 215 |

### Multi-day, calls-plus-puts baseline at least 100

Days with a qualifying name: 1040. Mean qualifiers on those days: 7.417. Share of those days with at least 3: 0.940.

| Slate | Horizon | Jump | Dates | Date hit rate | Tradable base | Quiet base | Per pick | Misses per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 5 | terminal | 939 | 0.048 | 0.067 | 0.031 | 0.017 | 58.936 | 1 | 14 | 32 |
| 3 | 5 | peak | 939 | 0.058 | 0.088 | 0.039 | 0.020 | 48.421 | 1 | 15 | 41 |
| 3 | 10 | terminal | 901 | 0.089 | 0.139 | 0.079 | 0.031 | 31.566 | 3 | 20 | 60 |
| 3 | 10 | peak | 901 | 0.130 | 0.201 | 0.112 | 0.047 | 20.452 | 4 | 24 | 98 |
| 3 | 20 | terminal | 825 | 0.179 | 0.255 | 0.175 | 0.065 | 14.373 | 13 | 34 | 114 |
| 3 | 20 | peak | 825 | 0.261 | 0.384 | 0.261 | 0.101 | 8.900 | 17 | 50 | 183 |
| 4 | 5 | terminal | 880 | 0.057 | 0.086 | 0.041 | 0.015 | 65.415 | 2 | 15 | 36 |
| 4 | 5 | peak | 880 | 0.069 | 0.112 | 0.051 | 0.019 | 52.333 | 2 | 16 | 48 |
| 4 | 10 | terminal | 842 | 0.108 | 0.176 | 0.103 | 0.029 | 33.722 | 2 | 25 | 70 |
| 4 | 10 | peak | 842 | 0.164 | 0.253 | 0.144 | 0.046 | 20.870 | 4 | 33 | 117 |
| 4 | 20 | terminal | 773 | 0.223 | 0.316 | 0.222 | 0.062 | 15.104 | 12 | 42 | 138 |
| 4 | 20 | peak | 773 | 0.325 | 0.466 | 0.326 | 0.098 | 9.171 | 16 | 64 | 224 |

### Equal-weight P&L

Stock is bought at the scoring close. The call is the nearest monthly contract whose delta is closest to 0.30 and between 0.20 and 0.40, bought at the ask and sold at the bid on the horizon or at expiry, whichever comes first. Each slate’s return is the average of the names that have a price. Hit rate is the share of those slate returns that are positive.

| Screen | Horizon | Leg | Slates | Mean | Median | Hit rate | Worst decile |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| single 3 | 5 | stock | 964 | -0.000 | 0.001 | 0.520 | -0.040 |
| single 3 | 5 | call | 676 | -0.174 | -0.466 | 0.237 | -0.872 |
| single 3 | 10 | stock | 927 | -0.000 | -0.001 | 0.494 | -0.054 |
| single 3 | 10 | call | 545 | 0.212 | -0.360 | 0.365 | -0.921 |
| single 3 | 20 | stock | 852 | 0.000 | -0.000 | 0.495 | -0.083 |
| single 3 | 20 | call | 360 | 1.322 | 0.706 | 0.647 | -0.824 |
| single 4 | 5 | stock | 931 | 0.000 | 0.000 | 0.503 | -0.038 |
| single 4 | 5 | call | 699 | -0.122 | -0.407 | 0.255 | -0.851 |
| single 4 | 10 | stock | 896 | 0.001 | -0.000 | 0.493 | -0.050 |
| single 4 | 10 | call | 580 | 0.296 | -0.216 | 0.405 | -0.906 |
| single 4 | 20 | stock | 825 | 0.003 | 0.003 | 0.536 | -0.074 |
| single 4 | 20 | call | 421 | 1.274 | 0.745 | 0.663 | -0.816 |
| multi 3 | 5 | stock | 857 | 0.002 | 0.003 | 0.530 | -0.040 |
| multi 3 | 5 | call | 629 | 0.009 | -0.405 | 0.296 | -0.860 |
| multi 3 | 10 | stock | 825 | 0.002 | 0.001 | 0.512 | -0.057 |
| multi 3 | 10 | call | 511 | 0.467 | -0.200 | 0.440 | -0.900 |
| multi 3 | 20 | stock | 756 | -0.004 | -0.001 | 0.487 | -0.084 |
| multi 3 | 20 | call | 306 | 1.632 | 0.667 | 0.660 | -0.830 |
| multi 4 | 5 | stock | 726 | 0.002 | 0.002 | 0.525 | -0.038 |
| multi 4 | 5 | call | 560 | -0.019 | -0.377 | 0.302 | -0.851 |
| multi 4 | 10 | stock | 696 | 0.002 | 0.003 | 0.545 | -0.058 |
| multi 4 | 10 | call | 470 | 0.415 | -0.149 | 0.432 | -0.875 |
| multi 4 | 20 | stock | 636 | -0.002 | -0.000 | 0.498 | -0.078 |
| multi 4 | 20 | call | 308 | 1.486 | 0.775 | 0.649 | -0.800 |

single top 3, 5 sessions, mean by year: 2021 stock -0.013 / call -0.408; 2022 stock -0.004 / call -0.316; 2023 stock 0.002 / call -0.065; 2024 stock 0.000 / call -0.161; 2025 stock 0.004 / call -0.103; 2026 stock -0.000 / call -0.302.
single top 3, 10 sessions, mean by year: 2021 stock -0.012 / call -0.233; 2022 stock -0.016 / call -0.274; 2023 stock 0.000 / call 0.297; 2024 stock 0.006 / call 0.507; 2025 stock 0.012 / call 0.412; 2026 stock -0.006 / call -0.095.
single top 3, 20 sessions, mean by year: 2021 stock -0.036 / call 0.581; 2022 stock -0.019 / call 0.523; 2023 stock 0.001 / call 1.875; 2024 stock 0.003 / call 1.688; 2025 stock 0.019 / call 1.454; 2026 stock 0.000 / call 0.396.
single top 4, 5 sessions, mean by year: 2021 stock -0.014 / call -0.338; 2022 stock -0.005 / call -0.259; 2023 stock 0.003 / call -0.043; 2024 stock -0.001 / call -0.098; 2025 stock 0.005 / call -0.054; 2026 stock 0.002 / call -0.225.
single top 4, 10 sessions, mean by year: 2021 stock -0.015 / call -0.135; 2022 stock -0.016 / call -0.147; 2023 stock 0.002 / call 0.400; 2024 stock 0.005 / call 0.543; 2025 stock 0.012 / call 0.429; 2026 stock -0.002 / call 0.101.
single top 4, 20 sessions, mean by year: 2021 stock -0.038 / call 0.932; 2022 stock -0.014 / call 0.731; 2023 stock 0.005 / call 1.728; 2024 stock 0.001 / call 1.398; 2025 stock 0.021 / call 1.380; 2026 stock 0.010 / call 0.581.
multi top 3, 5 sessions, mean by year: 2021 stock 0.005 / call 0.401; 2022 stock -0.003 / call -0.294; 2023 stock 0.002 / call 0.022; 2024 stock 0.001 / call -0.016; 2025 stock 0.006 / call 0.159; 2026 stock 0.001 / call -0.063.
multi top 3, 10 sessions, mean by year: 2021 stock 0.001 / call 1.302; 2022 stock -0.014 / call 0.038; 2023 stock 0.002 / call 0.526; 2024 stock 0.002 / call 0.343; 2025 stock 0.010 / call 0.602; 2026 stock 0.009 / call 0.502.
multi top 3, 20 sessions, mean by year: 2021 stock -0.032 / call 3.355; 2022 stock -0.022 / call 0.865; 2023 stock -0.004 / call 2.038; 2024 stock -0.001 / call 1.505; 2025 stock 0.008 / call 1.863; 2026 stock 0.013 / call 0.759.
multi top 4, 5 sessions, mean by year: 2021 stock -0.000 / call -0.296; 2022 stock -0.002 / call -0.132; 2023 stock 0.001 / call -0.029; 2024 stock 0.001 / call -0.064; 2025 stock 0.005 / call 0.219; 2026 stock 0.004 / call -0.160.
multi top 4, 10 sessions, mean by year: 2021 stock -0.005 / call 0.591; 2022 stock -0.014 / call 0.212; 2023 stock 0.000 / call 0.503; 2024 stock 0.004 / call 0.267; 2025 stock 0.009 / call 0.599; 2026 stock 0.013 / call 0.298.
multi top 4, 20 sessions, mean by year: 2021 stock -0.034 / call 1.980; 2022 stock -0.023 / call 1.037; 2023 stock -0.000 / call 1.935; 2024 stock 0.005 / call 1.072; 2025 stock 0.005 / call 2.011; 2026 stock 0.017 / call 0.571.

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

## Short-dated OTM calls, quiet stock, 2026-11-13

The volume is only calls with strike above the spot and 1–45 days to expiry. A single day is that volume at least 5 times its own prior 20-session average and at least 500 contracts. A multi-day build is two or more of the last five sessions at least 3 times that average, or a five-session total at least 5 times a normal five-session total spread over two or more days. The loudest day is still at least 500. The prior 20-session average of this same volume is at least 100. The stock’s 10-session move is under 5% (a second cut uses 3%), the scoring day is under 3%, and stock volume is under twice its median. Price is at least $5 and median dollar volume is at least $5 million. A delta 0.10–0.35 slice, a next-morning open-interest increase, an earnings blackout, and a single strike holding at least half the short-dated OTM volume are variants. The comparison is a random quiet stock with the same average. Downside hit rates are not in this test.

| Screen | Slate | Horizon | Dates | Date hit rate | Quiet base | Misses per hit | M&A | Earnings | Other |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| OTM strike, single, under 5% | 3 | 10 | 958 | 0.121 | 0.128 | 21.992 | 10 | 23 | 92 |
| OTM strike, single, under 5% | 3 | 20 | 873 | 0.282 | 0.290 | 8.062 | 28 | 53 | 208 |
| OTM strike, single, under 5% | 4 | 10 | 955 | 0.154 | 0.165 | 22.727 | 11 | 30 | 120 |
| OTM strike, single, under 5% | 4 | 20 | 867 | 0.343 | 0.360 | 8.450 | 33 | 61 | 273 |
| OTM strike, multi-day, under 5% | 3 | 10 | 948 | 0.160 | 0.129 | 16.236 | 7 | 29 | 129 |
| OTM strike, multi-day, under 5% | 3 | 20 | 851 | 0.330 | 0.293 | 6.598 | 20 | 55 | 261 |
| OTM strike, multi-day, under 5% | 4 | 10 | 942 | 0.193 | 0.166 | 17.291 | 7 | 36 | 163 |
| OTM strike, multi-day, under 5% | 4 | 20 | 842 | 0.387 | 0.364 | 6.814 | 23 | 64 | 344 |
| Single, open-interest confirmation | 3 | 10 | 951 | 0.113 | 0.127 | 24.248 | 8 | 19 | 86 |
| Single, open-interest confirmation | 3 | 20 | 861 | 0.260 | 0.290 | 8.821 | 26 | 40 | 197 |
| Single, open-interest confirmation | 4 | 10 | 941 | 0.151 | 0.165 | 23.442 | 11 | 22 | 121 |
| Single, open-interest confirmation | 4 | 20 | 850 | 0.331 | 0.361 | 8.605 | 30 | 54 | 270 |
| Multi-day, open-interest confirmation | 3 | 10 | 943 | 0.162 | 0.128 | 15.353 | 6 | 30 | 137 |
| Multi-day, open-interest confirmation | 3 | 20 | 844 | 0.302 | 0.292 | 7.064 | 15 | 46 | 253 |
| Multi-day, open-interest confirmation | 4 | 10 | 933 | 0.194 | 0.165 | 17.029 | 6 | 38 | 163 |
| Multi-day, open-interest confirmation | 4 | 20 | 831 | 0.374 | 0.362 | 7.269 | 16 | 60 | 326 |
| Single, no earnings in 5 sessions | 3 | 10 | 957 | 0.109 | 0.128 | 25.100 | 7 | 11 | 92 |
| Single, no earnings in 5 sessions | 3 | 20 | 872 | 0.274 | 0.290 | 8.343 | 26 | 38 | 216 |
| Single, no earnings in 5 sessions | 4 | 10 | 954 | 0.144 | 0.165 | 24.784 | 8 | 14 | 126 |
| Single, no earnings in 5 sessions | 4 | 20 | 866 | 0.337 | 0.360 | 8.758 | 29 | 44 | 282 |
| Multi-day, no earnings in 5 sessions | 3 | 10 | 946 | 0.149 | 0.129 | 17.429 | 4 | 13 | 137 |
| Multi-day, no earnings in 5 sessions | 3 | 20 | 850 | 0.320 | 0.293 | 6.704 | 18 | 40 | 273 |
| Multi-day, no earnings in 5 sessions | 4 | 10 | 941 | 0.180 | 0.166 | 18.503 | 7 | 14 | 172 |
| Multi-day, no earnings in 5 sessions | 4 | 20 | 842 | 0.381 | 0.363 | 6.888 | 23 | 44 | 360 |
| Single, 10-session move under 3% | 3 | 10 | 952 | 0.113 | 0.128 | 23.621 | 8 | 14 | 94 |
| Single, 10-session move under 3% | 3 | 20 | 867 | 0.279 | 0.290 | 8.031 | 26 | 41 | 221 |
| Single, 10-session move under 3% | 4 | 10 | 947 | 0.141 | 0.164 | 24.086 | 10 | 20 | 121 |
| Single, 10-session move under 3% | 4 | 20 | 857 | 0.334 | 0.359 | 8.575 | 31 | 54 | 273 |
| Multi-day, 10-session move under 3% | 3 | 10 | 938 | 0.142 | 0.128 | 18.817 | 11 | 20 | 111 |
| Multi-day, 10-session move under 3% | 3 | 20 | 836 | 0.294 | 0.292 | 7.416 | 18 | 44 | 236 |
| Multi-day, 10-session move under 3% | 4 | 10 | 923 | 0.184 | 0.166 | 18.638 | 13 | 29 | 146 |
| Multi-day, 10-session move under 3% | 4 | 20 | 818 | 0.368 | 0.363 | 7.499 | 24 | 58 | 303 |
| Delta 0.10–0.35, single | 3 | 10 | 964 | 0.114 | 0.130 | 24.148 | 3 | 20 | 92 |
| Delta 0.10–0.35, single | 3 | 20 | 880 | 0.261 | 0.292 | 9.076 | 8 | 58 | 196 |
| Delta 0.10–0.35, single | 4 | 10 | 959 | 0.150 | 0.168 | 23.590 | 4 | 22 | 130 |
| Delta 0.10–0.35, single | 4 | 20 | 873 | 0.324 | 0.361 | 9.092 | 10 | 73 | 263 |
| Delta 0.10–0.35, multi-day | 3 | 10 | 943 | 0.150 | 0.131 | 17.612 | 13 | 23 | 116 |
| Delta 0.10–0.35, multi-day | 3 | 20 | 853 | 0.319 | 0.293 | 6.826 | 32 | 52 | 243 |
| Delta 0.10–0.35, multi-day | 4 | 10 | 933 | 0.177 | 0.169 | 19.065 | 15 | 26 | 145 |
| Delta 0.10–0.35, multi-day | 4 | 20 | 841 | 0.367 | 0.363 | 7.306 | 36 | 66 | 303 |
| One strike at least half, single | 3 | 10 | 953 | 0.116 | 0.128 | 22.434 | 7 | 24 | 91 |
| One strike at least half, single | 3 | 20 | 869 | 0.266 | 0.290 | 8.691 | 26 | 50 | 193 |
| One strike at least half, single | 4 | 10 | 945 | 0.153 | 0.164 | 22.625 | 8 | 28 | 124 |
| One strike at least half, single | 4 | 20 | 861 | 0.328 | 0.359 | 8.674 | 29 | 66 | 261 |
| One strike at least half, multi-day | 3 | 10 | 939 | 0.138 | 0.128 | 18.699 | 9 | 21 | 113 |
| One strike at least half, multi-day | 3 | 20 | 838 | 0.315 | 0.293 | 7.325 | 22 | 53 | 227 |
| One strike at least half, multi-day | 4 | 10 | 923 | 0.181 | 0.165 | 18.743 | 10 | 27 | 150 |
| One strike at least half, multi-day | 4 | 20 | 818 | 0.381 | 0.361 | 7.368 | 31 | 63 | 297 |

### Call P&L

Nearest monthly call with delta closest to 0.30, bought at the ask and sold at the bid.

| Screen | Slate | Horizon | Slates | Mean | Median | Hit rate | Worst decile |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| single | 3 | 10 | 586 | 0.298 | -0.254 | 0.389 | -0.873 |
| single | 3 | 20 | 381 | 1.242 | 0.460 | 0.598 | -0.842 |
| single | 4 | 10 | 655 | 0.319 | -0.154 | 0.424 | -0.863 |
| single | 4 | 20 | 468 | 1.158 | 0.529 | 0.611 | -0.850 |
| multi | 3 | 10 | 641 | 0.538 | -0.151 | 0.456 | -0.891 |
| multi | 3 | 20 | 431 | 1.709 | 0.900 | 0.671 | -0.833 |
| multi | 4 | 10 | 697 | 0.547 | -0.100 | 0.469 | -0.875 |
| multi | 4 | 20 | 496 | 1.681 | 0.957 | 0.688 | -0.800 |

### The four previously loud resolved cases

- lantheus_2022 LNTH not flagged. Sample day 2022-02-11, ratio 2.380, 10-session return 0.149.
- maxar_2022 MAXR flagged. Sample day 2022-12-14, ratio 12.485, 10-session return -0.007.
- pfizer_2021 PFE flagged. Sample day 2021-11-04, ratio 7.115, 10-session return 0.023.
- zogenix_2022 ZGNX not flagged. Sample day 2022-01-18, ratio 1.747, 10-session return -0.095.

### Examples with a 15% high within 20 sessions

- COMP 2025-12-12 multi-day, ratio 162.729, 10-session return 0.031, spike days 3 (3 consecutive), later ma.
- COMP 2025-12-11 multi-day, ratio 158.675, 10-session return 0.033, spike days 2 (2 consecutive), later ma.
- DAY 2025-08-15 single day, ratio 59.239, 10-session return -0.043, spike days 1 (1 consecutive), later ma.
- SGFY 2022-02-04 multi-day, ratio 55.450, 10-session return 0.046, spike days 2 (1 consecutive), later ma.
- WWE 2023-03-20 multi-day, ratio 53.436, 10-session return 0.037, spike days 1 (1 consecutive), later ma.
- WWE 2023-03-17 multi-day, ratio 53.401, 10-session return -0.003, spike days 1 (1 consecutive), later ma.
- SGFY 2022-02-03 multi-day, ratio 53.155, 10-session return 0.008, spike days 2 (1 consecutive), later ma.
- WNS 2025-06-18 single day, ratio 47.674, 10-session return 0.007, spike days 1 (1 consecutive), later ma.
- PUMP 2026-04-20 multi-day, ratio 43.808, 10-session return 0.012, spike days 1 (1 consecutive), later ma.
- SAVE 2022-01-20 multi-day, ratio 43.210, 10-session return 0.001, spike days 4 (3 consecutive), later ma.
- SAVE 2022-01-19 multi-day, ratio 41.897, 10-session return -0.033, spike days 3 (3 consecutive), later ma.
- PR 2023-07-27 single day, ratio 41.205, 10-session return -0.044, spike days 1 (1 consecutive), later ma.
- PR 2023-07-26 single day, ratio 38.799, 10-session return -0.023, spike days 1 (1 consecutive), later ma.
- WNS 2025-06-17 single day, ratio 35.104, 10-session return 0.033, spike days 1 (1 consecutive), later ma.
- DINO 2025-08-08 single day, ratio 30.259, 10-session return 0.009, spike days 1 (1 consecutive), later ma.
- DINO 2025-08-07 single day, ratio 29.462, 10-session return -0.007, spike days 1 (1 consecutive), later ma.
- MGI 2022-02-11 single day, ratio 28.436, 10-session return -0.028, spike days 1 (1 consecutive), later ma.
- RDNT 2025-04-22 multi-day, ratio 26.657, 10-session return -0.023, spike days 1 (1 consecutive), later ma.
- RDNT 2025-04-23 multi-day, ratio 25.871, 10-session return 0.023, spike days 1 (1 consecutive), later ma.
- SSYS 2023-07-03 multi-day, ratio 22.553, 10-session return 0.002, spike days 2 (1 consecutive), later ma.

A qualifying name is a review tag. It is not an identification of a trader.

## Multi-day call P&L stress test, 2026-11-13

This is the 20-session call book for the multi-day short-dated OTM top 3. The contract is the nearest monthly call whose delta that morning is closest to 0.30 and between 0.20 and 0.40. It is bought at that day's ask and sold at the bid 20 sessions later, or on the last session on or before expiry if that comes first. The strike is chosen only from the entry day's quotes.

Published slate median: 1.061. Recomputed slate median: 0.900. Recomputed slate mean: 1.709 across 431 dates. Individual filled trades: 571, median 0.820, mean 1.775.

After removing the 5 largest trades, the remaining trades have median 0.800 and mean 1.610. The slate median with those trades removed is 0.857. After removing the 10 largest, trade median 0.800, trade mean 1.496, slate median 0.800.

Overlapping later signals in a name already held: 172. After keeping only the first open trade, the trade median is 0.762 and the slate median is 0.800. Deduped slate mean: 1.510.

The same call bought on three random quiet stocks on the same dates has slate median 0.737 and mean 1.342 across 456 dates.

### By year

| Year | Trades | Mean | Median |
| --- | ---: | ---: | ---: |
| 2021 | 18 | 2.648 | 0.698 |
| 2022 | 88 | 1.103 | 0.185 |
| 2023 | 151 | 2.086 | 1.042 |
| 2024 | 121 | 2.068 | 0.600 |
| 2025 | 136 | 1.557 | 0.714 |
| 2026 | 57 | 1.611 | 1.000 |

### By what the next 20 sessions contained

| Type | Trades | Mean | Median |
| --- | ---: | ---: | ---: |
| M&A | 19 | 1.607 | 1.000 |
| Earnings | 74 | 2.228 | 0.991 |
| Other | 478 | 1.712 | 0.800 |

The book survives only if the deduped slate median stays above the random quiet-stock call and the trade median stays positive after the 10 largest trades are removed.


The edge survives this cut.
