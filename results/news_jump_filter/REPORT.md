# News jump-cause filter (contaminated / unverified-first-public set)

Method: for each ≥15% reaction, use contemporaneous news to classify catalyst as M&A rumor/news, biotech-trial success, or tech breakthrough; **ignore earnings**.

Reviewed **18** events. **18** kept as M&A-contaminated (earlier public M&A news or process). **0** dropped as non-M&A.

| Event | Jump cause | News filter | Earlier public upper |
| --- | --- | --- | --- |
| ONXX:2013-06-30 | ma_rumor | keep_ma_contaminated | 2013-06-28 |
| CNQR:2014-09-18 | ma_rumor | keep_ma_contaminated | 2014-09-03 |
| KRFT:2015-03-25 | ma_rumor | keep_ma_contaminated | 2015-03-24 |
| PCP:2015-08-10 | ma_rumor | keep_ma_contaminated | 2015-08-09 |
| ARG:2015-11-17 | ma_rumor | keep_ma_contaminated | 2015-11-17 |
| VAL:2016-03-20 | ma_news | keep_ma_contaminated | 2016-03-20 |
| VA:2016-04-04 | ma_rumor | keep_ma_contaminated | 2016-03-28 |
| BIVV:2018-01-22 | ma_rumor | keep_ma_contaminated | 2018-01-21 |
| AVXS:2018-04-09 | ma_news | keep_ma_contaminated | 2018-02-26 |
| VRTU:2020-09-10 | ma_news | keep_ma_contaminated | 2020-08-30 |
| COHR:2021-01-19 | ma_news | keep_ma_contaminated | 2021-01-18 |
| GSKY:2021-09-15 | ma_news | keep_ma_contaminated | 2020-08-10 |
| MAXR:2022-12-16 | ma_rumor | keep_ma_contaminated | 2022-12-16 |
| PRVB:2023-03-13 | ma_news | keep_ma_contaminated | 2022-10-04 |
| RETA:2023-07-28 | ma_rumor | keep_ma_contaminated | 2023-07-27 |
| IMGN:2023-11-30 | ma_news | keep_ma_contaminated | 2023-10-24 |
| ITCI:2025-01-13 | ma_rumor | keep_ma_contaminated | 2025-01-12 |
| SAGE:2025-06-16 | ma_news | keep_ma_contaminated | 2025-01-10 |

None of these jumps are attributed to earnings. All remain blocked for clean first-public / training labels because of earlier-public or process contamination, not wrong catalyst type.
