import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from verify_gap_candidate import verify as original_verify
from verify_gap_candidate_v2 import verify


class VerifyGapCandidateV2Tests(unittest.TestCase):
    def fixture(self, root):
        seed = struct.pack('<4d', 1, 0, 1, 1)
        (root/'gap-seed.bin').write_bytes(seed)
        (root/'gap-seed.meta').write_text('gap-seed-v1; binary64 Fortran order\n'
            '1 2 2 100 10 50\n1000\n/point\n'+'a'*64+'\n')
        (root/'verify-gap-seed.x').write_bytes(b'owning executable')
        ancestor = root/'ancestor'; ancestor.mkdir()
        (ancestor/'verify-gap-seed.x').write_bytes(b'historical executable')
        command = [str(root/'verify-gap-seed.x'), '-in', str(root/'native.in')]
        manifest = dict(cwd=str(root), command=command, candidate_sha256=hashlib.sha256(seed).hexdigest(),
                        files=[dict(path=str(p), bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                               for p in (root/'gap-seed.bin', root/'gap-seed.meta', root/'verify-gap-seed.x',
                                         ancestor/'verify-gap-seed.x')])
        mp = root/'manifest.json'; mp.write_text(json.dumps(manifest))
        (root/'results/moment').mkdir(parents=True)
        receipt = dict(status='PASS', exit=0, error=None, wall_s=1, cwd=str(root), command=command,
                       max_individual_descendant_rss_bytes=100)
        (root/'results/moment/receipt.json').write_text(json.dumps(receipt))
        self.output(root, 1e-12)
        return mp, manifest, receipt

    def output(self, root, error):
        (root/'full-map.txt').write_text(
            '# full-nonlinear-map-v1; imposed seed; NOT a converged gap\n1 2 2 4\n'
            f'1000 1e-8 1 0 1e-9 4.01e-6\n1 {error} {error} 2\n2 {error} {error} 2\n')
        (root/'full-map.bin').write_bytes(struct.pack('<16d',
            1, 0, 1, 1, error, 0, error, error, 1, 0, 1, 1, 2, 0, 2, 2))

    def test_multiple_ancestor_executables_preserve_unchanged_residual_decision(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); mp, _, _ = self.fixture(root)
            with self.assertRaisesRegex(ValueError, 'unique prospective'): original_verify(root, mp)
            for error, expected in ((1e-12, True), (1., False)):
                self.output(root, error)
                result = verify(root, mp)
                self.assertEqual(result['stationary_residual_targets_met'], expected)
                self.assertEqual(result['thresholds'], dict(residual_infinity_ry=1e-10, rms_residual_over_gap=1e-5))
                self.assertFalse(result['conditioned_gap_error_bounded'])
                self.assertFalse(result['physical_response_verified'])

    def test_stale_root_command_argv_duplicate_and_input_are_rejected(self):
        for change in ('root', 'command', 'argv', 'duplicate', 'input'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); mp, manifest, receipt = self.fixture(root)
                if change == 'root': manifest['cwd'] = '/stale'
                if change == 'command': manifest['command'][0] = str(root/'ancestor/verify-gap-seed.x')
                if change == 'argv': receipt['command'] = receipt['command'][:1]
                if change == 'duplicate': manifest['files'].append(manifest['files'][2])
                if change == 'input': (root/'gap-seed.bin').write_bytes(struct.pack('<4d', 2, 0, 1, 1))
                mp.write_text(json.dumps(manifest))
                (root/'results/moment/receipt.json').write_text(json.dumps(receipt))
                with self.assertRaises(ValueError): verify(root, mp)

    def test_numerical_acceptance_body_matches_frozen_original(self):
        research = Path(__file__).parent
        original = (research/'verify_gap_candidate.py').read_text()
        current = (research/'verify_gap_candidate_v2.py').read_text()
        marker = '    full = full_readback(root)'
        self.assertEqual(original[original.index(marker):], current[current.index(marker):])


if __name__ == '__main__':
    unittest.main()
