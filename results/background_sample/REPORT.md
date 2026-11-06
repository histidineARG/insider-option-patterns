# Background coverage audit

Saved, outcome-independent stockquote sample. Counts describe source coverage, not a verified historical equity-option universe. Missing target rows do not establish that options were unlisted. No observations are presumed negative.

| Year | Stock-days | Dates | Chains | No target rows | Query failures | Incomplete baseline | Invalid volume | Usable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2013 | 100 | 5 | 98 | 2 | 0 | 1 | 1 | 97 |
| 2014 | 100 | 5 | 100 | 0 | 0 | 2 | 2 | 98 |
| 2015 | 100 | 5 | 100 | 0 | 0 | 1 | 1 | 99 |
| 2016 | 100 | 5 | 100 | 0 | 0 | 0 | 0 | 100 |
| 2017 | 100 | 5 | 100 | 0 | 0 | 1 | 1 | 99 |
| 2018 | 100 | 5 | 100 | 0 | 0 | 1 | 1 | 99 |
| 2019 | 100 | 5 | 100 | 0 | 0 | 0 | 0 | 100 |
| 2020 | 100 | 5 | 100 | 0 | 0 | 2 | 2 | 98 |
| 2021 | 100 | 5 | 100 | 0 | 0 | 1 | 1 | 99 |
| 2022 | 100 | 5 | 100 | 0 | 0 | 3 | 3 | 97 |
| 2023 | 100 | 5 | 100 | 0 | 0 | 5 | 5 | 95 |
| 2024 | 100 | 5 | 96 | 4 | 0 | 21 | 21 | 75 |
| 2025 | 100 | 5 | 25 | 75 | 0 | 0 | 0 | 25 |

Incomplete baseline and invalid volume counts apply to observed chains and can overlap. Usable requires an observed chain, a complete baseline, and valid volume data. Counts are unweighted and do not estimate population rates.

Regenerate from saved observations with `python3 background_report.py`. Review issuer identity, historical instrument classification, and first public disclosures before assigning labels or choosing chronological splits.
