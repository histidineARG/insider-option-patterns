import unittest

from ma_candidate_screen import detect_start, is_candidate, rank_against


class CandidateRuleTests(unittest.TestCase):
    def test_quiet_history_does_not_extend_the_window(self):
        closes = {i: 100.0 for i in range(0, 120)}
        volumes = {i: 1000.0 for i in range(0, 120)}
        market = {i: 100.0 for i in range(0, 120)}
        offset, extended = detect_start(closes, volumes, market, 110)
        self.assertEqual(offset, -10)
        self.assertFalse(extended)

    def test_two_shocks_and_extra_drift_extend_the_window(self):
        closes = {i: 100.0 for i in range(0, 121)}
        volumes = {i: 1000.0 for i in range(0, 121)}
        market = {i: 100.0 for i in range(0, 121)}
        # Event is 110, so t=-30 is 80 and t=-10 is 100. Two shocks sit inside that gap.
        closes[82] = 120.0
        closes[83] = 145.0
        for i in range(84, 101):
            closes[i] = 145.0
        closes[110] = 180.0
        volumes[82] = 5000
        volumes[83] = 5000
        offset, extended = detect_start(closes, volumes, market, 110)
        self.assertTrue(extended)
        self.assertLess(offset, -10)

    def test_candidate_needs_a_high_earnings_rank(self):
        percentile, zed = rank_against(100, [10, 20, 30, 40])
        self.assertGreaterEqual(percentile, 0.75)
        self.assertEqual(
            is_candidate([dict(percentile=percentile, z=zed), dict(percentile=None, z=None)]),
            'statistical-candidate',
        )
        self.assertEqual(
            is_candidate([dict(percentile=0.25, z=-0.5)]),
            'baseline-consistent',
        )


if __name__ == '__main__':
    unittest.main()
