# Plan: pre-announcement call footprint

Written 2026-11-13 before the database run. The alert constants in `insider_footprint.py` are the frozen test. Thresholds are not revised after the counts come back.

## Question

A keep in the 246-row news ledger means the jump had an eligible same-session catalyst in classes 2–11. It does not mean an insider traded. The question this test can answer is narrower: before those jumps, do calls concentrate in the cheap convex contracts a trader with advance knowledge of an up-move would buy, more than they do on the same names at other times?

## Sample

| Tier | Events | Role |
| --- | ---: | --- |
| A. Class 2 M&A keeps | 86 | Primary case. The reaction session is the ledger jump date |
| Placebo | same 86 names, 60 trading sessions earlier | Same chain, away from the jump |
| Earnings | nearest earnings reaction on that name, at least 40 sessions from every keep | Public, scheduled catalyst |
| B. Classes 3–11 | 160 | Contrast. Many of these dates are scheduled |

The 262 pending rows stay unlabeled. The positive window is the 10 NYSE sessions before the jump. The jump session is excluded. A missing chain day is left missing. An event with fewer than 8 observed window sessions or fewer than 10 baseline sessions is ineligible, not a non-hit.

The jump date proxies the first public print. An earlier rumor still contaminates the window. That limitation stays attached to every hit.

## Contract an informed buyer would choose

`optiondaily` is the chain: about 3.37 billion rows, indexed by `(underlying, qdate, type, edate, strike)`. Each row has `volume`, `oi`, `bid`, `ask`, and stored `iv`, `delta`, `gamma`, `theta`, `vega`.

The buyer who wants the largest stock move per premium dollar buys calls, about 3–25% out of the money, delta about 0.10–0.35, with expiry 5–45 days out, in one or two strikes, in size relative to that name's own recent call volume. Stored gamma on this table is not on a per-dollar Black–Scholes scale, so this first test uses the delta and moneyness band and does not divide by gamma.

Open interest the next morning can confirm that a historical print was opening. It is not part of this alert, because it is not known at that close.

## Frozen alert

A pre-event session alerts when all of these hold:

- Call volume is at least 100 and at least 3× the mean call volume of the prior 20 observed chain sessions. A zero baseline uses the 100-contract floor.
- At least 40% of that call volume is in the band above.
- That share is at least 0.10 above the median band share on baseline days that traded at least 20 calls.
- When the band itself has at least 20 contracts, one strike and expiry holds at least half of it.

An event is a hit if any of the 10 pre-event sessions alerts.

## What the comparison means

The primary comparison is paired. Among Tier A events eligible on both sides, count hits that occur only before the jump, only on the placebo, and on both. Repeat the pairing against earnings. Tier B is reported beside them and is not used to move a threshold.

A higher Tier A hit rate than the placebo and the earnings dates means the footprint shows up before these M&A jumps and is not the same pattern as ordinary pre-earnings call buying. A similar rate on earnings means the screen is finding scheduled-event trading. Either result is the test. No second threshold is searched.

A hit is a concentrated print in cheap calls. It does not name an account, and it does not make the 246 rows training labels.

## Later, only after this screen stays frozen

Label the 262 pending rows before any of them enter the case set. A lower jump threshold is a separate, pre-registered sensitivity. A logistic with the volume ratio, the band share, strike concentration, and the call/put ratio is justified only if this screen separates Tier A from earnings on the earlier years, with the last year left untouched.
