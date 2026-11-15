# +30% events and a timed stock hold

Exchange-traded products were removed before this refit (550 of 5,299 symbols). Deduped stock-hold means are below. The walk-forward choice changed.

| Book | Before walk mean | After walk mean | Before holdout mean | After holdout mean | Before holdout random | After holdout random |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prior choice: iforest 1-day p05, 10 sessions | 0.041 | -0.006 | 0.002 | -0.001 | -0.003 | 0.010 |
| New choice: boost 1-day top 4, 20 sessions | 0.006 | 0.008 | 0.029 | 0.059 | 0.076 | 0.020 |

The prior choice no longer has a positive holdout mean, and that mean is below its matched random hold. The new walk-forward choice has a holdout deduped mean of 0.059 against a matched random mean of 0.020 (n 333). Its walk-forward mean is 0.008 against 0.006. The call priced on that new rule, ask in and bid out, has n 2,883, mean 0.741, and median -0.707.

A +30% event is a forward high, or a close, at least 30% above the signal close within 5, 10, 20, or 40 sessions. An earnings reaction inside that window blanks the event. The trade is separate: buy the next open and sell the close after 5, 10, 20, or 40 of the name's sessions. There is no stop and no target. The cost is 10 bps round trip. The hold with the highest deduped walk-forward mean is the one whose holdout is read.

Market cap is not usable: the cap table has 28 rows and no current names.

## Base rate in the filtered universe

| Kind | Horizon | Sample | N | Rate |
| --- | ---: | --- | ---: | ---: |
| high | 5 | walk | 2951923 | 0.007 |
| high | 5 | holdout | 376835 | 0.009 |
| close | 5 | walk | 2951923 | 0.003 |
| close | 5 | holdout | 376835 | 0.004 |
| high | 10 | walk | 2778128 | 0.019 |
| high | 10 | holdout | 357565 | 0.025 |
| close | 10 | walk | 2778128 | 0.008 |
| close | 10 | holdout | 357565 | 0.012 |
| high | 20 | walk | 2434412 | 0.047 |
| high | 20 | holdout | 320666 | 0.069 |
| close | 20 | walk | 2434412 | 0.022 |
| close | 20 | holdout | 320666 | 0.032 |
| high | 40 | walk | 1773165 | 0.108 |
| high | 40 | holdout | 250009 | 0.157 |
| close | 40 | walk | 1773165 | 0.051 |
| close | 40 | holdout | 250009 | 0.075 |

## Lift for a 20-session high of at least 30%

| Method | Window | Tail | Sample | Lift | Conditional | Base | N | Interval |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| hbos | 1 | 1% | walk | 2.745 | 0.129 | 0.047 | 31601 | 2.57 to 2.91 |
| hbos | 1 | 1% | holdout | 2.267 | 0.157 | 0.069 | 3082 | 1.94 to 2.62 |
| hbos | 1 | 0.5% | walk | 2.910 | 0.137 | 0.047 | 17084 | n/a |
| hbos | 1 | 0.5% | holdout | 2.387 | 0.165 | 0.069 | 1321 | n/a |
| hbos | 1 | 0.1% | walk | 2.694 | 0.127 | 0.047 | 3300 | 2.30 to 3.12 |
| hbos | 1 | 0.1% | holdout | 2.663 | 0.184 | 0.069 | 239 | 1.72 to 3.75 |
| iforest | 1 | 1% | walk | 2.450 | 0.115 | 0.047 | 27898 | 2.30 to 2.57 |
| iforest | 1 | 1% | holdout | 1.715 | 0.119 | 0.069 | 3256 | 1.47 to 1.96 |
| iforest | 1 | 0.5% | walk | 2.824 | 0.133 | 0.047 | 14423 | n/a |
| iforest | 1 | 0.5% | holdout | 2.049 | 0.142 | 0.069 | 1496 | n/a |
| iforest | 1 | 0.1% | walk | 3.676 | 0.173 | 0.047 | 3251 | 3.26 to 4.10 |
| iforest | 1 | 0.1% | holdout | 1.928 | 0.133 | 0.069 | 240 | 1.34 to 2.61 |
| hbos | 3 | 1% | walk | 2.761 | 0.130 | 0.047 | 32384 | 2.56 to 2.95 |
| hbos | 3 | 1% | holdout | 2.212 | 0.153 | 0.069 | 2826 | 1.82 to 2.57 |
| hbos | 3 | 0.5% | walk | 2.990 | 0.141 | 0.047 | 17646 | n/a |
| hbos | 3 | 0.5% | holdout | 2.497 | 0.173 | 0.069 | 1399 | n/a |
| hbos | 3 | 0.1% | walk | 2.862 | 0.135 | 0.047 | 4524 | 2.46 to 3.25 |
| hbos | 3 | 0.1% | holdout | 3.025 | 0.210 | 0.069 | 210 | 1.78 to 4.37 |
| iforest | 3 | 1% | walk | 2.490 | 0.117 | 0.047 | 27324 | 2.32 to 2.64 |
| iforest | 3 | 1% | holdout | 1.754 | 0.122 | 0.069 | 3028 | 1.45 to 2.08 |
| iforest | 3 | 0.5% | walk | 2.948 | 0.139 | 0.047 | 14738 | n/a |
| iforest | 3 | 0.5% | holdout | 1.961 | 0.136 | 0.069 | 1487 | n/a |
| iforest | 3 | 0.1% | walk | 4.014 | 0.189 | 0.047 | 3173 | 3.47 to 4.60 |
| iforest | 3 | 0.1% | holdout | 2.078 | 0.144 | 0.069 | 264 | 1.29 to 2.78 |
| hbos | 5 | 1% | walk | 2.856 | 0.135 | 0.047 | 30575 | 2.65 to 3.06 |
| hbos | 5 | 1% | holdout | 2.358 | 0.164 | 0.069 | 2859 | 1.90 to 2.75 |
| hbos | 5 | 0.5% | walk | 3.164 | 0.149 | 0.047 | 15850 | n/a |
| hbos | 5 | 0.5% | holdout | 2.493 | 0.173 | 0.069 | 1294 | n/a |
| hbos | 5 | 0.1% | walk | 3.590 | 0.169 | 0.047 | 3945 | 3.11 to 4.06 |
| hbos | 5 | 0.1% | holdout | 3.370 | 0.234 | 0.069 | 265 | 2.02 to 4.75 |
| iforest | 5 | 1% | walk | 2.646 | 0.125 | 0.047 | 27256 | 2.45 to 2.84 |
| iforest | 5 | 1% | holdout | 1.804 | 0.125 | 0.069 | 2978 | 1.42 to 2.24 |
| iforest | 5 | 0.5% | walk | 3.122 | 0.147 | 0.047 | 14751 | n/a |
| iforest | 5 | 0.5% | holdout | 2.128 | 0.148 | 0.069 | 1435 | n/a |
| iforest | 5 | 0.1% | walk | 4.392 | 0.207 | 0.047 | 3389 | 3.87 to 5.03 |
| iforest | 5 | 0.1% | holdout | 1.757 | 0.122 | 0.069 | 246 | 0.87 to 2.83 |

## Features higher before a 20-session +30% high

- persist_mean: event 0.918, other names 0.401
- persist_max: event 0.918, other names 0.401
- vol_put_otm_d45: event 1.494, other names 1.130
- vol_call_atm_d45: event 1.462, other names 1.117
- vol_call_dotm_d07: event 1.500, other names 1.166
- dnot_put: event 1.465, other names 1.139
- vol_put_dotm_d45: event 1.496, other names 1.177
- vol_put_otm_d21: event 1.476, other names 1.160

## Sector, HBOS top 1%, 20-session high

- Utilities: top-1% rate 0.084 versus base 0.011, lift 7.550, n 261
- Financial: top-1% rate 0.083 versus base 0.020, lift 4.229, n 2230
- Conglomerates: top-1% rate 0.180 versus base 0.048, lift 3.708, n 89
- Industrial Goods: top-1% rate 0.077 versus base 0.026, lift 2.985, n 1239
- Services: top-1% rate 0.108 versus base 0.037, lift 2.892, n 5494
- Technology: top-1% rate 0.112 versus base 0.041, lift 2.721, n 6370
- Consumer Goods: top-1% rate 0.064 versus base 0.024, lift 2.685, n 2106
- Basic Materials: top-1% rate 0.092 versus base 0.036, lift 2.567, n 1865

## Classifier precision on the 20-session +30% high

| Model | Rule | Sample | Precision | Base | Lift | N |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| logistic | top4 | walk | 0.115 | 0.047 | 2.453 | 7888 |
| logistic | 0.5% | walk | 0.108 | 0.047 | 2.302 | 12871 |
| logistic | 0.1% | walk | 0.141 | 0.047 | 2.998 | 2575 |
| logistic | top4 | holdout | 0.130 | 0.069 | 1.874 | 872 |
| logistic | 0.5% | holdout | 0.126 | 0.069 | 1.826 | 1647 |
| logistic | 0.1% | holdout | 0.148 | 0.069 | 2.147 | 330 |
| boost | top4 | walk | 0.309 | 0.047 | 6.576 | 7888 |
| boost | 0.5% | walk | 0.311 | 0.047 | 6.616 | 12871 |
| boost | 0.1% | walk | 0.351 | 0.047 | 7.458 | 2575 |
| boost | top4 | holdout | 0.325 | 0.069 | 4.694 | 872 |
| boost | 0.5% | holdout | 0.349 | 0.069 | 5.049 | 1647 |
| boost | 0.1% | holdout | 0.339 | 0.069 | 4.908 | 330 |

## Timed stock hold, deduped

| Signal | Hold | Sample | N | Mean | Median | P10 | P90 | At least +30% | At or below -20% | Win | Random mean |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| boost 1d p05 | 10 | walk | 2745 | 0.006 | -0.014 | -0.242 | 0.249 | 0.073 | 0.145 | 0.466 | -0.005 |
| boost 1d p05 | 10 | holdout | 510 | 3.859 | -0.015 | -0.251 | 0.255 | 0.076 | 0.157 | 0.471 | -0.000 |
| boost 1d p05 | 20 | walk | 2719 | 0.005 | -0.043 | -0.317 | 0.322 | 0.112 | 0.236 | 0.422 | -0.019 |
| boost 1d p05 | 20 | holdout | 500 | 0.021 | -0.036 | -0.348 | 0.317 | 0.118 | 0.254 | 0.438 | -0.001 |
| boost 1d p05 | 40 | walk | 2135 | -0.045 | -0.103 | -0.463 | 0.415 | 0.141 | 0.377 | 0.374 | 0.022 |
| boost 1d p05 | 40 | holdout | 429 | 0.036 | -0.055 | -0.448 | 0.436 | 0.177 | 0.338 | 0.436 | -0.006 |
| boost 1d top4 | 10 | walk | 2823 | -0.009 | -0.023 | -0.244 | 0.225 | 0.061 | 0.150 | 0.440 | 0.005 |
| boost 1d top4 | 10 | holdout | 336 | 0.060 | -0.023 | -0.297 | 0.282 | 0.095 | 0.196 | 0.440 | 1.727 |
| boost 1d top4 | 20 | walk | 2784 | 0.008 | -0.036 | -0.321 | 0.325 | 0.112 | 0.216 | 0.432 | 0.006 |
| boost 1d top4 | 20 | holdout | 333 | 0.059 | -0.022 | -0.369 | 0.359 | 0.132 | 0.255 | 0.456 | 0.020 |
| boost 1d top4 | 40 | walk | 2179 | -0.013 | -0.071 | -0.451 | 0.423 | 0.160 | 0.329 | 0.402 | 0.011 |
| boost 1d top4 | 40 | holdout | 279 | -0.005 | -0.091 | -0.501 | 0.524 | 0.183 | 0.398 | 0.394 | 0.031 |
| hbos 1d p05 | 10 | walk | 10408 | -0.004 | -0.004 | -0.147 | 0.132 | 0.023 | 0.059 | 0.479 | 0.009 |
| hbos 1d p05 | 10 | holdout | 857 | 0.005 | -0.006 | -0.152 | 0.164 | 0.037 | 0.055 | 0.476 | 0.003 |
| hbos 1d p05 | 20 | walk | 9440 | -0.001 | -0.005 | -0.193 | 0.172 | 0.044 | 0.095 | 0.482 | 0.013 |
| hbos 1d p05 | 20 | holdout | 804 | 0.004 | -0.009 | -0.201 | 0.214 | 0.058 | 0.101 | 0.466 | 0.001 |
| hbos 1d p05 | 40 | walk | 7805 | 0.005 | -0.005 | -0.259 | 0.248 | 0.076 | 0.147 | 0.485 | 0.019 |
| hbos 1d p05 | 40 | holdout | 675 | 0.022 | -0.007 | -0.276 | 0.343 | 0.127 | 0.175 | 0.479 | 0.017 |
| hbos 1d p1 | 10 | walk | 17414 | -0.003 | -0.003 | -0.143 | 0.128 | 0.021 | 0.052 | 0.481 | 0.004 |
| hbos 1d p1 | 10 | holdout | 1806 | 0.001 | -0.003 | -0.156 | 0.148 | 0.026 | 0.063 | 0.486 | 0.480 |
| hbos 1d p1 | 20 | walk | 15756 | 0.000 | -0.004 | -0.186 | 0.171 | 0.039 | 0.088 | 0.487 | 0.010 |
| hbos 1d p1 | 20 | holdout | 1685 | 0.006 | -0.008 | -0.189 | 0.213 | 0.055 | 0.091 | 0.471 | 0.009 |
| hbos 1d p1 | 40 | walk | 12866 | 0.005 | -0.005 | -0.251 | 0.243 | 0.074 | 0.141 | 0.487 | 0.019 |
| hbos 1d p1 | 40 | holdout | 1433 | 0.016 | -0.008 | -0.266 | 0.310 | 0.106 | 0.165 | 0.484 | 0.015 |
| hbos 1d top4 | 10 | walk | 4539 | -0.004 | -0.003 | -0.147 | 0.128 | 0.022 | 0.061 | 0.484 | 0.003 |
| hbos 1d top4 | 10 | holdout | 570 | 0.014 | 0.005 | -0.154 | 0.171 | 0.040 | 0.063 | 0.521 | -0.005 |
| hbos 1d top4 | 20 | walk | 4093 | -0.001 | -0.003 | -0.194 | 0.167 | 0.041 | 0.096 | 0.490 | 0.003 |
| hbos 1d top4 | 20 | holdout | 513 | 0.024 | 0.002 | -0.195 | 0.263 | 0.076 | 0.097 | 0.515 | -0.001 |
| hbos 1d top4 | 40 | walk | 3372 | 0.002 | -0.004 | -0.255 | 0.240 | 0.071 | 0.149 | 0.486 | 0.013 |
| hbos 1d top4 | 40 | holdout | 416 | 0.043 | 0.003 | -0.271 | 0.384 | 0.132 | 0.166 | 0.507 | 0.006 |
| hbos 5d p05 | 10 | walk | 4707 | -0.008 | -0.007 | -0.172 | 0.142 | 0.030 | 0.078 | 0.460 | 0.005 |
| hbos 5d p05 | 10 | holdout | 354 | 0.007 | -0.001 | -0.169 | 0.165 | 0.034 | 0.065 | 0.492 | -0.000 |
| hbos 5d p05 | 20 | walk | 4263 | -0.000 | -0.008 | -0.230 | 0.197 | 0.055 | 0.118 | 0.474 | 0.010 |
| hbos 5d p05 | 20 | holdout | 343 | 0.020 | -0.005 | -0.197 | 0.283 | 0.087 | 0.099 | 0.475 | 0.003 |
| hbos 5d p05 | 40 | walk | 3452 | -0.005 | -0.010 | -0.308 | 0.259 | 0.081 | 0.183 | 0.466 | 0.015 |
| hbos 5d p05 | 40 | holdout | 296 | 0.032 | 0.009 | -0.288 | 0.345 | 0.128 | 0.179 | 0.510 | 0.024 |
| hbos 5d p1 | 10 | walk | 8517 | -0.006 | -0.005 | -0.158 | 0.133 | 0.027 | 0.067 | 0.475 | 0.003 |
| hbos 5d p1 | 10 | holdout | 742 | 0.002 | -0.007 | -0.163 | 0.149 | 0.035 | 0.067 | 0.476 | 0.002 |
| hbos 5d p1 | 20 | walk | 7671 | 0.002 | -0.003 | -0.201 | 0.188 | 0.046 | 0.101 | 0.488 | 0.009 |
| hbos 5d p1 | 20 | holdout | 711 | 0.010 | -0.005 | -0.210 | 0.239 | 0.069 | 0.113 | 0.478 | 0.003 |
| hbos 5d p1 | 40 | walk | 6207 | 0.006 | -0.007 | -0.274 | 0.260 | 0.084 | 0.161 | 0.480 | 0.023 |
| hbos 5d p1 | 40 | holdout | 604 | 0.015 | -0.006 | -0.304 | 0.331 | 0.124 | 0.199 | 0.487 | 0.006 |
| hbos 5d top4 | 10 | walk | 2248 | -0.008 | -0.008 | -0.161 | 0.131 | 0.032 | 0.069 | 0.455 | 0.001 |
| hbos 5d top4 | 10 | holdout | 256 | 0.014 | 0.003 | -0.169 | 0.193 | 0.039 | 0.070 | 0.520 | 0.005 |
| hbos 5d top4 | 20 | walk | 2033 | -0.004 | -0.004 | -0.214 | 0.189 | 0.056 | 0.110 | 0.474 | 0.002 |
| hbos 5d top4 | 20 | holdout | 237 | 0.038 | 0.005 | -0.194 | 0.303 | 0.105 | 0.101 | 0.527 | 0.011 |
| hbos 5d top4 | 40 | walk | 1660 | -0.002 | -0.009 | -0.296 | 0.257 | 0.081 | 0.169 | 0.471 | 0.008 |
| hbos 5d top4 | 40 | holdout | 197 | 0.053 | 0.022 | -0.275 | 0.364 | 0.147 | 0.173 | 0.543 | 0.015 |
| iforest 1d p05 | 10 | walk | 10376 | -0.006 | -0.005 | -0.153 | 0.128 | 0.024 | 0.062 | 0.471 | 0.003 |
| iforest 1d p05 | 10 | holdout | 1074 | -0.001 | -0.005 | -0.158 | 0.147 | 0.025 | 0.060 | 0.479 | 0.010 |
| iforest 1d p05 | 20 | walk | 9353 | -0.001 | -0.004 | -0.198 | 0.173 | 0.041 | 0.099 | 0.483 | 0.010 |
| iforest 1d p05 | 20 | holdout | 1010 | 0.003 | -0.006 | -0.205 | 0.204 | 0.050 | 0.104 | 0.477 | 0.020 |
| iforest 1d p05 | 40 | walk | 7576 | 0.003 | -0.006 | -0.271 | 0.247 | 0.077 | 0.158 | 0.480 | 0.011 |
| iforest 1d p05 | 40 | holdout | 855 | 0.015 | -0.005 | -0.283 | 0.303 | 0.101 | 0.167 | 0.488 | 0.022 |
| iforest 1d p1 | 10 | walk | 18712 | -0.005 | -0.003 | -0.141 | 0.121 | 0.019 | 0.055 | 0.482 | 0.004 |
| iforest 1d p1 | 10 | holdout | 2197 | 0.787 | -0.004 | -0.145 | 0.137 | 0.023 | 0.055 | 0.482 | 0.004 |
| iforest 1d p1 | 20 | walk | 16872 | -0.000 | -0.003 | -0.182 | 0.168 | 0.037 | 0.087 | 0.490 | 0.007 |
| iforest 1d p1 | 20 | holdout | 2058 | 0.001 | -0.003 | -0.185 | 0.188 | 0.042 | 0.084 | 0.485 | 0.009 |
| iforest 1d p1 | 40 | walk | 13560 | 0.003 | -0.003 | -0.248 | 0.229 | 0.067 | 0.140 | 0.490 | 0.019 |
| iforest 1d p1 | 40 | holdout | 1732 | 0.013 | 0.000 | -0.256 | 0.286 | 0.093 | 0.149 | 0.500 | 0.021 |
| iforest 1d top4 | 10 | walk | 5061 | -0.008 | -0.004 | -0.163 | 0.129 | 0.027 | 0.071 | 0.472 | 0.002 |
| iforest 1d top4 | 10 | holdout | 628 | 0.009 | 0.003 | -0.154 | 0.163 | 0.025 | 0.065 | 0.518 | 0.008 |
| iforest 1d top4 | 20 | walk | 4575 | -0.004 | -0.007 | -0.207 | 0.173 | 0.045 | 0.107 | 0.475 | 0.001 |
| iforest 1d top4 | 20 | holdout | 573 | 0.017 | 0.004 | -0.203 | 0.210 | 0.063 | 0.105 | 0.518 | 0.018 |
| iforest 1d top4 | 40 | walk | 3634 | -0.004 | -0.006 | -0.289 | 0.249 | 0.079 | 0.169 | 0.480 | 0.005 |
| iforest 1d top4 | 40 | holdout | 463 | 0.013 | -0.010 | -0.289 | 0.297 | 0.099 | 0.184 | 0.475 | 0.017 |
| iforest 5d p05 | 10 | walk | 4253 | -0.006 | -0.005 | -0.173 | 0.147 | 0.035 | 0.080 | 0.467 | 0.002 |
| iforest 5d p05 | 10 | holdout | 397 | 0.000 | -0.005 | -0.162 | 0.139 | 0.033 | 0.063 | 0.479 | -0.002 |
| iforest 5d p05 | 20 | walk | 3821 | 0.001 | -0.003 | -0.236 | 0.198 | 0.057 | 0.126 | 0.488 | 0.005 |
| iforest 5d p05 | 20 | holdout | 377 | 0.014 | -0.012 | -0.217 | 0.256 | 0.080 | 0.114 | 0.456 | 0.006 |
| iforest 5d p05 | 40 | walk | 2999 | -0.002 | -0.010 | -0.315 | 0.276 | 0.091 | 0.189 | 0.472 | 0.011 |
| iforest 5d p05 | 40 | holdout | 306 | 0.025 | 0.001 | -0.288 | 0.354 | 0.134 | 0.167 | 0.500 | 0.010 |
| iforest 5d p1 | 10 | walk | 7658 | -0.006 | -0.005 | -0.156 | 0.128 | 0.025 | 0.063 | 0.474 | 0.003 |
| iforest 5d p1 | 10 | holdout | 809 | 0.001 | -0.003 | -0.148 | 0.136 | 0.028 | 0.049 | 0.482 | 0.001 |
| iforest 5d p1 | 20 | walk | 6849 | 0.001 | -0.001 | -0.203 | 0.175 | 0.046 | 0.102 | 0.497 | 0.015 |
| iforest 5d p1 | 20 | holdout | 760 | 0.008 | -0.006 | -0.202 | 0.204 | 0.058 | 0.104 | 0.472 | 0.001 |
| iforest 5d p1 | 40 | walk | 5386 | -0.002 | -0.005 | -0.282 | 0.244 | 0.075 | 0.163 | 0.487 | 0.015 |
| iforest 5d p1 | 40 | holdout | 621 | 0.062 | -0.009 | -0.271 | 0.292 | 0.097 | 0.156 | 0.477 | 0.004 |
| iforest 5d top4 | 10 | walk | 2145 | -0.006 | -0.003 | -0.184 | 0.148 | 0.033 | 0.090 | 0.482 | 0.000 |
| iforest 5d top4 | 10 | holdout | 262 | 0.004 | -0.002 | -0.163 | 0.161 | 0.050 | 0.073 | 0.492 | 0.001 |
| iforest 5d top4 | 20 | walk | 1942 | 0.001 | -0.004 | -0.239 | 0.208 | 0.056 | 0.127 | 0.484 | 0.003 |
| iforest 5d top4 | 20 | holdout | 244 | 0.031 | -0.001 | -0.203 | 0.303 | 0.102 | 0.107 | 0.492 | 0.002 |
| iforest 5d top4 | 40 | walk | 1504 | -0.007 | -0.008 | -0.361 | 0.285 | 0.096 | 0.205 | 0.476 | 0.010 |
| iforest 5d top4 | 40 | holdout | 187 | 0.046 | 0.027 | -0.277 | 0.387 | 0.150 | 0.160 | 0.540 | 0.004 |

## Chosen hold and the call

Walk-forward choice: boost 1-day top4, exit after 20 sessions. Holdout deduped mean 0.059.
OTM call on that rule, ask in and bid out, same time exit: n 2883, dropped 5746, mean 0.741, median -0.707, at least +30% 0.238, at or below -20% 0.685.

## Verdict

boost 1-day top4, 20 sessions is the walk-forward hold with the highest deduped mean. The holdout mean stays positive and beats the matched random hold by 0.040.
