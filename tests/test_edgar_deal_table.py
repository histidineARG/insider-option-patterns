import unittest
from datetime import date

from edgar_deal_table import (
    announcement_session, assign_parties, earliest_deals, has_item_101, parse_display_name, prefer_common,
)


class EdgarDealTableTests(unittest.TestCase):
    def test_display_name_keeps_publ_out_of_the_ticker(self):
        parsed = parse_display_name('Olink Holding AB (publ)  (CIK 0001835539)')
        self.assertEqual(parsed['name'], 'Olink Holding AB (publ)')
        self.assertEqual(parsed['tickers'], [])
        self.assertEqual(parsed['cik'], '0001835539')

    def test_display_name_reads_tickers(self):
        parsed = parse_display_name('Constellation Acquisition Corp I  (CSTAF, CSTUF, CSTWF)  (CIK 0001834032)')
        self.assertEqual(parsed['tickers'], ['CSTAF', 'CSTUF', 'CSTWF'])

    def test_tender_subject_is_the_target_and_the_second_name_is_the_bidder(self):
        parties = assign_parties('SC TO-T', [
            'MorphoSys AG  (MPSYF)  (CIK 0001340243)',
            'NOVARTIS AG  (NVS, NVSEF)  (CIK 0001114448)',
        ])
        self.assertEqual(parties['form_role'], 'tender_target')
        self.assertEqual(parties['target']['tickers'], ['MPSYF'])
        self.assertEqual(parties['acquirer']['tickers'], ['NVS', 'NVSEF'])

    def test_item_101_is_required_for_the_eight_k_phrase(self):
        self.assertTrue(has_item_101(['1.01', '9.01']))
        self.assertFalse(has_item_101(['2.01', '9.01']))

    def test_warrant_ticker_drops_when_the_common_is_present(self):
        self.assertEqual(prefer_common(['TACHW', 'TACH', 'TACHU']), ['TACH'])

    def test_earliest_filing_inside_seven_days_is_kept(self):
        rows = [
            dict(symbol='AAA', qdate=date(2024, 1, 10), accession='b', acceptance_datetime='', file_date='2024-01-10'),
            dict(symbol='AAA', qdate=date(2024, 1, 8), accession='a', acceptance_datetime='', file_date='2024-01-08'),
            dict(symbol='AAA', qdate=date(2024, 2, 1), accession='c', acceptance_datetime='', file_date='2024-02-01'),
        ]
        kept = earliest_deals(rows)
        self.assertEqual([row['accession'] for row in kept], ['a', 'c'])
        self.assertEqual(kept[0]['also_accessions'], ['b'])

    def test_after_close_acceptance_maps_to_the_next_session(self):
        meta = {
            date(2024, 1, 8): dict(market_close_utc='2024-01-08 21:00:00+00:00'),
            date(2024, 1, 9): dict(market_close_utc='2024-01-09 21:00:00+00:00'),
        }
        day, basis = announcement_session('2024-01-08T21:30:00.000Z', '2024-01-09', meta)
        self.assertEqual(day, date(2024, 1, 9))
        self.assertEqual(basis, 'acceptance')


if __name__ == '__main__':
    unittest.main()
