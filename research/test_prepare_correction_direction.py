"""Normalized payload roundtrip and immutable inverse receipt/readback boundaries."""
import array
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import prepare_correction_direction as prepare
from fetch_public_response_inputs import digest


class PrepareCorrectionDirectionTest(unittest.TestCase):
    def test_payload_scale_rounding_and_candidate_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();gap=array.array('d',[.001,.002,0,.003,.004,.005])
            correction=array.array('d',[-1e-10,2e-10,0,3e-10,-4e-10,1e-10])
            before=gap.tobytes(),correction.tobytes()
            result=prepare.write_direction(root,gap,correction,[2,3,3],1000,'a'*64)
            self.assertEqual(result['step_ry'],4e-10)
            self.assertEqual(result['direction_infinity'],1)
            data=array.array('d');data.frombytes((root/'direction-state.bin').read_bytes())
            self.assertEqual(data[:6].tobytes(),gap.tobytes())
            self.assertEqual(result['rescaled_correction_max_absolute_difference_ry'],
                             max(abs(result['step_ry']*v-c) for v,c in zip(data[6:],correction)))
            self.assertEqual(before,(gap.tobytes(),correction.tobytes()))
            with self.assertRaisesRegex(ValueError,'Fresh'):
                prepare.write_direction(root,gap,correction,[2,3,3],1000,'a'*64)

    def test_invalid_context_state_and_padding_create_no_output(self):
        for name in ('counts','nan','zero','padding','beta','operator','overflow'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as directory:
                root=Path(directory).resolve();gap=[1.,0.,1.,1.];corr=[1e-10,0.,-2e-10,3e-10]
                counts=[1,2,2];beta=1000;operator='a'*64
                if name=='counts':counts=[1,2]
                if name=='nan':corr[0]=float('nan')
                if name=='zero':corr=[0.]*4
                if name=='padding':corr[1]=1e-10
                if name=='beta':beta=float('inf')
                if name=='operator':operator='g'*64
                if name=='overflow':corr[0]=1e308
                with self.assertRaises(ValueError):prepare.write_direction(root,gap,corr,counts,beta,operator)
                self.assertFalse(any(root.iterdir()))

    def inverse(self,root):
        prior=root/'inverse';(prior/'results/inverse').mkdir(parents=True)
        manifest=dict(cwd=str(prior),command=['python','inverse'],files=[],guard_source_sha256='a'*64,
                      guard_seconds=90,group_rss_cap_bytes=3221225472)
        path=root/'manifest.json';path.write_text(json.dumps(manifest))
        (prior/'run-manifest.json').write_bytes(path.read_bytes())
        payload=prior/'inverse-result.bin';payload.write_bytes(b'bound output')
        receipt=dict(status='PASS',exit=0,error=None,command=manifest['command'],cwd=str(prior),
                     guard_source_sha256='a'*64,continuous_deadline_s=90,wall_s=1,
                     max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=2048)
        (prior/'results/inverse/receipt.json').write_text(json.dumps(receipt))
        arithmetic=dict(full_source_residual_targets_met=True,correction_infinity_ry=1e-10,
                        outputs_sha256={'inverse-result.bin':digest(payload)})
        raw=dict(arithmetic,terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(path),scope='raw')
        (prior/'inverse-readback.json').write_text(json.dumps(raw))
        result=dict(raw,terminal_guard_pass=True,receipt=receipt,readback_sha256=digest(prior/'inverse-readback.json'))
        result_path=root/'result.json';result_path.write_text(json.dumps(result))
        return path,result_path,manifest,arithmetic

    def test_replay_owner_and_stale_receipt_output_readback(self):
        for mutation in ('none','guard','deadline','output','terminal','arithmetic','consumed'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root=Path(directory).resolve();path,result,m,a=self.inverse(root);prior=Path(m['cwd'])
                if mutation in ('guard','deadline'):
                    p=prior/'results/inverse/receipt.json';r=json.loads(p.read_text())
                    r['guard_source_sha256' if mutation=='guard' else 'continuous_deadline_s']='b'*64 if mutation=='guard' else 91
                    p.write_text(json.dumps(r))
                if mutation=='output':(prior/'inverse-result.bin').write_bytes(b'stale bytes')
                if mutation=='terminal':
                    r=json.loads(result.read_text());r['terminal_guard_pass']=False;result.write_text(json.dumps(r))
                if mutation=='consumed':(prior/'run-manifest.json').write_text('{}')
                if mutation=='arithmetic':a=dict(a,correction_infinity_ry=2e-10)
                before=Path.cwd()
                def validate(owner):
                    self.assertEqual(Path.cwd(),prior);self.assertEqual(owner,prior);return m
                with patch.object(prepare,'validate_inverse',side_effect=validate), \
                     patch.object(prepare,'inverse_arithmetic',return_value=a):
                    if mutation=='none':self.assertEqual(prepare.certify_inverse(path,result),(m,a))
                    else:
                        with self.assertRaises(ValueError):prepare.certify_inverse(path,result)
                self.assertEqual(Path.cwd(),before)
