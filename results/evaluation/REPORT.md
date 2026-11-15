# Gated chronological evaluation

Fixed-rule episode construction and logistic interfaces are implemented against the time-safe observation table. Population accuracy, precision, false-positive rates, and trading returns remain unauthorized while evidence gates fail.

ETP exclusion removed 0 observations and 0 events from this table. The research dataset applies the same filter when it is rebuilt, so a second pass here removes only names still present in the saved file.

## Blocked gates

- verified_outcome_labels
- historical_security_identity
- complete_population_frame
- natural_prevalence_or_valid_sampling_design
- vendor_delivery_timing
- passed_coverage_audit

## Fixed-rule episode diagnostics

| Rule | Eligible observations | Alert observations | Alert episodes | Labeled observations |
| --- | ---: | ---: | ---: | ---: |
| volume_100_ratio_3 | 2242 | 161 | 106 | 8 |
| volume_500_ratio_5 | 2242 | 74 | 58 | 8 |
| volume_1000_ratio_10 | 2242 | 29 | 25 | 8 |

Logistic status: blocked_by_evidence_gates. Reserved test authorization: False. Event-level recall remains null until training-ready events exist.

No threshold is selected from these diagnostics. Bootstrap clustered uncertainty and validation threshold selection stay deferred until labels and population membership pass audit.
