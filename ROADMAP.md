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
- News filter: keep causes **2–11** (M&A, biotech trial, tech breakthrough, commercial contract, partnership/license, regulatory approval, guidance step-up, legal unlock, product launch, activist/alternatives); drop 1 (earnings) using EDGAR 8-K Item 2.02 calendar (`edgar_earnings_calendar.py` / `price_jump_examine.py`). Canonical taxonomy: [METHODOLOGY.md](METHODOLOGY.md) §9.
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
- Reviewed cohort now 45 events with corporate-action/identity checklists complete. Clean `jump_ok` = 25; `first_public_disclosure_verified` = 27; `training_label_ready` = 0. News jump-cause filter policy is now keep **2–11** (see METHODOLOGY §9) and drop 1 (earnings) plus hard drops for sub-$5 `prev_close`, ETF/ETN denylist, and no-option presence; all 45 reviewed cohort events are still class-2 keep (18 contaminated). Classes 3–11 are kept by policy when found; existing `drop_other_not_234` rows (520) are re-bucket candidates under 5–11 and have not been re-labeled yet. See `results/news_jump_filter/` and `data/price_jump_news_reviews.json`. 2013–2016 ≥15% vol≥2× jump examine: 6609 jumps; ~723 earnings, 3604 `drop_sub_5`, 65 `drop_etf`, 19 `drop_no_option`. Manual reviews now 681 rows → **161 keep** under old 2/3/4 (92 biotech, 41 ma_news, 26 ma_rumor, 2 tech) and **520 drop_other**. Ge50/ge30/ge25/ge20 cleared. Ge15 (≥15%) news-confirm in progress: 233 pending (`results/price_jump_examine/news_queue_ge15.json`). Do not unlock `training_label_ready` or population/trading metrics.
- Use EDGAR-with-symbol pre-proxy jump census as a discovery bound, not as training labels.
- Expand scoped outcome-coverage reviews only when a complete source-backed negative search protocol exists.
- Do not authorize population metrics, threshold selection, or trading simulation while gates remain blocked.

## 2026-11-12 policy re-bucket checkpoint

- Source-backed first batch reclassified ERII, ZIOP, GLNG, INFI, ALNY, NAV, and CGEN to class 6; MBI to class 9. Prior labels, details, and locators are preserved per row in `policy_review.previous`.
- Manual ledger: 681 rows, 169 keep, 512 legacy drops awaiting reassessment. The 233 pending ge15 reviews are unchanged.
- Audit: `results/news_policy_rebucket/first8.json`. Historical database-derived snapshots have not been refreshed and retain prior counts. First-public timing and training readiness are not certified by this policy pass.

## 2026-11-12 next filtering batch

- Reviewed 15 additional legacy drops: 9 promoted (FSLR class 8; GDOT/NTWK class 5; SGMO/CEQP/XNCR/IMMR/ADXS/MNST class 6), 5 confirmed drops (COUP/TZOO/STMP/VIPS earnings; EDR reverse split), SPWR deferred for earlier-public timing conflict (Jan 2 08:00 ET release versus Jan 3 jump).
- Current manual ledger: 681 unique rows; 178 keep, 497 legacy drops awaiting reassessment, 4 earnings drops, 1 mechanical drop, 1 pending timing review. Cumulative expanded-policy reviews: 23.
- Audit: `results/news_policy_rebucket/NEXT15.md` and `next15.json`; prior fields preserved per row. Database-derived snapshots and queues were not refreshed. The saved 233-row ge15 queue predates the SPWR deferral and must not be represented as the current complete pending set.
- Next: continue legacy-drop reassessment; verify SPWR same-session attribution separately; retain evidence and timing gates.

## 2026-11-12 next three license reviews

- Promoted IMGN (2015-03-23), MGNX (2016-05-18), and historical Array BioPharma / ARRY (2015-01-23) to class 6 using primary releases. Preserve ARRY historical-issuer warning and announcement-versus-execution/closing distinctions.
- Ledger: 681 unique rows; 181 keep, 494 legacy drops, 4 earnings drops, 1 mechanical drop, 1 pending timing review. Cumulative policy reviews: 26.
- Audit: `results/news_policy_rebucket/NEXT3.md` and `next3.json`. Previous labels retained per row. First-public timing, training and evaluation remain gated; saved database snapshots and queues were not refreshed.
- Next: continue 494 legacy reassessments and resolve SPWR timing independently.

## 2026-11-12 autonomous_batch01_15

- Reviewed 15 legacy rows: {'keep': 5, 'drop': 7, 'defer': 3}.
- Current ledger: {'keep': 186, 'drop_other_not_234': 479, 'drop_mechanical': 1, 'pending_news_review': 4, 'drop_earnings': 9, 'drop_analyst': 1, 'drop_financing': 1}. Cumulative expanded-policy reviews: 41.
- Audit: `results/news_policy_rebucket/autonomous_batch01_15.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch02_12

- Reviewed 12 legacy rows: {'keep': 4, 'drop': 8}.
- Current ledger: {'keep': 190, 'drop_earnings': 16, 'drop_other_not_234': 467, 'drop_mechanical': 1, 'pending_news_review': 4, 'drop_analyst': 1, 'drop_financing': 2}. Cumulative expanded-policy reviews: 53.
- Audit: `results/news_policy_rebucket/autonomous_batch02_12.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch03_15

- Reviewed 15 legacy rows: {'keep': 5, 'drop': 8, 'defer': 2}.
- Current ledger: {'keep': 195, 'drop_earnings': 19, 'drop_other_not_234': 452, 'drop_mechanical': 1, 'pending_news_review': 6, 'drop_macro_sector': 3, 'drop_analyst': 2, 'drop_financing': 2, 'drop_etf': 1}. Cumulative expanded-policy reviews: 68.
- Audit: `results/news_policy_rebucket/autonomous_batch03_15.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch04_8

- Reviewed 8 legacy rows: {'keep': 3, 'drop': 1, 'defer': 4}.
- Current ledger: {'keep': 198, 'drop_earnings': 20, 'drop_other_not_234': 444, 'drop_mechanical': 1, 'pending_news_review': 10, 'drop_macro_sector': 3, 'drop_analyst': 2, 'drop_financing': 2, 'drop_etf': 1}. Cumulative expanded-policy reviews: 76.
- Audit: `results/news_policy_rebucket/autonomous_batch04_8.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous run summary

- Reassessed 50 additional rows: 17 promoted, 24 confirmed drops, 9 deferred (7 timing, 2 category/primary-cause). Ledger: 198 keep, 444 legacy reassessments remaining, 10 manual pending, 29 explicit drops. Expanded-policy reviews total 76.
- `results/news_policy_rebucket/CURRENT_STATUS.md` and `.json` summarize current counts. The adjacent legacy and pending queues are scoped to the 681-row manual ledger, not the full population. Saved population queue and database snapshots are unchanged.
- Validation: 74 unit tests pass, unique keys and all 50 prior-label/source overlays checked, `git diff --check` passes. Continue filtering without approval prompts; preserve timing and training gates.

## 2026-11-12 autonomous_batch05_10

- Reviewed 10 legacy rows: {'drop': 4, 'keep': 4, 'defer': 2}.
- Current ledger: {'keep': 202, 'drop_earnings': 24, 'drop_other_not_234': 434, 'drop_mechanical': 1, 'pending_news_review': 12, 'drop_macro_sector': 3, 'drop_analyst': 2, 'drop_financing': 2, 'drop_etf': 1}. Cumulative expanded-policy reviews: 86.
- Audit: `results/news_policy_rebucket/autonomous_batch05_10.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch06_10

- Reviewed 10 legacy rows: {'drop': 10}.
- Current ledger: {'keep': 202, 'drop_earnings': 32, 'drop_other_not_234': 424, 'drop_mechanical': 1, 'pending_news_review': 12, 'drop_macro_sector': 3, 'drop_analyst': 3, 'drop_financing': 2, 'drop_peer_earnings': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 96.
- Audit: `results/news_policy_rebucket/autonomous_batch06_10.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch07_15

- Reviewed 15 legacy rows: {'drop': 9, 'defer': 6}.
- Current ledger: {'keep': 202, 'drop_earnings': 32, 'drop_other_not_234': 409, 'drop_mechanical': 1, 'pending_news_review': 18, 'drop_macro_sector': 6, 'drop_analyst': 4, 'drop_financing': 3, 'drop_peer_sympathy': 2, 'drop_regulatory_process': 1, 'drop_peer_earnings': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 111.
- Audit: `results/news_policy_rebucket/autonomous_batch07_15.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 extended autonomous checkpoint

- This run now totals 85 reassessments: 21 promoted, 47 confirmed drops, 17 deferred (12 timing, 5 category/primary-cause). Expanded-policy reviews total 111.
- Current 681-row ledger: 202 keep, 409 legacy reassessments remaining, 18 manual pending, 52 explicit drops. `results/news_policy_rebucket/CURRENT_STATUS.md` and `.json` supersede the earlier 50-row summary; adjacent ledger queues were regenerated with matching source checksums.
- Corrected EBS catalyst chronology: December 8 release concerns CDC BioThrax procurement; NuThrax BARDA award was September 30. EBS December 9 remains pending for reaction timing. ADXS December 22 and EYES February 23 also have earlier-source date conflicts. Preserve prior descriptions for audit.
- Validation: 74 unit tests pass; all 85 production overlays reproduce saved labels, preserve earnings precedence, and retain prior fields and source locators. Unique symbol/session keys and diff whitespace checks pass.
- Remaining work: 409 legacy reviews plus 18 deferred manual rows; saved population queue remains separate and stale. Continue source-backed filtering without approval prompts. Training and evaluation gates stay blocked.

## 2026-11-12 autonomous_batch08_16

- Reviewed 16 legacy rows: {'keep': 3, 'drop': 6, 'defer': 7}.
- Current ledger: {'keep': 205, 'drop_earnings': 32, 'drop_other_not_234': 393, 'pending_news_review': 25, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 7, 'drop_analyst': 6, 'drop_financing': 4, 'drop_peer_sympathy': 2, 'drop_operating_update': 1, 'drop_regulatory_process': 1, 'drop_peer_earnings': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 127.
- Audit: `results/news_policy_rebucket/autonomous_batch08_16.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch09_8

- Reviewed 8 legacy rows: {'drop': 5, 'defer': 3}.
- Current ledger: {'keep': 205, 'drop_earnings': 32, 'drop_other_not_234': 385, 'pending_news_review': 28, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 8, 'drop_analyst': 6, 'drop_financing': 6, 'drop_peer_sympathy': 3, 'drop_regulatory_process': 2, 'drop_operating_update': 1, 'drop_peer_earnings': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 135.
- Audit: `results/news_policy_rebucket/autonomous_batch09_8.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch10_6

- Reviewed 6 legacy rows: {'keep': 1, 'drop': 3, 'defer': 2}.
- Current ledger: {'keep': 206, 'drop_earnings': 35, 'drop_other_not_234': 379, 'pending_news_review': 30, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 8, 'drop_analyst': 6, 'drop_financing': 6, 'drop_peer_sympathy': 3, 'drop_regulatory_process': 2, 'drop_operating_update': 1, 'drop_peer_earnings': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 141.
- Audit: `results/news_policy_rebucket/autonomous_batch10_6.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 continuation through 141 policy reviews

- Reassessed 30 more legacy rows in batches 08–10: 4 keep, 14 confirmed drops, 12 deferred (9 timing, 3 category/primary-cause). Expanded-policy reviews total 141; autonomous reviews total 115.
- Current ledger: 206 keep, 379 legacy reassessments remaining, 30 manual pending, 66 explicit drops across 681 unique symbol/session rows. `results/news_policy_rebucket/CURRENT_STATUS.md` and `.json` supersede prior current summaries; ledger-scoped queues regenerated with matching SHA-256.
- Promoted OMER/EXAS government reimbursement/coverage authorizations as class 7 equivalent decisions (not FDA approvals); SCTY standalone 2014 deployment outlook as class 8; EXPR Sycamore interest/special committee as class 11. Preserve these category judgments and concurrent-catalyst limitations in the row rationale.
- Timing/source corrections include ORMP April 1 versus April 13, EXPR January 14 before-open versus January 15, PFSW January 13 internal versus January 19 hosting versus January 21 jump, and HRTX September 22 data versus September 23 jump. BTU split timing predates its October 6 filing; do not label filing day a mechanical jump without price-adjustment evidence.
- Validation: 74 unit tests pass; all 115 autonomous production overlays and earnings precedence checked; unique keys, preserved prior fields/source locators and diff whitespace pass. Source databases, saved population queue and training/evaluation gates remain unchanged.

## 2026-11-12 autonomous_batch11_10

- Reviewed 10 legacy rows: {'keep': 3, 'drop': 3, 'defer': 4}.
- Current ledger: {'keep': 209, 'drop_earnings': 37, 'drop_other_not_234': 369, 'pending_news_review': 34, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 8, 'drop_analyst': 6, 'drop_financing': 6, 'drop_peer_sympathy': 3, 'drop_operating_update': 2, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 151.
- Audit: `results/news_policy_rebucket/autonomous_batch11_10.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch12_6

- Reviewed 6 legacy rows: {'keep': 2, 'drop': 2, 'defer': 2}.
- Current ledger: {'keep': 211, 'drop_earnings': 37, 'drop_other_not_234': 363, 'pending_news_review': 36, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 8, 'drop_analyst': 6, 'drop_financing': 7, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 157.
- Audit: `results/news_policy_rebucket/autonomous_batch12_6.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch13_10

- Reviewed 10 legacy rows: {'keep': 1, 'defer': 4, 'drop': 5}.
- Current ledger: {'keep': 212, 'drop_earnings': 37, 'drop_other_not_234': 353, 'pending_news_review': 40, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 10, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 1}. Cumulative expanded-policy reviews: 167.
- Audit: `results/news_policy_rebucket/autonomous_batch13_10.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch14_12

- Reviewed 12 legacy rows: {'keep': 1, 'defer': 7, 'drop': 4}.
- Current ledger: {'keep': 213, 'drop_earnings': 37, 'drop_other_not_234': 341, 'pending_news_review': 47, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 179.
- Audit: `results/news_policy_rebucket/autonomous_batch14_12.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch15_12

- Reviewed 12 legacy rows: {'drop': 12}.
- Current ledger: {'keep': 213, 'drop_earnings': 49, 'drop_other_not_234': 329, 'pending_news_review': 47, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 191.
- Audit: `results/news_policy_rebucket/autonomous_batch15_12.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch16_7

- Reviewed 7 legacy rows: {'keep': 4, 'defer': 3}.
- Current ledger: {'keep': 217, 'drop_earnings': 49, 'drop_other_not_234': 322, 'pending_news_review': 50, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 198.
- Audit: `results/news_policy_rebucket/autonomous_batch16_7.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch17_8

- Reviewed 8 legacy rows: {'drop': 6, 'keep': 1, 'defer': 1}.
- Current ledger: {'keep': 218, 'drop_earnings': 55, 'drop_other_not_234': 314, 'pending_news_review': 51, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 206.
- Audit: `results/news_policy_rebucket/autonomous_batch17_8.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch18_5

- Reviewed 5 legacy rows: {'keep': 2, 'drop': 1, 'defer': 2}.
- Current ledger: {'keep': 220, 'drop_earnings': 56, 'drop_other_not_234': 309, 'pending_news_review': 53, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 211.
- Audit: `results/news_policy_rebucket/autonomous_batch18_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch19_5

- Reviewed 5 legacy rows: {'drop': 4, 'defer': 1}.
- Current ledger: {'keep': 220, 'drop_earnings': 60, 'drop_other_not_234': 304, 'pending_news_review': 54, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 216.
- Audit: `results/news_policy_rebucket/autonomous_batch19_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch20_5

- Reviewed 5 legacy rows: {'drop': 5}.
- Current ledger: {'keep': 220, 'drop_earnings': 65, 'drop_other_not_234': 299, 'pending_news_review': 54, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 3, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 221.
- Audit: `results/news_policy_rebucket/autonomous_batch20_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch21_5

- Reviewed 5 legacy rows: {'keep': 1, 'drop': 1, 'defer': 3}.
- Current ledger: {'keep': 221, 'drop_earnings': 65, 'drop_other_not_234': 294, 'pending_news_review': 57, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 4, 'drop_operating_update': 3, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 226.
- Audit: `results/news_policy_rebucket/autonomous_batch21_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch22_5

- Reviewed 5 legacy rows: {'drop': 1, 'defer': 4}.
- Current ledger: {'keep': 221, 'drop_earnings': 65, 'drop_other_not_234': 289, 'pending_news_review': 61, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 4, 'drop_operating_update': 4, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 231.
- Audit: `results/news_policy_rebucket/autonomous_batch22_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch23_5

- Reviewed 5 legacy rows: {'keep': 2, 'defer': 3}.
- Current ledger: {'keep': 223, 'drop_earnings': 65, 'drop_other_not_234': 284, 'pending_news_review': 64, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 4, 'drop_operating_update': 4, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 236.
- Audit: `results/news_policy_rebucket/autonomous_batch23_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch24_5

- Reviewed 5 legacy rows: {'drop': 4, 'defer': 1}.
- Current ledger: {'keep': 223, 'drop_earnings': 69, 'drop_other_not_234': 279, 'pending_news_review': 65, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 4, 'drop_operating_update': 4, 'drop_regulatory_process': 2, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 241.
- Audit: `results/news_policy_rebucket/autonomous_batch24_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch25_5

- Reviewed 5 legacy rows: {'keep': 1, 'drop': 1, 'defer': 3}.
- Current ledger: {'keep': 224, 'drop_earnings': 69, 'drop_other_not_234': 274, 'pending_news_review': 68, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 4, 'drop_operating_update': 4, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 246.
- Audit: `results/news_policy_rebucket/autonomous_batch25_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch26_5

- Reviewed 5 legacy rows: {'drop': 4, 'keep': 1}.
- Current ledger: {'keep': 225, 'drop_earnings': 73, 'drop_other_not_234': 269, 'pending_news_review': 68, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 6, 'drop_financing': 8, 'drop_peer_sympathy': 4, 'drop_operating_update': 4, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 251.
- Audit: `results/news_policy_rebucket/autonomous_batch26_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch27_5

- Reviewed 5 legacy rows: {'drop': 4, 'defer': 1}.
- Current ledger: {'keep': 225, 'drop_earnings': 73, 'drop_peer_sympathy': 7, 'pending_news_review': 69, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 7, 'drop_financing': 8, 'drop_other_not_234': 264, 'drop_operating_update': 4, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 256.
- Audit: `results/news_policy_rebucket/autonomous_batch27_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch28_5

- Reviewed 5 legacy rows: {'drop': 4, 'defer': 1}.
- Current ledger: {'keep': 225, 'drop_earnings': 77, 'drop_peer_sympathy': 7, 'pending_news_review': 70, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 7, 'drop_financing': 8, 'drop_other_not_234': 259, 'drop_operating_update': 4, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 261.
- Audit: `results/news_policy_rebucket/autonomous_batch28_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch29_5

- Reviewed 5 legacy rows: {'defer': 4, 'drop': 1}.
- Current ledger: {'keep': 225, 'drop_earnings': 77, 'drop_peer_sympathy': 7, 'pending_news_review': 74, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 7, 'drop_financing': 8, 'drop_other_not_234': 254, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 266.
- Audit: `results/news_policy_rebucket/autonomous_batch29_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch30_5

- Reviewed 5 legacy rows: {'drop': 1, 'defer': 4}.
- Current ledger: {'keep': 225, 'drop_earnings': 77, 'drop_peer_sympathy': 7, 'pending_news_review': 78, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 13, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 249, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 271.
- Audit: `results/news_policy_rebucket/autonomous_batch30_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch31_5

- Reviewed 5 legacy rows: {'drop': 5}.
- Current ledger: {'keep': 225, 'drop_earnings': 77, 'drop_peer_sympathy': 7, 'pending_news_review': 78, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 18, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 244, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 276.
- Audit: `results/news_policy_rebucket/autonomous_batch31_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch32_5

- Reviewed 5 legacy rows: {'drop': 2, 'defer': 3}.
- Current ledger: {'keep': 225, 'drop_earnings': 77, 'drop_peer_sympathy': 7, 'pending_news_review': 81, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 20, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 239, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 281.
- Audit: `results/news_policy_rebucket/autonomous_batch32_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch33_5

- Reviewed 5 legacy rows: {'drop': 3, 'defer': 2}.
- Current ledger: {'keep': 225, 'drop_earnings': 77, 'drop_peer_sympathy': 9, 'pending_news_review': 83, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 234, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 286.
- Audit: `results/news_policy_rebucket/autonomous_batch33_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch34_5

- Reviewed 5 legacy rows: {'drop': 1, 'defer': 4}.
- Current ledger: {'keep': 225, 'drop_earnings': 78, 'drop_peer_sympathy': 9, 'pending_news_review': 87, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 229, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 291.
- Audit: `results/news_policy_rebucket/autonomous_batch34_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch35_5

- Reviewed 5 legacy rows: {'defer': 5}.
- Current ledger: {'keep': 225, 'drop_earnings': 78, 'drop_peer_sympathy': 9, 'pending_news_review': 92, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 224, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 296.
- Audit: `results/news_policy_rebucket/autonomous_batch35_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch36_5

- Reviewed 5 legacy rows: {'keep': 2, 'drop': 1, 'defer': 2}.
- Current ledger: {'keep': 227, 'drop_earnings': 78, 'drop_peer_sympathy': 10, 'pending_news_review': 94, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 8, 'drop_financing': 8, 'drop_other_not_234': 219, 'drop_operating_update': 5, 'drop_regulatory_process': 3, 'drop_peer_earnings': 1, 'drop_passive_ownership': 1, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 301.
- Audit: `results/news_policy_rebucket/autonomous_batch36_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch37_5

- Reviewed 5 legacy rows: {'drop': 3, 'defer': 2}.
- Current ledger: {'keep': 227, 'drop_earnings': 78, 'drop_peer_sympathy': 10, 'pending_news_review': 96, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 214, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 306.
- Audit: `results/news_policy_rebucket/autonomous_batch37_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch38_5

- Reviewed 5 legacy rows: {'keep': 3, 'defer': 2}.
- Current ledger: {'keep': 230, 'drop_earnings': 78, 'drop_peer_sympathy': 10, 'pending_news_review': 98, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 209, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 311.
- Audit: `results/news_policy_rebucket/autonomous_batch38_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch39_5

- Reviewed 5 legacy rows: {'drop': 3, 'keep': 1, 'defer': 1}.
- Current ledger: {'keep': 231, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 99, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 204, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 316.
- Audit: `results/news_policy_rebucket/autonomous_batch39_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch40_5

- Reviewed 5 legacy rows: {'defer': 5}.
- Current ledger: {'keep': 231, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 104, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 199, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 321.
- Audit: `results/news_policy_rebucket/autonomous_batch40_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch41_5

- Reviewed 5 legacy rows: {'keep': 1, 'defer': 4}.
- Current ledger: {'keep': 232, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 108, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 194, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 1, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 326.
- Audit: `results/news_policy_rebucket/autonomous_batch41_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch42_5

- Reviewed 5 legacy rows: {'drop': 1, 'keep': 1, 'defer': 3}.
- Current ledger: {'keep': 233, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 111, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 189, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 2, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 331.
- Audit: `results/news_policy_rebucket/autonomous_batch42_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch43_5

- Reviewed 5 legacy rows: {'defer': 5}.
- Current ledger: {'keep': 233, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 116, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 21, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 184, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 2, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 336.
- Audit: `results/news_policy_rebucket/autonomous_batch43_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch44_5

- Reviewed 5 legacy rows: {'drop': 1, 'defer': 4}.
- Current ledger: {'keep': 233, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 120, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 22, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 179, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 2, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 341.
- Audit: `results/news_policy_rebucket/autonomous_batch44_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch45_5

- Reviewed 5 legacy rows: {'keep': 1, 'defer': 4}.
- Current ledger: {'keep': 234, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 124, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 22, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 174, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 2, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 346.
- Audit: `results/news_policy_rebucket/autonomous_batch45_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-12 autonomous_batch46_5

- Reviewed 5 legacy rows: {'defer': 5}.
- Current ledger: {'keep': 234, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 129, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 22, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 169, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 2, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 351.
- Audit: `results/news_policy_rebucket/autonomous_batch46_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-13 autonomous_batch47_5

- Reviewed 5 legacy rows: {'defer': 5}.
- Current ledger: {'keep': 234, 'drop_earnings': 81, 'drop_peer_sympathy': 10, 'pending_news_review': 134, 'drop_mechanical': 1, 'drop_stale_news': 1, 'drop_macro_sector': 22, 'drop_analyst': 9, 'drop_financing': 8, 'drop_other_not_234': 164, 'drop_operating_update': 5, 'drop_regulatory_process': 4, 'drop_peer_earnings': 1, 'drop_passive_ownership': 2, 'drop_trial_anticipation': 2, 'drop_short_covering_media': 1, 'drop_etf': 2}. Cumulative expanded-policy reviews: 356.
- Audit: `results/news_policy_rebucket/autonomous_batch47_5.md` and `.json`; prior fields retained. Saved database snapshots and queues remain stale; timing, training and evaluation gates remain in place.

## 2026-11-13 autonomous_batch48_5

- Reviewed 5 legacy rows: 1 confirmed drop (RNA peer sympathy), 4 deferred (2 timing, 2 category/attribution).
- Ledger: 234 keep, 81 earnings drops, 11 peer-sympathy drops, 138 pending manual rows, 159 legacy drops awaiting reassessment; cumulative expanded-policy reviews: 361.
- RNA May 23, 2014 is directly attributed by contemporaneous coverage to sympathy with PTC’s European regulatory news. CBIO, TROX, GLF, and VJET remain pending for unresolved event timing or specific attribution.
- Audit: `results/news_policy_rebucket/autonomous_batch48_5.md` and `.json`; previous fields preserved. Database-derived snapshots and saved population queue remain stale; training and evaluation gates remain in place.


## 2026-11-13 autonomous_batch49_10 through autonomous_batch53_10

- Reviewed 50 legacy rows: 2 confirmed keeps, 13 confirmed exclusions, and 35 deferred for unresolved attribution, timing, or category.
- Ledger: 236 keep, 81 earnings drops, 12 peer-sympathy drops, 173 pending manual rows, and 109 legacy rows awaiting reassessment; cumulative expanded-policy reviews: 411.
- Confirmed exclusions cover broad sector moves, analyst actions, financing, peer sympathy, and spin-off price discovery. Two eligible catalysts were confirmed: a clinical-trial result and a commercial contract.
- Audits: `results/news_policy_rebucket/autonomous_batch49_10.md` through `autonomous_batch53_10.md` and matching JSON files. Prior labels and locators remain in `policy_review.previous`. Database-derived snapshots and the saved population queue remain stale; training and evaluation gates remain in place.

## 2026-11-13 autonomous_batch54_10 through autonomous_batch64_10

- Reviewed 109 legacy rows: 10 confirmed keeps, 10 confirmed exclusions, and 89 deferred for unresolved timing, attribution, or category.
- Current manual-ledger counts: 246 keep, 85 earnings drops, 13 peer-sympathy drops, 12 analyst drops, 262 pending; no legacy `drop_other_not_234` rows remain. Cumulative expanded-policy reviews: 520.
- Eligible catalysts include class-5 commercial news, class-11 strategic reviews, class-3 trial results, class-9 legal development, class-2 M&A rumor, class-7 device approval, and class-6 licensing. Supported exclusions include earnings, sector/peer sympathy, analyst action, financing, and operating updates.
- Audits: `results/news_policy_rebucket/autonomous_batch54_10.md` through `autonomous_batch64_10.md` and matching JSON files. Previous labels and locators remain in `policy_review.previous`.
- Legacy reassessment queue is empty. 262 rows remain pending in the 681-row manual ledger. Database-derived snapshots and saved population queue remain stale; first-public completeness and training/evaluation gates remain unverified.
