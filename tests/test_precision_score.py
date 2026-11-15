import unittest

from precision_score import average_precision, fold_report, rank_of, true_case_report


class PrecisionScoreTests(unittest.TestCase):
    def test_average_precision_averages_precision_at_each_positive(self):
        rows = [
            dict(score=3, label=1, role='deal', year='2024', symbol='A', event='1'),
            dict(score=2, label=0, role='earnings', year='2024', symbol='A', event='1'),
            dict(score=1, label=1, role='deal', year='2024', symbol='B', event='2'),
        ]
        self.assertAlmostEqual(average_precision(rows), (1 + 2 / 3) / 2)

    def test_top_k_reports_precision_and_the_base_rate(self):
        rows = [
            dict(score=5, label=1, role='deal', year='2024', symbol='A', event='1'),
            dict(score=4, label=0, role='earnings', year='2024', symbol='A', event='1'),
            dict(score=3, label=1, role='deal', year='2023', symbol='B', event='2'),
            dict(score=1, label=0, role='ordinary', year='2023', symbol='B', event='2'),
        ]
        report = fold_report(rows, ks=(2,))
        self.assertEqual(report['base_rate'], 0.5)
        self.assertEqual(report['at_k']['2']['precision'], 0.5)
        self.assertEqual(report['at_k']['2']['alerts_by_year'][0]['year'], '2024')

    def test_true_case_rank_counts_false_alerts(self):
        universe = [dict(score=0.9), dict(score=0.2)]
        cases = [dict(id='afop_2016', symbol='AFOP', event='2016-04-07', instrument='common_stock', score=0.5)]
        report = true_case_report(cases, universe, ks=(2,))
        self.assertEqual(report['cases'][0]['rank'], 2)
        self.assertEqual(report['at_k']['2']['cases'], 1)
        self.assertEqual(report['at_k']['2']['false_alerts'], 1)
        self.assertEqual(rank_of(0.5, [0.9, 0.2]), 2)


if __name__ == '__main__':
    unittest.main()
