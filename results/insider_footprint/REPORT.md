# Call-footprint screen

Frozen rule, applied once. A day alerts when call volume is at least 100 and at least 3× that name's prior-20-session mean, at least 40% of that volume sits in calls with delta 0.10–0.35, 5–45 days to expiry and 3–25% out of the money, that share is at least 0.10 above the name's baseline median, and one strike-expiry holds at least half of the band when the band has 20 contracts. An event hits when any of the 10 pre-event sessions alerts. The jump session itself is excluded.

Tier A is the 86 class-2 M&A keeps. The placebo is the same name 60 trading sessions earlier. The earnings control is the nearest earnings reaction on that name at least 40 sessions away from every keep for the name. Tier B is the other 160 keeps. Vendor gamma is not a gate: stored gamma on this table is not on a per-dollar Black–Scholes scale.

The jump date is the reaction session used by the news ledger. It is a proxy for first public disclosure, and an earlier rumor still contaminates that window. A hit is a cheap concentrated call print. It is not an identification of a trader.

| Cohort | Hits / eligible |
| --- | ---: |
| Tier A, 10 sessions before the jump | 10 / 85 (11.8%) |
| Same names, 60 sessions earlier | 7 / 77 (9.1%) |
| Same names, separated earnings reaction | 12 / 78 (15.4%) |
| Tier B, 10 sessions before the jump | 11 / 158 (7.0%) |

Paired Tier A versus placebo, among events eligible on both: 77 pairs, 9 hit only on the event, 7 hit only on the placebo, 0 hit on both. Continuity-corrected McNemar chi-square 0.06, p 0.803.

Paired Tier A versus earnings: 78 pairs, 7 event only, 11 earnings only, 1 both. Chi-square 0.50, p 0.480.

Secondary description, not a second test. Median across eligible events of the largest single-day call-volume ratio and of the largest band share in the window:

| Cohort | Median max volume ratio | Median max band share |
| --- | ---: | ---: |
| Tier A | 3.04 | 0.39 |
| Placebo | 2.98 | 0.41 |
| Earnings | 3.79 | 0.40 |
| Tier B | 3.99 | 0.28 |

Tier A events that hit:

- WMS 2013-01-31: 2013-01-30
- LEAP 2013-07-15: 2013-07-11
- RAD 2015-10-27: 2015-10-16
- CTB 2013-06-12: 2013-06-03
- CYT 2015-07-29: 2015-07-17
- LIN 2014-03-21: 2014-03-18
- MEG 2015-09-28: 2015-09-23
- BRLI 2015-06-04: 2015-05-22
- LSCC 2016-11-03: 2016-11-01
- SIG 2014-02-19: 2014-02-12

Thresholds were not changed after seeing these counts. Population precision, training readiness, and trading results are not estimated.
