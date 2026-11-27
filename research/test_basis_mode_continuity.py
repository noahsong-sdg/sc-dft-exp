from array import array
from pathlib import Path
import tempfile
import unittest

from basis_mode_continuity import check_prefix


class PreservedBasisBytesTest(unittest.TestCase):
    def test_q_and_aq_offsets_and_signed_zero_change(self):
        with tempfile.TemporaryDirectory() as directory:
            previous,current=(Path(directory)/name for name in ('previous.bin','current.bin'))
            previous.write_bytes(array('d',[0.,2.,3.,4.]).tobytes())
            # Two rows, old one column; new two columns; Q then AQ in Fortran order.
            current.write_bytes(array('d',[0.,2.,5.,6.,3.,4.,7.,8.]).tobytes())
            check_prefix(previous,current,2,1,2)
            current.write_bytes(array('d',[-0.,2.,5.,6.,3.,4.,7.,8.]).tobytes())
            with self.assertRaisesRegex(ValueError,'Changed retained'):check_prefix(previous,current,2,1,2)
            current.write_bytes(array('d',[0.,2.,5.,6.,3.,9.,7.,8.]).tobytes())
            with self.assertRaisesRegex(ValueError,'Changed retained'):check_prefix(previous,current,2,1,2)

    def test_truncated_persisted_basis_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            previous,current=(Path(directory)/name for name in ('previous.bin','current.bin'))
            previous.write_bytes(bytes(32));current.write_bytes(bytes(63))
            with self.assertRaisesRegex(ValueError,'Stale extended basis'):check_prefix(previous,current,2,1,2)
