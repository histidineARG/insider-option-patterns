# Research roadmap

Updated: 2026-11-06. Governing protocol: METHODOLOGY.md.

## Completed before this run

- Calendar-aware event features, price-only candidate cohort, and outcome-independent background pilot.
- Coverage audits: stockquote expands on 2024-11-04; historical frame membership explains most of the sampled 2025 option-coverage difference.
- Fixed-rule descriptive counts; no reliable negative labels or population accuracy estimates.
- Evidence-overlay cohort with primary-source chronology findings for all 26 price-qualified candidates.
- Time-safe observation table, frozen chronological partitions, gated evaluation interfaces, and conservative trading assumptions.

## Active work

1. Deepen first-disclosure media search and complete corporate-action / security-identity reviews until events can become training-ready.
2. Build complete scoped outcome reviews that can certify background negatives without inventing them.
3. Audit historical option listing eligibility and vendor delivery timing using information available on each observation date.
4. Keep population metrics and trading simulation blocked until evidence gates pass; reserved 2026 remains unauthorized.

## Current task, gap, and target

- Task: connect primary-source event chronology to time-safe feature/label construction, then implement chronological evaluation and trading gates.
- Completed in this checkpoint: announcement-session or press-time findings recorded for every price-qualified candidate; earlier public information, conflicts, ADS terms, issuer-identity notes, and unresolved searches preserved in `data/event_review_overrides.json`. Offline review overlay refreshes saved events without requerying prices. `research_dataset.py` builds 2,080 distinct stock-days with ten-session outcomes, disclosure diagnostics, and purged partitions; known positives and certified negatives remain zero. `evaluation.py` constructs fixed-rule alert episodes and logistic interfaces but blocks population metrics. `trading_assumptions.py` freezes conservative fill rules and reports blocked trading gates. Corporate-action/identity checklists are complete for all 45 cohort events (CIK, share class, reincarnation, consideration). `price_action_vet.py --deep` requeries OHLCV paths; reactions remain gap-dominated with documented path hazards.
- Gap: zero events are training-ready (`reviewed_cohort` still forces `training_label_ready=false`). Reviewed cohort is 45 priced events; `first_public_disclosure_verified` is true for 27 events (all 25 clean `jump_ok`, plus ADT and CALT via jump-cause M&A attribution; ADT keeps price-source conflict and CALT keeps ADS hazard). 20 events carry earlier-public / prior-process / source / ADS hazards that block clean jump attribution. First complete scoped outcome review certifies 9 background negatives (CSCO/BA/ORCL/WFC/SLB/GE/ABB/ACC/ACIA); registry otherwise still incomplete. Quote delivery timing and contract deliverables remain unverified. Reserved 2026 has no extracted observations and is not authorized.
- News filter: keep causes 2 (M&A), 3 (biotech trial), 4 (tech breakthrough); drop 1 (earnings) using EDGAR 8-K Item 2.02 calendar (`edgar_earnings_calendar.py` / `price_jump_examine.py`).
- Next target: all clean `jump_ok` events now have first-public bounds; next deepen contaminated windows and outcome-coverage negatives; keep contaminated windows documented (ONXX/RETA gap after after-close/before-open rumor; MAXR same-day earlier report; CNQR/SAGE earlier episodes; ARG/PCP/VA/VAL/KRFT/IMGN/BIVV/COHR/ITCI earlier-public) and out of clean attribution; begin scoped negative-outcome reviews only under `data/outcome_coverage_reviews.json`; keep evaluation gated.
- Completion target: evidence-supported evaluation and conservative trading results only after event, population, timing, and tradability gates pass. Otherwise report exact blocked gates and finish independent implementation work.

## Decisions

- Read source databases only; write artifacts in this checkout.
- No missing chain, unknown event history, or unreviewed security becomes a negative label.
- A dated press release does not establish absence of earlier public information.
- Maintain auditable source locators and review scope. Distinguish verified facts from review judgments.
- Commit tested milestones and continue independent work when evidence gates block downstream results.

## Current constraints

- The nonexhaustive registry cannot certify negative ten-session outcomes across the historical universe.
- Corporate actions, issuer identity, first disclosure, and vendor availability timing are not uniformly verified.
- 2013–2025 aggregate exploratory results have been inspected. An untouched final test needs a separately reserved, sufficiently covered period.
- Historical option listing metadata and complete population coverage are not yet established.

## Next actions

- Dated public-target confirmation stands at 41 confirmed price+volume reactions (3 market passes still blocked: TUMI rumor/official unresolved; RSE/ODP unsolicited proposals).
- Reviewed cohort now 45 events with corporate-action/identity checklists complete. Clean `jump_ok` = 25; `first_public_disclosure_verified` = 27; `training_label_ready` = 0. News jump-cause filter policy is keep 2/3/4 (M&A, biotech-trial, tech-breakthrough) and drop 1 (earnings) plus hard drops for sub-$5 `prev_close`, ETF/ETN denylist, and no-option presence; all 45 reviewed cohort events are class-2 keep (18 contaminated). Classes 3–4 kept when found in jump examine; see `results/news_jump_filter/` and `data/price_jump_news_reviews.json`. 2013–2016 ≥15% vol≥2× jump examine: 6609 jumps; ~723 earnings, 3604 `drop_sub_5`, 65 `drop_etf`, 19 `drop_no_option`. Manual reviews now 681 rows → **161 keep** (92 biotech, 41 ma_news, 26 ma_rumor, 2 tech) and **520 drop_other**. Ge50/ge30/ge25/ge20 cleared. Ge15 (≥15%) news-confirm in progress: 233 pending (`results/price_jump_examine/news_queue_ge15.json`). Do not unlock `training_label_ready` or population/trading metrics.
- Use EDGAR-with-symbol pre-proxy jump census as a discovery bound, not as training labels.
- Expand scoped outcome-coverage reviews only when a complete source-backed negative search protocol exists.
- Do not authorize population metrics, threshold selection, or trading simulation while gates remain blocked.
