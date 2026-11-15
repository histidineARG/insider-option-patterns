import unittest
from datetime import date, timedelta

from ma_holdout_score import feature_bounds


class HoldoutWindowTests(unittest.TestCase):
    def test_afop_after_close_keeps_the_announcement_session(self):
        sessions = [date(2016, 1, 1) + timedelta(days=i) for i in range(120)]
        index = {day: i for i, day in enumerate(sessions)}
        case = dict(event_date='2016-04-07', trade_start='2016-02-19', announcement_session='after_close')
        start, end = feature_bounds(case, sessions, index)
        self.assertEqual(sessions[end], date(2016, 4, 7))
        self.assertEqual(sessions[start], date(2016, 2, 19))

    def test_before_open_stops_the_session_before_the_headline(self):
        sessions = [date(2013, 1, 1) + timedelta(days=i) for i in range(80)]
        index = {day: i for i, day in enumerate(sessions)}
        case = dict(event_date='2013-02-14', trade_start='2013-02-13', announcement_session='before_open')
        start, end = feature_bounds(case, sessions, index)
        self.assertEqual(sessions[end], date(2013, 2, 13))
        self.assertLess(start, end)


if __name__ == '__main__':
    unittest.main()
