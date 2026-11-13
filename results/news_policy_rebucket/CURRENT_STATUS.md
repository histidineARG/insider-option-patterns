# Current filtering checkpoint

Reviewed 2026-11-12. Ten continuation batches (28–37): 50 legacy rows reassessed — 2 keep, 21 drop, 27 deferred. Cumulative autonomous reviews: 280.

| Status | Rows |
| --- | ---: |
| keep | 227 |
| drop_earnings | 78 |
| drop_peer_sympathy | 10 |
| pending_news_review | 96 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 21 |
| drop_analyst | 9 |
| drop_financing | 8 |
| drop_other_not_234 | 214 |
| drop_operating_update | 5 |
| drop_regulatory_process | 4 |
| drop_peer_earnings | 1 |
| drop_passive_ownership | 2 |
| drop_trial_anticipation | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 2 |

306 rows have expanded-policy review provenance. 214 legacy drops await reassessment; 96 rows in the manual ledger are pending. Scope: 681 unique symbol/session rows.

Latest audits: autonomous_batch28_5 through autonomous_batch37_5, each in Markdown and JSON. Prior labels and locators are preserved in policy_review.previous.

New keeps: LSCC April 13, 2016 takeover speculation after Tsinghua stake disclosure (class 2 rumor, not an inferred definitive offer); LYV June 12, 2013 favorable CTS Eventim arbitration decision (class 9).

Final exclusion assignments: drop_analyst: 2, drop_earnings: 5, drop_macro_sector: 8, drop_operating_update: 1, drop_passive_ownership: 1, drop_peer_sympathy: 3, drop_regulatory_process: 1. Earnings precedence is retained.

Pending evidence: AERI positive clinical release also includes preliminary completed-year cash figures; PCOM and VUZI partnership candidates lack direct jump attribution; OMER concurrent legal/scientific announcements; CROX and CZR partnership-capital/strategic-transaction eligibility; GNE exploration discovery eligibility; TDW legal release predates jump; PRTA data wire was after close; NRP legacy locator covers other companies; ATHM, NOAH and AMRC results do not align with jump session; remaining deferrals document timing or attribution gaps. No unsupported blanket sector assignment or retrospective backdating certifies a keep.

These queues cover only the manual ledger. Database-derived snapshots and saved population queues remain stale. First-public completeness, training readiness, population metrics and trading gates remain unverified/blocked.

Validation: unique keys, baseline field preservation, audit agreement, queue hashes and production overlays for all 280 autonomous rows; earnings precedence retained. Existing unit suite: 74 tests pass.
