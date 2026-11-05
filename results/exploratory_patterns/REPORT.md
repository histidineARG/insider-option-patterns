# Exploratory option-volume rules

These fixed rules are descriptive diagnostics, not fitted models, selected thresholds, or a backtest. No observations have been assigned reliable negative labels. Event and background samples have different selection and coverage; their counts cannot establish precision, false-positive rates, false-negative rates, or profitability.

Calls are OTM with 1–60 days to expiry. Each rule requires minimum aggregate volume and a multiple of the preceding 20 calendar sessions. A genuine zero baseline qualifies if current volume meets the minimum. Missing or invalid baseline data produces no evaluable observation, rather than a negative result.

Event counts use the last 10 pre-announcement sessions and require the next-session close proxy to precede the announcement date. They are not adjusted for earlier public rumors or real vendor delivery times. Background counts refer to individual sampled stock-days, not alert episodes.

| Minimum volume | Prior-volume multiple | Events with alert / events with usable data | Background observations with alert / usable observations |
| ---: | ---: | ---: | ---: |
| 100 | 3 | 10 / 23 | 3 / 57 |
| 500 | 5 | 8 / 23 | 1 / 57 |
| 1000 | 10 | 4 / 23 | 1 / 57 |

Do not choose a winning threshold from this table. Next steps are primary-source first-disclosure review, event-universe expansion, historical security classification and coverage repair, followed by chronological training/validation/test construction. An event without an alert in this diagnostic is not yet a validated false negative.
