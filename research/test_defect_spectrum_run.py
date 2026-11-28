import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import defect_spectrum_run as owner
from inverse_material_run import identity


class DefectSpectrumRunTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();compact=base/'compact';compact.mkdir();defect=base/'defect';defect.mkdir();tiles=base/'tiles';tiles.mkdir()
        files=[]
        for name in ('compact-q.bin','compact-u.bin','compact-state.bin','compact-state.meta'):
            path=compact/name;path.write_text('fixture');files.append(identity(path))
        for i in (1,2):path=tiles/f'compact-kernel-{i}.bin';path.write_text('fixture');files.append(identity(path))
        sdk=base/'sdk';sdk.write_text('fixture SDK')
        selected=base/'selected';selected.write_text(json.dumps(dict(cwd=str(tiles))))
        qual=base/'qual';qual.write_text(json.dumps(dict(selected_manifest=str(selected))))
        p=base/'p';p.write_text(json.dumps(dict(predecessor_manifest=str(qual))))
        build=base/'build';build.write_text(json.dumps(dict(defect_blas=str(sdk))))
        (defect/'compact-defect-control.in').write_text('header\n'+str(compact)+'\n');files.append(identity(defect/'compact-defect-control.in'))
        (defect/'results/material').mkdir(parents=True)
        for name in ('results/material/receipt.json','campaign_launch_watch.json'):(defect/name).write_text('{}')
        (defect/'compact-c.bin').write_text('fixture output')
        m=dict(cwd=str(defect),counts=[65,67,67,3],p_manifest=str(p),build_manifest=str(build),files=files)
        mp=base/'manifest';mp.write_text(json.dumps(m));(defect/'run-manifest.json').write_bytes(mp.read_bytes())
        recorded=dict(terminal_guard_pass=True,outputs={'compact-c.bin':identity(defect/'compact-c.bin')});rp=base/'result';rp.write_text(json.dumps(recorded))
        return mp,rp,recorded

    def test_stage_requires_fresh_root_and_matching_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory).resolve();mp,rp,recorded=self.fixture(base);root=base/'new'
            with patch.object(owner,'parent_analyze',return_value=recorded):m=owner.stage(mp,rp,root)
            self.assertEqual(m['counts'],[65,67,3]);self.assertEqual(m['guard_seconds'],90)
            self.assertEqual((root/'spectrum-control.in').read_text().splitlines()[-1],'65 67 3 64')
            with patch.object(owner,'parent_analyze',return_value=recorded):
                with self.assertRaises(ValueError):owner.stage(mp,rp,root)
            with patch.object(owner,'parent_analyze',return_value=dict(recorded,terminal_guard_pass=False)):
                with self.assertRaises(ValueError):owner.stage(mp,rp,base/'other')

    def test_owner_freshness_console_and_final_input_pins(self):
        for fault in ('none','owner','stale','console','pin'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                base=Path(directory).resolve();mp,rp,recorded=self.fixture(base);root=base/'new'
                with patch.object(owner,'parent_analyze',return_value=recorded):m=owner.stage(mp,rp,root)
                if fault=='owner':
                    with self.assertRaises(ValueError):owner.run(root)
                    continue
                if fault=='stale':(root/'spectrum.x').write_text('old executable')
                def native(command,**kwargs):
                    for name in owner.OUTPUTS:
                        if name!='spectrum-build-command.json':(root/name).write_text('fixture output')
                    if fault=='pin':Path(m['sdk']).write_text('changed')
                    return SimpleNamespace(stdout='bad' if fault=='console' else 'RETAINED_ROW_SPECTRUM_COMPLETE; no new kernels or adopted directions\n',stderr='')
                with contextlib.chdir(root),patch.object(owner.subprocess,'run',side_effect=native),patch.object(owner,'check',return_value=dict(adopted_directions=False)),contextlib.redirect_stdout(io.StringIO()):
                    if fault=='none':self.assertFalse(owner.run(root)['terminal_guard_pass'])
                    else:
                        with self.assertRaises(ValueError):owner.run(root)
                        self.assertFalse((root/'spectrum-readback.json').exists())
