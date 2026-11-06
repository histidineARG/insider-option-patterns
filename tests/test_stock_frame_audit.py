import unittest

from stock_frame_audit import summarize, transition


class StockFrameAuditTests(unittest.TestCase):
    def test_transition_uses_first_large_expansion_after_a_substantial_baseline(self):
        rows = [dict(qdate='2024-01-02', stockquote_rows=1),
                dict(qdate='2024-01-03', stockquote_rows=11000,
                     prior20_median_rows=1, count_ratio_to_prior20_median=11000),
                dict(qdate='2024-11-01', stockquote_rows=6000),
                dict(qdate='2024-11-04', stockquote_rows=27000,
                     prior20_median_rows=6000, count_ratio_to_prior20_median=4.5),
                dict(qdate='2024-11-05', stockquote_rows=27000,
                     prior20_median_rows=6000, count_ratio_to_prior20_median=4.5)]
        self.assertEqual(transition(rows[::-1]), ('2024-11-01', '2024-11-04'))

    def test_missing_transition_is_explicit(self):
        with self.assertRaises(ValueError):
            transition([dict(qdate='2024-01-02', stockquote_rows=6000)])

    def test_membership_does_not_turn_absence_or_query_failure_into_a_label(self):
        observations = [
            dict(symbol='OLD', qdate='2024-10-31', chain_observed=True,
                 option_coverage_status='observed_target_chain'),
            dict(symbol='OLD', qdate='2025-01-02', chain_observed=True,
                 option_coverage_status='observed_target_chain'),
            dict(symbol='NEW', qdate='2025-01-02', chain_observed=True,
                 option_coverage_status='observed_target_chain'),
            dict(symbol='MISSING', qdate='2025-01-02', option_coverage_status=
                 'no_target_rows_listing_status_unknown'),
            dict(symbol='ERROR', qdate='2025-01-02', option_coverage_status='query_failed')]
        details, summary = summarize(observations, {'OLD'}, '2024-11-04')
        self.assertEqual(len(details), 4)
        absent, present = summary
        self.assertEqual(absent['sampled_stock_days'], 3)
        self.assertEqual(absent['observed_chains'], 1)
        self.assertEqual(absent['no_target_rows'], 1)
        self.assertEqual(absent['query_failures'], 1)
        self.assertEqual(present['observed_chains'], 1)
        self.assertTrue(all('training_label' not in r for r in details))
        self.assertNotIn('baseline_membership', observations[0])
