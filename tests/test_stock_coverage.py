from datetime import date, timedelta
import unittest

from stock_coverage import classify


class StockCoverageTests(unittest.TestCase):
    def test_missing_and_sparse_counts_are_not_filled(self):
        calendar=[date(2024,1,1)+timedelta(days=i) for i in range(23)]
        counts={d:4000 for d in calendar[:20]}
        counts[calendar[20]]=1
        counts[calendar[22]]=900
        rows=classify(calendar,counts)
        self.assertEqual(rows[20]['status'],'sparse_session')
        self.assertEqual(rows[21]['status'],'missing_session')
        self.assertEqual(rows[22]['status'],'sparse_session')
        self.assertEqual(rows[20]['prior20_median_rows'],4000)


if __name__=='__main__':unittest.main()
