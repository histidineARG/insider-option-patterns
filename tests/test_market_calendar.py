from datetime import date
import unittest

from market_calendar import sessions


class CalendarTests(unittest.TestCase):
    def test_holidays_and_mourning_are_not_missing_data(self):
        days=set(sessions())
        for day in ['2022-06-20','2023-06-19','2024-06-19','2025-01-09']:
            self.assertNotIn(date.fromisoformat(day),days)
        self.assertIn(date(2026,11,4),days)

    def test_correct_full_year_counts_and_bounds(self):
        self.assertEqual(len(sessions('2014-01-01','2014-12-31')),252)
        self.assertEqual(len(sessions('2025-01-01','2025-12-31')),250)
        with self.assertRaises(ValueError):sessions(end='2027-01-01')


if __name__=='__main__':unittest.main()
