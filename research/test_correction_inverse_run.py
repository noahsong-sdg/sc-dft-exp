"""Owning runner boundaries; synthetic basis, real streamed solve, no material claim."""
import array
from contextlib import chdir
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import correction_inverse_run as runner
from inverse_material_run import identity
import test_stream_inverse_action as basis_fixture


class CorrectionInverseRunTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();inverse=base/'inverse';inverse.mkdir()
        basis,_,_,d,m=basis_fixture.StreamInverseActionTest().fixture(inverse)
        payload=array.array('d',d+[0.]*8+m+[1.,1.]);(inverse/'inverse-result.bin').write_bytes(payload.tobytes())
        root=base/'run';root.mkdir();source=base/'source';source.write_text('immutable')
        manifest=dict(cwd=str(root),command=[sys.executable,str(Path(runner.__file__).resolve())],files=[identity(source)])
        (root/'run-manifest.json').write_text(json.dumps(manifest))
        binding=dict(direction=array.array('d',[1.,-.5,.2,.1]),step=1e-9)
        states=dict(jacobian=array.array('d',[-.1,.2,-.3,.4]),residuals=[array.array('d',[0.]*4),array.array('d',[1e-12,-2e-12,3e-12,4e-12])])
        return root,manifest,(inverse,basis,4,2,binding,states),source

    def test_owned_real_action_roundtrip_and_terminal_withheld(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,data,_=self.fixture(Path(directory))
            with chdir(root),patch.object(runner,'validate',return_value=data):result=runner.run(root)
            self.assertFalse(result['terminal_guard_pass'])
            self.assertFalse(result['conditioned_gap_error_bounded'])
            self.assertEqual((root/'inverse-actions.bin').stat().st_size,96)
            self.assertGreater(result['correction_direction_inverse_defect_ratio'],0)
            with chdir(root),patch.object(runner,'validate') as validate:
                with self.assertRaisesRegex(ValueError,'Fresh'):runner.run(root)
                validate.assert_not_called()

    def test_owner_command_and_changed_input_do_not_produce_accepted_readback(self):
        for mutation in ('owner','command','input','native'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root,m,data,source=self.fixture(Path(directory))
                if mutation=='command':
                    m['command']=['other'];(root/'run-manifest.json').write_text(json.dumps(m))
                if mutation=='native':
                    payload=data[0]/'inverse-result.bin';a=array.array('d');a.frombytes(payload.read_bytes());a[4]=1e-10;payload.write_bytes(a.tobytes())
                def apply(*args):
                    answer=original(*args);source.write_text('changed');return answer
                original=runner.apply
                with chdir(root.parent if mutation=='owner' else root),patch.object(runner,'validate',return_value=data), \
                     patch.object(runner,'apply',side_effect=apply if mutation=='input' else original):
                    with self.assertRaises(ValueError):runner.run(root)
                self.assertFalse((root/'inverse-action-readback.json').exists())

    def parent(self,base):
        base=base.resolve();prior=base/'full';(prior/'results/moment').mkdir(parents=True)
        source=base/'input';source.write_text('frozen')
        m=dict(cwd=str(prior),files=[identity(source)])
        mp=base/'full-manifest.json';mp.write_text(json.dumps(m));(prior/'run-manifest.json').write_bytes(mp.read_bytes())
        for name in ('full-map.bin','full-map.txt','linear-image-checkpoint.meta','linear-image-checkpoint.bin',
                     'full-map-checkpoint.meta','full-map-checkpoint-state.bin','results/moment/receipt.json'):
            (prior/name).write_text('synthetic')
        rp=base/'full-result.json';rp.write_text('{}');return mp,rp

    def test_stage_fresh_closure_and_stale_consumed_parent(self):
        for stale in (False,True):
            with self.subTest(stale=stale),tempfile.TemporaryDirectory() as directory:
                base=Path(directory).resolve();mp,rp=self.parent(base);prior=Path(json.loads(mp.read_text())['cwd']);root=base/'run'
                if stale:(prior/'run-manifest.json').write_text('{}')
                if stale:
                    with self.assertRaisesRegex(ValueError,'consumed'):runner.stage(mp,rp,root)
                    self.assertFalse(root.exists())
                else:
                    m=runner.stage(mp,rp,root)
                    self.assertIn(identity(prior/'full-map.bin'),m['files'])
                    self.assertEqual(m['guard_seconds'],90)
                    with self.assertRaisesRegex(ValueError,'Fresh'):runner.stage(mp,rp,root)

    def test_validator_rejects_changed_recorded_result_and_incomplete_coverage(self):
        for mutation in ('recorded','partial','closure'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                base=Path(directory).resolve();mp,rp=self.parent(base);root=base/'run';m=runner.stage(mp,rp,root)
                checked=dict(terminal_guard_pass=True,complete_left_row_coverage=mutation!='partial',full_native_residual_verified=True)
                rp.write_text(json.dumps(checked if mutation!='recorded' else dict(checked,terminal_guard_pass=False)))
                m['files']=[identity(x['path']) for x in m['files']]
                if mutation=='closure':m['files']=[x for x in m['files'] if x['path']!=str(base/'input')]
                with patch.object(runner,'certify',return_value=checked):
                    with self.assertRaises(ValueError):runner.validate(root,m)
