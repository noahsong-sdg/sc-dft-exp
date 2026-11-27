import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from verify_gap_candidate import verify


class VerifyGapCandidateTest(unittest.TestCase):
    def test_receipt_identity_exact_seed_and_separate_residual_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            seed=struct.pack('<4d',1,0,1,1)
            (root/'gap-seed.bin').write_bytes(seed)
            (root/'gap-seed.meta').write_text('gap-seed-v1; binary64 Fortran order\n'
                '1 2 2 100 10 50\n1000\n/point\n'+'a'*64+'\n')
            (root/'verify-gap-seed.x').write_bytes(b'fixture identity only')
            manifest=dict(candidate_sha256=hashlib.sha256(seed).hexdigest(),files=[
                dict(path=str(root/n),bytes=(root/n).stat().st_size,
                     sha256=hashlib.sha256((root/n).read_bytes()).hexdigest())
                for n in ('gap-seed.bin','gap-seed.meta','verify-gap-seed.x')])
            path=root/'manifest.json';path.write_text(json.dumps(manifest))
            (root/'results/moment').mkdir(parents=True)
            receipt=dict(status='PASS',exit=0,error=None,wall_s=1,cwd=str(root),
                         command=[str(root/'verify-gap-seed.x')],max_individual_descendant_rss_bytes=100)
            receipt_path=root/'results/moment/receipt.json';receipt_path.write_text(json.dumps(receipt))
            for error,expected in ((1,False),(1e-12,True)):
                (root/'full-map.txt').write_text(
                    '# full-nonlinear-map-v1; imposed seed; NOT a converged gap\n1 2 2 4\n'
                    f'1000 1e-8 1 0 1e-9 4.01e-6\n1 {error} {error} 2\n2 {error} {error} 2\n')
                values=[1,0,1,1,error,0,error,error,1,0,1,1,2,0,2,2]
                payload=struct.pack('<16d',*values)
                (root/'full-map.bin').write_bytes(payload)
                result=verify(root,path)
                self.assertEqual(result['stationary_residual_targets_met'],expected)
                self.assertFalse(result['conditioned_gap_error_bounded'])
                self.assertFalse(result['physical_response_verified'])
            # A different evaluated seed must fail even if summary residuals pass.
            changed=bytearray(payload);struct.pack_into('<d',changed,0,1.01)
            (root/'full-map.bin').write_bytes(changed)
            with self.assertRaisesRegex(ValueError,'different gap'):
                verify(root,path)
            (root/'full-map.bin').write_bytes(payload)
            for bad in (dict(receipt,status='FAIL',exit=1),dict(receipt,cwd='/stale')):
                receipt_path.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):
                    verify(root,path)


if __name__=='__main__':
    unittest.main()
