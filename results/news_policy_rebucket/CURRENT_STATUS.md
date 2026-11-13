# Current filtering checkpoint

Reviewed 2026-11-12. Latest continuation: 16 legacy rows reassessed — 5 keep, 5 drop, 6 deferred. Cumulative autonomous reviews: 131.

| Status | Rows |
| --- | ---: |
| keep | 211 |
| drop_earnings | 37 |
| drop_other_not_234 | 363 |
| pending_news_review | 36 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 8 |
| drop_analyst | 6 |
| drop_financing | 7 |
| drop_peer_sympathy | 3 |
| drop_operating_update | 3 |
| drop_regulatory_process | 2 |
| drop_peer_earnings | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 1 |

157 rows have expanded-policy review provenance. 363 legacy drops await reassessment; 36 rows in the manual ledger are pending. These counts cover 681 unique symbol/session rows.

Latest audits: `autonomous_batch11_10` and `autonomous_batch12_6` (Markdown and JSON). Prior labels and source locators are preserved in `policy_review.previous`.

Interpretive judgments: Terex merger of equals and Balchem/iCAD acquisitions qualify under class 2 and the acquirer exception. MoneyGram remains a takeover-rumor keep despite Western Union denial; no completed deal is asserted. BJRI board nominations qualify under class 11. Preliminary quarterly results take precedence in WGO. Historical SNOW is Intrawest, and its self-tender is capital return.

Unresolved evidence: RBA first-public session; MMYT financing versus operational partnership; KNDI planned deployment versus completed launch; MNTX original forward forecast; CZR proposed versus completed restructuring unlock; CARA uncertain analyst/short-cover attribution. BCPC sources disagree on announcement date; earliest-public timing is not certified.

The adjacent JSON queues cover only this manual ledger. They do not replace the saved population queue or establish completeness across the population. Database-derived snapshots and population queues remain stale. First-public completeness, training readiness, population metrics and trading gates remain unverified/blocked.

Validation: unique keys, prior-label/source preservation and production overlays checked for all 131 autonomous rows; earnings precedence retained. Existing unit suite: 74 tests pass.
