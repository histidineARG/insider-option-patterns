import unittest

from cik_audit import run, suspicious


class CikAuditTests(unittest.TestCase):
    def test_former_names_prevent_false_suspicious_flag(self):
        self.assertFalse(suspicious('H.J. Heinz', 'Kraft Heinz Foods Co', ['HEINZ H J CO']))
        self.assertTrue(suspicious('Electronics for Imaging', 'SYPRIS SOLUTIONS INC', []))

    def test_run_marks_mismatched_cik_without_network(self):
        from pathlib import Path
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root/'results/reviewed_cohort'
            folder.mkdir(parents=True)
            (folder/'events.json').write_text(json.dumps([
                dict(event_id='EFII:2019-04-15', symbol='EFII', issuer='Electronics for Imaging',
                     issuer_cik='864240')]))
            manifest = run(root, fetch=lambda cik: dict(
                cik='0000864240', name='SYPRIS SOLUTIONS INC', tickers=['SYPR'], former_names=[]))
            self.assertEqual(manifest['suspicious'], 1)


if __name__ == '__main__':
    unittest.main()
