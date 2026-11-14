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

## Model

The binary screen is applied once and left as recorded in `REPORT.md`. The logistic does not search a new alert threshold. It asks whether the same session's continuous features rank a class-2 window above that name's placebo and earnings windows out of sample.

Features, taken from the one pre-event session with the largest call-volume ratio:

- log of the call-volume ratio versus the prior 20 sessions
- share of that call volume in the delta 0.10–0.35, 5–45 day, 3–25% out-of-the-money band
- share of the band in its busiest strike and expiry
- calls divided by calls plus puts
- log of band volume per contract of band open interest

Ridge penalty is 1 on features standardized with the 2013–2014 mean and spread. The intercept is unpenalized. 2015 is reported and does not change the fit. 2016 is the holdout. A one-feature volume-ratio model is the comparison.

A class-2 jump is not an insider-trading label. Earnings, scheduled catalysts, and ordinary speculation produce the same kind of price jump with no informed option trade. The logistic therefore cannot treat a miss as a missed insider. It can only show whether a footprint is common. A pattern that is present in a minority of events would leave the median paired score gap near zero and move the upper tail.

Label the 262 pending rows before any of them enter the case set. A lower jump threshold is a separate sensitivity and is not part of this fit.
