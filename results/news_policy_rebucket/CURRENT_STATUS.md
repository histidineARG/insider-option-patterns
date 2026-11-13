# Current filtering checkpoint

Reviewed 2026-11-12. Latest continuation: 31 legacy rows reassessed — 5 keep, 16 drop, 10 deferred. Cumulative autonomous reviews: 172.

| Status | Rows |
| --- | ---: |
| keep | 217 |
| drop_earnings | 49 |
| drop_other_not_234 | 322 |
| pending_news_review | 50 |
| drop_mechanical | 1 |
| drop_stale_news | 1 |
| drop_macro_sector | 13 |
| drop_analyst | 6 |
| drop_financing | 8 |
| drop_peer_sympathy | 3 |
| drop_operating_update | 3 |
| drop_regulatory_process | 2 |
| drop_peer_earnings | 1 |
| drop_passive_ownership | 1 |
| drop_trial_anticipation | 1 |
| drop_short_covering_media | 1 |
| drop_etf | 2 |

198 rows have expanded-policy review provenance. 322 legacy drops await reassessment; 50 rows in the manual ledger are pending. These counts cover 681 unique symbol/session rows.

Latest audits: `autonomous_batch14_12`, `autonomous_batch15_12`, `autonomous_batch16_7` (Markdown and JSON). Prior labels and source locators are preserved in `policy_review.previous`.

Keeps: NXPI Freescale, FRX Aptalis and PBH Insight deals use the acquirer exception; ABMD Impella PMA is class 7; TRGP takeover rumor remains class 2 despite later talks termination. Twelve quarterly-results cases are class 1; bundled guidance does not supersede earnings precedence. FXF is excluded as an exchange-traded currency trust.

Pending evidence: ROLL and MATX acquisition price attribution/public timing; ASYS stale 2009 repurchase locator; KNDI earlier-week outlook comments; GOL ownership-cap rule category/session attribution; X preliminary trade-remedy eligibility; IDCC license/settlement price attribution; HTLD acquisition attribution; TLYS outlook publication time. GOL ADS ratio change was scheduled February 26 and is not automatically a March 2/3 mechanical cause.

The adjacent JSON queues cover only this manual ledger. They do not replace the saved population queue or establish completeness across the population. Database-derived snapshots and population queues remain stale. First-public completeness, training readiness, population metrics and trading gates remain unverified/blocked.

Validation: unique keys, prior-label/source preservation and production overlays checked for all 172 autonomous rows; earnings precedence retained. Existing unit suite: 74 tests pass.
