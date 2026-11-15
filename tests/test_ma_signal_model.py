from datetime import date
import unittest

from ma_signal_model import FEATURES, OPTION_FEATURES, design, fold_of, overlaps_earnings, window_features


class SignalModelSplitTests(unittest.TestCase):
    def test_holdout_starts_on_2024_11_13(self):
        self.assertEqual(fold_of(date(2024, 11, 12)), 'later')
        self.assertEqual(fold_of(date(2024, 11, 13)), 'holdout')
        self.assertEqual(fold_of(date(2019, 12, 31)), 'train')
        self.assertEqual(fold_of(date(2020, 1, 2)), 'val')

    def test_earnings_inside_the_window_is_excluded(self):
        days = [date(2020, 1, 2), date(2020, 1, 3)]
        self.assertTrue(overlaps_earnings(days, [date(2020, 1, 3)]))
        self.assertFalse(overlaps_earnings(days, [date(2020, 2, 1)]))

    def test_stock_return_stops_at_the_last_session_in_the_window(self):
        expiry = date(2020, 2, 21)
        days = [date(2020, 1, 2), date(2020, 1, 3)]
        rows = {
            days[0]: {expiry: dict(call_vol=10, put_vol=1, otm_call_vol=4, call_oi=5)},
            days[1]: {expiry: dict(call_vol=12, put_vol=2, otm_call_vol=6, call_oi=20)},
        }
        features = window_features(rows, expiry, days, {days[0]: 10.0, days[1]: 11.0})
        self.assertAlmostEqual(features['pre_return'], 0.1)
        self.assertEqual(features['log_oi_build'] > 0, True)

    def test_option_check_does_not_include_the_stock_return(self):
        self.assertNotIn('pre_return', OPTION_FEATURES)
        samples = [{name: float(i) for name in FEATURES} for i in range(1, 4)]
        scaled, _, _ = design(samples, OPTION_FEATURES)
        self.assertEqual(len(scaled[0]), len(OPTION_FEATURES) + 1)


if __name__ == '__main__':
    unittest.main()
