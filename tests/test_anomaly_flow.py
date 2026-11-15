import unittest

import numpy as np

from anomaly_flow import (
    N_BUCKET, adjust_closes, build_frame, delta_oi, lift_stats,
)


def _quiet_book(n=160, price=20.0, volume=200.0):
    adj = np.full(n, price)
    total = np.full(n, volume)
    chain = np.ones(n, dtype=bool)
    block = np.zeros(n, dtype=bool)
    reaction = np.zeros(n, dtype=bool)
    vol = np.ones((n, N_BUCKET))
    prem = np.ones((n, N_BUCKET))
    oi = np.cumsum(np.ones((n, N_BUCKET)), axis=0)
    dnot = np.ones((n, N_BUCKET))
    return adj, total, chain, block, reaction, vol, prem, oi, dnot


class AnomalyFlowTests(unittest.TestCase):
    def test_a_spike_on_the_scoring_day_stays_out_of_its_baseline(self):
        adj, total, chain, block, reaction, vol, prem, oi, dnot = _quiet_book()
        vol[-1] = 11
        frame = build_frame(adj, total, chain, block, reaction, vol, prem, oi, dnot)[0]
        row = frame['x'][frame['index'] == len(adj) - 1]
        self.assertEqual(len(row), 1)
        self.assertAlmostEqual(float(row[0, 0]), 11.0, places=4)

    def test_the_same_spike_does_enter_a_later_baseline(self):
        adj, total, chain, block, reaction, vol, prem, oi, dnot = _quiet_book()
        vol[-6] = 11
        frame = build_frame(adj, total, chain, block, reaction, vol, prem, oi, dnot)[0]
        row = frame['x'][frame['index'] == len(adj) - 1]
        # 1 of 50 baseline days is 11, the rest are 1, and the scoring day is 1.
        self.assertLess(float(row[0, 0]), 1.0)

    def test_an_earnings_session_is_not_scored(self):
        adj, total, chain, block, reaction, vol, prem, oi, dnot = _quiet_book()
        block[-1] = True
        frame = build_frame(adj, total, chain, block, reaction, vol, prem, oi, dnot)[0]
        self.assertTrue(np.all(frame['index'] != len(adj) - 1))

    def test_cheap_names_and_thin_option_volume_are_dropped(self):
        adj, total, chain, block, reaction, vol, prem, oi, dnot = _quiet_book(price=9.0)
        self.assertTrue(all(frame is None for frame in build_frame(
            adj, total, chain, block, reaction, vol, prem, oi, dnot)))
        adj, total, chain, block, reaction, vol, prem, oi, dnot = _quiet_book(volume=40.0)
        self.assertTrue(all(frame is None for frame in build_frame(
            adj, total, chain, block, reaction, vol, prem, oi, dnot)))

    def test_a_forward_earnings_print_is_not_counted_as_a_jump(self):
        adj, total, chain, block, reaction, vol, prem, oi, dnot = _quiet_book()
        adj[120:125] = 30
        adj[155:] = 30
        reaction[123] = True
        frame = build_frame(adj, total, chain, block, reaction, vol, prem, oi, dnot)[0]
        early = frame['y15'][frame['index'] == 119]
        later = frame['y15'][frame['index'] == 150]
        self.assertTrue(np.isnan(early[0, 1]))
        self.assertEqual(float(later[0, 1]), 1.0)

    def test_open_interest_change_does_not_read_tomorrow(self):
        oi = np.array([[1.0], [5.0], [40.0]])
        change = delta_oi(oi)
        self.assertEqual(change[1, 0], 4.0)
        self.assertEqual(change[0, 0], 0.0)

    def test_four_for_one_is_not_a_loss(self):
        adjusted, factors, _breaks = adjust_closes(np.array([80.0, 80.0, 20.0, 20.0]))
        self.assertAlmostEqual(factors[2], 0.25)
        self.assertAlmostEqual(adjusted[3] / adjusted[0] - 1.0, 0.0)

    def test_lift_is_one_when_the_flag_is_random_noise_free(self):
        jump = np.array([1.0, 0.0, 1.0, 0.0])
        stats = lift_stats(np.array([True, True, False, False]), jump)
        self.assertAlmostEqual(stats['lift'], 1.0)


if __name__ == '__main__':
    unittest.main()
