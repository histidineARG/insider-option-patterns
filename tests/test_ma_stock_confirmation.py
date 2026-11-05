from datetime import date, timedelta
from decimal import Decimal
import unittest

from ma_stock_confirmation import measure


class StockConfirmationTests(unittest.TestCase):
    def data(self,close='115',volume=200):
        first=date(2024,1,1)
        days=[first+timedelta(days=i) for i in range(21)]
        rows=[dict(qdate=d,close=Decimal('100'),open=Decimal('100'),high=Decimal('100'),low=Decimal('100'),volume=100) for d in days]
        rows[-1].update(close=Decimal(close),open=Decimal(close),high=Decimal(close),volume=volume)
        return rows,days

    def test_exact_thresholds_and_current_volume_excluded(self):
        rows,days=self.data()
        result=measure(rows,days[-1],days[-2],days[:-1],2)
        self.assertTrue(result['market_screen_pass'])
        self.assertEqual(result['volume_avg20'],100)
        self.assertEqual(result['volume_ratio20'],2)

    def test_does_not_skip_missing_previous_session(self):
        rows,days=self.data();rows.pop(-2)
        result=measure(rows,days[-1],days[-2],days[:-1],2)
        self.assertEqual(result['status'],'missing_previous_session_quote')
        self.assertFalse(result['market_screen_pass'])

    def test_missing_baseline_is_not_fabricated(self):
        rows,days=self.data();rows.pop(3)
        result=measure(rows,days[-1],days[-2],days[:-1],2)
        self.assertEqual(result['status'],'incomplete_20_session_baseline')
        self.assertFalse(result['market_screen_pass'])

    def test_rejects_less_than_fifteen_percent(self):
        rows,days=self.data(close='114.99')
        self.assertFalse(measure(rows,days[-1],days[-2],days[:-1],2)['market_screen_pass'])


if __name__=='__main__':unittest.main()
