"""Contiguous real native correction-step restart and final normalization controls."""
import array
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from full_step_segments import certify, stage
from verify_gap_candidate_step import verify
import test_full_step_segment_analysis as fixtures
import test_full_map_segments as old_tests


class FullStepSegmentsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.FullStepSegmentAnalysisTest.setUpClass.__func__(cls)

    run_segment=old_tests.FullMapSegmentsTests.run_segment

    def prepare(self,base):
        root,mp,preparation=fixtures.FullStepSegmentAnalysisTest.prepare(self,base)
        self.preparation_patch=patch('full_step_segment_analysis.certify_direction',return_value=preparation)
        self.preparation_patch.start();self.addCleanup(self.preparation_patch.stop)
        result=base/'qualified-result.json';result.write_text(json.dumps(certify(mp)))
        return root,mp,result

    record=fixtures.FullStepSegmentAnalysisTest.record

    def test_complete_coverage_and_actual_perturbed_residuals(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);_,mp,recorded=self.prepare(base)
            root=base/'segment';m=stage(mp,recorded,root,67);public=self.run_segment(root,m)
            checked=certify(public)
            self.assertTrue(checked['complete_left_row_coverage'])
            self.assertEqual(checked['lineage_depth'],1)
            self.assertEqual(checked['normalization_readback']['max_absolute_difference'],0)
            correction=checked['correction_readback']
            self.assertEqual(correction['step_ry'],5.502435566805578e-10)
            self.assertAlmostEqual(correction['base']['residual_infinity_ry'],checked['full_candidate']['residual_infinity_ry'])
            self.assertFalse(correction['physical_response_verified'])
            self.assertFalse(correction['conditioned_gap_error_bounded'])
            self.assertNotEqual(correction['base'],correction['plus'])
            self.assertLessEqual(correction['independent_fd_error'],correction['independent_fd_bound'])

    def test_stale_parent_step_and_invalid_admission(self):
        for mutation in ('image','receipt','result','last','deadline','step'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                base=Path(directory);previous,mp,recorded=self.prepare(base)
                if mutation=='image':
                    p=previous/'linear-image-checkpoint.bin';a=array.array('d');a.frombytes(p.read_bytes());a[0]+=.01;p.write_bytes(a.tobytes())
                elif mutation=='receipt':
                    p=previous/'results/moment/receipt.json';r=json.loads(p.read_text());r['wall_s']=.02;p.write_text(json.dumps(r))
                elif mutation=='result':
                    r=json.loads(recorded.read_text());r['checkpoint']['sha256']['linear-image-checkpoint.bin']='0'*64;recorded.write_text(json.dumps(r))
                elif mutation=='step':(previous/'full-map-step.in').write_text('declared-full-map-step-v1\n1e-8\n')
                root=base/'segment'
                with self.assertRaises(ValueError):stage(mp,recorded,root,64 if mutation=='last' else 67,guard_seconds=481 if mutation=='deadline' else 480)
                self.assertFalse(root.exists())

    def test_fabricated_passing_residual_rejects_against_native_images(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);_,mp,recorded=self.prepare(base)
            root=base/'segment';m=stage(mp,recorded,root,67);public=self.run_segment(root,m)
            a=array.array('d');a.frombytes((root/'full-map.bin').read_bytes());a[142:284]=array.array('d',[0.])*142
            (root/'full-map.bin').write_bytes(a.tobytes())
            p=root/'full-map.txt';lines=p.read_text().splitlines()
            for index in (3,4):
                fields=lines[index].split();fields[1:3]=['0','0'];lines[index]=' '.join(fields)
            p.write_text('\n'.join(lines)+'\n')
            self.assertTrue(verify(root,public)['stationary_residual_targets_met'])
            with self.assertRaisesRegex(ValueError,'normalized output'):certify(public)

    def test_final_direction_cannot_change_with_compensated_jacobian(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);_,mp,recorded=self.prepare(base)
            root=base/'segment';m=stage(mp,recorded,root,67);public=self.run_segment(root,m)
            from full_step_segments import correction_readback
            a=array.array('d');a.frombytes((root/'full-map.bin').read_bytes())
            a[284]+=.01;a[426]-=.01
            (root/'full-map.bin').write_bytes(a.tobytes())
            # The old normalization relation alone accepts simultaneous v/Jv shifts.
            from full_map_segments import normalization_readback
            self.assertEqual(normalization_readback(root)['max_absolute_difference'],0)
            with self.assertRaisesRegex(ValueError,'direction differs'):correction_readback(root)
