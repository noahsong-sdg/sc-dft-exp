import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import resolved_inverse_run as owner
from inverse_material_run import identity


class ResolvedInverseRunTest(unittest.TestCase):
    def test_owner_stale_control_console_and_changed_pin(self):
        for fault in ('none','owner','stale','control','console','pin'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root=Path(directory).resolve();sdk=root/'sdk';sdk.write_text('fixture SDK')
                m=dict(cwd=str(root),command=[sys.executable,str(Path(owner.__file__).resolve())],counts=[65,67,2],compiler=sys.executable,sdk=str(sdk),**{k:'fixture' for k in ('compact','trials','full','previous','oldc')})
                control=root/'enriched-inverse-control.in';control.write_text('resolved-inverse-rows-v1\n'+'fixture\n'*5+'65 67 2\n')
                m['files']=[identity(p) for p in (control,sdk,Path(sys.executable),owner.RESEARCH/'resolved_inverse_rows.f90',owner.RESEARCH/'resolved_inverse_readback.py')]
                (root/'run-manifest.json').write_text(json.dumps(m))
                if fault=='owner':
                    with self.assertRaises(ValueError):owner.run(root)
                    continue
                if fault=='stale':(root/'inverse.x').write_text('old')
                if fault=='control':control.write_text('stale')
                def native(*args,**kwargs):
                    for name in owner.OUTPUTS:
                        if name!='inverse-build-command.json':(root/name).write_text('fixture')
                    if fault=='pin':sdk.write_text('changed')
                    return SimpleNamespace(stdout='bad' if fault=='console' else 'ENRICHED_INVERSE_ROWS_COMPLETE; DIAGNOSTIC ONLY, no adopted inverse\n',stderr='')
                with contextlib.chdir(root),patch.object(owner.subprocess,'run',side_effect=native),patch.object(owner,'check',return_value=dict(inverse_adopted=False)),contextlib.redirect_stdout(io.StringIO()):
                    if fault=='none':self.assertFalse(owner.run(root)['terminal_guard_pass'])
                    else:
                        with self.assertRaises(ValueError):owner.run(root)
                        self.assertFalse((root/'inverse-readback.json').exists())
