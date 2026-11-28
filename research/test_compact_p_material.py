import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import compact_p_material as owner
from compact_p_context import fingerprint
from compact_p_readback import HEADER
from fetch_public_response_inputs import digest
from inverse_material_run import identity
import test_compact_tile_material as legacy


class CompactPMaterialTest(unittest.TestCase):
    def fixture(self,base):
        base,native,p,b=legacy.CompactTileMaterialTest().fixture(base)
        prep,pr,pp=owner.accepted(*p[:2],'prepare','compact-preparation-result.json')
        bm,br,bp=owner.accepted(*b[:2],'build','compact-build-result.json')
        br['fresh_compile_count']=19
        sdk=base/'sdk';sdk.write_text('test SDK');bm['defect_blas']=str(sdk)
        for name,size in (('compact-q.bin',8*132*3),('compact-state.bin',40*132)):(p[2]/name).write_bytes(bytes(size))
        for path in (sdk,b[2]/'full-gap-check.x',p[2]/'compact-q.bin',p[2]/'compact-state.bin'):pp[str(path)]=identity(path)
        sm=dict(cwd=str(native),files=list(pp.values()),preparation_manifest=str(p[0]),preparation_result=str(p[1]),native_source_directory=str(native))
        smp=base/'selected-manifest.json';smp.write_text(json.dumps(sm))
        (native/'run-manifest.json').write_bytes(smp.read_bytes());(native/'results/material').mkdir(parents=True)
        for name in ('results/material/receipt.json','results/material/console.log','campaign_launch_watch.json'):(native/name).write_text('{}')
        (native/'compact-partial-p.bin').write_bytes(bytes(396*8))
        selected=dict(terminal_guard_pass=True,outputs={'compact-partial-p.bin':identity(native/'compact-partial-p.bin')})
        srp=base/'selected-result.json';srp.write_text(json.dumps(selected))
        bindings=dict(Q=p[2]/'compact-q.bin',state=p[2]/'compact-state.bin',executable=b[2]/'full-gap-check.x',blas=sdk,native_seed_metadata=native/'gap-seed.meta')
        fp,description=fingerprint([65,67,67,3],[100,10,50],1.25,'a'*64,pr['padded_candidate_sha256'],*(bindings[k] for k in ('Q','state','executable','blas')))
        reg=dict(schema='compact-P-context-registration-v1',fingerprint=fp,dependencies=description,
                 context_producer=identity(owner.RESEARCH/'compact_p_context.py'),accepted_preparation=identity(p[1]),accepted_build=identity(b[1]),
                 file_bindings={k:identity(v) for k,v in bindings.items()},material_restart_qualified=False,complete_P=False,full_space_norm_measured=False)
        rp=base/'registration.json';rp.write_text(json.dumps(reg))
        return (smp,srp,*b[:2],rp),selected,[(prep,pr,pp),(bm,br,bp)]

    def test_parent_registration_stale_inputs_and_build_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            args,selected,accepted=self.fixture(Path(directory))
            with patch.object(owner,'selected_analyze',return_value=selected),patch.object(owner,'accepted',side_effect=accepted):
                result=owner.parents(*args)
            self.assertEqual(result[6],[65,67,67,3])
            for fault in ('registration','build','selected'):
                original=args[-1].read_text();changed=json.loads(original)
                if fault=='registration':changed['file_bindings']['Q']['sha256']='f'*64;args[-1].write_text(json.dumps(changed))
                if fault=='build':accepted[1][1]['fresh_compile_count']=18
                if fault=='selected':selected['terminal_guard_pass']=False
                with patch.object(owner,'selected_analyze',return_value=selected),patch.object(owner,'accepted',side_effect=accepted):
                    with self.assertRaises(ValueError):owner.parents(*args)
                args[-1].write_text(original);accepted[1][1]['fresh_compile_count']=19;selected['terminal_guard_pass']=True

    def test_stage_and_receipt_readback_with_stale_persisted_result(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);args,selected,accepted=self.fixture(base);root=base/'qualification'
            with patch.object(owner,'selected_analyze',return_value=selected),patch.object(owner,'accepted',side_effect=accepted):m=owner.stage(*args,root)
            self.assertEqual(m['guard_seconds'],90);self.assertEqual(m['launch_normal_seconds'],120)
            self.assertTrue((root/'split').is_dir())
            self.assertEqual((root/'compact-P-control.in').read_text().splitlines()[-3:],['-','0 64','qualify'])
            receipt=dict(status='PASS',exit=0,error=None,command=m['command'],cwd=m['cwd'],wall_s=1.,guard_source_sha256=m['guard_source_sha256'],
                         continuous_deadline_s=90,max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=1024)
            (root/'results/material').mkdir(parents=True);rpath=root/'results/material/receipt.json';rpath.write_text(json.dumps(receipt))
            (root/'results/material/console.log').write_text('COMPACT_P_PASS_COMPLETE rows=64\nINCOMPLETE P; no coefficient or norm acceptance\n')
            (root/'campaign_launch_watch.json').write_text('{"phase":"completed"}')
            fp=m['fingerprint']
            for sub,completed in ((root,64),(root/'split',32)):
                (sub/'compact-p.meta').write_text(f'{HEADER}\n65 67 3\n{completed}\n{fp}\n1 2\n')
                (sub/'compact-p.bin').write_bytes(bytes(396*8))
            (root/'compact-P-qualification.txt').write_text(f'compact-P-split-qualification-v1; all P bits equal\n{fp}\n65 67 3 64\n1 2 1 2\n')
            (root/'compact-P-progress.txt').write_text('64 65 1 2\n')
            mp=root/'run-manifest.json'
            def read():
                with patch.object(owner,'selected_analyze',return_value=selected),patch.object(owner,'accepted',side_effect=accepted):return owner.analyze(mp)
            self.assertTrue(read()['material_restart_qualified'])
            receipt['wall_s']=91;rpath.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError,'receipt'):read()
            receipt['wall_s']=1;rpath.write_text(json.dumps(receipt))
            with (root/'compact-p.bin').open('r+b') as stream:stream.write(struct.pack('<d',1.))
            with self.assertRaisesRegex(ValueError,'accepted P'):read()
