from datetime import date
import unittest

from insider_resolved import expiry_class, in_sleeve, is_large, own_threshold, same_contract_oi, score_day


def call(day, strike, volume, oi, spot, delta, expiry, bid=0.4, ask=0.5):
    return dict(qdate=day, strike=strike, edate=expiry, volume=volume, oi=oi,
                delta=delta, underlying_last=spot, bid=bid, ask=ask)


class ResolvedRuleTests(unittest.TestCase):
    day = date(2013, 2, 13)
    expiry = date(2013, 6, 22)
    event = date(2013, 2, 14)
    quiet = {'monthly': 100}

    def judge(self, rows, nxt=None, move=-0.007, thresholds=None, event=None):
        return score_day(rows, nxt or [], move, thresholds or self.quiet, event or self.event)

    def test_saturday_after_the_third_friday_is_the_old_monthly(self):
        self.assertEqual(expiry_class(date(2013, 6, 22)), 'monthly')
        self.assertEqual(expiry_class(date(2013, 6, 21)), 'weekly')
        self.assertEqual(expiry_class(date(2015, 6, 19)), 'monthly')
        self.assertEqual(expiry_class(date(2015, 6, 12)), 'weekly')

    def test_heinz_shaped_print_is_large(self):
        row = call(self.day, 65, 2593, 364, 60.47, 0.17, self.expiry)
        self.assertTrue(in_sleeve(row))
        self.assertTrue(is_large(2593, 364, None))
        scored = self.judge([row])
        self.assertTrue(scored['hit'])
        self.assertEqual(scored['contracts'], 1)

    def test_a_normal_print_for_a_busy_name_does_not_qualify(self):
        row = call(self.day, 65, 200, 10, 60.47, 0.17, self.expiry)
        self.assertEqual(own_threshold([500] * 40), 1500)
        self.assertFalse(self.judge([row], thresholds={'monthly': 1500})['hit'])

    def test_kraft_sized_print_is_not_large(self):
        self.assertFalse(is_large(361, 20229, 20200))

    def test_next_day_open_interest_confirms_a_print(self):
        row = call(date(2016, 8, 18), 82.5, 211, 162, 76.16, 0.31, date(2016, 9, 16))
        nxt = call(date(2016, 8, 19), 82.5, 14, 329, 76.11, 0.29, date(2016, 9, 16))
        self.assertTrue(is_large(211, 162, 329))
        scored = self.judge([row], [nxt], 0.0, event=date(2016, 8, 22))
        self.assertTrue(scored['hit'])

    def test_far_out_of_the_money_zero_delta_stays_in_the_sleeve(self):
        row = call(date(2024, 1, 10), 30, 200, 23, 22.4, 0.0, date(2024, 3, 15), bid=0.05, ask=0.40)
        self.assertTrue(in_sleeve(row))

    def test_a_fifteen_percent_stock_day_does_not_count(self):
        row = call(self.day, 65, 2593, 364, 60.47, 0.17, self.expiry)
        scored = self.judge([row], move=0.20)
        self.assertFalse(scored['hit'])
        self.assertEqual(scored['reason'], 'stock_already_moved')

    def test_volume_is_not_pooled_across_expiries(self):
        june = call(self.day, 65, 60, 10, 60, 0.2, date(2013, 6, 22))
        september = call(self.day, 65, 60, 10, 60, 0.2, date(2013, 9, 21))
        self.assertFalse(self.judge([june, september])['hit'])

    def test_a_different_expiry_cannot_confirm_open_interest(self):
        bought = call(self.day, 65, 150, 400, 60, 0.2, date(2013, 6, 22))
        other_month = call(date(2013, 2, 14), 65, 10, 900, 60, 0.2, date(2013, 3, 16))
        self.assertIsNone(same_contract_oi(bought, [other_month]))
        self.assertFalse(self.judge([bought], [other_month])['hit'])

    def test_expiry_day_is_not_a_position_change(self):
        bought = call(date(2013, 6, 20), 65, 150, 400, 60, 0.2, date(2013, 6, 21))
        expired = call(date(2013, 6, 21), 65, 0, 0, 60, 0.0, date(2013, 6, 21))
        self.assertIsNone(same_contract_oi(bought, [expired]))
        self.assertFalse(self.judge([bought], [expired], event=date(2013, 6, 20))['hit'])

    def test_more_than_three_contracts_is_a_broad_lift(self):
        rows = [call(self.day, 60 + i, 200, 10, 55, 0.3, self.expiry) for i in range(4)]
        scored = self.judge(rows)
        self.assertFalse(scored['hit'])
        self.assertEqual(scored['reason'], 'broad_chain')


if __name__ == '__main__':
    unittest.main()
