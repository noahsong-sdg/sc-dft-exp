from pathlib import Path
import struct
import tempfile
import unittest

from response_assignment_analysis import analyze, compare_scales


class ResponseAssignmentAnalysisTests(unittest.TestCase):
    def test_matching_geometry_changed_indices_and_stale_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); prepare = root/'prepare'; prepare.mkdir()
            header = '# response-assignment-v1; native geometry only; NOT a gap transfer\n'
            (root/'response-assignment.txt').write_text(header+'1 2 2 2 1 1 2\n.01 10\n')
            (prepare/'native-init.meta').write_text('native-init-v1; arrays are native binary64/int32, Fortran order\n1 2 2 2 1 2 1\n0 1 1 1 1 1 1\nT\n')
            nodes = [-1., 1., .5, .5]
            x, w, v, h = [0., 0., .2, .4], [1., 0., 1., 1.], [2., 0., 3., 4.], [5., 0., 6., 7.]
            indices = [1, 0, 1, 1, 1, 0, 1, 2]
            native = struct.pack('<24d8i', *nodes, *x, *([0.]*4), *w, *([0.]*8), *indices)
            (prepare/'native-init.bin').write_bytes(native)
            payload = struct.pack('<20d8i', *nodes, *x, *w, *v, *h, *indices)
            binary = root/'response-assignment.bin'; binary.write_bytes(payload)
            report = analyze(root, prepare)
            self.assertTrue(report['mapping_compatible'])
            self.assertFalse(report['gap_transfer_verified'])
            reference = root/'reference'; reference.mkdir()
            (reference/'response-assignment.txt').write_text(header+'1 2 2 2 1 1 2\n.02 10\n')
            (reference/'response-assignment.bin').write_bytes(struct.pack('<20d8i',
                *nodes, *x, *w, *[2*a for a in v], *[4*a for a in h], *indices))
            scaled = compare_scales(root, reference)
            self.assertTrue(scaled['directional_scale_test_passed'])
            self.assertFalse(scaled['input_direction_verified'])
            (reference/'response-assignment.bin').write_bytes(payload)
            self.assertFalse(compare_scales(root, reference)['directional_scale_test_passed'])
            (reference/'response-assignment.txt').write_text(header+'1 2 2 2 1 1 2\n1e-200 10\n')
            with self.assertRaisesRegex(ValueError, 'normalization range'):
                compare_scales(root, reference)
            changed = indices.copy(); changed[-1] = 1
            binary.write_bytes(struct.pack('<20d8i', *nodes, *x, *w, *v, *h, *changed))
            self.assertFalse(analyze(root, prepare)['mapping_compatible'])
            binary.write_bytes(payload[:-1])
            with self.assertRaisesRegex(ValueError, 'payload'):
                analyze(root, prepare)
            binary.write_bytes(payload)
            (root/'response-assignment.txt').write_text(header.replace('v1', 'v0')+'1 2 2 2 1 1 2\n.01 10\n')
            with self.assertRaisesRegex(ValueError, 'schema'):
                analyze(root, prepare)


if __name__ == '__main__':
    unittest.main()
