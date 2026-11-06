# Option coverage probe

Read-only exact-symbol/date presence checks in both option tables. Controls are AAPL, MSFT, and SPY. Presence does not prove a complete chain; absence does not establish unlisted options or resolve ticker aliases.

| Date | Stockquote symbols | Sample | Primary | Alternate | Alternate only | Absent both | Query failures | Primary controls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024-04-10 | 5636 | 20 | 19 | 0 | 0 | 1 | 0 | 3/3 |
| 2024-07-12 | 5630 | 20 | 20 | 0 | 0 | 0 | 0 | 3/3 |
| 2024-07-26 | 5692 | 20 | 20 | 0 | 0 | 0 | 0 | 3/3 |
| 2024-08-29 | 5966 | 20 | 19 | 0 | 0 | 1 | 0 | 3/3 |
| 2024-11-01 | 5960 | 20 | 18 | 0 | 0 | 2 | 0 | 3/3 |
| 2025-01-31 | 22453 | 20 | 7 | 0 | 0 | 13 | 0 | 3/3 |
| 2025-04-16 | 22041 | 20 | 2 | 0 | 0 | 18 | 0 | 3/3 |
| 2025-10-21 | 23795 | 20 | 6 | 0 | 0 | 14 | 0 | 3/3 |
| 2025-12-17 | 24252 | 20 | 4 | 0 | 0 | 16 | 0 | 3/3 |
| 2025-12-30 | 24099 | 20 | 6 | 0 | 0 | 14 | 0 | 3/3 |

These checks retain the original outcome-independent sample. They do not filter missing symbols out of the universe or assign negative labels. Historical listing and instrument classification remain separate review tasks.

All control checks found primary-table data on every probed date. This rules out total primary-table absence on those dates, but not partial ingestion or symbol-specific gaps. Compare the stockquote frame sizes before interpreting cross-year option coverage.
