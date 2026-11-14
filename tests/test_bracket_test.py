import unittest
from datetime import date, timedelta

import numpy as np

from bracket_test import BREAKEVEN_TARGET, dedupe, net_return, theoretical_b, walk_bracket


class BracketTests(unittest.TestCase):
    def test_a_same_day_stop_and_target_fills_the_stop(self):
        kind, price, _day = walk_bracket(
            np.array([100.0]), np.array([130.0]), np.array([94.0]), np.array([110.0]),
            100.0, 0.05, 0.20, 1, None)
        self.assertEqual(kind, 'stop')
        self.assertAlmostEqual(price, 95.0)

    def test_a_gap_through_the_stop_fills_at_the_open(self):
        kind, price, _day = walk_bracket(
            np.array([100.0, 90.0]), np.array([101.0, 92.0]), np.array([99.0, 89.0]), np.array([100.0, 91.0]),
            100.0, 0.05, 0.20, 2, None, gap_on_first=False)
        self.assertEqual(kind, 'stop')
        self.assertAlmostEqual(price, 90.0)
        self.assertAlmostEqual(net_return(100.0, price, kind), 90.0 / 100.0 - 1.0 - 0.002)

    def test_the_five_percent_stop_needs_a_target_above_28_percent(self):
        self.assertAlmostEqual(theoretical_b(BREAKEVEN_TARGET, 0.05), 0.85 / 0.15)
        self.assertLess(theoretical_b(0.25, 0.05), 0.85 / 0.15)

    def test_a_second_signal_inside_twenty_sessions_is_dropped(self):
        sessions = [date(2024, 1, 1) + timedelta(days=i) for i in range(40)]
        index = {day: i for i, day in enumerate(sessions)}
        entries = np.array([sessions[1].toordinal(), sessions[10].toordinal(), sessions[30].toordinal()])
        keep = dedupe(entries, np.array([1, 1, 1]), index)
        self.assertEqual(keep.tolist(), [True, False, True])


if __name__ == '__main__':
    unittest.main()
