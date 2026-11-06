import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pymysql

from market_calendar import sessions
from reviewed_cohort import apply_saved_reviews, inputs, run


class ReviewedCohortTests(unittest.TestCase):
    def test_overlay_does_not_inherit_measurements_or_promote_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'data').mkdir()
            folder = root/'results/research_cohort'
            folder.mkdir(parents=True)
            (folder/'event_cohort.json').write_text(json.dumps([
                dict(symbol='XYZ', announcement_date='2020-01-02',
                     cohort_status='price_qualified', previous_close=10,
                     price_jump_at_least_15pct=True, training_label_ready=True)]))
            (root/'data/event_review_overrides.json').write_text(json.dumps(dict(
                events=[dict(symbol='XYZ', announcement_date='2020-01-02',
                             review_status='conflict', issuer_cik='999')],
                additional_candidates=[])))
            row = inputs(root)[0]
            self.assertEqual(row['review_status'], 'conflict')
            self.assertEqual(row['issuer_cik'], '999')
            self.assertFalse(row['training_label_ready'])
            self.assertNotIn('price_jump_at_least_15pct', row)

    def test_database_error_rolls_back_and_remains_a_query_failure(self):
        class Cursor:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, args=None):
                if args:
                    raise pymysql.OperationalError(2013, 'lost connection')

        class Connection:
            rolled_back = False
            def cursor(self): return Cursor()
            def rollback(self): self.rolled_back = True

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ['data/event_review_overrides.json',
                     'results/research_cohort/event_cohort.json', 'data/calendar/nyse_sessions.json']
            for name in paths:
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('[]')
            c = Connection()
            row = dict(symbol='XYZ', announcement_date='2020-01-02',
                       announcement_session='before_open', event_id='XYZ:2020-01-02',
                       review_status='pending', training_label_ready=False)
            with patch('reviewed_cohort.inputs', return_value=[row]), patch(
                    'reviewed_cohort.sessions', return_value=sessions()):
                result = run(c, root)
            self.assertTrue(c.rolled_back)
            self.assertEqual(result['price_status_counts'], {'query_failed': 1})
            self.assertEqual(result['training_ready_events'], 0)

    def test_apply_saved_reviews_updates_status_without_promoting_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root/'results/reviewed_cohort'
            folder.mkdir(parents=True)
            (root/'data').mkdir()
            (root/'results/research_cohort').mkdir(parents=True)
            (root/'data/calendar').mkdir(parents=True)
            events = [dict(symbol='XYZ', announcement_date='2020-01-02', event_id='XYZ:2020-01-02',
                           review_status='first_disclosure_and_corporate_action_review_pending',
                           training_label_ready=True, price_qualification_status='price_qualified',
                           close_return_pct=20.0, valid_feature_days=3,
                           days_with_usable_quote_candidates=1)]
            (folder/'events.json').write_text(json.dumps(events))
            (folder/'manifest.json').write_text(json.dumps(dict(feature_rows=3, quote_screen={})))
            (root/'data/event_review_overrides.json').write_text(json.dumps(dict(
                events=[dict(symbol='XYZ', announcement_date='2020-01-02',
                             review_status='announcement_verified_earlier_disclosure_search_incomplete',
                             finding='test', first_public_disclosure_verified=False,
                             corporate_action_review_complete=False)],
                additional_candidates=[])))
            for name in ('results/research_cohort/event_cohort.json',
                         'data/calendar/nyse_sessions.json'):
                (root/name).write_text('[]')
            result = apply_saved_reviews(root)
            updated = json.loads((folder/'events.json').read_text())[0]
            self.assertEqual(updated['review_status'],
                             'announcement_verified_earlier_disclosure_search_incomplete')
            self.assertFalse(updated['training_label_ready'])
            self.assertEqual(result['training_ready_events'], 0)
