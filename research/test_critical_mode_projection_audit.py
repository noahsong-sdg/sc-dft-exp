import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from critical_mode_projection_audit import audit


class CriticalModeProjectionAuditTests(unittest.TestCase):
    def test_distinct_projection_and_action_defects_and_stale_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); basis = root/'basis'; basis.mkdir()
            context = 'a'*64
            (root/'mode-control.in').write_text('/measured-mode\n'+context+'\n')
            r = math.sqrt(.5)
            (root/'mode-amplitudes.bin').write_bytes(struct.pack('<8d', r, r, 0, 0, 2*r, 3*r, 0, 0))
            (basis/'basis.meta').write_text('tc-basis-v1\n4 1\n100\n'+context+'\n100 10 10 2 2 2\n')
            (basis/'basis.bin').write_bytes(struct.pack('<8d', 1, 0, 0, 0, 2, 0, 0, 0))
            with patch('critical_mode_projection_audit.analyze', return_value=dict(dimensions=[2, 2, 2, 8], beta=100)):
                row = audit(root, [basis])['rows'][0]
                self.assertAlmostEqual(row['mode_projection_defect_norm'], r)
                self.assertAlmostEqual(row['mode_action_defect_norm'], 3*r)
                self.assertAlmostEqual(row['defect_action_over_defect_norm'], 3.)
                (basis/'basis.meta').write_text((basis/'basis.meta').read_text().replace(context, 'b'*64))
                with self.assertRaisesRegex(ValueError, 'Incompatible'):
                    audit(root, [basis])


if __name__ == '__main__':
    unittest.main()
