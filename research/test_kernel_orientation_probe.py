"""Hermetic extraction and strict output controls; actual source pilot separate."""
from pathlib import Path
import tempfile
import unittest

from kernel_orientation_probe import POINTS, fixture, analyze


class KernelOrientationProbeTest(unittest.TestCase):
    def test_exact_body_and_stale_source(self):
        body = 'FUNCTION Kweight(beta,x0,y0,z0) RESULT(Wk)\n! exact untouched body\nEND FUNCTION Kweight'
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory)/'kernel.f90'; p.write_text('prefix\n'+body+'\nsuffix\n')
            generated = fixture(p, 2.)
            self.assertIn(body, generated)
            self.assertNotIn('prefix', generated)
            with self.assertRaisesRegex(ValueError, 'beta'):
                fixture(p, float('nan'))
            p.write_text(body+'\n'+body)
            with self.assertRaisesRegex(ValueError, 'Unrecognized'):
                fixture(p, 2.)

    def test_complete_and_adversarial_readback(self):
        rows = []
        for k in (1, 2):
            for t in (0, 1):
                for i, (x, y, z) in enumerate(POINTS, 1):
                    rows.append(f'{k} {t} {i} {x} {y} {z} -2 {(-2 if k==1 else -3)}')
        result = analyze('\n'.join(rows))
        self.assertEqual(len(result['cycles']), 8)
        self.assertFalse(result['full_material_reciprocity_verified'])
        self.assertFalse(result['conditioned_gap_error_bounded'])
        for changed in (rows[:-1], [rows[1], rows[0], *rows[2:]],
                        [rows[0].rsplit(' ', 1)[0]+' -3', *rows[1:]],
                        [*rows[:-1], rows[-1].rsplit(' ', 1)[0]+' nan']):
            with self.assertRaises(ValueError):
                analyze('\n'.join(changed))
