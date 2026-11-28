import array
import json
from pathlib import Path
import tempfile
import unittest

from compact_defect_state import HEADER
from compact_tile_material import COPIED,stage
from fetch_public_response_inputs import digest
from inverse_material_run import identity


class CompactTileMaterialTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();native=base/'native';native.mkdir()
        with (native/'gap-seed.bin').open('wb') as f:array.array('d',[.125]*134).tofile(f)
        (native/'gap-seed.meta').write_text('gap-seed-v1; binary64 Fortran order\n65 67 67 100 10 50\n1.25\n/context\n'+'a'*64+'\n')
        for name in COPIED[2:]:(native/name).write_text('{}\n')
        full=base/'full.json';full.write_text(json.dumps(dict(cwd=str(native))))
        source=base/'source.json';source.write_text(json.dumps(dict(full_manifest=str(full))))
        def parent(name,label,rawname,fields,outputs,files):
            root=base/name;(root/'results'/label).mkdir(parents=True)
            m=dict(cwd=str(root),command=['fixture',name],files=files,guard_seconds=90,
                   group_rss_cap_bytes=3221225472,guard_source_sha256='b'*64)
            if name=='prep':m['source_manifest']=str(source)
            for path,text in outputs.items():(root/path).write_text(text)
            mp=base/(name+'-manifest.json');mp.write_text(json.dumps(m));(root/'run-manifest.json').write_bytes(mp.read_bytes())
            (root/'campaign_launch_watch.json').write_text('{"phase":"completed"}')
            receipt=dict(status='PASS',exit=0,error=None,command=m['command'],cwd=m['cwd'],wall_s=1,
                         guard_source_sha256='b'*64,continuous_deadline_s=90,
                         max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=2048)
            (root/'results'/label/'receipt.json').write_text(json.dumps(receipt))
            raw=dict(fields,terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),
                     outputs={path:identity(root/path) for path in outputs})
            (root/rawname).write_text(json.dumps(raw));rp=base/(name+'-result.json')
            rp.write_text(json.dumps(dict(raw,terminal_guard_pass=True,receipt=receipt,readback_sha256=digest(root/rawname))))
            return mp,rp,root
        meta=HEADER+'\n65 67 67 3\n1.25\n'+'a'*64+'\n'+digest(native/'gap-seed.bin')+'\n'+digest(source)+'\n'
        prep=parent('prep','prepare','compact-preparation-result.json',dict(rank=3,beta=1.25,operator_sha256='a'*64,
                    padded_candidate_sha256=digest(native/'gap-seed.bin'),active_states=132,
                    recipe=dict(calibration_max_errors=[0.]*3,calibration_bounds=[1e-10]*3)),
                    {'compact-state.meta':meta},[identity(p) for p in (source,full,*(native/x for x in COPIED))])
        build=parent('build','build','compact-build-result.json',dict(fresh_compile_count=18,build_plan_matches_console=True,
                     cache_checks=902,cache_all_bitwise_equal=True,historical_custom_objects_used=False,material_runtime_qualified=False),
                     {'full-gap-check.x':'qualified fixture executable'},[])
        return base,native,prep,build

    def test_two_parent_closures_exact_copies_and_control_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            base,native,p,b=self.fixture(Path(directory));root=base/'new'
            m=stage(*p[:2],*b[:2],root)
            self.assertEqual(m['guard_seconds'],90);self.assertEqual(m['launch_normal_seconds'],120)
            self.assertEqual(m['command'],[str(root/'compact-native-tiles.x'),'-in',str(root/'native.in')])
            pins={x['path']:x for x in m['files']}
            for name in COPIED:self.assertEqual((root/name).read_bytes(),(native/name).read_bytes())
            for name in (*COPIED,'compact-native-tiles.x','seed-control.in','compact-tile-control.in'):
                self.assertEqual(pins[str(root/name)],identity(root/name))
            self.assertEqual((root/'compact-tile-control.in').read_text().splitlines()[1:3],[str(p[2]),'3'])
            self.assertIn(str(b[2]/'full-gap-check.x'),pins)
            with self.assertRaises(ValueError):stage(*p[:2],*b[:2],root)

    def test_stale_public_receipt_output_and_consumed_reject_before_directory(self):
        for fault in ('receipt','recorded','raw','output','consumed','watcher','source'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                base,native,p,b=self.fixture(Path(directory));root=base/'new'
                target={'receipt':b[2]/'results/build/receipt.json','recorded':p[1],
                        'raw':p[2]/'compact-preparation-result.json','output':b[2]/'full-gap-check.x',
                        'consumed':p[2]/'run-manifest.json','watcher':b[2]/'campaign_launch_watch.json',
                        'source':native/'gap-seed.bin'}[fault]
                if fault=='output' or fault=='source':target.write_bytes(b'x'*target.stat().st_size)
                else:
                    data=json.loads(target.read_text())
                    if fault=='receipt':data['wall_s']=91
                    if fault=='recorded':data['terminal_guard_pass']=False
                    if fault=='raw':data['inputs_unchanged']=False
                    if fault=='consumed':data['command']=['different']
                    if fault=='watcher':data['phase']='running'
                    target.write_text(json.dumps(data))
                with self.assertRaises(ValueError):stage(*p[:2],*b[:2],root)
                self.assertFalse(root.exists())
