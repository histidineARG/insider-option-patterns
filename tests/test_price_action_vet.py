from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

from price_action_vet import (
    classify, evaluate, expected_sessions, parse_cash_offer_usd, path_analysis,
    recomputed_return, run)



class PriceActionVetTests(unittest.TestCase):
    def test_return_and_session_mapping(self):
        calendar = [date(2016, 4, 6), date(2016, 4, 7), date(2016, 4, 8)]
        reaction, previous = expected_sessions('2016-04-07', 'after_close', calendar)
        self.assertEqual((reaction, previous), ('2016-04-08', '2016-04-07'))
        self.assertAlmostEqual(recomputed_return(15.46, 18.45), 19.340232858990944)

    def test_earlier_public_on_previous_session_classifies(self):
        calendar = [date(2023, 7, 26), date(2023, 7, 27), date(2023, 7, 28)]
        row = evaluate(dict(
            event_id='RETA:2023-07-28', symbol='RETA', announcement_date='2023-07-28',
            announcement_session='before_open', reaction_date='2023-07-28',
            previous_session='2023-07-27', previous_close=100.0, reaction_close=154.0,
            close_return_pct=54.0, price_jump_at_least_15pct=True,
            earlier_public_date_lower='2023-07-27', earlier_public_date_upper='2023-07-27',
            review_status='earlier_disclosure_time_unresolved'), calendar)
        self.assertTrue(row['measurement_ok'])
        self.assertEqual(row['price_action_status'],
                         'jump_ok_prior_close_may_reflect_earlier_public')

    def test_earlier_public_before_window_classifies(self):
        calendar = [date(2014, 9, 18), date(2014, 9, 19)]
        row = evaluate(dict(
            event_id='CNQR:2014-09-18', symbol='CNQR', announcement_date='2014-09-18',
            announcement_session='after_close', reaction_date='2014-09-19',
            previous_session='2014-09-18', previous_close=100.0, reaction_close=118.0,
            close_return_pct=18.0, price_jump_at_least_15pct=True,
            earlier_public_date_lower='2014-09-02', earlier_public_date_upper='2014-09-03',
            review_status='conflicting_primary_disclosure_dates'), calendar)
        self.assertEqual(row['price_action_status'],
                         'jump_ok_earlier_public_before_measured_window')

    def test_not_ads_phrase_is_not_ads_hazard(self):
        calendar = [date(2018, 4, 6), date(2018, 4, 9)]
        row = evaluate(dict(
            event_id='AVXS:2018-04-09', symbol='AVXS', announcement_date='2018-04-09',
            announcement_session='before_open', reaction_date='2018-04-09',
            previous_session='2018-04-06', previous_close=100.0, reaction_close=180.0,
            close_return_pct=80.0, price_jump_at_least_15pct=True,
            earlier_public_date_upper='2018-02-26',
            review_status='prior_takeover_speculation_public',
            share_class_notes='NASDAQ common stock AVXS; cash tender offer, not ADS.'), calendar)
        self.assertNotIn('ads_or_ordinary_share_comparison_hazard', row['hazards'])
        self.assertEqual(row['price_action_status'], 'jump_ok_prior_process_unresolved')

    def test_price_source_conflict_status(self):
        calendar = [date(2016, 2, 12), date(2016, 2, 16)]
        row = evaluate(dict(
            event_id='ADT:2016-02-16', symbol='ADT', announcement_date='2016-02-16',
            announcement_session='before_open', reaction_date='2016-02-16',
            previous_session='2016-02-12', previous_close=26.87, reaction_close=39.64,
            close_return_pct=(39.64 / 26.87 - 1) * 100, price_jump_at_least_15pct=True,
            review_status='announcement_verified_price_source_conflict'), calendar)
        self.assertEqual(row['price_action_status'], 'jump_ok_price_source_conflict')

    def test_classify_priority(self):
        self.assertEqual(
            classify(['earlier_public_on_previous_session'],
                     ['price_source_conflict'], True, True),
            'jump_ok_prior_close_may_reflect_earlier_public')
        self.assertEqual(classify([], [], False, True), 'measurement_failed')

    def test_parse_cash_offer(self):
        self.assertEqual(parse_cash_offer_usd('Cash $72.50 per common share.'), 72.5)
        self.assertIsNone(parse_cash_offer_usd('SEK 208 per ordinary share'))
        self.assertEqual(parse_cash_offer_usd('Cash $26.00 plus $2.00 CVR'), 26.0)
        self.assertIsNone(parse_cash_offer_usd(
            'All-cash take-private valued around $1.7 billion per complaint narrative.'))
        self.assertEqual(parse_cash_offer_usd('Cash tender $218/share; Outside Date extension.'), 218.0)

    def test_path_analysis_gap_and_drift(self):
        calendar = [date(2016, 2, d) for d in (8, 9, 10, 11, 12, 16)]
        quotes = [
            dict(qdate='2016-02-08', open=27, high=28, low=26, close=27, volume=100),
            dict(qdate='2016-02-09', open=27, high=28, low=26, close=27.4, volume=100),
            dict(qdate='2016-02-10', open=27, high=28, low=26, close=27.3, volume=100),
            dict(qdate='2016-02-11', open=26, high=27, low=26, close=26.4, volume=100),
            dict(qdate='2016-02-12', open=26, high=27, low=26, close=26.87, volume=100),
            dict(qdate='2016-02-16', open=40.62, high=41.3, low=39.45, close=39.64, volume=70000),
        ]
        path = path_analysis(dict(
            reaction_date='2016-02-16', previous_session='2016-02-12',
            consideration_notes='Cash deal; proxy cites approximate 56% offer premium.'), calendar, quotes)
        self.assertTrue(path['gap_dominated'])
        self.assertAlmostEqual(path['path_close_return_pct'], (39.64 / 26.87 - 1) * 100)

    def test_run_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'results/reviewed_cohort'
            folder.mkdir(parents=True)
            cal = root / 'data/calendar'
            cal.mkdir(parents=True)
            sessions = [
                dict(session='2016-02-12', market_open_utc='x', market_close_utc='y'),
                dict(session='2016-02-16', market_open_utc='x', market_close_utc='y'),
            ]
            content = (json.dumps(sessions, indent=2) + '\n').encode()
            import hashlib
            (cal / 'nyse_sessions.json').write_bytes(content)
            (cal / 'manifest.json').write_text(json.dumps(dict(
                start='2012-01-01', end='2026-12-31',
                sha256=hashlib.sha256(content).hexdigest())))
            ret = (39.64 / 26.87 - 1) * 100
            (folder / 'events.json').write_text(json.dumps([dict(
                event_id='ADT:2016-02-16', symbol='ADT', announcement_date='2016-02-16',
                announcement_session='before_open', reaction_date='2016-02-16',
                previous_session='2016-02-12', previous_close=26.87, reaction_close=39.64,
                close_return_pct=ret, price_jump_at_least_15pct=True,
                review_status='announcement_verified_price_source_conflict')]))
            manifest = run(root)
            self.assertEqual(manifest['events'], 1)
            self.assertEqual(manifest['measurement_ok'], 1)
            self.assertTrue((root / 'results/price_action_vet/REPORT.md').exists())


if __name__ == '__main__':
    unittest.main()
