# Exchange-traded product universe

`etp_universe.json` is the snapshot `etp_exclusion.py` loads. Candidate universes, screens, and backtests drop these symbols and CIKs unless the script is run with `--include-etp`.

## What is included

A ticker is included when any of these hold:

- `optiondb.stock.industry` is `Exchange Traded Fund`
- `optiondb.stock.is_etf = 1` and the company name is `Barclays PLC` or `Credit Suisse AG` (bank-wrapper ETNs such as TVIX). The common stocks BCS and CS are not flagged.
- The company or security name matches an ETF/ETN token, the phrase "exchange traded", or a product sponsor pattern (ProShares, Direxion, iShares, SPDR, iPath, VelocityShares, and similar). `iPath` does not match UiPath. `ARK` does not match the letters inside another word.
- The ticker is in `optiondb.sectoretf`
- The ticker is in `data/event_review_overrides.json` under `etf_etn_denylist` (delisted products already identified, including VXZ)
- The NASDAQ Trader files `nasdaqlisted.txt` and `otherlisted.txt` mark `ETF` as `Y`, or the listed security name matches the name rule. Test issues are skipped.

A current NASDAQ flag is ignored when `stock` already describes that ticker as an operating company. That keeps a reused ticker, such as a former operating company, from being dropped for the years this database still stores it as that company.

A CIK from `cik2symbol` is stored only when every ticker on that CIK is already in the symbol set.

Closed-end funds stay in the universe unless one of the rules above identifies them. The ticker `ETF` is Aberdeen Emerging Markets Telecommunications Fund, a closed-end fund, and is not excluded by the ticker text alone.

`SPY` is in this set. Scripts that need SPY only as a market benchmark load that series on its own and do not pass it through the candidate filter.

## Refresh

From the repository root, with `OPTIONDB_PASSWORD` set and the local `optiondb` reachable:

```bash
python3 etp_exclusion.py --refresh
```

The command rereads optiondb and downloads the two NASDAQ Trader symbol directories. It rewrites this snapshot, including `version`, `sha256`, and the file-creation lines from NASDAQ. Commit the new JSON after checking that operating companies such as AAPL, PATH, and the closed-end ticker ETF are still absent, and that SPY, QQQ, VXZ, and JDST are present.

If the NASDAQ download fails, the snapshot still rebuilds from optiondb and the denylist. The `nasdaq.error` field records that.

This list is comprehensive relative to those sources on the refresh date. It is not a hand-checked list of every product ever listed. A delisted ETP that is missing from `stock`, `sectoretf`, the denylist, and the current NASDAQ files can remain in a universe until the denylist or `stock` row is updated and the snapshot is refreshed.

## Census

```bash
python3 etp_exclusion.py --census
```

That writes `results/etp_exclusion/CENSUS.md` with symbol counts. It does not refit the chain scans.

## Rerun

These commands apply the default exclusion. The chain scans were not rerun in the change that added the filter.

```bash
python3 background_sample.py --start-year 2013 --end-year 2025 --dates-per-year 5 --symbols-per-date 20 --seed 1984
python3 quiet_screen.py
python3 quiet_otm_screen.py
python3 quiet_otm_pnl_stress.py
python3 walkforward_score.py
python3 anomaly_flow.py
python3 straddle_test.py
python3 bracket_test.py
python3 jump30_test.py
python3 gb30_trade_test.py
python3 direction_test.py
```

`walkforward_score.py` ignores a checkpoint that was built with exchange-traded products included. `--include-etp` keeps the old version 2 checkpoint behavior.

The saved background sample (`dates_per_year=5`, `symbols_per_date=20`, seed 1984) has 1300 stock-days, 208 of them products. It was not redrawn here because that rerun queries an option chain for every sampled name.
