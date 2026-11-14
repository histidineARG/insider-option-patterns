import unittest
from datetime import date, timedelta

import numpy as np

from straddle_test import (
    choose_expiry, choose_strangle_leg, combo_return, crosses_earnings, dedupe_trades,
    hold_exit, iv_snapshot, leg_costs,
)


class StraddleTests(unittest.TestCase):
    def test_expiry_prefers_the_twenty_to_thirty_day_band(self):
        entry = date(2024, 6, 3)
        pairs = [(entry + timedelta(days=12), 12), (entry + timedelta(days=24), 24), (entry + timedelta(days=40), 40)]
        self.assertEqual(choose_expiry(pairs), entry + timedelta(days=24))

    def test_strangle_stays_out_of_the_money(self):
        calls = [
            dict(strike=90, delta=0.70),
            dict(strike=110, delta=0.25),
            dict(strike=130, delta=0.10),
        ]
        picked = choose_strangle_leg(calls, 100, 'call')
        self.assertEqual(picked['strike'], 110)

    def test_ask_bid_and_mid_slippage_are_both_reported(self):
        costs = leg_costs(0.90, 1.10)
        self.assertAlmostEqual(costs['ask'], 1.10)
        self.assertAlmostEqual(costs['mid_in'], 1.05)
        self.assertAlmostEqual(costs['mid_out'], 0.95)
        self.assertIsNone(leg_costs(1.2, 1.0))
        ret = combo_return(2.0, 1.0)
        self.assertAlmostEqual(ret, -0.5)

    def test_a_hold_that_reaches_earnings_is_flagged(self):
        sessions = [date(2024, 6, 3) + timedelta(days=i) for i in range(12)]
        index = {day: i for i, day in enumerate(sessions)}
        self.assertTrue(crosses_earnings(sessions[0], sessions[5], sessions, index, {sessions[4]}))
        self.assertFalse(crosses_earnings(sessions[0], sessions[5], sessions, index, {sessions[0]}))

    def test_ten_session_gap_drops_the_second_trade(self):
        sessions = [date(2024, 1, 1) + timedelta(days=i) for i in range(30)]
        index = {day: i for i, day in enumerate(sessions)}
        trades = [
            dict(symbol='AAA', entry=sessions[1], quote=0.1),
            dict(symbol='AAA', entry=sessions[5], quote=0.2),
            dict(symbol='AAA', entry=sessions[20], quote=0.3),
        ]
        kept = dedupe_trades(trades, index)
        self.assertEqual([row['entry'] for row in kept], [sessions[1], sessions[20]])

    def test_iv_baseline_does_not_include_the_entry_print(self):
        days = [date(2024, 1, 1) + timedelta(days=i) for i in range(50)]
        iv = np.full(50, 0.20)
        iv[-1] = 0.40
        entry, base, rank = iv_snapshot(days, iv, days[-1])
        self.assertEqual(entry, 0.40)
        self.assertAlmostEqual(base, 0.20)
        self.assertEqual(rank, 1.0)

    def test_expiry_exit_is_before_the_expiration(self):
        sessions = [date(2024, 6, 3) + timedelta(days=i) for i in range(40)]
        index = {day: i for i, day in enumerate(sessions)}
        expiry = sessions[30]
        exit_day = hold_exit(sessions[0], expiry, sessions, index, 'expiry')
        self.assertLessEqual(exit_day, expiry - timedelta(days=2))
        self.assertGreater(exit_day, sessions[0])


if __name__ == '__main__':
    unittest.main()
