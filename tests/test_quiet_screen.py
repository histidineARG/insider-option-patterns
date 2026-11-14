import unittest

from quiet_screen import classify_volume, quiet_stock, rank_score, tradable


class QuietScreenTests(unittest.TestCase):
    def test_one_spike_day_is_not_a_multi_day_build(self):
        # One day at 10x, the other four at zero. Cumulative is 10x a day, 2x a normal five-day total.
        loud = classify_volume([0, 0, 0, 0, 1000], 100)
        self.assertTrue(loud['single'])
        self.assertFalse(loud['multi'])
        self.assertEqual(loud['spike_days'], 1)
        self.assertEqual(loud['consecutive'], 1)

    def test_two_elevated_days_are_a_multi_day_build(self):
        loud = classify_volume([0, 0, 400, 400, 100], 100)
        self.assertTrue(loud['multi'])
        self.assertFalse(loud['single'])
        self.assertEqual(loud['spike_days'], 2)
        self.assertEqual(loud['consecutive'], 2)

    def test_cumulative_build_needs_more_than_one_active_day(self):
        # 3000 on one day is 6x a normal five-day total, but it is still one day.
        loud = classify_volume([0, 0, 0, 0, 3000], 100)
        self.assertTrue(loud['single'])
        self.assertFalse(loud['multi'])
        # The same total spread over two days is a build.
        spread = classify_volume([0, 0, 0, 1500, 1500], 100)
        self.assertTrue(spread['multi'])

    def test_quiet_and_tradable_gates(self):
        self.assertTrue(tradable(8, 6_000_000))
        self.assertFalse(tradable(4, 6_000_000))
        self.assertFalse(tradable(8, 1_000_000))
        self.assertTrue(quiet_stock(0.02, 0.01, 100, 80, 0.05))
        self.assertFalse(quiet_stock(0.08, 0.01, 100, 80, 0.05))
        self.assertFalse(quiet_stock(0.02, 0.04, 100, 80, 0.05))
        self.assertFalse(quiet_stock(0.02, 0.01, 200, 80, 0.05))

    def test_rank_requires_the_otm_share(self):
        self.assertIsNone(rank_score(8, 0.2))
        self.assertAlmostEqual(rank_score(8, 0.5), 4)


if __name__ == '__main__':
    unittest.main()
