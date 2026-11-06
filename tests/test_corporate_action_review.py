import json
from pathlib import Path
import tempfile
import unittest

from corporate_action_review import evaluate, run


class CorporateActionReviewTests(unittest.TestCase):
    def test_never_auto_marks_complete_even_when_ready(self):
        row = evaluate(dict(
            symbol='XYZ', announcement_date='2020-01-02', event_id='XYZ:2020-01-02',
            issuer_cik='1', identity_source='https://example.test',
            share_class_notes='common', split_ticker_change_reviewed=True,
            reincarnation_reviewed=True, consideration_notes='cash'))
        self.assertTrue(row['ready_to_mark_complete'])
        self.assertFalse(row['corporate_action_review_complete'])

    def test_missing_share_class_remains_a_blocker(self):
        row = evaluate(dict(symbol='XYZ', announcement_date='2020-01-02', issuer_cik='1',
                            review_status='announcement_verified_issuer_identity_corrected',
                            identity_source='https://example.test'))
        self.assertIn('share_class_or_ads_terms_recorded', row['blockers'])

    def test_run_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root/'results/reviewed_cohort'
            folder.mkdir(parents=True)
            (root/'data').mkdir()
            (folder/'events.json').write_text(json.dumps([
                dict(symbol='XYZ', announcement_date='2020-01-02', event_id='XYZ:2020-01-02',
                     issuer_cik='1')]))
            (root/'data/event_review_overrides.json').write_text(json.dumps(dict(
                events=[], additional_candidates=[])))
            manifest = run(root)
            self.assertEqual(manifest['marked_complete'], 0)
            self.assertTrue((root/'results/corporate_action_review/REPORT.md').exists())


if __name__ == '__main__':
    unittest.main()
