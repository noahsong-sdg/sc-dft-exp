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
