import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import digest
from full_map_segments import OUTPUTS
from stage_segmented_occupation import stage


class StageSegmentedOccupationTests(unittest.TestCase):
    def fixture(self, root):
        full, reduced = root/'full', root/'reduced'
        (full/'results/moment').mkdir(parents=True); reduced.mkdir()
        for name in (*OUTPUTS, 'run-manifest.json', 'full-map.bin', 'full-map.txt',
                     'results/moment/console.log', 'results/moment/receipt.json'):
            (full/name).write_text('fixture bytes')
        for name in ('reduced-control.in', 'reduced-gap.bin', 'reduced-result.txt'):
            (reduced/name).write_text('pinned reduced bytes')
        files = [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in reduced.iterdir()]
        manifest = root/'manifest.json'
        manifest.write_text(json.dumps(dict(cwd=str(full), files=files, operator_context_sha256='a'*64)))
        checked = dict(complete_left_row_coverage=True, full_candidate=dict(stationary_residual_targets_met=False),
                       terminal_guard_pass=True, inputs_unchanged=True, manifest_sha256=digest(manifest),
                       receipt={}, checkpoint=dict(sha256={}), microscopic_split_qualified=False)
        result = root/'result.json'; result.write_text(json.dumps(checked))
        return reduced, manifest, result, checked

    def test_binds_all_outputs_and_reduced_candidate_before_staging(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); reduced, mp, rp, checked = self.fixture(root)
            with patch('stage_segmented_occupation.certify', return_value=checked):
                manifest = stage(mp, rp, reduced, root/'stage')
                pins = {item['path']: item for item in manifest['files']}
                for path in (rp, mp, root/'full/full-map.bin', root/'full/full-map-checkpoint-state.bin',
                             reduced/'reduced-control.in'):
                    self.assertEqual(pins[str(path)]['sha256'], digest(path))
                self.assertEqual(manifest['command'][-1], str(root/'stage/basis'))
                self.assertEqual(manifest['guard_seconds'], 180)
                self.assertFalse((root/'stage/basis').exists())
                with self.assertRaisesRegex(ValueError, 'Fresh'):
                    stage(mp, rp, reduced, root/'stage')
                (reduced/'reduced-control.in').write_text('changed')
                with self.assertRaisesRegex(ValueError, 'outside certified'):
                    stage(mp, rp, reduced, root/'rejected')
                self.assertFalse((root/'rejected').exists())

    def test_partial_or_changed_published_certificate_creates_no_output(self):
        for change in ('partial', 'record'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); reduced, mp, rp, checked = self.fixture(root)
                if change == 'partial': checked['complete_left_row_coverage'] = False
                else:
                    saved = json.loads(rp.read_text()); saved['full_candidate'] = {}
                    rp.write_text(json.dumps(saved))
                with patch('stage_segmented_occupation.certify', return_value=checked):
                    with self.assertRaisesRegex(ValueError, 'Published complete'):
                        stage(mp, rp, reduced, root/'rejected')
                self.assertFalse((root/'rejected').exists())


if __name__ == '__main__':
    unittest.main()
