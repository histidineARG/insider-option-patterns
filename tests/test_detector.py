from datetime import date, timedelta
import unittest
from detector import Settings, score

class DetectorTests(unittest.TestCase):
    target = date(2026, 1, 30)

    def days(self, baseline, current=1000, oi=100):
        return [dict(qdate=self.target-timedelta(days=i+1), volume=v, oi=10, premium=0)
                for i,v in enumerate(baseline)] + [dict(qdate=self.target, volume=current, oi=oi, premium=1234)]

    def test_surge_excludes_target_and_future(self):
        days = self.days([90,110]*10)
        days.append(dict(qdate=self.target+timedelta(days=1), volume=999999))
        alert = score(days,self.target,Settings())
        self.assertEqual(alert['baseline_mean'],100)
        self.assertEqual(alert['volume_ratio'],10)

    def test_ordinary_volume(self):
        self.assertIsNone(score(self.days([100]*20,100),self.target,Settings()))

    def test_insufficient_history(self):
        self.assertIsNone(score(self.days([10]*9),self.target,Settings()))

    def test_zero_baseline_and_oi(self):
        alert = score(self.days([0]*20,oi=0),self.target,Settings())
        self.assertTrue(alert['zero_baseline'])
        self.assertIsNone(alert['volume_ratio'])
        self.assertIsNone(alert['volume_oi'])

    def test_oi_filter(self):
        self.assertIsNone(score(self.days([100]*20,oi=2000),self.target,Settings()))

    def test_latest_lookback_only(self):
        self.assertEqual(score(self.days([100]*20+[100000]*5),self.target,Settings())['baseline_mean'],100)

    def test_missing_target(self):
        self.assertIsNone(score([],self.target,Settings()))

if __name__ == '__main__':
    unittest.main()
