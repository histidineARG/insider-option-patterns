import json
from pathlib import Path
import tempfile
import unittest

import pymysql

from option_coverage_probe import probes, run


class ProbeTests(unittest.TestCase):
    def test_controls_deduplicated_and_year_boundary_respected(self):
        plan = probes([dict(symbol='OLD', qdate='2023-12-29'),
                       dict(symbol='AAPL', qdate='2024-01-02'),
                       dict(symbol='XYZ', qdate='2024-01-02')], 2024)
        self.assertEqual(len(plan), 4)
        self.assertEqual(plan['AAPL', '2024-01-02'], 'sample_and_control')
        self.assertEqual(plan['XYZ', '2024-01-02'], 'sample')
        self.assertEqual(plan['MSFT', '2024-01-02'], 'control')

    def test_query_failure_is_separate_from_absence_and_transaction_rolled_back(self):
        class Cursor:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def execute(self, sql, args=None):
                self.result = None
                if args and args[0] == 'XYZ':
                    if 'FROM optiondaily3 ' in sql:
                        raise pymysql.OperationalError(1146, 'table unavailable')
                elif args:
                    self.result = dict(present=1)
            def fetchone(self): return self.result

        class Connection:
            rolled_back = False
            def cursor(self): return Cursor()
            def rollback(self): self.rolled_back = True

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'results/background_sample'
            folder.mkdir(parents=True)
            (folder / 'observations.json').write_text(json.dumps([
                dict(symbol='XYZ', qdate='2025-01-02')]))
            (folder / 'sampling_frames.json').write_text(json.dumps([
                dict(qdate='2025-01-02', stockquote_symbols=20000)]))
            c = Connection()
            result = run(c, root)[0]
            self.assertTrue(c.rolled_back)
            self.assertEqual(result['query_failures'], 1)
            self.assertEqual(result['absent_both'], 0)
            self.assertEqual(result['primary_controls_present'], 3)
            self.assertEqual(result['sampled_symbols'], 1)
