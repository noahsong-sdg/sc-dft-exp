"""Saved-data ownership/closure/receipt boundaries and separate-probe sign control."""
import array
from contextlib import chdir
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import secant_inverse_run as runner
from fetch_public_response_inputs import digest
from inverse_material_run import identity


def write(path,value):path.write_text(json.dumps(value));return path


class SecantInverseRunTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();prior=base/'prior';prior.mkdir();inverse=base/'inverse';inverse.mkdir();old=base/'old';old.mkdir()
        (prior/'results/inverse').mkdir(parents=True)
        (inverse/'inverse-control.in').write_text('header\nbasis\ngeometry\n'+str(old)+'\n')
        (inverse/'inverse-result.bin').write_bytes(array.array('d',[1,1,.3,.4,0,0]).tobytes())
        (old/'full-map.bin').write_bytes(array.array('d',[2,3,.3,.4,0,1,0,-1]).tobytes())
        actions=array.array('d',[1,1,.1,.2,.3,.4]);(prior/'inverse-actions.bin').write_bytes(actions.tobytes())
        parent=dict(cwd=str(prior),command=['frozen'],files=[identity(inverse/'inverse-result.bin'),identity(old/'full-map.bin'),
                    identity(Path(runner.__file__).resolve()),identity(runner.RESEARCH/'secant_inverse_action.py')],
                    guard_seconds=90,group_rss_cap_bytes=3221225472,guard_source_sha256='guard')
        mp=write(base/'parent.json',parent);(prior/'run-manifest.json').write_bytes(mp.read_bytes())
        receipt=dict(status='PASS',exit=0,error=None,command=parent['command'],cwd=str(prior),guard_source_sha256='guard',
                     continuous_deadline_s=90,wall_s=20,max_individual_descendant_rss_bytes=100,sampled_peak_group_rss_bytes=100)
        write(prior/'results/inverse/receipt.json',receipt)
        raw=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),
                 independent_action_max_errors=[0.]*3,independent_action_bounds=[1e-12]*3,
                 outputs_sha256={'inverse-actions.bin':digest(prior/'inverse-actions.bin')},
                 correction_direction_inverse_defect_ratio=1.,frozen_inverse_plus_residual_infinity_ry=.2,
                 frozen_inverse_plus_residual_over_original_correction=.5,
                 original_native_correction_max_difference_ry=0.,original_native_correction_bound_ry=1e-12)
        rawpath=write(prior/'inverse-action-readback.json',raw)
        rp=write(base/'result.json',dict(raw,terminal_guard_pass=True,receipt=receipt,readback_sha256=digest(rawpath)))
        root=base/'run';m=runner.stage(mp,rp,root)
        context=(inverse,base/'unused',2,1,dict(direction=array.array('d',[1,0]),step=.4),
                 dict(jacobian=array.array('d',[-1,-1]),residuals=[array.array('d',[.3,.4]),array.array('d',[.1,.2])]))
        return root,m,context

    def test_real_update_roundtrip_and_separate_probe(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,context=self.fixture(Path(directory))
            with chdir(root),patch.object(runner,'full_context',return_value=context):result=runner.run(root)
            self.assertFalse(result['terminal_guard_pass']);self.assertFalse(result['conditioned_gap_error_bounded'])
            self.assertEqual(result['training_defect_after'],0.)
            self.assertEqual(result['separate_probe_defect_before'],0.)
            self.assertEqual(result['separate_probe_defect_after'],.5)
            self.assertEqual((root/'secant-actions.bin').stat().st_size,96)
            with chdir(root),self.assertRaisesRegex(ValueError,'Fresh'):runner.run(root)

    def test_stale_parent_receipt_result_closure_and_metric_rejected(self):
        for mutation in ('pin','closure','receipt','recorded','metric','oldbase','equation'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root,m,context=self.fixture(Path(directory));mp=Path(m['diagnostic_manifest'])
                prior=Path(json.loads(mp.read_text())['cwd']);rp=Path(m['diagnostic_result'])
                if mutation=='pin':(prior/'inverse-actions.bin').write_bytes(b'stale')
                if mutation=='closure':m['files']=[x for x in m['files'] if x['path']!=str(context[0]/'inverse-result.bin')]
                if mutation in ('receipt','recorded','metric','equation'):
                    path=prior/'results/inverse/receipt.json' if mutation=='receipt' else rp
                    data=json.loads(path.read_text())
                    if mutation=='receipt':data['status']='FAIL'
                    if mutation=='recorded':data['terminal_guard_pass']=False
                    if mutation=='metric':data['correction_direction_inverse_defect_ratio']=0.
                    if mutation=='equation':data['independent_action_bounds']=[float('inf')]*3
                    write(path,data)
                    if mutation=='equation':
                        rawpath=prior/'inverse-action-readback.json';raw=json.loads(rawpath.read_text())
                        raw['independent_action_bounds']=data['independent_action_bounds'];write(rawpath,raw)
                        data['readback_sha256']=digest(rawpath);write(rp,data)
                    m['files']=[identity(x['path']) for x in m['files']]
                if mutation=='oldbase':context[-1]['residuals'][0][0]=.5
                with patch.object(runner,'full_context',return_value=context),self.assertRaises(ValueError):runner.accepted(m)

    def test_fresh_owner_command_and_changed_final_pins(self):
        for mutation in ('owner','command','final'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root,m,context=self.fixture(Path(directory))
                if mutation=='command':m['command']=['other'];write(root/'run-manifest.json',m)
                original=runner.action
                def changed(*args):
                    result=original(*args);Path(m['diagnostic_result']).write_text('{}');return result
                with chdir(root.parent if mutation=='owner' else root),patch.object(runner,'full_context',return_value=context), \
                     patch.object(runner,'action',side_effect=changed if mutation=='final' else original):
                    with self.assertRaises(ValueError):runner.run(root)
                self.assertFalse((root/'secant-readback.json').exists())
