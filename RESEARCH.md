# Research mandate: informed options activity and executable returns

Status: research design and initial source/coverage checks, 2026-11-05.
No model has been fitted or validated. Existing detector.py is a baseline only;
its arbitrary defaults are not established trading rules.

## Two testable hypotheses

H1: Public EOD chain features observable at decision time distinguish documented
pre-event informed activity from comparable market observations.
H2: A rule using those features earns positive out-of-sample net returns when
entered after signal availability, with explicit loss, liquidity and capacity limits.
H1 does not imply H2. Legal culpability cannot be inferred from market data.

## Initial evidence

Index queries against optiondaily verified these coverage endpoints (not continuity):
- TUMI: 2013-01-02 to 2016-08-19.
- AFOP: 2013-09-23 to 2016-06-17.
- LNKD: 2013-01-02 to 2017-01-10.

Sources to retain with source URL, access date, quoted page/paragraph references,
case ID, issuer identifier, trade interval, announcement timestamp, instrument,
strike, expiry, quantity where disclosed, procedural status and status-as-of date:

- ADT / John Afriyie: SEC complaint alleges purchases Jan 28–Feb 12, 2016;
  acquisition announcement Feb 16 before open. Calls at strikes 32, 33, 34.
  Complaint is an allegation source, not a conviction record.
  https://www.sec.gov/litigation/complaints/2016/comp23519.pdf
- INCY / Matthew Panuwat: SEC reports April 5, 2024 civil liability verdict;
  short-term OTM calls in a peer of acquisition target Medivation.
  https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25970
- Audentes / Mahmoud Abdelkader: SEC settlement announcement alleges OTM call
  purchases Oct 17–18, 2019 ahead of Dec 2 announcement. Settlement proposed
  in this source; do not equate with conviction or assume latest disposition.
  https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25660
- AFOP / Peter Chang: SEC charges concern company shares, not verified OTM calls.
  https://www.sec.gov/enforcement-litigation/litigation-releases/lr-23937
- Acacia / Bechtolsheim: underlying complaint describes short puts. Useful
  instrument taxonomy control; not a long-call training example.
  https://www.sec.gov/files/litigation/complaints/2024/comp26014.pdf
- TUMI and LNKD remain user-nominated studies, not verified options enforcement
  positives. TUMI proxy describes public rumors around the transaction:
  https://www.sec.gov/Archives/edgar/data/1535031/000119312516590453/d166077dprer14a.htm
  LNKD announcement was June 13, 2016 before open:
  https://www.sec.gov/Archives/edgar/data/1271024/000104746916014430/a2229104zdefm14a.htm

## Labels and sampling

Build an evidence-reviewed case registry, keeping allegations, settlements,
civil verdicts and criminal convictions separate. Each legal outcome needs its
own dated source. De-duplicate defendants trading the same event; otherwise one
scheme becomes several apparently independent successes. Include unsuccessful,
small and late trades when disclosed, rather than selecting spectacular profits.

Use three separate outcomes:
1. Documented case-linked activity, for pattern-recovery diagnostics.
2. Future public event/jump within fixed 5/10/20 trading-session horizons.
3. Net executable return of a precommitted option-selection/exit policy.

Non-case observations are unlabeled, not proven legal trading. Report recall on
covered documented cases, and event/return precision on the full eligible universe.
Do not claim a population insider-trading FPR or FNR: undiscovered activity and
selective enforcement make those unidentifiable from SEC labels alone.

Sample controls using contemporary size/liquidity/sector/volatility and earnings
proximity, with time-only information. Train using weighted sampling if necessary;
measure final precision and alert rates at natural prevalence. Include all M&A
announcements with option coverage, not just enforcement-linked successes.

## Data audit before modeling

Verify EOD vendor timestamps, delivery latency, corrections and quote semantics.
Audit chain completeness by date/symbol, duplicated contracts, underlying prices,
negative/zero/stale/crossed quotes, Greek missingness, stock splits and adjusted
contract multipliers, ticker reuse, delistings and cash settlements.
Map permanent issuer IDs. Today's stock master is not a historical universe.
Determine whether OI dated t reflects t-1 or t positions and when it was released.
Do not use next-session OI to explain a signal traded before its publication.
Record data cutoff and immutable extract hashes; current historical corrections
may make a retrospective study different from a true point-in-time test.

## Features and model sequence

Compute contract, expiry/moneyness-bucket and underlying-day features:
- Volume relative to lagged 20/60-session distributions and robust percentiles.
- Symbol-specific and matched-peer surprises; absolute dollar/contract scale.
- Volume relative to available OI; persistence and change in chain participation.
- Strike/expiry concentration, top-contract share and concentration changes.
- Delta/moneyness/DTE exposure and call/put imbalance across matched buckets.
- IV/skew/term-structure changes and quote spread/liquidity measures.
- Price/volume behavior in underlying, public rumors, earnings proximity and market regime.

No hard OTM-only gate initially: compare OTM-only with a broader call universe.
EOD volume cannot identify buyer/seller initiation, opening trades, accounts or
insiders. Closing midpoint times volume is a proxy, not actual money spent.
Separate contract persistence from bucket persistence as price and DTE evolve.

Compare simple volume ratio, robust anomaly score, regularized logistic model,
and gradient boosting in that order. Prefer interpretable incremental evidence;
add complexity only for consistent out-of-sample improvement. Calibrate on
validation data at real prevalence. A case-classification probability is not a
probability of profit or legal misconduct.

## Execution and portfolio specification

Signal timestamp = actual data availability, not simply exchange close.
With EOD-only history, primary executable proxy is next-session close ask entry,
then later-session bid exit. This is delayed and still assumes displayed quotes
are executable; disclose it. Next-open execution requires historical open/intraday
quotes. Never use signal-day closing prices for a signal requiring that day's final volume.

Prespecify expiry/delta selection and holding rules using only entry information;
compare fixed 5/10/20-session exits and expiry, without hindsight-best exits.
No missing quotes treated as free fills. Model spreads, commissions, contract
multiplier, volume participation, premium limits and unavailable exits; report
coverage and conservative loss bounds for unresolved outcomes. Delistings need
actual OCC terms. Do not fabricate exercise proceeds from incomplete chains.

Measure signals announced before entry separately: detected but not monetizable
through the announcement. Track timing attrition from every detected case to
eligible contract, valid entry, valid exit and realized P&L.

Cap premium at risk per name and portfolio; account for overlapping holdings,
sector/event concentration and all premium losses. A high hit rate is not the
objective; expected net payoff, drawdown and capacity are.

## Validation and decision gates

User-nominated examples are development cases and cannot be independent tests.
Use expanding chronological train/validation/test folds, purging overlapping
feature/label windows and grouping issuer/event/tipping network. Treat group
isolation and temporal isolation explicitly; report any necessary exclusions.
Freeze the last chronological holdout before looking at its returns. Recent data
has incomplete enforcement labels, so do not treat no recent case as a negative.
Retrospective future-discovered cases can diagnose patterns; a simulated live
classifier must train only on labels actually available at its training cutoff.

Report PR-AUC, precision/recall at fixed alert budgets, case/event recall,
alerts per 1,000 eligible symbol-days and distinct weekly opportunities.
ROC-AUC is secondary for rare events. Report entry-eligible recall separately.
For returns: net expectancy, median trade, win/loss sizes, total premium at risk,
portfolio return with explicit cash assumptions, drawdown, turnover and capacity.
Use event/time-block confidence intervals and leave-one-big-winner-out sensitivity.
Compare matched random entries, simple volume signals, underlying-stock trades
and earnings-aware rules. Record all tried variants and account for selection.

Advance only if performance survives conservative fills, natural prevalence,
multiple time periods, clustered uncertainty and removal of dominant winners.
Acceptable alert budget, drawdown and capital requirements must be set before
choosing a final operating threshold; they are not currently user-specified.

## Next deliverables

1. Evidence-reviewed registry and source archive; audit report on coverage and latency.
2. Contract-level replication of documented trade intervals with daily feature timelines.
3. Point-in-time universe features and matched control/event datasets.
4. Frozen experiment manifest, temporal model comparisons and execution-aware backtest.
5. Prospective paper-trading log before any live deployment.
