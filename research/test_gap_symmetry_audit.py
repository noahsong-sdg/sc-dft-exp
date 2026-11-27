from pathlib import Path
import tempfile
import struct
import unittest

from gap_symmetry_audit import HEADER, analyze, audit_records, mapped_cell, read_rotations

IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
INVERSION = ((-1, 0, 0), (0, -1, 0), (0, 0, -1))


class GapSymmetryTests(unittest.TestCase):
    def test_shifted_mapping_and_asymmetric_gap(self):
        self.assertEqual(mapped_cell(2, 0, 4, INVERSION), 4)
        self.assertEqual(mapped_cell(1, 1, 4, INVERSION), 64)
        records = {(0, 2, 1, 0): (.2, .5, .01), (0, 4, 1, 0): (.2, .5, .01),
                   (1, 1, 2, -1): (2., .25, .02), (1, 64, 2, -1): (2., .25, .02)}
        result = audit_records(records, 4, [IDENTITY, INVERSION])
        self.assertTrue(result['gap_symmetry_test_passed'])
        records[1, 64, 2, -1] = (2., .25, .021)
        result = audit_records(records, 4, [IDENTITY, INVERSION])
        self.assertTrue(result['geometry_orbits_compatible'])
        self.assertFalse(result['gap_symmetry_test_passed'])
        self.assertAlmostEqual(result['max_gap_difference_ry'], .001)
        del records[1, 64, 2, -1]
        self.assertGreater(audit_records(records, 4, [IDENTITY, INVERSION])['missing_orbit_records'], 0)

    def test_geometry_mismatch_and_off_grid_rotation(self):
        records = {(0, 2, 1, 0): (.2, .5, .01), (0, 4, 1, 0): (.3, .5, .01)}
        result = audit_records(records, 4, [IDENTITY, INVERSION])
        self.assertEqual(result['geometry_comparisons_beyond_64eps'], 2)
        self.assertFalse(result['gap_symmetry_test_passed'])
        shear = ((1, 1, 0), (0, 1, 0), (0, 0, 1))
        self.assertIsNone(mapped_cell(1, 1, 4, shear))

    def test_native_order_and_stale_rotation_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'symmetry.txt'
            # Nonsymmetric matrix distinguishes Fortran column from row order.
            path.write_text(HEADER+'\n2 4 4 4 1 1 1\n1 0 0 0 1 0 0 0 1\n1 0 0 1 1 0 0 0 1\n')
            size, rotations = read_rotations(path)
            self.assertEqual(size, 4)
            self.assertEqual(rotations[1], ((1, 1, 0), (0, 1, 0), (0, 0, 1)))
            for content in (path.read_text().replace('v1', 'v0'), HEADER+'\n2 4 4 4 1 1 1\n1 0 0 0 1 0 0 0 1\n'):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    read_rotations(path)

    def test_file_bound_candidate_and_wrong_cell_grid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); prepare = root/'prepare'; prepare.mkdir()
            symmetry = root/'symmetry.txt'
            symmetry.write_text(HEADER+'\n2 1 1 1 1 1 1\n1 0 0 0 1 0 0 0 1\n-1 0 0 0 -1 0 0 0 -1\n')
            (prepare/'native-init.meta').write_text(
                'native-init-v1; arrays are native binary64/int32, Fortran order\n'
                '2 2 2 2 1 1 1\n0 .2 1 1 1 1 1\nT\n')
            reals = [-.1, .1, .5, .5]+[-.1, .1]*2+[0.]*4+[1.]*4+[0.]*8
            (prepare/'native-init.bin').write_bytes(struct.pack('<24d8i', *reals, *([1]*8)))
            (root/'reduced-gap.bin').write_bytes(struct.pack('<4d', *([.01]*4)))
            average = .01*1000*13.605693122994
            (root/'reduced-result.txt').write_text(
                '# reduced-nonlinear-v1; candidate; FULL native residual required\n'
                f'2 2 2 2 1\n1000 .15 1 0 0 0 13.605693122994\n{average} {average} .01 {average}\n')
            result = analyze(root, prepare, symmetry)
            self.assertTrue(result['gap_symmetry_test_passed'])
            self.assertEqual(result['states'], 4)
            self.assertFalse(result['physical_response_verified'])
            symmetry.write_text(symmetry.read_text().replace('2 1 1 1 1 1 1', '2 2 2 2 1 1 1'))
            with self.assertRaisesRegex(ValueError, 'different geometry'):
                analyze(root, prepare, symmetry)


if __name__ == '__main__':
    unittest.main()
