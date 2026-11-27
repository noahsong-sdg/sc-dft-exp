import json
from pathlib import Path
import tempfile
import unittest

from resource_accounting import summarize


class ResourceAccountingTest(unittest.TestCase):
    def test_failed_work_is_included_and_unrelated_receipts_are_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, status, wall in (('accepted', 'PASS', 50.), ('stopped', 'FAIL', 17.)):
                folder = root / name
                folder.mkdir()
                (folder / 'receipt.json').write_text(json.dumps(dict(
                    continuous_deadline_s=120, status=status, wall_s=wall,
                    error=None if status == 'PASS' else 'Host memory pressure not normal',
                    exit=0 if status == 'PASS' else -15,
                    max_individual_descendant_rss_bytes=1000,
                    sampled_peak_group_rss_bytes=2000, guard_source_sha256='a' * 64)))
            (root / 'receipt.json').write_text('{"legacy_build": "not a guarded run"}')
            result = summarize(root)
            self.assertEqual(result['total_guarded_wall_s'], 67.)
            self.assertEqual(result['totals']['FAIL'], dict(attempts=1, wall_s=17.))
            self.assertEqual(len(result['attempts']), 2)
            self.assertTrue(all(len(row['receipt_sha256']) == 64 for row in result['attempts']))

    def test_unavailable_inventory_is_not_zero_compute(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                summarize(Path(directory) / 'absent')


if __name__ == '__main__':
    unittest.main()
