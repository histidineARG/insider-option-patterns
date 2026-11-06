import unittest

from price_jump_examine import apply_hard_filters, apply_news_reviews, build_news_queue


def _jump(**kwargs):
    base = dict(
        symbol='AAAA',
        qdate='2015-06-01',
        prev_qdate='2015-05-29',
        close=12.0,
        prev_close=10.0,
        close_return=0.2,
        volume=1000,
        prev_volume=400,
        vol_ratio=2.5,
        cik='0000000001',
        jump_cause=None,
        cause_class='unclassified',
        news_filter='pending_news_review',
    )
    base.update(kwargs)
    return base


class PriceJumpExamineFiltersTests(unittest.TestCase):
    def test_earnings_drop_wins_over_review_overlay(self):
        rows = [apply_hard_filters([
            _jump(news_filter='drop_earnings', cause_class='1_earnings', jump_cause='earnings',
                  prev_close=10.0),
        ], etf_denylist=set(), option_present={('AAAA', '2015-06-01')})[0]]
        reviews = {('AAAA', '2015-06-01'): dict(
            jump_cause='tech_breakthrough',
            cause_class='4_tech_breakthrough',
            news_filter='keep',
            locator='https://example.test/x',
        )}
        out = apply_news_reviews(rows, reviews)[0]
        self.assertEqual(out['news_filter'], 'drop_earnings')
        self.assertEqual(out['jump_cause'], 'earnings')

    def test_review_overlay_wins_over_pending(self):
        rows = apply_hard_filters([
            _jump(symbol='GENE', qdate='2015-01-29', prev_close=6.0, close_return=1.82),
        ], etf_denylist=set(), option_present={('GENE', '2015-01-29')})
        reviews = {('GENE', '2015-01-29'): dict(
            jump_cause='tech_breakthrough',
            cause_class='4_tech_breakthrough',
            news_filter='keep',
            locator='https://example.test/gene',
            detail='kept',
        )}
        out = apply_news_reviews(rows, reviews)[0]
        self.assertEqual(out['news_filter'], 'keep')
        self.assertEqual(out['cause_class'], '4_tech_breakthrough')
        self.assertEqual(out['news_locator'], 'https://example.test/gene')

    def test_sub_5_and_etf_and_no_option_drops(self):
        etf = {'UVXY'}
        present = {('OKAY', '2015-06-01')}
        rows = apply_hard_filters([
            _jump(symbol='PENY', prev_close=4.99),
            _jump(symbol='UVXY', prev_close=8.0, qdate='2015-06-01'),
            _jump(symbol='MISS', prev_close=8.0, qdate='2015-06-01'),
            _jump(symbol='OKAY', prev_close=8.0, qdate='2015-06-01', close_return=0.55),
            _jump(symbol='EARN', news_filter='drop_earnings', cause_class='1_earnings',
                  jump_cause='earnings', prev_close=3.0),
        ], etf_denylist=etf, option_present=present)
        by_sym = {r['symbol']: r for r in rows}
        self.assertEqual(by_sym['PENY']['news_filter'], 'drop_sub_5')
        self.assertEqual(by_sym['UVXY']['news_filter'], 'drop_etf')
        self.assertEqual(by_sym['MISS']['news_filter'], 'drop_no_option')
        self.assertEqual(by_sym['OKAY']['news_filter'], 'pending_news_review')
        self.assertTrue(by_sym['OKAY']['has_option'])
        self.assertEqual(by_sym['EARN']['news_filter'], 'drop_earnings')

    def test_queue_requires_ge50_cik_option_and_excludes_extreme_from_first_batch(self):
        from pathlib import Path
        rows = [
            _jump(symbol='OKAY', close_return=0.55, prev_close=8.0, has_option=True,
                  news_filter='pending_news_review'),
            _jump(symbol='LOW', close_return=0.40, prev_close=8.0, has_option=True,
                  news_filter='pending_news_review', qdate='2015-06-02'),
            _jump(symbol='BIG', close_return=1.2, prev_close=9.0, has_option=True,
                  news_filter='pending_news_review', qdate='2015-06-03'),
            _jump(symbol='NOCIK', close_return=0.6, prev_close=8.0, has_option=True,
                  cik=None, news_filter='pending_news_review', qdate='2015-06-04'),
        ]
        queue = build_news_queue(rows, Path('.'))
        syms = [r['symbol'] for r in queue]
        self.assertEqual(syms, ['BIG', 'OKAY'])
        first = [r['symbol'] for r in queue if r['include_in_first_news_batch']]
        self.assertEqual(first, ['OKAY'])


if __name__ == '__main__':
    unittest.main()
