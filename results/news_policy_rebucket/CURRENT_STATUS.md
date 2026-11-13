# Current filtering checkpoint

Reviewed 2026-11-12. Latest continuation: 10 legacy rows reassessed — 1 keep, 5 drop, 4 deferred. Cumulative autonomous reviews: 141.

| Status | Rows |
| --- | ---: |
| keep | 212 |
| drop_earnings | 37 |
| drop_other_not_234 | 353 |
| pending_news_review | 40 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 10 |
| drop_analyst | 6 |
| drop_financing | 8 |
| drop_peer_sympathy | 3 |
| drop_operating_update | 3 |
| drop_regulatory_process | 2 |
| drop_peer_earnings | 1 |
| drop_passive_ownership | 1 |
| drop_trial_anticipation | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 1 |

167 rows have expanded-policy review provenance. 353 legacy drops await reassessment; 40 rows in the manual ledger are pending. These counts cover 681 unique symbol/session rows.

Latest audit: `autonomous_batch13_10` (Markdown and JSON). Prior labels and source locators are preserved in `policy_review.previous`.

Interpretive judgments: SCTY June 17 acquisition qualifies under the class 2 acquirer exception. AGIO planned presentation is anticipation rather than successful readout; VNDA reported 13G ownership increase alone does not establish activism. ESI is historical ITT Educational Services and its loan is financing. CVI and SM are classified under documented broad sector catalysts.

Timing/source corrections: VISN August 22 account describes news after August 19 jump/halt; agreement execution date is not public-release time. SCTY May 13 earnings were scheduled after the close. ARGS legacy June 13 filing is director news, not June 6 clinical data. LTRPA indirect exposure to TripAdvisor partnership remains pending issuer-attribution and category review.

The adjacent JSON queues cover only this manual ledger. They do not replace the saved population queue or establish completeness across the population. Database-derived snapshots and population queues remain stale. First-public completeness, training readiness, population metrics and trading gates remain unverified/blocked.

Validation: unique keys, prior-label/source preservation and production overlays checked for all 141 autonomous rows; earnings precedence retained. Existing unit suite: 74 tests pass.
