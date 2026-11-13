from datetime import date, timedelta
import unittest

from insider_accumulation import score_window, sleeve_keys


class AccumulationTests(unittest.TestCase):
    def row(self, day, strike, oi, volume, delta=0.25, spot=10):
        return dict(qdate=day, strike=strike, edate=date(2024, 2, 15), volume=volume, oi=oi,
                    delta=delta, underlying_last=spot, bid=0.2, ask=0.3)

    def test_sleeve_keeps_the_cheap_call_that_covers_the_event(self):
        event = date(2024, 1, 20)
        anchor = date(2024, 1, 5)
        rows = [
            self.row(anchor, 11, 10, 1),
            self.row(anchor, 20, 10, 1),
            self.row(anchor, 11, 10, 1, delta=0.8),
        ]
        keys = sleeve_keys(rows, event)
        self.assertEqual(keys, {(11.0, date(2024, 2, 15))})

    def test_build_in_one_contract_hits(self):
        anchor = date(2024, 1, 5)
        baseline = [anchor - timedelta(days=i + 1) for i in range(20)]
        window = [anchor + timedelta(days=i + 1) for i in range(10)]
        rows = [self.row(day, 11, 10, 1) for day in baseline]
        rows.append(self.row(anchor, 11, 20, 0))
        for day in window[:-1]:
            rows.append(self.row(day, 11, 40, 20))
        rows.append(self.row(window[-1], 11, 200, 40))
        scored = score_window(rows, {(11.0, date(2024, 2, 15))}, window, baseline, anchor)
        self.assertTrue(scored['eligible'])
        self.assertTrue(scored['hit'])
        self.assertGreaterEqual(scored['net_oi'], 100)

    def test_volume_without_open_interest_build_does_not_hit(self):
        anchor = date(2024, 1, 5)
        baseline = [anchor - timedelta(days=i + 1) for i in range(20)]
        window = [anchor + timedelta(days=i + 1) for i in range(10)]
        rows = [self.row(day, 11, 50, 1) for day in baseline + [anchor] + window]
        for day in window:
            rows.append(self.row(day, 11, 50, 50))
        scored = score_window(rows, {(11.0, date(2024, 2, 15))}, window, baseline, anchor)
        self.assertTrue(scored['eligible'])
        self.assertFalse(scored['hit'])


if __name__ == '__main__':
    unittest.main()
