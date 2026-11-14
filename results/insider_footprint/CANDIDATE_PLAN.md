# News-first M&A candidate plan

Adopted 2026-11-13. A row in the output is a statistical candidate for review. It is not evidence that anyone traded on inside information.

## What this machine can do

Prices and end-of-day option chains run from 2013-01-02 through 2026-11-12. Deal headlines run through 2022-07-25 (`takeover` stops 2021-08-21). There is no intraday headline clock, so a date is the announcement session. There is no PERMNO or FIGI map. Market adjustment uses SPY, not a sector index. Earnings dates run through 2022-01-04.

The 86 class-2 names stay the 2013–2016 one-day review. They are not the pool.

## Admission

A headline is one event. Same symbol within 7 days is collapsed. It is admitted only when all of these hold:

1. The row came from a deal headline, `maevent`, `research_ma_events`, or the class-2 ledger, not from a jump screen.
2. The announcement close is at least 15% above the close ten sessions earlier.
3. The name has an option chain on a session at least 20 sessions before the start of the price path.
4. No session in the path has a one-day move of +100% or −50%, which we treat as a split or a bad print.

## Where the path starts

Abnormal return is the stock’s close-to-close return minus its own beta times SPY. Beta and volatility use the 60 sessions before t = −30. The start stays at t = −10 unless, somewhere from t = −30 through t = −11, the cumulative move from that date through the announcement exceeds the ten-session move by 5 percentage points, and at least two of those earlier sessions are both a +2 standard-deviation abnormal return and at least 1.5 times the stock’s own median volume. A slow drift without those shocks does not extend the window.

## Options

Monthly means the Saturday after the third Friday before February 2015, and the third Friday after that. Any other Friday is a weekly. Volume and open interest are summed only inside one expiry. An expiry day is not a sale. The series is the nearest monthly, and the nearest weekly if one is listed, that expires after the announcement. Activity is measured from the path start through the session before the announcement.

The benchmark is that stock’s own prior earnings windows of the same length, up to eight. A statistical candidate is one whose peak call volume or open-interest build on the deal series ranks at or above the 75th percentile of its own earnings windows, or at least 2 standard deviations above them, with at least three earnings windows. Otherwise it is baseline-consistent. Missing earnings history is reported separately.
