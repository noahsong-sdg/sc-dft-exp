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

    def test_guarded_build_failure_counts_despite_old_native_only_description(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'public-response-build-control-001/results/build'
            path.mkdir(parents=True)
            (path/'receipt.json').write_text(json.dumps(dict(
                continuous_deadline_s=1200, status='FAIL', wall_s=16.464,
                command=['python3', 'build_public_response.py', 'fresh-build'],
                cwd=str(path.parent.parent), error='Native command exit 1', exit=1,
                max_individual_descendant_rss_bytes=41877504,
                sampled_peak_group_rss_bytes=41451520, guard_source_sha256='b'*64)))
            result = summarize(directory)
            self.assertEqual(result['total_guarded_wall_s'], 16.464)
            self.assertEqual(result['totals']['FAIL']['attempts'], 1)
            self.assertIn('includes builds or downloads', result['scope'])

    def test_unavailable_inventory_is_not_zero_compute(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                summarize(Path(directory) / 'absent')


if __name__ == '__main__':
    unittest.main()
