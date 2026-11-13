import unittest
from datetime import date

from walkforward_score import (
    causal_features, classify_news, forward_flags, random_hit_probability, slate_summary,
)


class WalkforwardTests(unittest.TestCase):
    def test_feature_window_stops_at_the_scoring_close(self):
        score = date(2024, 1, 12)
        earlier = date(2024, 1, 10)
        later = date(2024, 1, 16)
        expiry = date(2024, 2, 16)
        rows = {
            earlier: {expiry: dict(call_vol=5, put_vol=1, otm_call_vol=1, call_oi=4)},
            score: {expiry: dict(call_vol=8, put_vol=1, otm_call_vol=2, call_oi=9)},
            later: {expiry: dict(call_vol=100, put_vol=1, otm_call_vol=100, call_oi=500)},
        }
        closes = {earlier: 10.0, score: 11.0, later: 20.0}
        features = causal_features(rows, closes, [earlier, score], score)
        self.assertAlmostEqual(features['pre_return'], 0.1)

    def test_forward_jump_uses_the_horizon_close_and_the_max_close(self):
        flags = forward_flags(10.0, [10.5, 12.0, 11.0], False)
        self.assertFalse(flags['terminal'])
        self.assertTrue(flags['peak'])

    def test_a_split_sized_print_is_not_a_jump(self):
        flags = forward_flags(10.0, [21.0], False)
        self.assertTrue(flags['bad'])
        self.assertFalse(flags['terminal'])
        self.assertFalse(flags['peak'])

    def test_random_slate_and_false_picks(self):
        self.assertAlmostEqual(random_hit_probability(4, 1, 3), 0.75)
        records = [{
            'slate': [
                dict(jumps={'5': dict(terminal=True, peak=True)}, news={'5': 'ma'}),
                dict(jumps={'5': dict(terminal=False, peak=False)}, news={'5': 'other'}),
                dict(jumps={'5': dict(terminal=False, peak=False)}, news={'5': 'other'}),
            ],
            'universe': {5: dict(eligible=10, terminal=1, peak=1)},
        }]
        summary = slate_summary(records, 3, 5, 'terminal')
        self.assertEqual(summary['date_hit_rate'], 1)
        self.assertEqual(summary['false_picks_per_hit'], 2)
        self.assertEqual(summary['hits']['ma'], 1)
        self.assertEqual(summary['hits']['other'], 0)

    def test_news_class_uses_only_sessions_after_the_score(self):
        sessions = [date(2024, 1, d) for d in range(10, 16)]
        index = {day: i for i, day in enumerate(sessions)}
        ma = {'AAA': {date(2024, 1, 12)}}
        kind = classify_news('AAA', date(2024, 1, 10), date(2024, 1, 15), sessions, index, ma, {})
        self.assertEqual(kind, 'ma')
        kind = classify_news('AAA', date(2024, 1, 12), date(2024, 1, 15), sessions, index, ma, {})
        self.assertEqual(kind, 'other')


if __name__ == '__main__':
    unittest.main()
