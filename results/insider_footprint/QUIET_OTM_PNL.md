## Multi-day call P&L stress test, 2026-11-13

Exchange-traded products were removed before this rerun (2,431 of 8,616 symbols). This is the 20-session call on the multi-day short-dated OTM top 3.

| Metric | Before | After |
| --- | ---: | ---: |
| Filled trades | 555 | 571 |
| Trade mean | 1.835 | 1.775 |
| Trade median | 0.955 | 0.820 |
| Slate mean | 1.815 | 1.709 |
| Slate median | 1.061 | 0.900 |
| Deduped trade median | 0.827 | 0.762 |
| Deduped slate median | 0.875 | 0.800 |
| Trade median after dropping the 10 largest | 0.900 | 0.800 |
| Random quiet-stock slate mean | 1.444 | 1.342 |
| Random quiet-stock slate median | 0.894 | 0.737 |

The deduped slate median stays above the random quiet-stock slate median (0.800 versus 0.737), and the trade median stays positive after the 10 largest trades are removed. The edge survives this cut.

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
