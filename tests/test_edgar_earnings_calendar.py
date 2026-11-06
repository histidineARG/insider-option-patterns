import unittest
from datetime import date, datetime, timezone

from edgar_earnings_calendar import extract_item_202_rows
from price_jump_examine import reaction_session_with_meta


class EdgarEarningsCalendarTests(unittest.TestCase):
    def test_extracts_only_item_202_eight_k(self):
        filings = dict(
            form=['8-K', '8-K', '10-Q', '8-K/A'],
            items=['2.02,9.01', '1.01,9.01', '', '2.02'],
            filingDate=['2020-01-28', '2020-02-01', '2020-02-05', '2020-01-29'],
            acceptanceDateTime=['2020-01-28T21:30:00.000Z', '2020-02-01T12:00:00.000Z',
                                '2020-02-05T12:00:00.000Z', '2020-01-29T22:00:00.000Z'],
            reportDate=['2020-01-28', '2020-02-01', '2020-02-05', '2020-01-29'],
            accessionNumber=['a', 'b', 'c', 'd'],
            primaryDocument=['ex.htm', 'ex.htm', 'q.htm', 'ex.htm'],
        )
        rows = extract_item_202_rows(filings)
        self.assertEqual([r['accession'] for r in rows], ['a', 'd'])

    def test_after_close_acceptance_maps_to_next_session(self):
        meta = {
            date(2019, 1, 29): dict(
                session='2019-01-29',
                market_open_utc='2019-01-29 14:30:00+00:00',
                market_close_utc='2019-01-29 21:00:00+00:00',
            ),
            date(2019, 1, 30): dict(
                session='2019-01-30',
                market_open_utc='2019-01-30 14:30:00+00:00',
                market_close_utc='2019-01-30 21:00:00+00:00',
            ),
        }
        acc = datetime(2019, 1, 29, 21, 30, 18, tzinfo=timezone.utc)
        self.assertEqual(reaction_session_with_meta(acc, meta), date(2019, 1, 30))

    def test_before_open_acceptance_maps_to_same_session(self):
        meta = {
            date(2020, 4, 30): dict(
                session='2020-04-30',
                market_open_utc='2020-04-30 13:30:00+00:00',
                market_close_utc='2020-04-30 20:00:00+00:00',
            ),
        }
        acc = datetime(2020, 4, 30, 12, 0, 0, tzinfo=timezone.utc)
        self.assertEqual(reaction_session_with_meta(acc, meta), date(2020, 4, 30))


if __name__ == '__main__':
    unittest.main()
