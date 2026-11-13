# Validation holdout

Frozen 2026-11-13. The holdout is 2024-11-13 through 2026-11-12. Nothing in that window was used to choose the admission rule, the early-run rule, or the earnings comparison. The screen was not rerun to chase a result.

## Holdout score

The holdout cannot be scored. Prices and option chains exist through 2026-11-12. Deal headlines do not: `takeover` ends 2021-08-21, `news` ends 2022-07-25, and `research_ma_events` ends 2024-05-28. The price-confirmed pool has zero events on or after 2024-11-13. No headlines were added to fill the hole.

## Development screen, through 2024-11-12

These counts are the screen already stored in `candidate_screen.json`. Every scored event falls before the holdout.

| Result | Count |
| --- | ---: |
| Ten-session path at least 15% | 1,838 |
| Admitted after the option-history and bad-print checks | 1,726 |
| Path start before t = −10 | 146 (8%) |
| Statistical candidates versus that stock’s own earnings | 854 |
| Baseline-consistent | 731 |
| No earnings benchmark | 141 |

Across 1,820 expiry series that have an earnings benchmark, the median percentile of the deal window versus that stock’s own earnings windows is 0.75. Half of the series sit at or above the 75th percentile. If deal windows matched earnings windows, that share would be about a quarter. The early-run share, 8%, is under the 30% line at which the longer window would be marking ordinary drift.

A statistical candidate is a review tag. It is not an identification of a trader.
