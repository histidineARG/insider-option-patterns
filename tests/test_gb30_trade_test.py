import unittest

import numpy as np

from gb30_trade_test import equity_curve, exit_path, group_shapley, low_event


class Gb30TradeTests(unittest.TestCase):
    def test_same_day_stop_and_target_fills_the_stop(self):
        kind, price, _off = exit_path(
            np.array([100.0, 100.0]), np.array([140.0, 140.0]), np.array([80.0, 80.0]),
            np.array([110.0, 110.0]), np.zeros(2, dtype=bool),
            mode='bracket', hold=1, stop=0.10, target=0.30, trail=None)
        self.assertEqual(kind, 'stop')
        self.assertAlmostEqual(price, 90.0)

    def test_a_gap_through_the_stop_fills_at_the_open(self):
        kind, price, off = exit_path(
            np.array([100.0, 80.0]), np.array([101.0, 82.0]), np.array([99.0, 79.0]),
            np.array([100.0, 81.0]), np.zeros(2, dtype=bool),
            mode='bracket', hold=1, stop=0.10, target=0.30, trail=None)
        self.assertEqual(kind, 'stop')
        self.assertEqual(off, 1)
        self.assertAlmostEqual(price, 80.0)

    def test_a_gap_through_the_target_fills_at_the_open(self):
        kind, price, off = exit_path(
            np.array([100.0, 150.0]), np.array([101.0, 155.0]), np.array([99.0, 149.0]),
            np.array([100.0, 152.0]), np.zeros(2, dtype=bool),
            mode='target', hold=1, stop=None, target=0.30, trail=None)
        self.assertEqual(kind, 'target')
        self.assertEqual(off, 1)
        self.assertAlmostEqual(price, 150.0)

    def test_the_trail_uses_the_prior_close_and_not_the_entry_day(self):
        kind, price, off = exit_path(
            np.array([100.0, 100.0]), np.array([101.0, 101.0]), np.array([70.0, 96.0]),
            np.array([108.0, 100.0]), np.zeros(2, dtype=bool),
            mode='trail', hold=1, stop=None, target=None, trail=0.10)
        self.assertEqual(kind, 'stop')
        self.assertEqual(off, 1)
        self.assertAlmostEqual(price, 108.0 * 0.90)

    def test_a_plain_hold_is_the_later_close_minus_the_round_trip(self):
        kind, price, off = exit_path(
            np.array([100.0, 101.0, 102.0]), np.array([100.0, 101.0, 102.0]),
            np.array([100.0, 101.0, 102.0]), np.array([100.0, 110.0, 130.0]),
            np.zeros(3, dtype=bool), mode='hold', hold=2, stop=None, target=None, trail=None)
        self.assertEqual(kind, 'time')
        self.assertEqual(off, 2)
        self.assertAlmostEqual(price, 130.0)

    def test_earnings_inside_the_hold_drops_the_trade(self):
        earn = np.array([False, True])
        self.assertIsNone(exit_path(
            np.array([100.0, 100.0]), np.array([100.0, 100.0]), np.array([100.0, 100.0]),
            np.array([100.0, 100.0]), earn, mode='hold', hold=1, stop=None, target=None, trail=None))

    def test_the_downside_label_is_the_low_and_earnings_blank_it(self):
        close = np.full(8, 100.0)
        low = close.copy()
        low[3] = 60.0
        earn = np.zeros(8, dtype=bool)
        y = low_event(low, close, earn, horizon=5)
        self.assertEqual(y[0], 1.0)
        earn[3] = True
        y = low_event(low, close, earn, horizon=5)
        self.assertTrue(np.isnan(y[0]))

    def test_group_shapley_gives_the_only_live_group_the_whole_effect(self):
        def predict(x):
            return x[:, 0]

        x = np.array([[1.0, 0.0], [3.0, 0.0]])
        got = group_shapley(predict, x, np.zeros(2), {'a': [0], 'b': [1]}, np.random.RandomState(1), n=2)
        self.assertAlmostEqual(got['signed']['a'], 2.0)
        self.assertAlmostEqual(got['signed']['b'], 0.0)

    def test_equity_deploys_one_slot_and_charges_the_round_trip_at_the_exit(self):
        trades = [dict(symbol='AAA', entry=0, exit=2, entry_px=100.0, exit_px=110.0, score=1.0)]
        closes = {('AAA', 0): 100.0, ('AAA', 1): 100.0, ('AAA', 2): 110.0}
        curve = equity_curve(trades, lambda s, d: closes[(s, d)], [0, 1, 2], slots=4)
        self.assertAlmostEqual(curve[-1], 1.0 + 0.25 * 0.10 - 0.25 * 0.001)


if __name__ == '__main__':
    unittest.main()
