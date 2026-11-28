"""Source-build the file driver; reject stale state before diagnostic output."""
import math
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


def pack(values):
    return struct.pack('<'+'d'*len(values), *values)


class LowRankInverseDriverTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('gfortran')
        if not compiler:
            raise AssertionError('Native fixture compiler required')
        cls.build = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.build.cleanup)
        root = Path(cls.build.name); qe = root/'qe'; qe.mkdir()
        (qe/'make.inc').write_text(f'MPIF90 = {compiler}\nLD = {compiler}\n'
                                  'F90FLAGS = -O2\nLAPACK_LIBS = -llapack\nBLAS_LIBS = -lblas\n')
        makefile = Path(__file__).with_name('portable_gap')/'low_rank_inverse.mk'
        subprocess.run(['make', '-f', str(makefile), 'QE_ROOT='+str(qe)],
                       cwd=root, check=True, capture_output=True)
        cls.executable = root/'inverse-actions.x'

    def fixture(self, root):
        basis, geometry, full = (root/name for name in ('basis', 'geometry', 'full'))
        for path in (basis, geometry, full):
            path.mkdir()
        context = 'a'*64; beta = 1000.
        (basis/'basis.meta').write_text('tc-basis-v1\n4 2\n1000\n'+context+'\n2 10 10 2 1 2\n')
        q = [[1., 0., 0., 0.], [0., 0., 1., 0.]]
        u = [[.5, 0., .3, .4], [.2, 0., .9, .6]]
        (basis/'basis.bin').write_bytes(pack([v for col in q+u for v in col]))
        (geometry/'native-init.meta').write_text(
            'native-init-v1; arrays are native binary64/int32, Fortran order\n'
            '1 2 2 2 1 1 1\n1 1e-7 1e-8 1 1 1 1\nT\n')
        x = [0., 0., .001, .003]
        geometry_values = [-1., 1., .5, .5]+x+[0.]*4+[1., 0., 1., 1.]+[0.]*8
        (geometry/'native-init.bin').write_bytes(pack(geometry_values)+struct.pack('<8i', *([1]*8)))
        (full/'gap-seed.meta').write_text('gap-seed-v1; binary64 Fortran order\n'
            '1 2 2 2 10 50\n1000\n'+str(geometry)+'\n'+context+'\n')
        gap = [.001, 0., .0015, .0012]; residual = [1e-12, 0., -2e-12, 3e-12]
        direction = [1., 0., -.3, -.2]; diagonal = []
        for xi, delta in zip(x, gap):
            energy = math.hypot(xi, delta)
            t = math.exp(-beta*energy)
            denominator = ((1-math.exp(-beta*abs(xi)))/(1+math.exp(-beta*abs(xi)))/abs(xi)
                           if xi else beta/2)
            diagonal.append((((xi/energy)**2*(1-t)/(1+t)/energy
                              +beta/2*(delta/energy)**2*4*t/(1+t)**2)/denominator) if energy else 0.)
        diagonal[1] = 0.
        a = [[sum(u[k][i]*q[k][j] for k in range(2)) for j in range(4)] for i in range(4)]
        jv = [-direction[i]+sum(a[i][j]*diagonal[j]*direction[j] for j in range(4)) for i in range(4)]
        (full/'gap-seed.bin').write_bytes(pack(gap))
        (full/'full-map.bin').write_bytes(pack(gap+residual+direction+jv))
        lines = ['# full-nonlinear-map-v1; imposed seed; NOT a converged gap',
                 '1 2 2 4', '1000 1e-8 0 0 0 1e-5']
        for side, indices in enumerate(([0], [2, 3]), 1):
            stats = [max(abs(residual[i]) for i in indices),
                     math.sqrt(sum(residual[i]**2 for i in indices)/len(indices)),
                     max(abs(jv[i]) for i in indices)]
            lines.append(str(side)+' '+' '.join(map(repr, stats)))
        (full/'full-map.txt').write_text('\n'.join(lines)+'\n')
        control = f'low-rank-inverse-control-v1\n{basis}\n{geometry}\n{full}\n{context}\n1000\n2 10 10 2 1 2\n'
        (root/'inverse-control.in').write_text(control)
        return basis, geometry, full, control, q, u, diagonal, residual, direction

    def test_source_built_driver_and_independent_exponential_derivative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            basis, geometry, full, _, q, u, diagonal, residual, direction = self.fixture(root)
            subprocess.run([str(self.executable)], cwd=root, check=True, capture_output=True)
            lines = (root/'inverse-result.txt').read_text().splitlines()
            self.assertEqual(lines[0], '# low-rank-inverse-v1; DIAGNOSTIC; NO full-space bound')
            self.assertEqual(list(map(int, lines[1].split())), [4, 2, 1, 2, 2])
            data = struct.unpack('<18d', (root/'inverse-result.bin').read_bytes())
            derivative, correction, probe = data[:4], data[4:8], data[8:12]
            for actual, expected in zip(derivative, diagonal):
                self.assertAlmostEqual(actual, expected, delta=3e-15)
            for i in range(4):
                model_action = correction[i]-sum(u[k][i]*sum(q[k][j]*diagonal[j]*correction[j]
                                                           for j in range(4)) for k in range(2))
                self.assertAlmostEqual(model_action, residual[i], delta=2e-26)
            self.assertLess(max(map(abs, probe)), 2e-14)
            expected_matrix = [[float(i == j)-sum(q[i][k]*diagonal[k]*u[j][k] for k in range(4))
                                for j in range(2)] for i in range(2)]
            for j in range(2):
                for i in range(2):
                    self.assertAlmostEqual(data[12+2*j+i], expected_matrix[i][j], delta=3e-15)
            a, b = expected_matrix[0]; c, d = expected_matrix[1]
            trace = a*a+b*b+c*c+d*d; det = (a*d-b*c)**2
            expected_sv = [math.sqrt((trace+sign*math.sqrt(trace*trace-4*det))/2) for sign in (1, -1)]
            for actual, expected in zip(data[16:], expected_sv):
                self.assertAlmostEqual(actual, expected, delta=3e-14)
            self.assertEqual(correction[1], 0.)
            self.assertEqual(probe[1], 0.)

    def test_stale_context_candidate_padding_and_payload_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            basis, geometry, full, control, *_ = self.fixture(root)
            meta = (basis/'basis.meta').read_bytes()
            gap = (full/'gap-seed.bin').read_bytes()
            values = list(struct.unpack('<16d', (full/'full-map.bin').read_bytes()))
            nan_values = list(values); nan_values[-1] = math.nan
            bad_padding = list(values); bad_padding[13] = 1.
            cases = [
                (basis/'basis.meta', meta.replace(b'a'*64, b'b'*64), 'Stale inverse basis context'),
                (basis/'basis.meta', meta.replace(b'1000', b'999'), 'Stale inverse basis context'),
                (basis/'basis.meta', meta.replace(b'10 10', b'10 11'), 'Stale inverse basis context'),
                (basis/'basis.bin', (basis/'basis.bin').read_bytes()[:-1], 'Stale inverse payload size'),
                (geometry/'native-init.meta', (geometry/'native-init.meta').read_bytes().replace(b'1 2 2 2', b'1 2 2 1'), 'Stale inverse geometry'),
                (full/'gap-seed.meta', (full/'gap-seed.meta').read_bytes().replace(b'a'*64, b'b'*64), 'Stale inverse full-map context'),
                (full/'gap-seed.bin', gap[:8]+pack([-0.])+gap[16:], 'Different inverse candidate'),
                (full/'full-map.bin', pack(values)[:-1], 'Stale inverse payload size'),
                (full/'full-map.bin', pack(nan_values), 'Nonfinite inverse state'),
                (full/'full-map.bin', pack(bad_padding), 'Nonzero inverse padding'),
                (full/'full-map.txt', (full/'full-map.txt').read_bytes()+b'old data\n', 'Trailing inverse metadata'),
            ]
            for index, (path, payload, message) in enumerate(cases):
                with self.subTest(message=message):
                    original = path.read_bytes(); path.write_bytes(payload)
                    run = root/f'reject-{index}'; run.mkdir(); (run/'inverse-control.in').write_text(control)
                    result = subprocess.run([str(self.executable)], cwd=run, capture_output=True, text=True)
                    path.write_bytes(original)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(message, result.stderr)
                    self.assertFalse((run/'inverse-result.txt').exists())


if __name__ == '__main__':
    unittest.main()
