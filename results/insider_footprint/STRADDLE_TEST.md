# Long straddles on the anomaly tail

Signals are the anomaly-test HBOS scores for the 1-day and 5-day windows, and the isolation-forest scores for the 1-day window, all against the 100-day baseline. Top 1% and top 0.5% use the training-score threshold. Top 4 is the four highest scores that day. The holdout from 2025-11-13 was not used to pick the rule.

The straddle buys the call and put at the strike closest to the spot. The expiry is the one closest to 25 days, preferring 20-30 days and otherwise staying inside 8-45. The strangle buys the 25-delta call above the spot and the 25-delta put below it, on that same expiry. Entries are the ask and exits are the bid. The other cost is the mid plus 5% at entry and the mid minus 5% at exit. A hold that reaches an earnings reaction is left out of the book.

Priced legs: 902100. Dropped for no valid bid/ask: 801352. No listed structure: 18608. No exit session: 0. Left out because the hold crosses earnings: 172310.

Return is the change in premium. The interval is a ticker bootstrap of the deduped ask/bid trades. Random is the same structure on a filtered name from the same month and the same IV-rank quintile.

| Signal | Rule | Structure | Hold | Sample | N | Quote mean | Quote median | Win | Deduped mean | Deduped CI | Random mean | Mid mean | IV vs 100-day | Realized minus IV | Terminal | Max DD |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| hbos 1d | p1 | straddle | d5 | walk | 40507 | -0.185 | -0.230 | 0.168 | -0.197 | -0.202 to -0.191 | -0.239 | -0.123 | 0.174 | -0.099 | 0.000 | 1.000 |
| hbos 1d | p1 | straddle | d5 | holdout | 3781 | -0.214 | -0.251 | 0.153 | -0.234 | -0.245 to -0.220 | -0.303 | -0.113 | 0.187 | -0.077 | 0.000 | 1.000 |
| hbos 1d | p1 | straddle | d10 | walk | 31456 | -0.247 | -0.331 | 0.170 | -0.248 | -0.255 to -0.240 | -0.289 | -0.193 | 0.174 | -0.080 | 0.000 | 1.000 |
| hbos 1d | p1 | straddle | d10 | holdout | 2980 | -0.267 | -0.356 | 0.163 | -0.295 | -0.313 to -0.274 | -0.339 | -0.181 | 0.188 | -0.037 | 0.001 | 0.999 |
| hbos 1d | p1 | straddle | expiry | walk | 20168 | -0.477 | -0.605 | 0.095 | -0.486 | -0.498 to -0.473 | -0.530 | -0.424 | 0.167 | -0.084 | 0.000 | 1.000 |
| hbos 1d | p1 | straddle | expiry | holdout | 2039 | -0.463 | -0.615 | 0.111 | -0.492 | -0.519 to -0.467 | -0.539 | -0.390 | 0.198 | -0.042 | 0.003 | 0.997 |
| hbos 1d | p05 | straddle | d5 | walk | 21634 | -0.181 | -0.230 | 0.172 | -0.191 | -0.198 to -0.183 | -0.238 | -0.126 | 0.183 | -0.086 | 0.000 | 1.000 |
| hbos 1d | p05 | straddle | d5 | holdout | 1783 | -0.202 | -0.248 | 0.154 | -0.224 | -0.243 to -0.205 | -0.286 | -0.113 | 0.222 | -0.071 | 0.000 | 1.000 |
| hbos 1d | p05 | straddle | d10 | walk | 17096 | -0.248 | -0.336 | 0.169 | -0.247 | -0.257 to -0.239 | -0.287 | -0.200 | 0.182 | -0.071 | 0.000 | 1.000 |
| hbos 1d | p05 | straddle | d10 | holdout | 1456 | -0.247 | -0.343 | 0.175 | -0.274 | -0.302 to -0.245 | -0.347 | -0.170 | 0.223 | -0.037 | 0.005 | 0.995 |
| hbos 1d | p05 | straddle | expiry | walk | 11071 | -0.469 | -0.601 | 0.099 | -0.474 | -0.489 to -0.459 | -0.527 | -0.424 | 0.176 | -0.079 | 0.000 | 1.000 |
| hbos 1d | p05 | straddle | expiry | holdout | 1005 | -0.440 | -0.603 | 0.127 | -0.470 | -0.513 to -0.421 | -0.541 | -0.374 | 0.223 | -0.036 | 0.007 | 0.993 |
| hbos 1d | top4 | straddle | d5 | walk | 7215 | -0.189 | -0.238 | 0.165 | -0.195 | -0.204 to -0.187 | -0.237 | -0.143 | 0.189 | -0.092 | 0.000 | 1.000 |
| hbos 1d | top4 | straddle | d5 | holdout | 834 | -0.195 | -0.247 | 0.173 | -0.211 | -0.234 to -0.184 | -0.315 | -0.107 | 0.239 | -0.067 | 0.000 | 1.000 |
| hbos 1d | top4 | straddle | d10 | walk | 5935 | -0.259 | -0.341 | 0.167 | -0.253 | -0.264 to -0.241 | -0.295 | -0.220 | 0.191 | -0.082 | 0.000 | 1.000 |
| hbos 1d | top4 | straddle | d10 | holdout | 699 | -0.218 | -0.343 | 0.173 | -0.262 | -0.298 to -0.219 | -0.349 | -0.143 | 0.245 | -0.019 | 0.001 | 0.999 |
| hbos 1d | top4 | straddle | expiry | walk | 3799 | -0.479 | -0.602 | 0.096 | -0.477 | -0.495 to -0.460 | -0.509 | -0.442 | 0.187 | -0.094 | 0.000 | 1.000 |
| hbos 1d | top4 | straddle | expiry | holdout | 457 | -0.415 | -0.594 | 0.140 | -0.435 | -0.499 to -0.365 | -0.520 | -0.355 | 0.238 | -0.018 | 0.009 | 0.991 |
| hbos 5d | p1 | straddle | d5 | walk | 38757 | -0.201 | -0.237 | 0.148 | -0.211 | -0.217 to -0.205 | -0.238 | -0.124 | 0.180 | -0.159 | 0.000 | 1.000 |
| hbos 5d | p1 | straddle | d5 | holdout | 3765 | -0.228 | -0.257 | 0.137 | -0.240 | -0.258 to -0.220 | -0.302 | -0.113 | 0.179 | -0.111 | 0.000 | 1.000 |
| hbos 5d | p1 | straddle | d10 | walk | 29847 | -0.268 | -0.336 | 0.149 | -0.269 | -0.278 to -0.260 | -0.289 | -0.199 | 0.187 | -0.125 | 0.000 | 1.000 |
| hbos 5d | p1 | straddle | d10 | holdout | 3021 | -0.283 | -0.357 | 0.153 | -0.299 | -0.323 to -0.269 | -0.340 | -0.180 | 0.185 | -0.052 | 0.002 | 0.998 |
| hbos 5d | p1 | straddle | expiry | walk | 17461 | -0.522 | -0.632 | 0.068 | -0.537 | -0.550 to -0.525 | -0.525 | -0.456 | 0.178 | -0.129 | 0.000 | 1.000 |
| hbos 5d | p1 | straddle | expiry | holdout | 1942 | -0.488 | -0.629 | 0.096 | -0.507 | -0.545 to -0.459 | -0.551 | -0.403 | 0.208 | -0.055 | 0.001 | 0.999 |
| hbos 5d | p05 | straddle | d5 | walk | 21056 | -0.196 | -0.238 | 0.152 | -0.207 | -0.214 to -0.197 | -0.242 | -0.125 | 0.204 | -0.157 | 0.000 | 1.000 |
| hbos 5d | p05 | straddle | d5 | holdout | 1903 | -0.227 | -0.256 | 0.126 | -0.236 | -0.257 to -0.209 | -0.298 | -0.121 | 0.230 | -0.115 | 0.000 | 1.000 |
| hbos 5d | p05 | straddle | d10 | walk | 16466 | -0.271 | -0.343 | 0.145 | -0.264 | -0.276 to -0.252 | -0.291 | -0.208 | 0.210 | -0.130 | 0.000 | 1.000 |
| hbos 5d | p05 | straddle | d10 | holdout | 1613 | -0.278 | -0.361 | 0.146 | -0.279 | -0.317 to -0.238 | -0.337 | -0.184 | 0.237 | -0.069 | 0.005 | 0.995 |
| hbos 5d | p05 | straddle | expiry | walk | 9636 | -0.524 | -0.635 | 0.069 | -0.535 | -0.550 to -0.519 | -0.538 | -0.463 | 0.204 | -0.133 | 0.000 | 1.000 |
| hbos 5d | p05 | straddle | expiry | holdout | 1016 | -0.477 | -0.631 | 0.104 | -0.494 | -0.545 to -0.437 | -0.534 | -0.400 | 0.254 | -0.057 | 0.010 | 0.990 |
| hbos 5d | top4 | straddle | d5 | walk | 6977 | -0.201 | -0.241 | 0.151 | -0.201 | -0.213 to -0.186 | -0.241 | -0.140 | 0.221 | -0.182 | 0.000 | 1.000 |
| hbos 5d | top4 | straddle | d5 | holdout | 834 | -0.212 | -0.252 | 0.143 | -0.239 | -0.276 to -0.204 | -0.316 | -0.103 | 0.292 | -0.109 | 0.000 | 1.000 |
| hbos 5d | top4 | straddle | d10 | walk | 5546 | -0.283 | -0.350 | 0.142 | -0.282 | -0.296 to -0.263 | -0.292 | -0.231 | 0.231 | -0.153 | 0.000 | 1.000 |
| hbos 5d | top4 | straddle | d10 | holdout | 680 | -0.260 | -0.366 | 0.166 | -0.276 | -0.338 to -0.199 | -0.320 | -0.166 | 0.294 | -0.060 | 0.004 | 0.996 |
| hbos 5d | top4 | straddle | expiry | walk | 3255 | -0.526 | -0.625 | 0.068 | -0.534 | -0.552 to -0.511 | -0.526 | -0.474 | 0.231 | -0.158 | 0.000 | 1.000 |
| hbos 5d | top4 | straddle | expiry | holdout | 414 | -0.443 | -0.644 | 0.118 | -0.445 | -0.544 to -0.327 | -0.516 | -0.369 | 0.304 | -0.054 | 0.052 | 0.948 |
| iforest 1d | p1 | straddle | d5 | walk | 33191 | -0.243 | -0.271 | 0.127 | -0.250 | -0.254 to -0.244 | -0.239 | -0.133 | 0.171 | -0.122 | 0.000 | 1.000 |
| iforest 1d | p1 | straddle | d5 | holdout | 3333 | -0.303 | -0.320 | 0.107 | -0.315 | -0.329 to -0.302 | -0.304 | -0.126 | 0.173 | -0.125 | 0.000 | 1.000 |
| iforest 1d | p1 | straddle | d10 | walk | 23693 | -0.313 | -0.365 | 0.124 | -0.311 | -0.319 to -0.304 | -0.289 | -0.213 | 0.176 | 0.003 | 0.000 | 1.000 |
| iforest 1d | p1 | straddle | d10 | holdout | 2331 | -0.357 | -0.405 | 0.113 | -0.374 | -0.389 to -0.355 | -0.346 | -0.212 | 0.173 | -0.083 | 0.000 | 1.000 |
| iforest 1d | p1 | straddle | expiry | walk | 12924 | -0.578 | -0.670 | 0.050 | -0.583 | -0.590 to -0.576 | -0.535 | -0.479 | 0.175 | -0.112 | 0.000 | 1.000 |
| iforest 1d | p1 | straddle | expiry | holdout | 1383 | -0.584 | -0.686 | 0.054 | -0.591 | -0.614 to -0.562 | -0.553 | -0.455 | 0.194 | -0.083 | 0.000 | 1.000 |
| iforest 1d | p05 | straddle | d5 | walk | 17202 | -0.247 | -0.280 | 0.128 | -0.254 | -0.260 to -0.248 | -0.238 | -0.145 | 0.196 | -0.118 | 0.000 | 1.000 |
| iforest 1d | p05 | straddle | d5 | holdout | 1501 | -0.289 | -0.322 | 0.112 | -0.306 | -0.325 to -0.284 | -0.303 | -0.124 | 0.222 | -0.118 | 0.000 | 1.000 |
| iforest 1d | p05 | straddle | d10 | walk | 12259 | -0.319 | -0.376 | 0.120 | -0.316 | -0.324 to -0.307 | -0.286 | -0.226 | 0.203 | 0.103 | 0.000 | 1.000 |
| iforest 1d | p05 | straddle | d10 | holdout | 1084 | -0.356 | -0.407 | 0.111 | -0.367 | -0.392 to -0.341 | -0.369 | -0.219 | 0.225 | -0.088 | 0.000 | 1.000 |
| iforest 1d | p05 | straddle | expiry | walk | 6778 | -0.577 | -0.671 | 0.050 | -0.584 | -0.594 to -0.573 | -0.525 | -0.483 | 0.208 | -0.125 | 0.000 | 1.000 |
| iforest 1d | p05 | straddle | expiry | holdout | 657 | -0.558 | -0.685 | 0.065 | -0.565 | -0.611 to -0.521 | -0.535 | -0.440 | 0.247 | -0.079 | 0.002 | 0.998 |
| iforest 1d | top4 | straddle | d5 | walk | 6564 | -0.248 | -0.288 | 0.130 | -0.258 | -0.268 to -0.248 | -0.244 | -0.156 | 0.219 | -0.124 | 0.000 | 1.000 |
| iforest 1d | top4 | straddle | d5 | holdout | 750 | -0.278 | -0.326 | 0.127 | -0.305 | -0.332 to -0.275 | -0.293 | -0.115 | 0.230 | -0.125 | 0.000 | 1.000 |
| iforest 1d | top4 | straddle | d10 | walk | 4718 | -0.333 | -0.393 | 0.120 | -0.331 | -0.342 to -0.320 | -0.281 | -0.249 | 0.226 | -0.126 | 0.000 | 1.000 |
| iforest 1d | top4 | straddle | d10 | holdout | 524 | -0.310 | -0.403 | 0.141 | -0.329 | -0.368 to -0.282 | -0.331 | -0.172 | 0.237 | -0.094 | 0.001 | 0.999 |
| iforest 1d | top4 | straddle | expiry | walk | 2587 | -0.587 | -0.675 | 0.046 | -0.590 | -0.605 to -0.576 | -0.533 | -0.504 | 0.236 | -0.148 | 0.000 | 1.000 |
| iforest 1d | top4 | straddle | expiry | holdout | 315 | -0.535 | -0.672 | 0.073 | -0.554 | -0.615 to -0.462 | -0.477 | -0.419 | 0.240 | -0.080 | 0.004 | 0.996 |
| hbos 1d | p1 | strangle | d10 | walk | 20529 | -0.399 | -0.580 | 0.140 | -0.405 | -0.422 to -0.391 | -0.424 | -0.309 | 0.159 | -0.068 | 0.000 | 1.000 |
| hbos 1d | p1 | strangle | d10 | holdout | 1844 | -0.401 | -0.588 | 0.145 | -0.425 | -0.463 to -0.374 | -0.458 | -0.270 | 0.191 | -0.015 | 0.000 | 1.000 |
| hbos 1d | p1 | strangle | expiry | walk | 5437 | -0.638 | -0.903 | 0.090 | -0.648 | -0.682 to -0.617 | -0.587 | -0.577 | 0.137 | -0.035 | 0.000 | 1.000 |
| hbos 1d | p1 | strangle | expiry | holdout | 563 | -0.546 | -0.902 | 0.124 | -0.590 | -0.684 to -0.467 | -0.716 | -0.464 | 0.227 | 0.010 | 0.001 | 0.999 |
| hbos 1d | top4 | strangle | d10 | walk | 4017 | -0.429 | -0.604 | 0.139 | -0.433 | -0.454 to -0.414 | -0.426 | -0.360 | 0.173 | -0.073 | 0.000 | 1.000 |
| hbos 1d | top4 | strangle | d10 | holdout | 448 | -0.402 | -0.591 | 0.147 | -0.447 | -0.508 to -0.380 | -0.417 | -0.287 | 0.237 | 0.014 | 0.000 | 1.000 |
| hbos 1d | top4 | strangle | expiry | walk | 1114 | -0.697 | -0.914 | 0.076 | -0.686 | -0.722 to -0.642 | -0.532 | -0.655 | 0.129 | -0.054 | 0.000 | 1.000 |
| hbos 1d | top4 | strangle | expiry | holdout | 149 | -0.393 | -0.880 | 0.174 | -0.466 | -0.657 to -0.157 | -0.489 | -0.313 | 0.311 | 0.047 | 0.237 | 0.763 |
| hbos 5d | p1 | strangle | d10 | walk | 18839 | -0.417 | -0.576 | 0.126 | -0.416 | -0.432 to -0.399 | -0.407 | -0.308 | 0.172 | -0.110 | 0.000 | 1.000 |
| hbos 5d | p1 | strangle | d10 | holdout | 1835 | -0.404 | -0.575 | 0.134 | -0.418 | -0.480 to -0.338 | -0.465 | -0.241 | 0.194 | -0.027 | 0.000 | 1.000 |
| hbos 5d | p1 | strangle | expiry | walk | 3744 | -0.651 | -0.897 | 0.080 | -0.671 | -0.713 to -0.624 | -0.617 | -0.572 | 0.141 | -0.068 | 0.000 | 1.000 |
| hbos 5d | p1 | strangle | expiry | holdout | 438 | -0.500 | -0.888 | 0.128 | -0.555 | -0.718 to -0.331 | -0.487 | -0.392 | 0.294 | -0.001 | 0.001 | 0.999 |
| hbos 5d | top4 | strangle | d10 | walk | 3499 | -0.449 | -0.600 | 0.123 | -0.461 | -0.486 to -0.433 | -0.427 | -0.361 | 0.216 | -0.134 | 0.000 | 1.000 |
| hbos 5d | top4 | strangle | d10 | holdout | 415 | -0.405 | -0.590 | 0.147 | -0.439 | -0.504 to -0.359 | -0.404 | -0.246 | 0.286 | -0.043 | 0.000 | 1.000 |
| hbos 5d | top4 | strangle | expiry | walk | 749 | -0.732 | -0.906 | 0.064 | -0.749 | -0.795 to -0.698 | -0.689 | -0.671 | 0.182 | -0.101 | 0.000 | 1.000 |
| hbos 5d | top4 | strangle | expiry | holdout | 99 | -0.183 | -0.844 | 0.222 | -0.268 | -0.713 to 0.323 | -0.427 | -0.085 | 0.472 | 0.071 | 0.262 | 0.738 |
| iforest 1d | p1 | strangle | d10 | walk | 12540 | -0.465 | -0.600 | 0.103 | -0.471 | -0.483 to -0.458 | -0.393 | -0.319 | 0.169 | -0.099 | 0.000 | 1.000 |
| iforest 1d | p1 | strangle | d10 | holdout | 1185 | -0.467 | -0.594 | 0.109 | -0.472 | -0.516 to -0.407 | -0.431 | -0.263 | 0.195 | -0.058 | 0.000 | 1.000 |
| iforest 1d | p1 | strangle | expiry | walk | 2028 | -0.705 | -0.893 | 0.059 | -0.718 | -0.747 to -0.681 | -0.631 | -0.587 | 0.159 | -0.097 | 0.000 | 1.000 |
| iforest 1d | p1 | strangle | expiry | holdout | 210 | -0.442 | -0.887 | 0.133 | -0.518 | -0.702 to -0.245 | -0.439 | -0.316 | 0.319 | 0.041 | 0.011 | 0.989 |
| iforest 1d | top4 | strangle | d10 | walk | 2367 | -0.481 | -0.629 | 0.109 | -0.483 | -0.510 to -0.450 | -0.377 | -0.357 | 0.212 | -0.102 | 0.000 | 1.000 |
| iforest 1d | top4 | strangle | d10 | holdout | 282 | -0.392 | -0.609 | 0.121 | -0.401 | -0.524 to -0.168 | -0.436 | -0.182 | 0.226 | -0.065 | 0.002 | 0.999 |
| iforest 1d | top4 | strangle | expiry | walk | 395 | -0.768 | -0.907 | 0.046 | -0.754 | -0.793 to -0.715 | -0.736 | -0.678 | 0.176 | -0.162 | 0.000 | 1.000 |
| iforest 1d | top4 | strangle | expiry | holdout | 64 | -0.072 | -0.867 | 0.172 | -0.192 | -0.687 to 0.644 | 0.610 | 0.094 | 0.329 | 0.146 | 0.171 | 0.839 |

## Verdict

hbos 1-day p05 held d5 is the walk-forward straddle with the highest deduped ask/bid mean. Its edge versus matched random straddles is 0.047 in the walk-forward and 0.062 in the holdout. It is not tradable after the ask/bid cost. The holdout book does not clear both a positive mean and the matched random book, or the typical trade still gives back a large share of the premium.
