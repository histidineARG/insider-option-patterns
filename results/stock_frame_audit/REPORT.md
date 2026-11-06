# Stockquote frame expansion

The first large expansion detected in saved session counts is 2024-11-04; the preceding session is 2024-11-01. Detection requires at least 10,000 rows, a preceding 20-session median of at least 1,000, and at least twice that median.

Positive-price symbol sets increase from 5,960 to 22,991: 5,932 retained, 17,059 added, and 28 removed.

Saved post-expansion observations grouped by exact ticker presence in the preceding-session frame:

| Year | Baseline membership | Stock-days | Observed chains | No target rows | Query failures |
| --- | --- | ---: | ---: | ---: | ---: |
| 2025 | absent | 75 | 1 | 74 | 0 |
| 2025 | present | 25 | 24 | 1 | 0 |

Expansion date is a source-count diagnostic, not a verified vendor change date.
Exact symbols do not resolve issuer identity, ticker reuse, or instrument type.
Later symbols absent from the baseline may be new listings or renamed securities.
Original samples and labels are unchanged. Membership strata are descriptive, not eligibility filters.

Membership compares all later observations with one historical session. It cannot justify excluding subsequent listings from validation. Chain coverage uses the saved background extraction, not new chain queries. The source-count snapshot and current membership query may have different refresh times.
