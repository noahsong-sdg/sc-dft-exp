import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import compact_defect_material as owner
from compact_tile_material import COPIED
from fetch_public_response_inputs import digest
from inverse_material_run import identity


class CompactDefectMaterialTest(unittest.TestCase):
    def test_stale_full_P_and_invalid_saved_actions_reject_before_build(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);mp=base/'manifest';rp=base/'result';ap=base/'actions';root=base/'parent';root.mkdir();(root/'compact-p.bin').write_bytes(bytes(8))
            m=dict(files=[],counts=[65,67,67,3],cwd=str(root));mp.write_text(json.dumps(m));rp.write_text('{"complete_P":true}')
            with patch.object(owner,'p_analyze',return_value=dict(complete_P=False)):
                with self.assertRaisesRegex(ValueError,'full P defect parent'):owner.parents(mp,rp,ap,base/'build',base/'br')
            bindings={str(p):identity(p) for p in (mp,rp,root/'compact-p.bin',owner.RESEARCH/'compact_p_action_readback.py',owner.RESEARCH/'compact_p_actions.py')}
            action=dict(accepted_complete_P_manifest_sha256=digest(mp),accepted_complete_P_result_sha256=digest(rp),complete_P=True,inputs_unchanged=True,
                        independent_full_P_action_controls_passed=True,controls=3,bindings=bindings,left_P_Dv=[1.]*3,right_QT_D_ADv=[1.]*3,
                        absolute_errors=[1.]*3,bounds=[2.]*3)
            ap.write_text(json.dumps(action))
            with patch.object(owner,'p_analyze',return_value=dict(complete_P=True)):
                with self.assertRaisesRegex(ValueError,'Invalid P action control'):owner.parents(mp,rp,ap,base/'build',base/'br')

    def test_stage_boundaries_receipt_control_and_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory).resolve();source=base/'source';source.mkdir();compact=base/'compact';compact.mkdir();build=base/'build';build.mkdir()
            for name in COPIED:(source/name).write_text('fixture '+name)
            (build/'full-gap-check.x').write_text('fixture executable')
            (compact/'compact-state.meta').write_text('header\n65 67 67 3\n1.25\n'+'a'*64+'\n'+'b'*64+'\n'+'c'*64+'\n')
            p=dict(cwd=str(source),counts=[65,67,67,3],fingerprint='f'*64);prep=dict(cwd=str(compact));bm=dict(cwd=str(build));pins={}
            parents=(p,prep,bm,pins);root=base/'new';args=(base/'pm',base/'pr',base/'ap',base/'bm',base/'br')
            with patch.object(owner,'parents',return_value=parents):m=owner.stage(*args,root)
            self.assertEqual(m['stops'],[64,64]);self.assertEqual(m['guard_seconds'],90)
            (root/'results/material').mkdir(parents=True)
            receipt=dict(status='PASS',exit=0,error=None,command=m['command'],cwd=m['cwd'],wall_s=1.,guard_source_sha256=m['guard_source_sha256'],continuous_deadline_s=90,
                         max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=1024)
            rp=root/'results/material/receipt.json';rp.write_text(json.dumps(receipt));(root/'campaign_launch_watch.json').write_text('{"phase":"completed"}')
            (root/'results/material/console.log').write_text('COMPACT_DEFECT_PARTIAL; NOT a full-space norm\n')
            (root/'compact-defect.meta').write_text('a\nb\nc\n'+'f'*64+'\n')
            for name in ('compact-c.bin','compact-defect-rows.bin','defect-kernel-left.bin','defect-kernel-right.bin'):(root/name).write_bytes(bytes(8))
            progress=root/'compact-defect-progress.txt';progress.write_text('1 32 64 1 2 3 0\n1 64 64 1 2 3 0\n2 32 64 1 2 3 4\n2 64 64 1 2 3 4\n')
            with patch.object(owner,'parents',return_value=parents),patch.object(owner,'controls',return_value=dict(cpu_s=[1.,2.,3.,4.])):
                manifest=root/'run-manifest.json';self.assertTrue(owner.analyze(manifest)['terminal_guard_pass'])
                receipt['wall_s']=91;rp.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(ValueError,'receipt'):owner.analyze(manifest)
                receipt['wall_s']=1;rp.write_text(json.dumps(receipt));progress.write_text(progress.read_text().replace('2 64 64','2 63 64'))
                with self.assertRaisesRegex(ValueError,'progress coverage'):owner.analyze(manifest)
