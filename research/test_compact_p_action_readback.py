import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from compact_p_action_readback import analyze


class CompactPActionReadbackTest(unittest.TestCase):
    def test_incomplete_or_stale_recorded_parent_rejected_before_saved_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);mp=root/'manifest';rp=root/'result';mp.write_text('{}')
            for checked,recorded in ((dict(complete_P=False),dict(complete_P=False)),
                                     (dict(complete_P=True,checkpoint='new'),dict(complete_P=True,checkpoint='old')),
                                     (dict(complete_P=True),dict(complete_P=True,postread_wall_s=float('nan')))):
                rp.write_text(json.dumps(recorded))
                with patch('compact_p_action_readback.segment_analyze',return_value=checked):
                    with self.assertRaisesRegex(ValueError,'Unaccepted complete P'):analyze(mp,rp)
