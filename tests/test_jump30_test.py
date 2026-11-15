import unittest

import numpy as np

from jump30_test import distribution, forward_labels, net_hold


class Jump30Tests(unittest.TestCase):
    def test_a_high_of_thirty_percent_is_an_event_even_if_the_close_is_not(self):
        close = np.array([100.0, 110.0, 105.0, 100.0, 100.0, 100.0])
        high = np.array([100.0, 140.0, 106.0, 101.0, 100.0, 100.0])
        earn = np.zeros(6, dtype=bool)
        labels = forward_labels(high, close, earn, horizons=(5,))
        self.assertEqual(labels[5]['high'][0], 1.0)
        self.assertEqual(labels[5]['close'][0], 0.0)

    def test_earnings_inside_the_window_blanks_the_event(self):
        close = np.full(8, 100.0)
        high = close.copy()
        high[3] = 150.0
        earn = np.zeros(8, dtype=bool)
        earn[3] = True
        labels = forward_labels(high, close, earn, horizons=(5,))
        self.assertTrue(np.isnan(labels[5]['high'][0]))

    def test_the_hold_is_the_close_over_the_next_open_minus_costs(self):
        ret = net_hold(100.0, 130.0)
        self.assertAlmostEqual(ret, 0.30 - 0.001)
        stats = distribution(np.array([0.40, -0.25, 0.05, -0.30]))
        self.assertEqual(stats['up30'], 0.25)
        self.assertEqual(stats['down20'], 0.5)


if __name__ == '__main__':
    unittest.main()
