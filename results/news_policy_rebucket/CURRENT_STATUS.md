# Current filtering checkpoint

Reviewed 2026-11-12. Ten continuation batches (18–27): 50 legacy rows reassessed — 7 keep, 25 drop, 18 deferred. Cumulative autonomous reviews: 230.

| Status | Rows |
| --- | ---: |
| keep | 225 |
| drop_earnings | 73 |
| drop_peer_sympathy | 7 |
| pending_news_review | 69 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 13 |
| drop_analyst | 7 |
| drop_financing | 8 |
| drop_other_not_234 | 264 |
| drop_operating_update | 4 |
| drop_regulatory_process | 3 |
| drop_peer_earnings | 1 |
| drop_passive_ownership | 1 |
| drop_trial_anticipation | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 2 |

256 rows have expanded-policy review provenance. 264 legacy drops await reassessment; 69 rows in the manual ledger are pending. Scope: 681 unique symbol/session rows.

Latest audits: autonomous_batch18_5 through autonomous_batch27_5, each in Markdown and JSON. Prior labels and locators are preserved in policy_review.previous.

New keeps: WMB Access Midstream acquisition, SIG Zale acquisition, NUS regulatory resolution, LSCC Canyon Bridge acquisition, COTY reported P&G auction win, ACRX Grunenthal license and DLNG material long-term customer charters. Acquisition acquirer exceptions and rumor status are recorded in the individual audits.

Eighteen new earnings exclusions include preliminary completed-quarter results and bundled guidance. Other exclusions cover subscriber operating update, regulatory-process anticipation, peer sympathy and analyst initiation. Eighteen uncertain cases remain pending for publication timing, direct price attribution or category evidence; earlier or later announcements are not backdated to the jump session.

These queues cover only the manual ledger. Database-derived snapshots and saved population queues remain stale. First-public completeness, training readiness, population metrics and trading gates remain unverified/blocked.

Validation: unique keys, prior-field preservation, source pointers and production overlays for all 230 autonomous rows; earnings precedence retained. Existing unit suite: 74 tests pass.
