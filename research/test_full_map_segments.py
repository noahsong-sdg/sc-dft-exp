import array
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from full_map_segments import certify, stage
from verify_gap_candidate_v2 import verify
import test_full_map_segment_analysis as fixtures


class FullMapSegmentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.FullMapSegmentAnalysisTests.setUpClass()
        cls.fixture = fixtures.FullMapSegmentAnalysisTests()

    @classmethod
    def tearDownClass(cls):
        fixtures.FullMapSegmentAnalysisTests.tearDownClass()

    def prepare(self, root):
        previous, manifest = self.fixture.prepare(root)
        result = root/'qualified-result.json'
        result.write_text(json.dumps(certify(manifest)))
        return previous, manifest, result

    def run_segment(self, root, manifest):
        run = subprocess.run(manifest['command'], cwd=root, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        output = root/'results/moment'; output.mkdir(parents=True)
        (output/'console.log').write_text(run.stdout)
        (output/'receipt.json').write_text(json.dumps(dict(status='PASS', exit=0, error=None,
            wall_s=.01, cwd=str(root), command=manifest['command'],
            max_individual_descendant_rss_bytes=100000, sampled_peak_group_rss_bytes=100000,
            guard_source_sha256=manifest['guard_source_sha256'], continuous_deadline_s=manifest['guard_seconds'])))
        path = root.parent/'segment-public.json'; path.write_text(json.dumps(manifest))
        return path

    def test_separate_process_continues_qualified_chain_and_final_output(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); previous, mp, recorded = self.prepare(base)
            root = base/'segment'
            manifest = stage(mp, recorded, root, 67)
            public = self.run_segment(root, manifest)
            checked = certify(public)
            self.assertTrue(checked['complete_left_row_coverage'])
            self.assertEqual(checked['lineage_depth'], 1)
            self.assertEqual(checked['normalization_readback']['max_absolute_difference'], 0.)
            self.assertFalse(checked['full_candidate']['stationary_residual_targets_met'])
            original = base/'original'; original.mkdir()
            self.fixture.fixture.require_pass(original, 'original')
            self.assertEqual((root/'full-map.bin').read_bytes(), (original/'full-map.bin').read_bytes())

    def test_modified_certified_parent_and_invalid_admission_create_no_output(self):
        for change in ('image', 'receipt', 'result', 'last', 'deadline'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as folder:
                base = Path(folder); previous, mp, recorded = self.prepare(base)
                if change == 'image':
                    path = previous/'linear-image-checkpoint.bin'; values = array.array('d')
                    values.frombytes(path.read_bytes()); values[0] += .01; path.write_bytes(values.tobytes())
                if change == 'receipt':
                    path = previous/'results/moment/receipt.json'; data = json.loads(path.read_text())
                    data['wall_s'] = .02; path.write_text(json.dumps(data))
                if change == 'result':
                    data = json.loads(recorded.read_text()); data['checkpoint']['sha256']['linear-image-checkpoint.bin'] = '0'*64
                    recorded.write_text(json.dumps(data))
                root = base/'segment'
                with self.assertRaises(ValueError):
                    stage(mp, recorded, root, 64 if change == 'last' else 67,
                          guard_seconds=481 if change == 'deadline' else 480)
                self.assertFalse(root.exists())

    def test_passing_fabricated_residual_cannot_bypass_checkpoint_normalization(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); _, mp, recorded = self.prepare(base)
            root = base/'segment'; manifest = stage(mp, recorded, root, 67)
            public = self.run_segment(root, manifest)
            values = array.array('d'); values.frombytes((root/'full-map.bin').read_bytes())
            n = 142
            values[n:2*n] = array.array('d', [0.]*n)
            (root/'full-map.bin').write_bytes(values.tobytes())
            lines = (root/'full-map.txt').read_text().splitlines()
            for i in (3, 4):
                fields = lines[i].split(); fields[1:3] = ['0', '0']; lines[i] = ' '.join(fields)
            (root/'full-map.txt').write_text('\n'.join(lines)+'\n')
            self.assertTrue(verify(root, public)['stationary_residual_targets_met'])
            with self.assertRaisesRegex(ValueError, 'normalized output'):
                certify(public)


if __name__ == '__main__':
    unittest.main()
