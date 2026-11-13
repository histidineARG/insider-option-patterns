# Current filtering checkpoint

Reviewed 2026-11-12. This run reassessed 50 legacy rows: 17 keep, 24 drop, 9 deferred. The ledger remains 681 unique symbol/session rows.

| Status | Rows |
| --- | ---: |
| keep | 198 |
| drop_earnings | 20 |
| drop_other_not_234 | 444 |
| drop_mechanical | 1 |
| pending_news_review | 10 |
| drop_macro_sector | 3 |
| drop_analyst | 2 |
| drop_financing | 2 |
| drop_etf | 1 |

76 rows have expanded-policy review provenance; 444 legacy drops await reassessment. Ten manual-ledger rows are pending (the prior SPWR deferral plus nine from this run).

The accompanying `legacy_reassessment_queue.json` and `pending_manual_ledger.json` cover only the manual ledger. They do not replace the saved 233-row population queue or certify that all population candidates are represented. Database-derived snapshots and population queues remain unchanged.

Batch audit files: `autonomous_batch01_15`, `autonomous_batch02_12`, `autonomous_batch03_15`, `autonomous_batch04_8` (Markdown and JSON). Prior fields and source locators are retained per row. Training readiness, population metrics and trading remain gated.

Review judgments: acquirer-side M&A is eligible only under the explicit methodology exception with attributed deal news. Standalone outlook updates are distinct from quarterly earnings/preliminary results. Mixed financing/partnership and concept demonstrations stay pending when the primary cause or commercialization evidence is unresolved.
