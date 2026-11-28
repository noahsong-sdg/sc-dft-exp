import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

import compact_p_segment as owner
from compact_p_readback import HEADER
from compact_tile_material import COPIED
from inverse_material_run import identity


class CompactPSegmentTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();prior=base/'prior';prior.mkdir();compact=base/'compact';compact.mkdir()
        fp='f'*64
        (compact/'compact-state.meta').write_text('header\n65 67 67 3\n1.25\n'+'a'*64+'\n'+'b'*64+'\n'+'c'*64+'\n')
        for name in (*COPIED,'compact-P-native.x'):(prior/name).write_text('fixture '+name)
        (prior/'compact-p.bin').write_bytes(bytes(396*8))
        (prior/'compact-p.meta').write_text(f'{HEADER}\n65 67 3\n64\n{fp}\n1 2\n')
        (prior/'results/material').mkdir(parents=True)
        for name in ('results/material/receipt.json','results/material/console.log','campaign_launch_watch.json'):(prior/name).write_text('{}')
        m=dict(cwd=str(prior),files=[identity(prior/name) for name in (*COPIED,'compact-P-native.x')],
               **{k:'fixture' for k in ('selected_manifest','selected_result','build_manifest','build_result','registration')})
        mp=base/'prior-manifest.json';mp.write_text(json.dumps(m));(prior/'run-manifest.json').write_bytes(mp.read_bytes())
        recorded=dict(material_restart_qualified=True,continuous_checkpoint=dict(completed_left_rows=64,cpu_s=[1.,2.]),
                      outputs={name:identity(prior/name) for name in ('compact-p.meta','compact-p.bin')})
        rp=base/'prior-result.json';rp.write_text(json.dumps(recorded))
        parents=({}, {},dict(cwd=str(compact)),dict(rank=3,operator_sha256='a'*64),{},fp,[65,67,67,3],{})
        return mp,rp,recorded,parents

    def test_predecessor_requires_replayed_verdict_and_exact_output(self):
        with tempfile.TemporaryDirectory() as directory:
            mp,rp,recorded,parents=self.fixture(Path(directory))
            with patch.object(owner,'qualify_analyze',return_value=recorded),patch.object(owner,'parents',return_value=parents):
                self.assertEqual(owner.predecessor(mp,rp)[4],'f'*64)
                changed=dict(recorded,material_restart_qualified=False);rp.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError,'Unaccepted'):owner.predecessor(mp,rp)
                rp.write_text(json.dumps(recorded));path=Path(json.loads(mp.read_text())['cwd'])/'compact-p.bin';path.write_bytes(b'x'*path.stat().st_size)
                with self.assertRaisesRegex(ValueError,'Changed P predecessor'):owner.predecessor(mp,rp)

    def test_final_short_segment_owner_coverage_and_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);mp,rp,recorded,parents=self.fixture(base);root=base/'segment'
            with patch.object(owner,'qualify_analyze',return_value=recorded),patch.object(owner,'parents',return_value=parents):
                m=owner.stage(mp,rp,root)
                self.assertEqual((root/'compact-P-control.in').read_text().splitlines()[-2:],['64 65','segment'])
                receipt=dict(status='PASS',exit=0,error=None,command=m['command'],cwd=m['cwd'],wall_s=1.,guard_source_sha256=m['guard_source_sha256'],
                             continuous_deadline_s=900,max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=1024)
                (root/'results/material').mkdir(parents=True);(root/'results/material/receipt.json').write_text(json.dumps(receipt))
                (root/'results/material/console.log').write_text('COMPACT_P_PASS_COMPLETE rows= 65 left= 65 mode=segment\n')
                (root/'campaign_launch_watch.json').write_text('{"phase":"completed"}')
                (root/'compact-p.meta').write_text(f'{HEADER}\n65 67 3\n65\n'+ 'f'*64+'\n2 3\n')
                (root/'compact-p.bin').write_bytes(bytes(396*8));progress=root/'compact-P-progress.txt';progress.write_text('65 65 2 3\n')
                manifest=root/'run-manifest.json';self.assertTrue(owner.analyze(manifest)['complete_P'])
                progress.write_text('64 65 2 3\n')
                with self.assertRaisesRegex(ValueError,'progress coverage'):owner.analyze(manifest)
                progress.write_text('65 65 2 3\n')
                with (root/'compact-p.bin').open('r+b') as stream:stream.write(struct.pack('<d',1.))
                with self.assertRaisesRegex(ValueError,'completed left'):owner.analyze(manifest)

    def test_progress_native_stride_and_cumulative_cpu(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'progress';path.write_text('1056 1060 2 3\n1060 1060 4 5\n')
            self.assertEqual(owner.progress(path,1060,[1,2],[4,5]),2)
            for text in ('1024 1060 2 3\n1060 1060 4 5\n','1056 1060 .5 3\n1060 1060 4 5\n','1056 1060 2 3\n1060 1060 4 6\n'):
                path.write_text(text)
                with self.assertRaises(ValueError):owner.progress(path,1060,[1,2],[4,5])
