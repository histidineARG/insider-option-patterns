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
- Completed in this checkpoint: announcement-session or press-time findings recorded for every price-qualified candidate; earlier public information, conflicts, ADS terms, issuer-identity notes, and unresolved searches preserved in `data/event_review_overrides.json`. Offline review overlay refreshes saved events without requerying prices. `research_dataset.py` builds 2,080 distinct stock-days with ten-session outcomes, disclosure diagnostics, and purged partitions; known positives and certified negatives remain zero. `evaluation.py` constructs fixed-rule alert episodes and logistic interfaces but blocks population metrics. `trading_assumptions.py` freezes conservative fill rules and reports blocked trading gates. Corporate-action checklist evidence is recorded for all 26 events. `price_action_vet.py --deep` requeries OHLCV paths for all 26: every reaction is gap-dominated, 24/26 show ≥2× volume, and path diagnostics flag ITCI’s +14.9% previous-session move, CNQR’s +8.6% earlier-public day, ADT’s −15.7% pre-print and 26.40/26.87 source conflict, plus offer-premium comparisons where a single USD cash figure parses.
- Gap: zero events are training-ready. Reviewed cohort expanded to 45 priced events (26 prior + 19 confirmed M&A seeded as `additional_candidates`); corporate-action checklist is complete only for the prior set, and first-public-disclosure verification remains false for all 45. Several carry earlier-public contamination or source/ADS hazards that block clean attribution. No complete outcome registry certifies background negatives. Quote delivery timing and contract deliverables remain unverified. Reserved 2026 has no extracted observations and is not authorized.
- Next target: deepen first-disclosure searches for events with clean price-action status until a subset can set `first_public_disclosure_verified` without overclaiming; resolve or document contaminated jump windows (ONXX, RETA prior-close risk; MAXR same-day earlier report; CNQR/SAGE earlier episodes before the measured window) before treating those jumps as disclosure-aligned; begin scoped negative-outcome reviews only under `data/outcome_coverage_reviews.json`; keep evaluation gated.
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
- Reviewed cohort now 45 events. Expansion stubs all have deepened first-disclosure notes or earlier-public boundaries; corporate-action checklists remain incomplete for the expansion set. Clean `jump_ok` stands at 25; none yet `first_public_disclosure_verified`.
- Use EDGAR-with-symbol pre-proxy jump census as a discovery bound, not as training labels.
- Expand scoped outcome-coverage reviews only when a complete source-backed negative search protocol exists.
- Do not authorize population metrics, threshold selection, or trading simulation while gates remain blocked.
