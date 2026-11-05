from datetime import date, timedelta
import unittest

from research_cohort import calendar_features, cohort_decision


class ResearchCohortTests(unittest.TestCase):
    def test_price_qualification_survives_missing_volume_baseline(self):
        row=dict(eligibility='target_evidence_reviewed',date_verified=True,
                 announcement_session='before_open',price_jump_at_least_15pct=True,
                 market_screen_pass=False,status='incomplete_20_session_baseline')
        self.assertEqual(cohort_decision(row),'price_qualified')
        row['announcement_session']='unknown'
        self.assertEqual(cohort_decision(row),'announcement_timing_review_pending')

    def fixture(self):
        calendar=[date(2024,1,1)+timedelta(days=i) for i in range(55)]
        rows=[dict(qdate=d,chain_rows=5,call_volume=0,put_volume=1,
                   otm_call_volume=0,otm_call_oi_diagnostic=0,top_otm_call_volume=0,
                   invalid_otm_volume_rows=0) for d in calendar]
        return calendar,rows

    def test_calendar_gap_invalidates_baseline_instead_of_skipping(self):
        calendar,rows=self.fixture()
        rows=[r for r in rows if r['qdate']!=calendar[25]]
        result=calendar_features(rows,calendar,calendar[50])
        day=next(r for r in result if r['qdate']==calendar[30])
        self.assertFalse(day['baseline_complete'])
        self.assertNotIn('otm_ratio20',day)
        missing=next(r for r in result if r['qdate']==calendar[25])
        self.assertFalse(missing['chain_observed'])
        self.assertNotIn('otm_call_volume',missing)

    def test_zero_days_and_future_leakage_and_entry_timing(self):
        calendar,rows=self.fixture()
        rows[50]['otm_call_volume']=999999
        result=calendar_features(rows,calendar,calendar[50])
        self.assertEqual(len(result),30)
        self.assertTrue(all(r['qdate']<calendar[50] for r in result))
        self.assertTrue(result[-1]['zero_volume_baseline'])
        self.assertIsNone(result[-1]['otm_ratio20'])
        self.assertEqual(result[-1]['otm_call_volume'],0)
        self.assertFalse(result[-1]['next_close_strictly_before_announcement'])
        self.assertTrue(result[-2]['next_close_strictly_before_announcement'])
        self.assertTrue(all(r['training_label'] is None for r in result))

    def test_negative_volume_suppresses_features(self):
        calendar,rows=self.fixture()
        rows[40]['invalid_otm_volume_rows']=1
        result=calendar_features(rows,calendar,calendar[50])
        self.assertFalse(result[-1]['volume_data_valid'])
        self.assertNotIn('otm_ratio20',result[-1])


if __name__=='__main__':unittest.main()
