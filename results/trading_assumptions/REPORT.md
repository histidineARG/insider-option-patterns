# Conservative trading assumptions

Trading simulation remains blocked. The assumptions below are frozen for later use and do not invent fills, returns, or executable historical quotes.

## Assumptions

- **Signal availability:** Feature session close plus vendor delivery. Actual historical vendor delay is unverified, so no observation is marked execution-ready.
- **Entry:** Earliest considered entry is the next exchange-session close strictly before the earliest verified disclosure bound. This is a timing proxy, not a fill.
- **Option selection:** Candidate contracts must satisfy the fixed research quote screen recorded in the reviewed-cohort manifest. Multipliers, deliverables, and adjusted contracts remain unverified; midpoint fills are not assumed.
- **Cost model:** When usable bid/ask quotes exist, buy at ask and sell at bid. Absent a usable quote, the trade is non-executable rather than filled at last trade or midpoint.
- **Holding period:** Hold until the earlier of the verified disclosure reaction session or the close of the tenth subsequent exchange session after the feature date. No intraday exit is claimed.
- **Position sizing:** Unit notional per episode for diagnostics only. Capital limits and simultaneous position caps are unspecified until population evaluation is authorized.

## Explicit exclusions

- No fill when vendor delivery timing is unverified.
- No fill when quote eligibility or contract multiplier is unverified.
- No fill when disclosure chronology remains unresolved.
- No short premium strategies in this protocol version.

## Blocked gates

- population_evaluation_unauthorized
- no_research_eligible_observations
- no_verified_executable_positives
- vendor_delivery_timing_unverified
- contract_deliverables_unverified

No net trading performance is reported from this artifact.
