# SEC case alignment: preliminary findings

Generated 2026-11-05. Descriptive case study; no trained model, control sample, or trading backtest.

25 case/event records processed; 24 have EOD observations before their event within the extracted trade interval.

## Important findings

- Virtusa: 250 market contracts in the three documented series on the alleged purchase day, matching the complaint total. The next-open announcement precludes capturing its announcement move with a signal based on the previous final EOD volume.
- EFII: 199 market contracts in the documented series over the purchase interval versus 187 alleged purchases. Its longer-dated calls are excluded by a 60-DTE screen. Exact-series ratios use contracts selected retrospectively from the complaint; they are diagnostic, not deployable predictions.
- Heinz: the peak OTM ratio is about 0.12 with a 60-DTE ceiling versus 16.02 across expirations. Expiry filters can reverse the conclusion.
- Kraft and Joy Global: aggregate volume does not show a large surge in the documented windows. Successful recovery of spectacular cases cannot establish general recall.
- Kaman has no local chain rows for 2024-01-08 inside the examined interval. Historical data gaps need a full audit.

## Comparison

Ratios compare each observed session with its prior 20 observed chain sessions. Short-dated = OTM calls with 1–60 calendar DTE; all-expiry = all unexpired OTM calls. Case-selected exact series include ITM contracts where documented. Missing sessions are reported, not filled with zero.

| Symbol | Event | Peak short-dated ratio | Peak all-expiry ratio | Documented series market volume | Alleged purchases |
|---|---|---:|---:|---:|---:|
| [HNZ](https://www.sec.gov/newsroom/press-releases/2013-219) | 2013-02-14 | 0.12 | 16.02 | — | — |
| [ONXX](https://www.sec.gov/newsroom/press-releases/2013-2013-123htm) | 2013-06-30 | 3.51 | 1.98 | — | — |
| [CNQR](https://www.sec.gov/files/litigation/complaints/2016/comp23571.pdf) | 2014-09-18 | 0.90 | 0.83 | — | — |
| [KRFT](https://www.sec.gov/file/34-83889pdf) | 2015-03-25 | 0.38 | 0.76 | 361.00 | 100.00 |
| [ADT](https://www.sec.gov/litigation/complaints/2016/comp23519.pdf) | 2016-02-16 | 12.83 | 6.94 | 4,095.00 | 2,279.00 |
| [JOY](https://www.sec.gov/files/litigation/admin/2020/34-89178.pdf) | 2016-07-21 | 0.47 | 0.42 | — | 50.00 |
| [INCY](https://www.sec.gov/files/litigation/complaints/2021/comp-pr2021-155.pdf) | 2016-08-22 | 5.56 | 3.36 | 724.00 | 578.00 |
| [SWC](https://www.sec.gov/files/litigation/complaints/2017/comp-pr2017-125.pdf) | 2016-12-09 | 9.35 | 5.86 | 5,590.00 | — |
| [CEB](https://www.sec.gov/files/litigation/complaints/2020/comp24982.pdf) | 2017-01-05 | 9.09 | 5.56 | — | 377.00 |
| [GNCMA](https://www.sec.gov/files/litigation/complaints/2017/comp-pr2017-80.pdf) | 2017-04-04 | 6.46 | 6.13 | 2,368.00 | 1,293.00 |
| [BIVV](https://www.sec.gov/litigation/complaints/2019/comp24500.pdf) | 2018-01-22 | 8.70 | 7.47 | 2,450.00 | 1,607.00 |
| [EFII](https://www.sec.gov/files/litigation/complaints/2019/comp-pr2019-149.pdf) | 2019-04-15 | 1.38 | 2.84 | 199.00 | 187.00 |
| [BOLD](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25660) | 2019-12-02 | 0.78 | 2.04 | — | — |
| [DKS](https://www.sec.gov/litigation/complaints/2020/comp24967.pdf) | 2019-11-26 | 35.70 | 28.47 | 1,526.00 | 132.00 |
| [TWLO](https://www.sec.gov/file/sec-complaint-2397) | 2020-05-06 | — | — | — | — |
| [VRTU](https://www.sec.gov/files/litigation/complaints/2022/comp25431.pdf) | 2020-09-10 | 266.67 | 121.21 | 250.00 | 250.00 |
| [ODP](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25788) | 2021-01-11 | 0.26 | 4.69 | — | — |
| [COHR](https://www.sec.gov/files/litigation/complaints/2022/comp-pr2022-129-bhardwaj.pdf) | 2021-01-19 | 24.26 | 11.96 | — | — |
| [GSKY](https://www.sec.gov/files/litigation/complaints/2021/comp-pr2021-230.pdf) | 2021-09-15 | 17.64 | 22.62 | 4,405.00 | 2,631.00 |
| [PFE](https://www.sec.gov/newsroom/press-releases/2023-123) | 2021-11-05 | 1.98 | 1.94 | — | — |
| [ZGNX](https://www.sec.gov/files/litigation/complaints/2024/comp25989.pdf) | 2022-01-19 | 1.76 | 1.70 | — | — |
| [LNTH](https://www.sec.gov/files/litigation/admin/2025/33-11362.pdf) | 2022-02-24 | 1.35 | 1.10 | — | 15.00 |
| [MAXR](https://www.sec.gov/files/litigation/admin/2025/34-102266.pdf) | 2022-12-16 | 3.65 | 5.34 | — | 2.00 |
| [KAMN](https://www.sec.gov/files/litigation/complaints/2025/comp26378.pdf) | 2024-01-19 | 33.90 | 16.56 | 711.00 | 618.00 |
| [CALT](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-26609) | 2024-05-28 | 12.38 | 6.05 | — | — |

## Interpretation and limits

Market volume belongs to all participants; agreement with a complaint does not reveal account identities. Alleged purchases may cover only a subset of defendants or series. Counts are not guaranteed to reconcile unless dates, contracts and source coverage are identical.

The ad hoc diagnostic (at least 100 short-dated OTM calls and 3x lagged volume, or a zero baseline) fires in 12 extracted windows. Only 9 have a subsequent trading-session close strictly before the event date. These counts are not a false-negative estimate, a profitability result or an executable opportunity count. The calendar is optiondb.tradingday and historical calendar completeness has not been independently audited.

The registry deliberately separates complaint allegations, administrative settlements, reported civil verdicts and investigations. Charnas/ODP is investigation-only in the cited source and is not an adjudicated positive. Legal status strings describe the reviewed source, not necessarily the latest disposition.

## Search coverage

The case inventory is **not exhaustive**. It contains 25 extracted case/event records plus 31 discovery records awaiting detailed review; multi-company and multi-event discovery records are not independent cases. Year-specific and named-case SEC searches were used. Local direct requests to the SEC enforcement archive returned HTTP 403. Search-engine recall is unknown; no denominator of all enforcement documents has been enumerated. The later successful EDGAR filing search concerns corporate M&A filings, not enforcement releases, and does not close this gap.

Case-linked exact-series features must not be used as supervised input without reconstructing an ex ante contract selection rule. No false-positive or false-negative rates, predictive probabilities, expected returns, or live-trading performance have been estimated.

## Files

- `data/sec_cases.json`: case evidence, dates, contract specifications and source locators.
- `data/sec_discovery_candidates.json`: pending and excluded records.
- `results/sec_alignment/daily_features.csv`: daily comparison series.
- `results/sec_alignment/case_matches.csv`: per-case summary and data gaps.
- `data/coverage_2026.json`: pre-backfill audit; `data/backfill_result_2026.json`: October 9 repair and remaining 14 missing dates.
