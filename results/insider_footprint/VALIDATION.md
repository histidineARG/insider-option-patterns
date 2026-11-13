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

## Daily top picks, 2026-11-13

On each session the frozen logistic scores every optionable name from the ten sessions ending at that close. Names are ordered by the linear score, because the probability saturates near 1 when that ten-session return is very large. It names the top 3 and the top 4. A hit is a later close at least 15% above that close, either at the horizon or at the highest close inside it. A one-day move of +100% or −50%, or a split, is not counted as a jump. A session counts only when every name in the slate has a close at that horizon. The coefficients are the 2013–2019 fit. This test does not choose a new cutoff.

The stock return in the score is the change from ten sessions earlier through the scoring close. It does not use the path into a later headline. That return has the largest frozen weight, so the top of the list is the names that already rose the most. On this run the median ten-session return of the highest-ranked name was about 25 times, and the 10th percentile was still about 9 times.

Names scanned: 8616. Scoring sessions: 1221. Standardization check gap: 0.0.

| Slate | Horizon | Jump | Dates | Date hit rate | Random slate | Hit rate per pick | False picks per hit | M&A | Earnings | Other |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| top 3 | 5 | terminal | 956 | 0.306 | 0.080 | 0.120 | 7.337 | 0 | 11 | 333 |
| top 3 | 5 | peak | 956 | 0.474 | 0.108 | 0.199 | 4.032 | 2 | 20 | 548 |
| top 3 | 10 | terminal | 777 | 0.413 | 0.148 | 0.177 | 4.658 | 1 | 32 | 379 |
| top 3 | 10 | peak | 777 | 0.644 | 0.221 | 0.311 | 2.211 | 7 | 48 | 671 |
| top 3 | 20 | terminal | 505 | 0.481 | 0.246 | 0.202 | 3.951 | 8 | 34 | 264 |
| top 3 | 20 | peak | 505 | 0.770 | 0.386 | 0.411 | 1.432 | 15 | 72 | 536 |
| top 4 | 5 | terminal | 934 | 0.401 | 0.104 | 0.127 | 6.899 | 1 | 13 | 459 |
| top 4 | 5 | peak | 934 | 0.584 | 0.141 | 0.204 | 3.896 | 3 | 22 | 738 |
| top 4 | 10 | terminal | 746 | 0.517 | 0.191 | 0.181 | 4.536 | 3 | 41 | 495 |
| top 4 | 10 | peak | 746 | 0.752 | 0.282 | 0.316 | 2.168 | 11 | 62 | 869 |
| top 4 | 20 | terminal | 472 | 0.568 | 0.311 | 0.209 | 3.792 | 11 | 38 | 345 |
| top 4 | 20 | peak | 472 | 0.852 | 0.473 | 0.412 | 1.430 | 18 | 84 | 675 |

Date hit rate is the share of sessions where at least one name in the slate jumps. Random slate is the average probability that a random draw of the same size, from that session’s optionable names, contains a jump. False picks per hit is the number of slate names that do not jump divided by the number that do.

M&A uses the EDGAR announcement table and the earlier headline pool when the reaction session falls inside the forward window. Earnings uses 8-K Item 2.02 reaction sessions in that window. A jump with neither is other. A rank is a review tag, not an identification of a trader.

No new high-precision rule is frozen from this table. A cutoff chosen after these rates would be a proposal for a later test.
