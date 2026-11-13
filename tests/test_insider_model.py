from datetime import date
import unittest

from insider_model import auc, evaluate_model, fit_ridge_logistic, predict, window_features


class WindowFeatureTests(unittest.TestCase):
    def day(self, offset, call_vol, band_vol, put_vol=0, band_oi=10, top_share=0.8):
        return dict(qdate=date(2024, 1, offset), call_vol=call_vol, band_vol=band_vol,
                    put_vol=put_vol, band_oi=band_oi, top_share=top_share)

    def test_uses_the_loudest_ratio_day(self):
        baseline = [self.day(i, 10, 1) for i in range(1, 21)]
        window = [self.day(i, 10, 9, top_share=0.2) for i in range(1, 9)]
        window.append(self.day(20, 100, 40, put_vol=25, band_oi=20, top_share=0.7))
        features = window_features(window, baseline)
        self.assertEqual(features['session'], '2024-01-20')
        self.assertAlmostEqual(features['band_share'], 0.4)
        self.assertAlmostEqual(features['top_share'], 0.7)
        self.assertAlmostEqual(features['call_fraction'], 100 / 125)
        self.assertAlmostEqual(features['log_band_turnover'], __import__('math').log1p(40 / 21))

    def test_short_window_has_no_features(self):
        self.assertIsNone(window_features([self.day(1, 10, 1)], [self.day(i, 10, 1) for i in range(1, 21)]))


class LogisticTests(unittest.TestCase):
    def sample(self, symbol, year, role, label, ratio):
        return dict(symbol=symbol, event=f'{year}-06-01', role=role, year=year, label=label,
                    features=dict(log_volume_ratio=ratio, band_share=0.2, top_share=0.5,
                                  call_fraction=0.6, log_band_turnover=0.3))

    def test_separated_training_rows_rank_correctly(self):
        samples = []
        for i in range(12):
            samples.append(self.sample(f'P{i}', 2013, 'case', 1, 2.0))
            samples.append(self.sample(f'P{i}', 2013, 'placebo', 0, 0.2))
        for i in range(8):
            samples.append(self.sample(f'H{i}', 2016, 'case', 1, 2.0))
            samples.append(self.sample(f'H{i}', 2016, 'placebo', 0, 0.2))
        result = evaluate_model(samples)
        self.assertTrue(result['fit'])
        self.assertGreater(result['folds']['holdout_2016']['auc'], 0.9)
        self.assertGreater(result['coefficients']['log_volume_ratio'], 0)

    def test_auc_ties(self):
        self.assertEqual(auc([0.5, 0.5], [1, 0]), 0.5)

    def test_ridge_fit_scores_between_zero_and_one(self):
        design = [[1.0, x] for x in (0.0, 1.0, 2.0, 3.0)]
        beta = fit_ridge_logistic(design, [0, 0, 1, 1], ridge=1.0)
        for row in design:
            score = predict(beta, row)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


if __name__ == '__main__':
    unittest.main()
