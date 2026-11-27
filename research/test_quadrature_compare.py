import math
from pathlib import Path
import struct
import tempfile
import unittest

from quadrature_compare import compare


class QuadratureCompareTest(unittest.TestCase):
    def test_one_weight_ulp_is_reported_without_accepting_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata, state, fresh = [root / name for name in ('meta', 'state', 'fresh')]
            metadata.write_text('native-init-v1; arrays are native binary64/int32, Fortran order\n'
                                '1 1 1 2 1 1 1\n1 1e-7 1e-8 1 1 1 1\nT\n')
            state.write_bytes(struct.pack('<4d', -1., 1., .5, .5) + bytes(96))
            fresh.write_bytes(struct.pack('<4d', -1., 1., math.nextafter(.5, 1.), .5))
            result = compare(fresh, metadata, state)
            self.assertEqual(result['differences']['xi0'], [])
            self.assertEqual(result['differences']['dx0'][0]['ulps_at_saved_value'], 1.)
            self.assertEqual(result['differences']['dx0'][0]['index'], 1)
            for corrupt in (fresh.read_bytes()[:-1], struct.pack('<4d', -1., 1., math.nan, .5)):
                fresh.write_bytes(corrupt)
                with self.assertRaises(ValueError):
                    compare(fresh, metadata, state)
            fresh.write_bytes(struct.pack('<4d', -1., 1., .5, .5))
            metadata.write_text(metadata.read_text().replace('native-init-v1', 'native-init-v0'))
            with self.assertRaises(ValueError):
                compare(fresh, metadata, state)


if __name__ == '__main__':
    unittest.main()
