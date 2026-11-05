# Public-company M&A discovery inventory

Retrieved November 5, 2026. Scope is U.S.-listed/SEC-filing target candidates;
this is not restricted to U.S.-incorporated companies, and public operating-company
eligibility still needs review.

## Official SEC filing search, 2013–2026

`sec_filing_search/merger_filings_2013_2026.csv` contains **9,465 distinct filing
documents**, expanded into **9,504 issuer-document rows** covering **3,899 CIKs**.
The query uses four root-form families: PREM14A, DEFM14A, DEFM14C and SC 14D9.
SEC search also returned SC 14D9/A amendments under that root family.

| Filing year | Documents retrieved |
|---|---:|
| 2013 | 705 |
| 2014 | 776 |
| 2015 | 812 |
| 2016 | 836 |
| 2017 | 753 |
| 2018 | 723 |
| 2019 | 566 |
| 2020 | 559 |
| 2021 | 724 |
| 2022 | 662 |
| 2023 | 596 |
| 2024 | 602 |
| 2025 | 630 |
| 2026 through November 5 | 521 |

Every year's retrieved count reconciles to the SEC search's exact reported total.
The 103 original response pages, query URLs, totals and output SHA256 are retained
in `sec_filing_search/`. This is a reconciled enumeration of **returned documents
for these form families**, not a census of all M&A deals. Multiple filings and
amendments can concern one deal. Multiple deals can concern one issuer.

Filing dates are not announcement dates. Candidates may include funds, SPACs,
foreign issuers, and transactions outside the intended target universe. Failed
approaches with no subsequent merger proxy/tender response are missing. Broader
coverage requires 8-K/6-K, S-4/F-4, SC TO-T and SC 13E3 records and public news.
The raw records preserve document links for subsequent review; dates and public
target status are explicitly unverified, and outcomes are unknown.

Run `python3 edgar_ma_search.py` from the repository root to reproduce the search.
Official endpoint: https://efts.sec.gov/LATEST/search-index

## Supplemental open dataset

The original 4,156-row SEC-derived dataset is preserved, with revision and SHA256
in `provenance.json`. Of these, 3,271 have earliest merger-filing proxies since
2013; 2,798 carry the provider's review flag. Local undated CIK-symbol mappings
found nearby option rows for 834 candidate records. This is coverage near filing
proxies, not verified option coverage before true deal announcements.

The provider collapses records to one earliest filing per CIK. This can miss
subsequent transactions; even filtering earliest dates at 2013 can remove issuers
with later in-scope deals. This dataset ends in 2024, while the official search
above extends through 2026. Do not add these counts together or assume the two
inventories are independent.

Credit: Tyler Contorno, *EDGAR M&A Deal Events (2010–2024)*, 2026.
Source and MIT license: https://huggingface.co/datasets/tcontorno/edgar-ma-deals

## Existing local records

- `local_maevent_all.csv`: all 446 original maevent rows. Only 62 are dated since
  2013, of which 61 have symbols; 54 have nearby options data. Most rows have no
  announcement date. Preserve existing retrospective z-scores for provenance,
  but never use them as point-in-time predictors or select deals by those scores.
- `local_mafromnews_since_2013.csv`: 779 news-link records, mainly 2015–2017.
  A news date may concern rumor, shareholder approval, or closing rather than
  first announcement. They are discovery leads, not validated events.
- The local takeover table contains 101,535 noisy news records, not 101,535 deals;
  it was inspected but not treated as an event universe.

## Reviewed examples and labeling

`reviewed_event_examples.json` records six manually reviewed examples, with source
links and separate definitive-announcement, earlier-public-discussion and outcome
dates where established. Examples include four terminated combinations: Halliburton/
Baker Hughes, Pfizer/Allergan, JetBlue/Spirit and Kroger/Albertsons. LinkedIn/Microsoft
has a verified completion source. The AFOP/Corning closing source says completion
is expected later that day, so the record is not promoted to confirmed completed.

Earlier public information is essential: the definitive agreement can follow
public takeover discussions or competing bids by weeks or months. None of these
examples is marked ready for training until the first-public-information timestamp
and historical security identity are reviewed. Failed M&A is an outcome category;
it is not automatically a negative label for pre-announcement informed trading.

Next event-level fields: permanent issuer/security IDs, target/acquirer role,
first rumor/public report timestamp, definitive announcement timestamp, bidder,
offer terms and revisions, final status, terminal announcement timestamp, source
locator, and matched historical option identifiers. No chronology or deal status
should be inferred solely from a filing-form name.
