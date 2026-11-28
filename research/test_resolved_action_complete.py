import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import resolved_action_complete as owner
from inverse_material_run import identity


class ResolvedActionCompleteTest(unittest.TestCase):
    def test_owner_freshness_console_and_final_pin_check(self):
        for fault in ('none','owner','stale','console','pin'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root=Path(directory).resolve()
                for name in (*owner.COPIED,'enrichment-native.x','seed-control.in','enrichment-action-control.in'):(root/name).write_text('fixture')
                m=dict(cwd=str(root),command=[sys.executable,str(Path(owner.__file__).resolve())],stop=65,guard_seconds=900,counts=[65,67,3],compact='fixture',trials='fixture',files=[identity(p) for p in root.iterdir()])
                (root/'run-manifest.json').write_text(json.dumps(m))
                if fault=='owner':
                    with self.assertRaises(ValueError):owner.run(root)
                    continue
                if fault=='stale':(root/owner.OUTPUTS[0]).write_text('stale')
                def native(*args,**kwargs):
                    for name in owner.OUTPUTS:(root/name).write_text('fixture output')
                    if fault=='pin':(root/'native.in').write_text('changed input')
                    return SimpleNamespace(stdout='bad' if fault=='console' else 'ENRICHMENT_ACTION_PASS_COMPLETE rows=65 left=65\n',stderr='')
                with contextlib.chdir(root),patch.object(owner.subprocess,'run',side_effect=native),patch.object(owner,'controls',return_value=dict(complete_A_and_P=True)),contextlib.redirect_stdout(io.StringIO()):
                    if fault=='none':self.assertFalse(owner.run(root)['terminal_guard_pass'])
                    else:
                        with self.assertRaises(ValueError):owner.run(root)
                        self.assertFalse((root/'resolved-action-readback.json').exists())
