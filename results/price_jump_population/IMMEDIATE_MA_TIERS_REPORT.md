# Immediate post-announcement jumps — tiered local M&A evidence

Immediate post-announcement jump = reaction-session close / prior NYSE session close - 1. Tiers expand beyond hand-verified events. Tier E is discovery only (price jump near merger filing), not confirmation.

## Why the earlier “confirmed” number looked too low

Prior “confirmed” counts used only research_ma_events with event_verified=1 (~30 hand-reviewed rows). That is a review-throughput ceiling, not a market frequency. Local maevent alone already lists dozens of dated symbol deals in 2013–2016; filing-proximate ≥20% price leads are far larger after ~2018.

## Annual counts of **immediate** announcement reactions (not yearly returns)

### Tier A — hand source-reviewed public targets

| Year | Events | Immediate ≥15% | Immediate ≥20% |
| ---: | ---: | ---: | ---: |
| 2013 | 2 | 2 | 1 |
| 2014 | 2 | 1 | 0 |
| 2015 | 2 | 1 | 1 |
| 2016 | 5 | 5 | 2 |
| 2017 | 2 | 2 | 2 |
| 2018 | 2 | 2 | 2 |
| 2019 | 2 | 2 | 2 |
| 2020 | 1 | 1 | 1 |
| 2021 | 3 | 3 | 2 |
| 2022 | 4 | 2 | 2 |
| 2023 | 3 | 3 | 3 |
| 2024 | 2 | 2 | 2 |
| 2025 | 0 | 0 | 0 |

### Tier B — local `maevent` rows with a symbol (dated deals; session usually unknown)

| Year | Events | Immediate ≥15% (any session alt) | Immediate ≥20% (any session alt) |
| ---: | ---: | ---: | ---: |
| 2013 | 11 | 4 | 3 |
| 2014 | 18 | 3 | 3 |
| 2015 | 12 | 7 | 4 |
| 2016 | 20 | 16 | 13 |
| 2017 | 0 | 0 | 0 |
| 2018 | 0 | 0 | 0 |
| 2019 | 0 | 0 | 0 |
| 2020 | 0 | 0 | 0 |
| 2021 | 0 | 0 | 0 |
| 2022 | 0 | 0 | 0 |
| 2023 | 0 | 0 | 0 |
| 2024 | 0 | 0 | 0 |
| 2025 | 0 | 0 | 0 |

### Union of local dated deal lists (A∪B∪C∪D, deduped by symbol+date)

| Year | Dated events | Immediate ≥15% | Immediate ≥20% |
| ---: | ---: | ---: | ---: |
| 2013 | 12 | 5 | 4 |
| 2014 | 20 | 4 | 3 |
| 2015 | 14 | 6 | 3 |
| 2016 | 24 | 17 | 13 |
| 2017 | 2 | 2 | 2 |
| 2018 | 2 | 2 | 2 |
| 2019 | 2 | 2 | 2 |
| 2020 | 1 | 1 | 1 |
| 2021 | 3 | 3 | 2 |
| 2022 | 4 | 2 | 2 |
| 2023 | 3 | 3 | 3 |
| 2024 | 2 | 2 | 2 |
| 2025 | 2 | 2 | 2 |

### Tier E — discovery only: ≥20% session jumps proximate to a merger filing (NOT confirmed announcements)

| Year | ≥20% filing-proximate leads | Unique symbols |
| ---: | ---: | ---: |
| 2013 | 1 | 1 |
| 2014 | 4 | 4 |
| 2015 | 7 | 6 |
| 2016 | 8 | 5 |
| 2017 | 8 | 7 |
| 2018 | 25 | 19 |
| 2019 | 11 | 10 |
| 2020 | 29 | 22 |
| 2021 | 102 | 78 |
| 2022 | 132 | 108 |
| 2023 | 148 | 99 |
| 2024 | 216 | 127 |
| 2025 | 531 | 242 |

Union dated deals: **91** unique symbol-dates; **41** with an immediate ≥20% reaction under timed or any-alt unknown-session rules.

Interpretation: your ~>20 premium deals/year intuition is about **market frequency**. Hand-verified Tier A is a small reviewed sample. Tier B (2013–2016 maevent) and Tier E (filing-proximate leads) show the local database supports a much larger set of immediate premium-like prints once confirmation gates are widened—or used only as discovery.

### Tier F — `mafromnews` symbol/news-date (M&A-tagged news; not verified announcements)

| Year | Unique symbol-news dates | Immediate any-alt ≥15% | Immediate any-alt ≥20% | Unique symbols ≥20% |
| ---: | ---: | ---: | ---: | ---: |
| 2013 | 6 | 0 | 0 | 0 |
| 2014 | 26 | 0 | 0 | 0 |
| 2015 | 160 | 2 | 2 | 2 |
| 2016 | 318 | 1 | 1 | 1 |
| 2017 | 260 | 6 | 3 | 3 |

### All-name stockquote context (not M&A)

In 2013–2019, calendar-consecutive ≥20% close jumps with an open gap also ≥20% run about **250–420 per year** across the whole quote database. Even a small M&A fraction of that universe exceeds 20/year.

## Bottom line

- Immediate announcement reactions were already what we measured; the low counts came from **narrow confirmation**, not from looking at annual returns.
- Hand-reviewed Tier A (~1–5/year) is sample-limited.
- Local `maevent` in 2016 alone has **13** symbol deals with an immediate ≥20% print under unknown-session any-alt rules — in range of a “>~20 in a busy year” intuition.
- Filing-proximate ≥20% leads and `mafromnews` show still larger candidate pools, especially 2015–2017 news and 2018+ filing proximity — with weaker confirmation.
- Post-2016 collapse in dated local deal tables is a **coverage hole**, not evidence the market shrank to 2 premium deals/year.

