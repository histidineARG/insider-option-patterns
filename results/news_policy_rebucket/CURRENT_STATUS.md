# Current filtering checkpoint

Reviewed 2026-11-13. Ten continuation batches (38–47): 50 legacy rows reassessed — 7 keep, 4 drop, 39 deferred. Cumulative autonomous reviews: 330.

| Status | Rows |
| --- | ---: |
| keep | 234 |
| drop_earnings | 81 |
| drop_peer_sympathy | 10 |
| pending_news_review | 134 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 22 |
| drop_analyst | 9 |
| drop_financing | 8 |
| drop_other_not_234 | 164 |
| drop_operating_update | 5 |
| drop_regulatory_process | 4 |
| drop_peer_earnings | 1 |
| drop_passive_ownership | 2 |
| drop_trial_anticipation | 2 |
| drop_short_covering_media | 1 |
| drop_etf | 2 |

356 of 681 rows have expanded-policy review provenance. 164 legacy drops remain for reassessment, and 134 rows are pending in this manual ledger.

Audits: autonomous_batch38_5 through autonomous_batch47_5, each in Markdown and JSON. Prior labels and locators remain in policy_review.previous.

New keeps: ANGI reported strategic alternatives; MRC received buyout reports; GTN was acquired; ATHN disclosed an Ascension provider agreement; VNDA won a Fanapt patent injunction; ALNY reported positive patisiran Phase 2 data; and IONS reported positive Spinraza Phase 3 results.

Five exclusions: three same-session earnings releases, AGIO presentation-date anticipation, and CMC election-related steel-sector movement. Thirty-eight rows remain pending because catalyst timing, direct attribution, or policy category needs further evidence.

These queues cover only the 681-row manual ledger. Database-derived snapshots and the saved population news queue remain stale. First-public completeness, training readiness, population metrics, and trading gates remain unverified.

Validation: unique keys, baseline field preservation, audit agreement, queue hashes, and production overlays for all 330 autonomous rows; earnings precedence retained.
