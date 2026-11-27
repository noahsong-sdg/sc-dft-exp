from pathlib import Path
import struct
import tempfile
import unittest

from cell_moment_cache import HEADER, read_pair


class CellMomentCacheTests(unittest.TestCase):
    def fixture(self, root):
        header = HEADER+'\n{phase}\n2 3 3 1 2\n.01 10 .01 0 0\n'
        values = [-1., 1., .5, .5] + [1., 2., 3., 4.]*4
        for phase in ('raw', 'averaged'):
            (root/f'cell-moments-{phase}.txt').write_text(header.format(phase=phase))
            (root/f'cell-moments-{phase}.bin').write_bytes(struct.pack('<20d', *values))

    def test_phase_context_and_stale_payload_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.fixture(root)
            self.assertEqual(read_pair(root)[0], [2, 3, 3, 1, 2])
            path = root/'cell-moments-averaged.txt'
            good = path.read_text()
            for bad in (good.replace('v1;', 'v0;'), good.replace('\naveraged\n', '\nraw\n'),
                        good.replace('.01 10 .01', '.02 10 .01')):
                path.write_text(bad)
                with self.assertRaises(ValueError):
                    read_pair(root)
            path.write_text(good)
            binary = root/'cell-moments-raw.bin'
            original = binary.read_bytes()
            for bad in (original[:-1], original+bytes(8), struct.pack('<d', float('nan'))+original[8:]):
                binary.write_bytes(bad)
                with self.assertRaises(ValueError):
                    read_pair(root)
            binary.write_bytes(original)
            other = root/'cell-moments-averaged.bin'
            other.write_bytes(struct.pack('<d', -2.)+original[8:])
            with self.assertRaisesRegex(ValueError, 'phases'):
                read_pair(root)


if __name__ == '__main__':
    unittest.main()
