from array import array
from pathlib import Path
import tempfile
import unittest

from basis_partial_analysis import read_payload


class BasisPayloadTest(unittest.TestCase):
    def test_two_native_arrays_and_stale_shapes(self):
        # Two arrays, three rows, two sides, two trial columns; binary64.
        values = array('d', range(24))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'basis.bin'
            path.write_bytes(values.tobytes())
            self.assertEqual(read_payload(path, 3, 2), values)
            for content in (values.tobytes()[:-8], values.tobytes() * 2):
                path.write_bytes(content)
                with self.assertRaisesRegex(ValueError, 'binary shape'):
                    read_payload(path, 3, 2)

    def test_nonfinite_payload_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'basis.bin'
            path.write_bytes(array('d', [0., float('nan'), 0., 0.]).tobytes())
            with self.assertRaisesRegex(ValueError, 'Nonfinite'):
                read_payload(path, 1, 1)
