"""Owning preparation source boundaries and actual compact action calibration."""
import array
from contextlib import chdir
from fractions import Fraction as F
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import prepare_compact_defect as runner
from fetch_public_response_inputs import digest
from inverse_material_run import identity
import test_compact_defect_state as compact_fixture


def write(path,value):path.write_text(json.dumps(value));return path


class PrepareCompactDefectTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();old,basis,q,u,vectors,_=compact_fixture.CompactDefectStateTest().fixture(base)
        prior=base/'prior';(prior/'results/inverse').mkdir(parents=True)
        source=base/'source';source.write_text('immutable')
        parent=dict(cwd=str(prior),command=['accepted'],files=[identity(source)],guard_seconds=90,group_rss_cap_bytes=3221225472,guard_source_sha256='guard')
        mp=write(base/'source-manifest.json',parent);(prior/'run-manifest.json').write_bytes(mp.read_bytes())
        receipt=dict(status='PASS',exit=0,error=None,command=['accepted'],cwd=str(prior),continuous_deadline_s=90,
                     wall_s=20,guard_source_sha256='guard',max_individual_descendant_rss_bytes=100,sampled_peak_group_rss_bytes=100)
        write(prior/'results/inverse/receipt.json',receipt)
        (prior/'inverse-actions.bin').write_bytes(array.array('d',[0.]*18).tobytes())
        raw=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),outputs_sha256={'inverse-actions.bin':digest(prior/'inverse-actions.bin')},independent_action_max_errors=[0.]*3,independent_action_bounds=[1e-12]*3)
        rawpath=write(prior/'inverse-action-readback.json',raw)
        rp=write(base/'source-result.json',dict(raw,terminal_guard_pass=True,receipt=receipt,readback_sha256=digest(rawpath)))
        root=base/'prepare';m=runner.stage(mp,rp,root)
        rhss=[[1.,0,0,-.5,.25,.125],[1e-12,2e-12,0,4e-12,5e-12,6e-12],[2e-11,3e-11,0,-1e-11,4e-11,2e-11]]
        w=[.8,-.2,-.6,.4];expected=array.array('d')
        # Independent full padded B; inactive Q/U/D zeros preserve identity there.
        b=[[F(i==j)+sum(F(u[k][i])*F(w[l*2+k])*F(q[l][j])*F(vectors[4][j]) for k in range(2) for l in range(2)) for j in range(6)] for i in range(6)]
        for rhs in rhss:expected.extend(float(sum(x*F(y) for x,y in zip(row,rhs))) for row in b)
        data=(basis,vectors,[2.,1,3,4],[2,3,3],2,1.25,'a'*64,rhss,expected)
        return root,m,data,source

    def test_real_compaction_and_chosen_W_roundtrip_terminal_withheld(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,data,_=self.fixture(Path(directory))
            with chdir(root),patch.object(runner,'inputs',return_value=data):result=runner.run(root)
            self.assertFalse(result['terminal_guard_pass']);self.assertFalse(result['conditioned_gap_error_bounded'])
            self.assertEqual(result['active_states'],5)
            self.assertEqual(len(result['recipe']['calibration_max_errors']),3)
            with chdir(root),patch.object(runner,'inputs') as inputs:
                with self.assertRaisesRegex(ValueError,'Fresh'):runner.run(root)
                inputs.assert_not_called()

    def test_owner_reference_and_changed_final_input_rejected(self):
        for mode in ('owner','reference','final'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as directory:
                root,m,data,source=self.fixture(Path(directory))
                if mode=='reference':data[-1][0]+=1
                original=runner.actions
                def action(*args):
                    result=original(*args);source.write_text('changed');return result
                with chdir(root.parent if mode=='owner' else root),patch.object(runner,'inputs',return_value=data), \
                     patch.object(runner,'actions',side_effect=action if mode=='final' else original):
                    with self.assertRaises(ValueError):runner.run(root)
                self.assertFalse((root/'compact-preparation-result.json').exists())

    def test_source_receipt_closure_recorded_and_cap_rejected_before_context(self):
        for mode in ('receipt','closure','recorded','cap'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as directory:
                root,m,data,source=self.fixture(Path(directory));mp=Path(m['source_manifest']);rp=Path(m['source_result']);prior=Path(json.loads(mp.read_text())['cwd'])
                if mode=='closure':m['files']=[x for x in m['files'] if x['path']!=str(source)]
                if mode=='recorded':result=json.loads(rp.read_text());result['terminal_guard_pass']=False;write(rp,result)
                if mode in ('receipt','cap'):
                    path=prior/'results/inverse/receipt.json';receipt=json.loads(path.read_text())
                    if mode=='receipt':receipt['status']='FAIL'
                    else:receipt['max_individual_descendant_rss_bytes']=4*1024**3
                    write(path,receipt);result=json.loads(rp.read_text());result['receipt']=receipt;write(rp,result)
                m['files']=[identity(x['path']) for x in m['files']]
                with patch.object(runner,'full_context') as context:
                    with self.assertRaises(ValueError):runner.inputs(m)
                    context.assert_not_called()
