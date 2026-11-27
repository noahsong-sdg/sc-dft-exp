import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import portable_z_sweep as sweep
from fetch_public_response_inputs import digest


class ZSweepAdmissionTest(unittest.TestCase):
    def test_certified_checkpoint_resumes_and_changed_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); build=root/'build'; init=root/'init'; partial=root/'partial'; inputs=root/'inputs'
            for p in (build/'qe',init,partial,inputs,root/'portable_gap'): p.mkdir(parents=True)
            for parent,label,token in [(init,'init','FRESH_GAP_INITIALIZATION_ROUNDTRIP_PASS'),
                    (partial,'zpartial','Z_PARTIAL_DIRECT_CACHED_PASS')]:
                (parent/'run-manifest.json').write_text(json.dumps(dict(command=[label],files=[])))
                out=parent/'results'/label;out.mkdir(parents=True)
                (out/'receipt.json').write_text(json.dumps(dict(status='PASS',exit=0,error=None,command=[label],cwd=str(parent))))
                (out/'console.log').write_text(token+'\n')
            (init/'native-init.bin').write_bytes(b'fresh native data')
            (init/'native-init.meta').write_text('fresh native metadata')
            (init/'native.in').write_text("outdir='"+str(inputs)+"/'")
            (root/'fresh_gap_initialization_result.json').write_text(json.dumps(dict(retained_state_consumed=False,
                exact_own_array_roundtrip=True,state_sha256=digest(init/'native-init.bin'),metadata_sha256=digest(init/'native-init.meta'))))
            (partial/'z-partial.bin').write_bytes(b'partial comparison')
            beta=19613.355577892344
            (root/'portable_z_partial_result.json').write_text(json.dumps(dict(partial_arrays_bitwise_equal=True,
                binary_sha256=digest(partial/'z-partial.bin'),beta=beta)))
            for name in ('public_response_inputs.json','public_gap_coulomb_inputs.json'):
                (root/name).write_text('{"files":{}}')
            for p in (root/'macos_native_guard.py',root/'public_response_probe.mk',build/'build-result.json',build/'qe/make.inc'):
                p.write_text('fixture')
            for name in ('z_sweep_driver.f90','z_checkpoint.f90','z_sweep.mk','z_partial.mk','z_build.mk',
                    'prefix_operator.f90','zsf_workspace.f90','native_rotation.f90','slab_operator.f90',
                    'native_state_io.f90','native_coefficients.f90','hash_stream.c','hash_pipe.c'):
                (root/'portable_gap'/name).write_text('fixture source')
            with patch.object(sweep,'RESEARCH',root):
                previous=root/'qualification'
                m=sweep.stage(build,init,partial,inputs,previous,1,16,qualification=True)
                (previous/'z-checkpoint.meta').write_text('ordered-Z-checkpoint-v1; partial sums, not full Z\n'
                    +m['context_sha256']+'\n66867 67940 67940 16\n'+repr(beta)+'\n')
                (previous/'z-checkpoint.bin').write_bytes(bytes(16*67940))
                out=previous/'results/zsweep';out.mkdir(parents=True)
                (out/'receipt.json').write_text(json.dumps(dict(status='PASS',exit=0,error=None,command=m['command'],
                    cwd=str(previous),continuous_deadline_s=240,wall_s=1,guard_source_sha256=digest(root/'macos_native_guard.py'))))
                (out/'console.log').write_text('Z_SWEEP_CHECKPOINT_PASS\nZ_SWEEP_SPLIT_BITWISE_PASS\n')
                (previous/'z-sweep.x').write_bytes(b'fixture executable')
                sweep.certify(previous)
                resumed=sweep.stage(build,init,partial,inputs,root/'resume',17,32,previous=previous)
                self.assertEqual(resumed['context_sha256'],m['context_sha256'])
                with self.assertRaisesRegex(ValueError,'noncontiguous'):
                    sweep.stage(build,init,partial,inputs,root/'skipped',18,32,previous=previous)
                self.assertFalse((root/'skipped').exists())
                data=bytearray((previous/'z-checkpoint.bin').read_bytes());struct.pack_into('<d',data,0,.25)
                (previous/'z-checkpoint.bin').write_bytes(data)
                with self.assertRaisesRegex(ValueError,'Changed certified'):
                    sweep.stage(build,init,partial,inputs,root/'changed',17,32,previous=previous)
                self.assertFalse((root/'changed').exists())

    def test_interval_and_existing_destination_boundaries(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with self.assertRaisesRegex(ValueError,'Fresh'):
                sweep.stage(root,root,root,root,root,1,16,qualification=True)
            with self.assertRaisesRegex(ValueError,'interval'):
                sweep.stage(root,root,root,root,root/'new',1,40000,qualification=True)
            with self.assertRaisesRegex(ValueError,'predecessor'):
                sweep.stage(root,root,root,root,root/'new',1,16)
