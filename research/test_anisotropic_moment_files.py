"""Actual file schemas: resolve two nodes, preserve the one-node native branch."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

from anisotropic_moment_analysis import analyze
from cell_moment_cache import HEADER as CACHE_HEADER
from compare_legacy_gap import digest
from gap_symmetry_audit import HEADER as ROTATION_HEADER
from linear_response import stiffness


class AnisotropicMomentFileTest(unittest.TestCase):
    def test_one_node_falls_back_to_native_single_state_and_stale_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            prepare = root/'prepare'; prepare.mkdir()
            candidate = root/'candidate'; candidate.mkdir()
            meta = 'native-init-v1; arrays are native binary64/int32, Fortran order\n3 3 3 2 1 2 1\n0 1 1 1 1 1 1\nT\n'
            (prepare/'native-init.meta').write_text(meta)
            nodes = [-.01, .01, .5, .5]
            x, weight = [-.01, .01, .2]*2, [.5, .5, 1.]*2
            indices = [1]*6+[1, 1, 2]*2
            values = nodes+x+[0.]*6+weight+[0.]*12
            (prepare/'native-init.bin').write_bytes(struct.pack('<34d12i', *values, *indices))
            (candidate/'reduced-gap.bin').write_bytes(struct.pack('<6d', *([.0001]*6)))
            (candidate/'reduced-result.txt').write_text(
                '# reduced-nonlinear-v1; candidate; FULL native residual required\n'
                '3 3 3 2 1\n1000 .15 1 0 0 0 13.605693122994\n'
                '1.3605693122994 1.3605693122994 .0001 1.3605693122994\n')
            (root/'response-assignment.txt').write_text(
                '# response-assignment-v1; native geometry only; NOT a gap transfer\n'
                '3 3 3 2 1 1 2\n.01 10\n')
            (root/'response-assignment.bin').write_bytes(struct.pack('<28d12i',
                *nodes, *x, *weight, *([2.]*6), *([3.]*6), *indices))
            dos = [1., 1., 1., 0.]*2
            fields = dos+[2*v for v in dos]+[4*v for v in dos]+[3*v for v in dos]
            for phase in ('raw', 'averaged'):
                (root/f'cell-moments-{phase}.txt').write_text(
                    CACHE_HEADER+f'\n{phase}\n2 1 2 1 2\n.01 10 .01 0 0\n')
                (root/f'cell-moments-{phase}.bin').write_bytes(struct.pack('<36d', *nodes, *fields))
            (root/'response-symmetry.txt').write_text(ROTATION_HEADER+'\n1 1 1 1 1 1 1\n1 0 0 0 1 0 0 0 1\n')
            lines = ['# velocity-moment-diagnostic-v1; imposed constant gap; NOT a material prediction',
                     '2 1 2 4 1', '.01 10', '0 0 1', '0 0 0']
            for temperature in (2, 4, 8):
                states = [(xi, 1.5/13605.693122994, .5, 200., 30000.) for xi in (-.01, .01, -.01)]
                value = stiffness(states, 157887.51240203338/temperature, 10.)
                lines.append(' '.join(map(str, [temperature]+[value]*7)))
            (root/'velocity-moments.txt').write_text('\n'.join(lines)+'\n')
            for name in ('velocity-moment-probe.x', 'native.in'):
                (root/name).write_bytes(b'fixture')
            results = root/'results/moment'; results.mkdir(parents=True)
            (results/'console.log').write_text('Number of symmetries conserving q_FFLO : 1\n')
            receipt = dict(status='PASS', exit=0, error=None, cwd=str(root),
                           command=[str(root/'velocity-moment-probe.x'), '-in', str(root/'native.in')])
            receipt_path = results/'receipt.json'; receipt_path.write_text(json.dumps(receipt))
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps(dict(files=[dict(path=str(root/name),
                bytes=(root/name).stat().st_size, sha256=digest(root/name))
                for name in ('velocity-moment-probe.x', 'native.in')])))
            result = analyze(root, candidate, prepare, manifest)
            self.assertEqual(result['omitted_native_states'], [1, 1])
            for row in result['grids']:
                self.assertEqual(row['retained_resolved_states'], 2)
                expected = stiffness([(.2, .0001, 1., 200., 30000.)], 1000., 10.)
                self.assertAlmostEqual(row['unchanged_single_state_branch_response'], expected)
                self.assertAlmostEqual(row['combined_raw_second'], row['raw_second']+expected)
            receipt_path.write_text(json.dumps({**receipt, 'status': 'FAIL'}))
            with self.assertRaisesRegex(ValueError, 'receipt'):
                analyze(root, candidate, prepare, manifest)
            receipt_path.write_text(json.dumps(receipt))
            (root/'native.in').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'prospective'):
                analyze(root, candidate, prepare, manifest)


if __name__ == '__main__':
    unittest.main()
