import math
from pathlib import Path
import struct
import tempfile
import unittest

from portable_grid_probe import compare, stage


class GridProbeTest(unittest.TestCase):
    def test_one_ulp_weight_difference_is_measured_not_accepted(self):
        values = [1.0]*600
        reference = struct.pack('<200d', *values[:200])
        self.assertTrue(compare(struct.pack('<600d', *values), reference)['transformed_grid_bitwise_equal'])
        values[351] = math.nextafter(1.0, 2.0)
        result = compare(struct.pack('<600d', *values), reference)
        self.assertEqual(result['sections']['dx0'][0]['index'], 52)
        self.assertEqual(result['sections']['dx0'][0]['difference_in_reference_ulps'], 1)
        self.assertFalse(result['gap_state_accepted'])
        with self.assertRaisesRegex(ValueError, 'Stale'):
            compare(b'', reference)
        values[0] = math.nan
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            compare(struct.pack('<600d', *values), reference)

    def test_existing_root_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            sentinel = root/'keep'; sentinel.write_text('preserved')
            with self.assertRaisesRegex(ValueError, 'Fresh'):
                stage(root/'missing', root/'missing', root/'missing', root)
            self.assertEqual(sentinel.read_text(), 'preserved')
