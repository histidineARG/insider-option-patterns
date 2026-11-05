from datetime import date, timedelta
import unittest
from sec_match import annotate, daily_query, summarize


class AlignmentTests(unittest.TestCase):
    def day(self, day, volume):
        return dict(qdate=day,chain_rows=1,call_volume=volume,put_volume=0,
                    otm_volume=volume,otm_oi=100,top_otm_volume=volume,
                    otm_all_expiries_volume=volume,source_series_volume=volume,
                    source_series_rows=1)

    def test_baseline_excludes_current_and_future(self):
        start=date(2024,1,1)
        days=[self.day(start+timedelta(days=i),10) for i in range(20)]
        days.extend([self.day(start+timedelta(days=20),100),self.day(start+timedelta(days=21),10000)])
        result=annotate(days)
        self.assertEqual(result[20]['otm_ratio20'],10)
        self.assertEqual(result[20]['source_series_volume_ratio20'],10)
        self.assertTrue(result[20]['diagnostic_alert'])

    def test_no_same_day_event_leakage(self):
        target=date(2024,1,3)
        case=dict(id='x',symbol='X',trade_start=str(target),trade_end=str(target),
                  event_date=str(target),evidence_status='allegation',window_quality='subset',
                  contracts=[],source_url='https://www.sec.gov/example')
        result=summarize(case,annotate([self.day(target,1000)]),[target])
        self.assertEqual(result['observed_pre_event_sessions'],0)
        self.assertEqual(result['match_status'],'no_usable_pre_event_eod')

    def test_parameterized_contract_query(self):
        case=dict(symbol='X',trade_start='2024-01-01',event_date='2024-01-10',
                  contracts=[dict(strike=25,expiry='2024-02-16')])
        sql,args=daily_query(case)
        self.assertEqual(sql.count('%s'),len(args))
        self.assertEqual(args[:4],[25,'2024-02-16',25,'2024-02-16'])
        self.assertNotIn("underlying='X'",sql)

    def test_zero_baseline_is_explicit(self):
        start=date(2024,1,1)
        days=[self.day(start+timedelta(days=i),0) for i in range(20)]
        days.append(self.day(start+timedelta(days=20),100))
        result=annotate(days)[20]
        self.assertTrue(result['zero_baseline'])
        self.assertIsNone(result['otm_ratio20'])
        self.assertTrue(result['diagnostic_alert'])


if __name__=='__main__':
    unittest.main()
