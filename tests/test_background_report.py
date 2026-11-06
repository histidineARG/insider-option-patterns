import unittest

from background_report import summarize


class BackgroundReportTests(unittest.TestCase):
    def test_coverage_exclusions_overlap_without_inventing_negatives(self):
        rows = [
            dict(qdate='2020-01-02', chain_observed=True,
                 baseline_complete=True, volume_data_valid=True),
            dict(qdate='2020-01-02', chain_observed=True,
                 baseline_complete=False, volume_data_valid=False),
            dict(qdate='2020-02-03', option_coverage_status=
                 'no_target_rows_listing_status_unknown'),
            dict(qdate='2021-01-04', option_coverage_status='query_failed'),
        ]
        first, second = summarize(rows)
        self.assertEqual(first, dict(year=2020, sampled_stock_days=3,
                         sampled_dates=2, observed_chains=2, no_target_rows=1,
                         query_failures=0, incomplete_baselines=1,
                         invalid_volume=1, usable_observations=1))
        self.assertEqual(second['query_failures'], 1)
        self.assertEqual(second['usable_observations'], 0)

    def test_empty_sample(self):
        self.assertEqual(summarize([]), [])
