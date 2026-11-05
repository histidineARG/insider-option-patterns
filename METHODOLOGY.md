# M&A option-pattern research protocol

Agreed research direction: 2026-11-05. This is a study design, not a validated
model or a claim of predictive performance. It complements [RESEARCH.md](RESEARCH.md).

## Objective

Identify option activity observable before a public acquisition announcement
that distinguishes qualifying events from background observations. Separately
test whether alerts generate executable net option returns. Market patterns
cannot establish insider identity or illegal trading.

The sequence is: verified M&A events → public targets with announcement price
jumps of at least 15% → historical option availability and coverage → pre-event
pattern discovery → chronological evaluation across the optionable universe →
trading simulation.

## 1. Event cohort

Retain all discovered M&A events in the registry independently of price action.
For this study, select verified acquisition announcements since 2013 involving
publicly traded targets. Require at least a 15% close-to-close target share-price
increase from the session before the announcement reaction session to that
session's close. Map after-close and nontrading-day announcements to the next
trading session; flag uncertain timestamps rather than choosing the best return.

Record first public rumors, public bids, definitive agreements, completion, and
termination separately. Identify whether a signal predates the first relevant
public disclosure or follows an already public rumor. Retain announced deals
that later fail; completion is a separate attribute. Review splits, ticker changes,
issuer identity, and other corporate actions before accepting price reactions.
Do not require a volume surge for cohort membership; retain it as a measurement.

The price threshold defines the historical outcome, never a predictor available
before the event. Do not select cases by whichever nearby date has the largest jump.

## 2. Option availability and data coverage

Determine whether options were listed before the event, whether historical chain
data is present, and whether quotes were usable. Distinguish no listed options,
missing source data, insufficient history, and inadequate tradability. Report
these exclusions and their counts explicitly; missing observations are not
automatic model failures. Define eligibility using information available on each
historical signal date, including liquidity rules fixed before final testing.

## 3. Pattern discovery

Initially examine 30 trading sessions before each event, comparing observations
with earlier company history and comparable stocks. Candidate features include:

- Call volume relative to historical volume and open interest.
- Concentration across strikes and expirations.
- OTM distance and days to expiration.
- Call/put activity and changes in open interest.
- Repeated bursts across sessions.
- Implied volatility, quoted spreads, stock volume, and stock-price changes.

Use only data available at decision time, including realistic vendor delivery and
open-interest publication timing. Separate genuine zero activity from absent
chains. EOD aggregates cannot reliably identify buyers, sellers, opening trades,
or coordinated accounts. SEC cases supply evidence-backed examples, with legal
status preserved; other M&A events are not automatically insider-trading labels.

## 4. Background population

Include ordinary stock-days, earnings, other public news, large non-M&A moves,
and unusual option activity without a qualifying subsequent event. Matched
controls by liquidity, size, volatility, and calendar period can help discovery.
Final validation must preserve natural event prevalence and the historical
optionable universe, including subsequently delisted companies where covered.
Artificially balanced test data cannot establish operational alert precision.

## 5. Initial prediction target and decision timing

Initial target: using information available after today's close, predict a
qualifying acquisition announcement within the next 10 trading sessions, with
an opportunity to enter before public disclosure. Ten sessions is a starting
hypothesis, not an established optimum. Fix exact session boundaries before
constructing labels and avoid repeated optimization against the final test.

An after-close signal cannot capture an announcement before the next market
open. Track such cases separately as lacking an executable entry. Select
contracts, estimate costs, and apply exits without using future event knowledge.
Non-M&A alerts can be negative for this prediction target and profitable trades;
correct event predictions can still lose money through expiry or expensive entry.

## 6. Chronological validation

Use earlier years for discovery and training, subsequent years for validation
and threshold selection, and the newest sufficiently complete years for an
untouched final test. Choose exact dates after auditing coverage. Keep overlapping
windows from the same event together and purge boundary observations whose
feature or outcome windows overlap protected test information. Fit preprocessing,
feature selection, and any resampling using training data only.

Start with an interpretable statistical score and a simple logistic model.
Compare both on identical eligible observations and chronological splits.
Report sensitivity to choices such as prediction horizon, liquidity, and the
15% outcome threshold without selecting the final test's best configuration.

## 7. Evaluation and threshold choice

Report observation-level metrics and distinct alert episodes separately. Fix
alert deduplication and cooldown rules on training/validation data. Count a
qualifying event once when measuring event recall, even if it generated many
alerts. Report uncertainty, preferably accounting for clustering by event,
issuer, and time, and avoid treating overlapping daily observations as independent.

| Measure | Meaning |
| --- | --- |
| Event recall | Fraction of eligible events receiving a timely alert |
| Event false-negative rate | Fraction of eligible events missed |
| Alert precision | Fraction of distinct alert episodes preceding a qualifying event |
| Observation false-positive rate | Fraction of eligible background observations triggering alerts |
| Alert burden | New alert episodes per day/week and simultaneous positions |
| Lead time | Time between an executable alert and first relevant public disclosure |
| Net trading performance | Returns, losses, drawdown, and capital usage after realistic costs |

A small false-positive rate can still yield poor precision for rare events.
For illustration, among 100,000 observations with 100 positives, 60% recall and
a 1% false-positive rate yield 60 true alerts and about 999 false alerts: roughly
6% precision. Observation-level recall in this example is distinct from event recall.

Do not promise an acceptable error rate in advance. Select thresholds on
validation data using alert burden, recall, precision, and net trading economics;
freeze them before final testing and report the entire tradeoff.

## 8. Trading evaluation and deliverables

Specify signal availability, next feasible entry, option selection, position
sizing, holding period, exit, spreads, fees, expiry losses, and capital limits.
Where EOD data cannot support an executable quote assumption, report that
limitation and conservative cost sensitivity rather than assuming midpoint fills.
Compare against simple baselines and report concentration in a few large winners.

Deliver an auditable event/coverage funnel, time-safe feature and label tables,
chronological model comparisons, precision/recall and alert-burden tradeoffs,
and a separate cost-aware trading simulation. The immediate question is whether
pre-announcement option activity adds predictive value at a manageable alert rate;
profitability is a separate empirical result.

## References

- [Time-series validation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit)
- [Data leakage and evaluating natural class prevalence](https://github.com/scikit-learn-contrib/imbalanced-learn/blob/master/doc/common_pitfalls.rst)
