import unittest
from datetime import date, timedelta

import numpy as np

from direction_test import (
    SIGNS, adjust_closes, composite_scores, net_of_cost, symbol_panel, verdict, wilson,
)


class DirectionTests(unittest.TestCase):
    def test_a_four_for_one_split_does_not_become_a_loss(self):
        closes = np.array([100.0] * 10 + [25.0] * 5)
        adjusted, factors, breaks = adjust_closes(closes)
        self.assertAlmostEqual(factors[10], 0.25)
        self.assertAlmostEqual(adjusted[9], 25.0)
        self.assertFalse(breaks.any())
        self.assertAlmostEqual(adjusted[12] / adjusted[8] - 1.0, 0.0)

    def test_the_composite_penalises_the_last_month(self):
        calm = np.zeros((8, 11))
        hot = np.zeros((8, 11))
        hot[:, 1] = 0.2
        scores = composite_scores(np.vstack([calm, hot]))
        self.assertLess(scores[8:].mean(), scores[:8].mean())
        self.assertEqual(SIGNS['ret_21'], -1.0)
        self.assertEqual(SIGNS['mom_12_1'], 1.0)

    def test_a_future_close_does_not_change_today(self):
        rng = np.random.RandomState(0)
        closes = 80 * np.cumprod(1 + rng.normal(0.0003, 0.01, size=420))
        dates = [date(2016, 1, 4) + timedelta(days=i) for i in range(420)]
        volumes = np.full(420, 200_000.0)
        spy = {day: (100.0, 1.0) for day in dates}
        short = symbol_panel(dates[:360], closes[:360], volumes[:360], [], [], [], spy)
        long = symbol_panel(dates, closes, volumes, [], [], [], spy)
        self.assertIsNotNone(short)
        short_dates, short_x = short[0], short[1]
        long_dates, long_x = long[0], long[1]
        cutoff = dates[330].toordinal()
        short_map = {int(day): row for day, row in zip(short_dates, short_x) if int(day) <= cutoff}
        long_map = {int(day): row for day, row in zip(long_dates, long_x)}
        self.assertGreater(len(short_map), 10)
        for day, row in short_map.items():
            np.testing.assert_allclose(row, long_map[day], equal_nan=True)

    def test_cost_is_ten_basis_points(self):
        self.assertAlmostEqual(net_of_cost(np.array([0.02]))[0], 0.019)

    def test_the_verdict_requires_the_holdout_as_well(self):
        cells = [{
            'model': 'composite', 'horizon': 20, 'k': 10, 'holdout': False,
            'hit': 0.56, 'base': 0.51, 'ci': [0.53, 0.59],
            'by_year': [{'year': year, 'hit': 0.56, 'base': 0.51} for year in range(2016, 2026)],
        }, {
            'model': 'composite', 'horizon': 20, 'k': 10, 'holdout': True,
            'hit': 0.50, 'base': 0.52, 'ci': [0.45, 0.55], 'by_year': [],
        }]
        self.assertFalse(verdict(cells)['robust'])

    def test_wilson_interval_contains_the_rate(self):
        low, high = wilson(60, 100)
        self.assertLess(low, 0.60)
        self.assertGreater(high, 0.60)


if __name__ == '__main__':
    unittest.main()
