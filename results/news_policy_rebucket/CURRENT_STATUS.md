# Current filtering checkpoint

Reviewed 2026-11-12. This run reassessed 85 legacy rows: 21 keep, 47 drop, 17 deferred. The ledger remains 681 unique symbol/session rows.

| Status | Rows |
| --- | ---: |
| keep | 202 |
| drop_earnings | 32 |
| drop_other_not_234 | 409 |
| drop_mechanical | 1 |
| pending_news_review | 18 |
| drop_macro_sector | 6 |
| drop_analyst | 4 |
| drop_financing | 3 |
| drop_peer_sympathy | 2 |
| drop_regulatory_process | 1 |
| drop_peer_earnings | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 1 |

111 rows have expanded-policy review provenance; 409 legacy drops await reassessment. Eighteen manual-ledger rows are pending (the prior SPWR deferral plus seventeen from this run).

The accompanying `legacy_reassessment_queue.json` and `pending_manual_ledger.json` cover only the manual ledger. They do not replace the saved 233-row population queue or certify that all population candidates are represented. Database-derived snapshots and population queues remain unchanged.

Batch audit files: `autonomous_batch01_15`, `autonomous_batch02_12`, `autonomous_batch03_15`, `autonomous_batch04_8`, `autonomous_batch05_10`, `autonomous_batch06_10`, `autonomous_batch07_15` (Markdown and JSON). Prior fields and source locators are retained per row. Training readiness, population metrics and trading remain gated.

Review judgments: acquirer-side M&A is eligible only under the explicit methodology exception with attributed deal news. Standalone outlook updates are distinct from quarterly earnings/preliminary results. Mixed financing/partnership and concept demonstrations stay pending when the primary cause or commercialization evidence is unresolved.

Validation: all 85 new rows have unique keys, preserved prior labels and source locators; the production overlay reproduces their categories and decisions, and earnings precedence holds. The 74 existing unit tests pass.
