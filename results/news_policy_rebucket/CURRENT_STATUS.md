# Current filtering checkpoint

Reviewed 2026-11-12. Latest continuation: 30 legacy rows reassessed — 4 keep, 14 drop, 12 deferred. Earlier autonomous continuation: 85 rows; cumulative autonomous reviews: 115.

| Status | Rows |
| --- | ---: |
| keep | 206 |
| drop_earnings | 35 |
| drop_other_not_234 | 379 |
| pending_news_review | 30 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 8 |
| drop_analyst | 6 |
| drop_financing | 6 |
| drop_peer_sympathy | 3 |
| drop_regulatory_process | 2 |
| drop_operating_update | 1 |
| drop_peer_earnings | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 1 |

141 rows have expanded-policy review provenance. 379 legacy drops await reassessment; 30 rows in the manual ledger are pending. These counts cover 681 unique symbol/session rows.

Latest audits: `autonomous_batch08_16`, `autonomous_batch09_8`, `autonomous_batch10_6` (Markdown and JSON). Prior labels and source locators are preserved in `policy_review.previous`.

Interpretive judgments: OMER and EXAS government coverage/payment authorizations are treated as class 7 equivalent decisions, distinct from FDA product approval. SCTY forward deployment guidance is class 8 with concurrent historical operating metrics; EXPR takeover interest/special committee is class 11, not a completed acquisition.

Timing corrections: ORMP first-patient release was April 1, not April 13; EXPR outlook release was January 14 at 06:15 ET, before January 15 jump; PFSW source has January 13 internal and January 19 hosting dates, before January 21 jump. HRTX positive data were released September 22; September 23 reaction alignment remains pending. BTU split occurred before the October 6 filing date and is not automatically a same-day mechanical jump.

The adjacent JSON queues cover only this manual ledger. They do not replace the saved population queue or establish completeness across the population. Database-derived snapshots and population queues remain stale. First-public completeness, training readiness, population metrics and trading gates remain unverified/blocked.

Validation: unique keys, prior-label/source preservation and production overlays checked for all 115 autonomous rows; earnings precedence retained. Existing unit suite: 74 tests pass.
