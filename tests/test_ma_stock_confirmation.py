from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest

from ma_stock_confirmation import candidates, measure


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

    def test_price_only_qualification_survives_invalid_volume(self):
        rows,days=self.data(volume=0)
        result=measure(rows,days[-1],days[-2],days[:-1],2)
        self.assertTrue(result['price_jump_at_least_15pct'])
        self.assertFalse(result['market_screen_pass'])
        self.assertEqual(result['status'],'invalid_reaction_volume')

    def test_announcement_date_reviews_correct_local_maevent_dates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ma = root / 'data/m_and_a'
            ma.mkdir(parents=True)
            (ma / 'local_maevent_all.csv').write_text(
                'maid,symbol,announcedate,acquiree,acquirer\n'
                '1,OMX,2013-02-18,OfficeMax,Office Depot\n'
                '2,AFFX,2016-01-11,Affymetrix,Thermo\n')
            (root / 'data/sec_cases.json').write_text(json.dumps(dict(cases=[])))
            (ma / 'reviewed_event_examples.json').write_text(json.dumps(dict(events=[])))
            (ma / 'announcement_date_reviews.json').write_text(json.dumps(dict(reviews=[
                dict(symbol='OMX', prior_candidate_date='2013-02-18',
                     announcement_date='2013-02-20', announcement_session='intraday',
                     announcement_timing_source='https://example.test/omx',
                     announcement_timing_locator='test', date_verified=True),
                dict(symbol='AFFX', prior_candidate_date='2016-01-11',
                     announcement_date='2016-01-08', announcement_session='after_close',
                     announcement_timing_source='https://example.test/affx',
                     announcement_timing_locator='test', date_verified=True),
            ])))
            rows = { (r['symbol'], r['announcement_date']): r for r in candidates(root) }
            self.assertIn(('OMX', '2013-02-20'), rows)
            self.assertNotIn(('OMX', '2013-02-18'), rows)
            self.assertEqual(rows[('OMX', '2013-02-20')]['announcement_session'], 'intraday')
            self.assertTrue(rows[('OMX', '2013-02-20')]['date_verified'])
            self.assertIn(('AFFX', '2016-01-08'), rows)
            self.assertEqual(rows[('AFFX', '2016-01-08')]['announcement_session'], 'after_close')


if __name__=='__main__':unittest.main()
