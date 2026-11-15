"""Offline checks for the shared ETF/ETN/ETP filter and its call sites."""
import unittest
from pathlib import Path

from detector import screen_symbols
from etp_exclusion import (
    load_universe,
    name_is_exchange_product,
    partition_rows,
    partition_symbols,
)
from insider_model import samples_from_records

ROOT = Path(__file__).resolve().parents[1]

MUST_EXCLUDE = (
    'SPY', 'QQQ', 'IWM', 'DIA', 'EEM', 'GLD', 'SLV', 'USO', 'TLT', 'HYG',
    'VXZ', 'JDST', 'TQQQ', 'SQQQ', 'UVXY', 'VXX', 'SOXL', 'LABU', 'SPXU',
    'BITO', 'ARKK', 'XLF', 'IBIT', 'TVIX', 'XIV',
)
MUST_KEEP = ('AAPL', 'MSFT', 'NVDA', 'JPM', 'PATH', 'AET', 'ETF', 'GLAD', 'NFLX', 'C', 'BCS', 'CS')

WIRED = (
    'detector.py',
    'walkforward_score.py',
    'anomaly_flow.py',
    'quiet_screen.py',
    'quiet_otm_screen.py',
    'quiet_otm_pnl_stress.py',
    'straddle_test.py',
    'bracket_test.py',
    'jump30_test.py',
    'gb30_trade_test.py',
    'insider_footprint.py',
    'insider_model.py',
    'insider_accumulation.py',
    'insider_resolved.py',
    'research_dataset.py',
    'evaluation.py',
    'exploratory_patterns.py',
    'background_sample.py',
    'research_cohort.py',
    'ma_broad_screen.py',
    'ma_news_pool.py',
    'ma_candidate_screen.py',
    'ma_signal_model.py',
    'ma_holdout_score.py',
    'ma_news_pattern.py',
    'price_jump_examine.py',
    'edgar_deal_table.py',
)


class NameRuleTests(unittest.TestCase):
    def test_tokens_do_not_match_inside_ordinary_names(self):
        self.assertFalse(name_is_exchange_product('Aetna Inc.'))
        self.assertFalse(name_is_exchange_product('UiPath, Inc. Class A Common Stock'))
        self.assertFalse(name_is_exchange_product('CatchMark Timber Trust, Inc.'))
        self.assertFalse(name_is_exchange_product('Netflix, Inc.'))
        self.assertFalse(name_is_exchange_product('Aberdeen Emerging Markets Telecommunications Fund, Inc.'))
        self.assertFalse(name_is_exchange_product('Invesco Value Municipal Income Trust'))

    def test_product_names_match(self):
        self.assertTrue(name_is_exchange_product('SPDR S&P 500'))
        self.assertTrue(name_is_exchange_product('Invesco QQQ Trust'))
        self.assertTrue(name_is_exchange_product('iPath Series B S&P 500 VIX Short-Term Futures ETN'))
        self.assertTrue(name_is_exchange_product('Direxion Daily Jr Gld Mnrs Bear 3X ETF'))
        self.assertTrue(name_is_exchange_product('ProShares Ultra Bloomberg Natural Gas'))
        self.assertTrue(name_is_exchange_product('2x Long VIX Futures ETF'))


class UniverseTests(unittest.TestCase):
    def test_snapshot_covers_known_products_and_spares_operating_companies(self):
        universe = load_universe()
        self.assertGreater(len(universe.symbols), 1000)
        self.assertTrue(universe.version)
        missing = [symbol for symbol in MUST_EXCLUDE if not universe.is_symbol(symbol)]
        present = [symbol for symbol in MUST_KEEP if universe.is_symbol(symbol)]
        self.assertEqual(missing, [])
        self.assertEqual(present, [])

    def test_partition_drops_products_unless_opted_out(self):
        kept, stats = partition_symbols(['AAPL', 'SPY', 'VXZ', 'JDST', 'AET', 'PATH', 'ETF'])
        self.assertEqual(kept, ['AAPL', 'AET', 'PATH', 'ETF'])
        self.assertEqual(stats['removed'], 3)
        self.assertTrue(stats['excluded'])
        kept_all, opted = partition_symbols(['SPY', 'AAPL'], include_etp=True)
        self.assertEqual(kept_all, ['SPY', 'AAPL'])
        self.assertEqual(opted['removed'], 0)
        self.assertFalse(opted['excluded'])

    def test_cik_match_excludes_an_unknown_ticker(self):
        universe = load_universe()
        cik = next(iter(universe.ciks))
        self.assertTrue(universe.is_etp('NOTREAL', cik))
        rows, stats = partition_rows(
            [dict(symbol='NOTREAL', cik=cik), dict(symbol='AAPL', cik='0000320193')],
            cik_key='cik',
        )
        self.assertEqual([row['symbol'] for row in rows], ['AAPL'])
        self.assertEqual(stats['removed'], 1)

    def test_detector_and_logistic_samples_use_the_filter(self):
        kept, stats = screen_symbols(['msft', 'SPY'])
        self.assertEqual(kept, ['msft'])
        self.assertEqual(stats['removed'], 1)
        kept_on, _stats = screen_symbols(['SPY'], include_etp=True)
        self.assertEqual(kept_on, ['SPY'])
        samples = samples_from_records([
            dict(symbol='SPY', tier='A', qdate='2014-06-02', features={'log_volume_ratio': 1}),
            dict(symbol='AAA', tier='B', qdate='2014-06-02'),
        ])
        self.assertEqual(samples, [])

    def test_benchmark_spy_query_stays_outside_the_candidate_list(self):
        text = (ROOT / 'gb30_trade_test.py').read_text()
        direction = (ROOT / 'direction_test.py').read_text() if (ROOT / 'direction_test.py').exists() else ''
        self.assertIn("symbols + ['SPY']", text)
        self.assertLess(text.index('read_symbol_file'), text.index("symbols + ['SPY']"))
        self.assertIn("symbol='SPY'", direction or (ROOT / 'ma_holdout_score.py').read_text())

    def test_entry_points_import_the_filter(self):
        for name in WIRED:
            text = (ROOT / name).read_text()
            self.assertIn('etp_exclusion', text, name)


if __name__ == '__main__':
    unittest.main()
