import array
from fractions import Fraction as F
import json
import math
from pathlib import Path
import tempfile
import unittest

import test_compact_tile_material as admission_fixture
from compact_tile_material import stage
from compact_tile_readback import analyze,controls
from fetch_public_response_inputs import digest
from inverse_material_run import identity


class CompactTileReadbackTest(unittest.TestCase):
    def fixture(self,base):
        base,native,p,b=admission_fixture.CompactTileMaterialTest().fixture(base)
        n=132;left=65;right=67;rank=3;compact=p[2]
        state=[[.125]*n,[i/128 for i in range(n)],[(1+i%5)/16 for i in range(n)],[(i%7)/16 for i in range(n)],[(1+i%9)/16 for i in range(n)]]
        q=[[((7*i+3*k)%17-8)/64 for i in range(n)] for k in range(rank)]
        with (compact/'compact-state.bin').open('wb') as f:
            for values in state:array.array('d',values).tofile(f)
        with (compact/'compact-q.bin').open('wb') as f:
            for values in q:array.array('d',values).tofile(f)
        rawpath=compact/'compact-preparation-result.json';raw=json.loads(rawpath.read_text())
        for name in ('compact-state.bin','compact-q.bin'):raw['outputs'][name]=identity(compact/name)
        rawpath.write_text(json.dumps(raw));recorded=json.loads(p[1].read_text());recorded.update(raw,terminal_guard_pass=True,readback_sha256=digest(rawpath));p[1].write_text(json.dumps(recorded))
        root=base/'material';m=stage(*p[:2],*b[:2],root);mp=base/'material-manifest.json';mp.write_bytes((root/'run-manifest.json').read_bytes())
        def kernel(orientation,i,j):return F(((13 if orientation==1 else 17)*(i+1)+(7 if orientation==1 else 5)*(j+1))%(23 if orientation==1 else 29)-(11 if orientation==1 else 14),32)
        for tile in (1,2):
            values=[float(kernel(o,i,j)) for o in (1,2) for j in range(32*(tile-1),32*tile) for i in range(right)]
            with (root/f'compact-kernel-{tile}.bin').open('wb') as f:array.array('d',values).tofile(f)
        weights=[F(dk/2*(1.25/2 if x==0 else math.tanh(1.25*abs(x)/2)/abs(x))) for x,dk in zip(state[1],state[2])]
        out=[]
        for j in range(n):
            for k in range(rank):
                if j<64:value=sum(F(q[k][left+i])*F(state[4][left+i])*(-kernel(2,i,j)*weights[j]/(1+F(state[3][left+i]))) for i in range(right))
                elif j<left:value=F(0)
                else:value=sum(F(q[k][i])*F(state[4][i])*(-kernel(1,j-left,i)*weights[j]/(1+F(state[3][i]))) for i in range(64))
                out.append(float(value))
        with (root/'compact-partial-p.bin').open('wb') as f:array.array('d',out).tofile(f)
        lines=['selected-compact-native-tiles-v1; partial P only; NOT a norm','0']
        for tile in (1,2):
            lines.extend([f'{tile} kernel_cpu_s .1',f'{tile} contraction_cpu_s .01'])
            for r in (1,2,3):
                for j in (1+32*(tile-1),32*tile):lines.append(f'left {r} {j} 0 0 1e-10')
                for j in (1,34,67):lines.append(f'right {r} {j} 0 0 1e-10')
        (root/'compact-tile-checks.txt').write_text('\n'.join(lines)+'\n')
        (root/'results/material').mkdir(parents=True)
        receipt=dict(status='PASS',exit=0,error=None,command=m['command'],cwd=m['cwd'],wall_s=1,
                     guard_source_sha256=m['guard_source_sha256'],continuous_deadline_s=90,
                     max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=2048)
        (root/'results/material/receipt.json').write_text(json.dumps(receipt))
        (root/'campaign_launch_watch.json').write_text('{"phase":"completed"}')
        (root/'results/material/console.log').write_text('COMPACT_NATIVE_TILES_PASS rows=64; DIAGNOSTIC ONLY, incomplete P\n')
        return root,compact,mp

    def test_exact_partial_P_controls_and_complete_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root,compact,mp=self.fixture(Path(directory));result=analyze(mp)
            self.assertEqual(result['independent_controls'],21);self.assertTrue(result['terminal_guard_pass'])
            self.assertFalse(result['complete_P']);self.assertFalse(result['physical_response_verified'])
            self.assertLess(result['max_absolute_error'],1e-14)

    def test_changed_sample_unvisited_nonfinite_and_receipt_coverage_rejected(self):
        for fault in ('sample','unvisited','nonfinite','shape','receipt','coverage'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root,compact,mp=self.fixture(Path(directory))
                if fault in ('sample','unvisited'):
                    path=root/'compact-partial-p.bin'
                    with path.open('r+b') as f:f.seek(8*(64*3 if fault=='unvisited' else 0));array.array('d',[1.]).tofile(f)
                if fault=='nonfinite':
                    with (root/'compact-kernel-1.bin').open('r+b') as f:array.array('d',[float('nan')]).tofile(f)
                if fault=='shape':(root/'compact-kernel-1.bin').write_bytes(b'stale')
                if fault=='receipt':
                    path=root/'results/material/receipt.json';data=json.loads(path.read_text());data['wall_s']=91;path.write_text(json.dumps(data))
                if fault=='coverage':
                    path=root/'compact-tile-checks.txt';path.write_text(path.read_text().replace('left 1 1 ','left 1 32 ',1))
                with self.assertRaises(ValueError):analyze(mp)
