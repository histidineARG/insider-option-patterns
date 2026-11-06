import json
from pathlib import Path
import tempfile
import unittest

from research_dataset import assign_label, build, disclosure_status, partition_rows, run


def calendar_slice():
    # Enough sessions for a 20-day baseline and 10-day outcome around mid-window.
    from datetime import date, timedelta
    rows = []
    day = date(2020, 1, 2)
    while len(rows) < 60:
        if day.weekday() < 5:
            session = day.isoformat()
            rows.append(dict(session=session,
                             market_open_utc=f'{session} 14:30:00+00:00',
                             market_close_utc=f'{session} 21:00:00+00:00'))
        day += timedelta(days=1)
    return rows


PROTOCOL = dict(
    prediction_horizon_sessions=10, baseline_sessions=20,
    partitions=[dict(name='train', start='2013-01-01', end='2019-12-31'),
                dict(name='validation', start='2020-01-01', end='2022-12-31')])


class ResearchDatasetTests(unittest.TestCase):
    def test_unreviewed_candidate_blocks_negative_and_keeps_label_null(self):
        row = dict(symbol='ABC', qdate='2020-02-20', outcome_window_complete=True,
                   feature_close_utc='2020-02-20 21:00:00+00:00',
                   outcome_end='2020-03-05', outcome_end_utc='2020-03-05 21:00:00+00:00',
                   entry_close_proxy_utc='2020-02-21 21:00:00+00:00')
        event = dict(symbol='ABC', announcement_date='2020-02-25', event_id='ABC:2020-02-25',
                     training_label_ready=False, first_public_disclosure_verified=False,
                     corporate_action_review_complete=False, price_jump_at_least_15pct=True)
        label, ids, status = assign_label(row, [event], [])
        self.assertIsNone(label)
        self.assertEqual(status, 'candidate_or_disclosure_review_unresolved')
        self.assertEqual(ids, [])

    def test_complete_scoped_review_can_certify_negative(self):
        row = dict(symbol='ABC', qdate='2020-02-20', outcome_window_complete=True,
                   feature_close_utc='2020-02-20 21:00:00+00:00',
                   outcome_end='2020-03-05', outcome_end_utc='2020-03-05 21:00:00+00:00',
                   entry_close_proxy_utc='2020-02-21 21:00:00+00:00')
        review = dict(symbol='ABC', complete=True, source='https://example.test/review',
                      locator='scoped acquisition-outcome search',
                      security_identity_verified=True,
                      start_utc='2020-02-01T00:00:00+00:00',
                      end_utc='2020-03-10T00:00:00+00:00')
        label, ids, status = assign_label(row, [], [review])
        self.assertEqual(label, 0)
        self.assertEqual(status, 'negative_from_complete_scoped_outcome_review')

    def test_verified_positive_requires_entry_before_disclosure(self):
        row = dict(symbol='ABC', qdate='2020-02-20', outcome_window_complete=True,
                   feature_close_utc='2020-02-20 21:00:00+00:00',
                   outcome_end='2020-03-05', outcome_end_utc='2020-03-05 21:00:00+00:00',
                   entry_close_proxy_utc='2020-02-21 21:00:00+00:00')
        event = dict(symbol='ABC', announcement_date='2020-02-25', event_id='ABC:2020-02-25',
                     training_label_ready=True, first_public_disclosure_verified=True,
                     corporate_action_review_complete=True, price_jump_at_least_15pct=True,
                     first_public_lower_utc='2020-02-25T14:30:00+00:00',
                     first_public_upper_utc='2020-02-25T14:30:00+00:00')
        label, ids, status = assign_label(row, [event], [])
        self.assertEqual(label, 1)
        self.assertEqual(ids, ['ABC:2020-02-25'])
        self.assertEqual(status, 'verified_executable_positive')

    def test_disclosure_status_uses_earlier_boundary_conservatively(self):
        event = dict(earlier_public_date_lower='2020-02-10', earlier_public_date_upper='2020-02-11',
                     first_public_disclosure_verified=False)
        self.assertEqual(disclosure_status(event, '2020-02-10', '2020-02-11'),
                         'at_or_after_known_earlier_disclosure_boundary')

    def test_partition_purge_marks_crossing_windows(self):
        rows = [dict(qdate='2019-12-20', feature_start='2019-11-20', outcome_end='2020-01-05',
                     context_event_ids=[], outcome_event_ids=[])]
        partition_rows(rows, PROTOCOL['partitions'])
        self.assertEqual(rows[0]['partition'], 'train')
        self.assertEqual(rows[0]['purge_reason'], 'feature_or_outcome_window_crosses_partition')

    def test_build_keeps_research_ineligible_without_inventing_labels(self):
        calendar = calendar_slice()
        signal = calendar[25]['session']
        features = [dict(symbol='ABC', qdate=signal, event_id='ABC:2020-02-20',
                         chain_observed=True, baseline_complete=True, volume_data_valid=True,
                         otm_call_volume=10, otm_mean20=1)]
        background = [dict(symbol='XYZ', qdate=signal, chain_observed=True,
                           baseline_complete=True, volume_data_valid=True,
                           otm_call_volume=0, otm_mean20=0)]
        events = [dict(event_id='ABC:2020-02-20', symbol='ABC', announcement_date='2020-02-20',
                       training_label_ready=False, first_public_disclosure_verified=False,
                       corporate_action_review_complete=False, price_jump_at_least_15pct=True)]
        rows = build(features, background, events, calendar, PROTOCOL, [], followup_end='2020-03-20')
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r['training_label'] is None for r in rows))
        self.assertTrue(all(r['research_eligible'] is False for r in rows))
        self.assertIn('ABC:2020-02-20', rows[0]['disclosure_diagnostics']
                      if rows[0]['symbol'] == 'ABC' else rows[1]['disclosure_diagnostics'])

    def test_run_writes_zero_label_audit_from_repo_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Point run at a shallow copy of required artifacts via relative paths.
            for path in ['results/reviewed_cohort/features.json',
                         'results/background_sample/observations.json',
                         'results/reviewed_cohort/events.json',
                         'data/evaluation_protocol.json',
                         'data/outcome_coverage_reviews.json',
                         'data/calendar/nyse_sessions.json',
                         'data/calendar/manifest.json']:
                src = Path(path)
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(src.read_bytes())
            # Tiny synthetic inputs keep the offline unit test fast and deterministic.
            (root/'results/reviewed_cohort/features.json').write_text('[]')
            (root/'results/background_sample/observations.json').write_text(json.dumps([
                dict(symbol='AAA', qdate='2020-06-01', chain_observed=True,
                     baseline_complete=True, volume_data_valid=True,
                     otm_call_volume=0, otm_mean20=0)]))
            (root/'results/reviewed_cohort/events.json').write_text('[]')
            (root/'data/outcome_coverage_reviews.json').write_text(
                json.dumps(dict(as_of='2026-11-06', scope='empty', reviews=[])))
            (root/'data/evaluation_protocol.json').write_text(json.dumps(dict(
                prediction_horizon_sessions=10, baseline_sessions=20,
                partitions=[dict(name='validation', start='2020-01-01', end='2022-12-31')],
                test_authorized=False)))
            manifest = run(root=root)
            self.assertEqual(manifest['known_positive_labels'], 0)
            self.assertEqual(manifest['known_negative_labels'], 0)
            self.assertEqual(manifest['research_eligible'], 0)
            self.assertTrue((root/'results/research_dataset/REPORT.md').exists())


if __name__ == '__main__':
    unittest.main()
