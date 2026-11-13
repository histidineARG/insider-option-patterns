# Footprint logistic

One ridge logistic. Features are taken from the single pre-event session with the largest call-volume ratio: log volume ratio, share of call volume in the delta 0.10–0.35 band, that band's top strike share, call share of call-plus-put volume, and log band volume per contract of open interest. Ridge penalty is 1 on the standardized features. Fit uses 2013–2014. The 2015 numbers were not used to change anything. 2016 is the holdout.

The label is a class-2 window versus that name's own placebo and earnings windows. A higher score means the session looks more like the pre-jump windows in the training years. It is not a probability that a person traded on inside information.

| Fold | Windows | AUC | M&A scores above its placebo | M&A scores above its earnings |
| --- | ---: | ---: | ---: | ---: |
| 2013–2014 train | 36 cases, 59 controls | 0.602 | 15/28 (54%) | 21/31 (68%) |
| 2015 validation | 27 cases, 52 controls | 0.542 | 19/27 (70%) | 14/25 (56%) |
| 2016 holdout | 22 cases, 44 controls | 0.529 | 11/22 (50%) | 12/22 (55%) |

A model that uses only the volume ratio has 2016 AUC 0.433.

Standardized coefficients, intercept unpenalized:

- intercept: -0.507
- log_volume_ratio: 0.181
- band_share: -0.066
- top_share: 0.133
- call_fraction: 0.242
- log_band_turnover: -0.003

Thresholds and the penalty were not revised after these numbers. No trading result is claimed.
