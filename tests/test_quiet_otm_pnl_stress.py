import unittest
from datetime import date, timedelta

from quiet_otm_pnl_stress import dedupe_trades, trimmed


class PnlStressTests(unittest.TestCase):
    def test_a_second_signal_while_the_hold_is_open_is_dropped(self):
        sessions = [date(2024, 1, 1) + timedelta(days=i) for i in range(40)]
        index = {day: i for i, day in enumerate(sessions)}
        trades = [
            dict(symbol='AAA', entry='2024-01-02', exit='2024-01-22', call_return=1.0),
            dict(symbol='AAA', entry='2024-01-03', exit='2024-01-23', call_return=4.0),
            dict(symbol='BBB', entry='2024-01-02', exit='2024-01-22', call_return=0.2),
        ]
        kept, dropped = dedupe_trades(trades, index)
        self.assertEqual([row['symbol'] + row['entry'] for row in kept], ['AAA2024-01-02', 'BBB2024-01-02'])
        self.assertEqual(len(dropped), 1)

    def test_dropping_the_largest_trades_removes_them_from_the_median(self):
        stats = trimmed([0.1, 0.2, 5.0, 0.0], 1)
        self.assertEqual(stats['n'], 3)
        self.assertAlmostEqual(stats['median'], 0.1)


if __name__ == '__main__':
    unittest.main()
