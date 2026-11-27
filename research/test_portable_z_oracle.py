import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from portable_z_oracle import completed_sweep


class CompletedZAdmissionTest(unittest.TestCase):
    def fixture(self, root, completed=66867):
        out=root/'results/zsweep';out.mkdir(parents=True)
        context='b'*64
        saved=dict(context=context,counts=[66867,67940,67940],completed=completed,beta=2.0)
        m=dict(command=['fixture'],files=[],context_sha256=context,rows=[17,completed],
            qualified_chain=True,qualification=False)
        r=dict(status='PASS',exit=0,error=None,command=m['command'],cwd=str(root))
        (root/'run-manifest.json').write_text(json.dumps(m))
        (out/'receipt.json').write_text(json.dumps(r))
        (out/'console.log').write_text('Z_SWEEP_CHECKPOINT_PASS\nCHECKED_FULL_Z_FS \n')
        (root/'z-checkpoint.meta').write_text('ordered-Z-checkpoint-v1; partial sums, not full Z\n'
            +context+'\n66867 67940 67940 '+str(completed)+'\n2.0\n')
        (root/'z-checkpoint.bin').write_bytes(bytes(16*67940))
        (root/'full-z.bin').write_bytes(bytes(16*67940))
        (root/'full-z.meta').write_text('native-Z-v1; binary64 Fortran order\n66867 67940 67940 100 1\n2 0 0 0 1 1 0 0\n F\n')
        (root/'z-sweep.x').write_bytes(b'fixture executable')
        result=dict(status='PASS',checkpoint=saved)
        for key,name in [('manifest_sha256','run-manifest.json'),('receipt_sha256','results/zsweep/receipt.json'),
                ('checkpoint_sha256','z-checkpoint.bin'),('metadata_sha256','z-checkpoint.meta'),
                ('executable_sha256','z-sweep.x')]:
            result[key]=digest(root/name)
        (root/'z-sweep-result.json').write_text(json.dumps(result))
        return m

    def test_completed_sums_and_distinct_full_output_are_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            expected=self.fixture(root)
            self.assertEqual(expected,completed_sweep(root))
            (root/'full-z.bin').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'differs from certified'):
                completed_sweep(root)

    def test_partial_checkpoint_is_not_full_Z(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);self.fixture(root,33450)
            with self.assertRaisesRegex(ValueError,'Incomplete'):
                completed_sweep(root)

    def test_stale_full_metadata_and_mutated_checkpoint_rejected(self):
        for mutation in ('temperature','trailing','checkpoint'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);self.fixture(root)
                if mutation=='checkpoint':
                    (root/'z-checkpoint.bin').write_bytes(b'changed')
                else:
                    p=root/'full-z.meta';text=p.read_text()
                    p.write_text(text.replace('100 1','100 2') if mutation=='temperature' else text+'stale\n')
                with self.assertRaises(ValueError):
                    completed_sweep(root)


class ZOracleCertificateTest(unittest.TestCase):
    def test_persisted_samples_bound_to_full_Z_and_mutations_rejected(self):
        import portable_z_oracle as oracle
        import struct
        for mutation in ('none','sample','metadata','receipt'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as folder:
                base=Path(folder);completed=base/'completed';completed.mkdir()
                CompletedZAdmissionTest.fixture(self,completed)
                p=completed/'full-z.meta';p.write_text(p.read_text().replace('2 0 0 0','2 .1 0 0'))
                root=base/'oracle';root.mkdir();out=root/'results/zoracle';out.mkdir(parents=True)
                command=['fixture'];m=dict(command=command,files=[],guard_seconds=420)
                (root/'run-manifest.json').write_text(json.dumps(m))
                (root/'z-oracle-control.in').write_text(str(base/'geometry')+'\n'+str(completed)+'\n')
                receipt=dict(status='PASS',exit=0,error=None,command=command,cwd=str(root),
                    continuous_deadline_s=420,wall_s=1,
                    guard_source_sha256=digest(oracle.RESEARCH/'macos_native_guard.py'))
                if mutation=='receipt':receipt['exit']=7
                (out/'receipt.json').write_text(json.dumps(receipt))
                (out/'console.log').write_text('Z_SIX_UNCACHED_FULL_SUMS_BITWISE_PASS\n')
                rows=['first, last, first positive-dk ABS(xi)<native emin; deduplicated in that order']
                for side,count in ((1,66867),(2,67940)):
                    for number,index in enumerate((1,count,2),1):
                        rows.append(f'{side} {number} {index} 1 1 0 1')
                if mutation=='metadata':rows[-1]='2 3 67940 1 1 0 1'
                (root/'z-samples.meta').write_text('\n'.join(rows)+'\n')
                data=bytearray(96)
                if mutation=='sample':struct.pack_into('<d',data,48,.25)
                (root/'z-oracle-samples.bin').write_bytes(data)
                (root/'z-oracle.x').write_bytes(b'fixture executable')
                if mutation=='none':
                    result=oracle.certify(root)
                    self.assertTrue(result['six_full_sums_bitwise_equal'])
                    self.assertFalse(result['physical_response_verified'])
                    self.assertEqual(len(result['samples']),6)
                    from portable_basis_partial import accepted_oracle
                    _,geometry,source=accepted_oracle(root)
                    self.assertEqual(source,completed)
                    self.assertEqual(geometry,base/'geometry')
                    changed=bytearray(data);struct.pack_into('<d',changed,0,.5)
                    (root/'z-oracle-samples.bin').write_bytes(changed)
                    with self.assertRaisesRegex(ValueError,'Changed or unqualified'):
                        accepted_oracle(root)
                else:
                    with self.assertRaises(ValueError):oracle.certify(root)
                    self.assertFalse((root/'z-oracle-result.json').exists())
