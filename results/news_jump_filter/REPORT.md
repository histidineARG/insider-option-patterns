# News jump-cause filter

Policy: **keep 2–11; drop 1**. Canonical taxonomy: [METHODOLOGY.md](../../METHODOLOGY.md) §9.

| # | Class | Action |
| --- | --- | --- |
| 1 | Earnings report | **drop** |
| 2 | M&A rumor / news (`ma_rumor`, `ma_news`) | **keep** |
| 3 | Biotech clinical-trial success (`biotech_trial`) | **keep** |
| 4 | Tech breakthrough (`tech_breakthrough`) | **keep** |
| 5 | Commercial contract / award / order (`commercial_contract`) | **keep** |
| 6 | Partnership / license (`partnership_license`) | **keep** |
| 7 | Regulatory approval / clearance (`regulatory_approval`) | **keep** |
| 8 | Guidance / outlook step-up (`guidance_stepup`) | **keep** |
| 9 | Legal / regulatory unlock (`legal_unlock`) | **keep** |
| 10 | Product launch / commercialization (`product_launch`) | **keep** |
| 11 | Activist / strategic alternatives (`activist_alt`) | **keep** |

Hard drops (not numbered keep classes): sub-$5 prior close, ETF/ETN denylist, no option chain, mechanical prints, dilutive financing as primary cause, peer-sympathy, analyst-only, unexplained.

Reviewed cohort **45** events under this filter: **45** keep, **0** drop_earnings.
Cause counts: {'2_ma': 45}. Cohort members remain class-2 only; classes 3–11 are reserved keeps when found. Prior `drop_other_not_234` reviews are re-bucket candidates and were not re-labeled in this policy update.

Contamination (earlier-public / prior-process) does not change keep-vs-drop under this rule; it only blocks clean first-public / training labels.

| Event | Class | Jump cause | News filter | First public |
| --- | --- | --- | --- | --- |
| HNZ:2013-02-14 | 2_ma | ma_news | keep | True |
| SFD:2013-05-29 | 2_ma | ma_news | keep | True |
| ONXX:2013-06-30 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| XRTX:2013-12-23 | 2_ma | ma_news | keep | True |
| BEAM:2014-01-13 | 2_ma | ma_news | keep | True |
| ZLC:2014-02-19 | 2_ma | ma_news | keep | True |
| SUSS:2014-04-28 | 2_ma | ma_news | keep | True |
| CNQR:2014-09-18 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| FMI:2015-01-12 | 2_ma | ma_news | keep | True |
| KRFT:2015-03-25 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| POZN:2015-06-08 | 2_ma | ma_news | keep | True |
| PCP:2015-08-10 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| KLAC:2015-10-21 | 2_ma | ma_news | keep | True |
| ARG:2015-11-17 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| AFFX:2016-01-08 | 2_ma | ma_news | keep | True |
| ALR:2016-02-01 | 2_ma | ma_news | keep | True |
| CSCD:2016-02-04 | 2_ma | ma_news | keep | True |
| LF:2016-02-05 | 2_ma | ma_news | keep | True |
| ADT:2016-02-16 | 2_ma | ma_news | keep | True |
| CKP:2016-03-02 | 2_ma | ma_news | keep | True |
| VAL:2016-03-20 | 2_ma | ma_news | keep_ma_contaminated | False |
| RKUS:2016-04-04 | 2_ma | ma_news | keep | True |
| VA:2016-04-04 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| AFOP:2016-04-07 | 2_ma | ma_news | keep | True |
| LNKD:2016-06-13 | 2_ma | ma_news | keep | True |
| JOY:2016-07-21 | 2_ma | ma_news | keep | True |
| SWC:2016-12-09 | 2_ma | ma_news | keep | True |
| CEB:2017-01-05 | 2_ma | ma_news | keep | True |
| GNCMA:2017-04-04 | 2_ma | ma_news | keep | True |
| BIVV:2018-01-22 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| AVXS:2018-04-09 | 2_ma | ma_news | keep_ma_contaminated | False |
| EFII:2019-04-15 | 2_ma | ma_news | keep | True |
| BOLD:2019-12-02 | 2_ma | ma_news | keep | True |
| VRTU:2020-09-10 | 2_ma | ma_news | keep_ma_contaminated | False |
| COHR:2021-01-19 | 2_ma | ma_news | keep_ma_contaminated | False |
| GSKY:2021-09-15 | 2_ma | ma_news | keep_ma_contaminated | False |
| ZGNX:2022-01-19 | 2_ma | ma_news | keep | True |
| MAXR:2022-12-16 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| PRVB:2023-03-13 | 2_ma | ma_news | keep_ma_contaminated | False |
| RETA:2023-07-28 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| IMGN:2023-11-30 | 2_ma | ma_news | keep_ma_contaminated | False |
| KAMN:2024-01-19 | 2_ma | ma_news | keep | True |
| CALT:2024-05-28 | 2_ma | ma_news | keep | True |
| ITCI:2025-01-13 | 2_ma | ma_rumor | keep_ma_contaminated | False |
| SAGE:2025-06-16 | 2_ma | ma_news | keep_ma_contaminated | False |

Classes 3–11 keepers in this reviewed cohort: 0 (cohort still M&A-sourced). Policy reserves them as keep when jump-examine / news review finds them.
