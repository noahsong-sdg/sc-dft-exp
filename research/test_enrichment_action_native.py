import array
from fractions import Fraction as F
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from compact_defect_state import compact as pack
import test_compact_p_native_pass as parent_fixture
from enrichment_action_readback import controls


class EnrichmentActionNativeTest(unittest.TestCase):
    def test_full_partial_final_short_tile_and_stale_controls_against_dense(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);compact,meta,_,vectors=parent_fixture.CompactPNativePassTest().fixture(base)
            research=Path(__file__).resolve().parent
            sources=('compact_defect_io.f90','streamed_defect_core.f90','enrichment_action_core.f90',
                     'enrichment_action_native_pass.f90','reduced_nonlinear_core.f90')
            subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                            'stubs.f90',*(str(research/x) for x in sources),'main.f90','-llapack','-lblas','-o','enrich.x'],
                           cwd=base,check=True,capture_output=True)
            trial=[[((i*7+k*11)%19-9)/32 for i in range(132)] for k in range(3)]
            trialroot=base/'trials';trialroot.mkdir()
            with (trialroot/'trial-inputs.bin').open('wb') as stream:
                for col in trial:array.array('d',col).tofile(stream)
            xi=pack(vectors[1],[65,67,67],False);dk=pack(vectors[2],[65,67,67],False)
            w=[F(k/2*(1.25/2 if x==0 else math.tanh(1.25*abs(x)/2)/abs(x))) for x,k in zip(xi,dk)]
            z=list(map(F,pack(vectors[3],[65,67,67],False)));d=list(map(F,pack(vectors[4],[65,67,67],True)))
            def launch(name,stop=65,extra='',rank=3):
                root=base/name;root.mkdir();(root/'seed-control.in').write_text('/unused\n'+'a'*64+'\n')
                control='\n'.join(['enrichment-action-pass-v1',str(compact),str(rank),'a'*64,meta['padded_candidate_sha256'],'b'*64,str(trialroot),str(stop)])+'\n'+extra
                (root/'enrichment-action-control.in').write_text(control)
                return root,subprocess.run([str(base/'enrich.x')],cwd=root,capture_output=True,text=True)
            for stop in (64,65):
                root,done=launch(str(stop),stop);self.assertEqual(done.returncode,0,done.stderr)
                a=[[F(0) for _ in range(132)] for _ in range(132)]
                for i in range(67):
                    for j in range(stop):
                        a[j][65+i]=-F((13*(i+1)+7*(j+1))%23-11,32)*w[65+i]/(1+z[j])
                        a[65+i][j]=-F((17*(i+1)+5*(j+1))%29-14,32)*w[j]/(1+z[65+i])
                expected_action=[float(sum(a[i][j]*F(trial[k][j]) for j in range(132))) for k in range(3) for i in range(132)]
                expected_p=[float(sum(F(trial[k][i])*d[i]*a[i][j] for i in range(132))) for j in range(132) for k in range(3)]
                for name,expected in (('enrichment-actions.bin',expected_action),('enrichment-p.bin',expected_p)):
                    actual=array.array('d');actual.frombytes((root/name).read_bytes());self.assertEqual(len(actual),len(expected))
                    self.assertLess(max(abs(x-y) for x,y in zip(actual,expected)),1e-13)
                left=array.array('d');left.frombytes((root/'enrichment-kernel-left.bin').read_bytes())
                for k,j in enumerate((1,32,64,65,33,65)):
                    for i in range(67):self.assertEqual(left[67*k+i],((13*(i+1)+7*j)%23-11)/32 if j<=stop else 0.)
                right=array.array('d');right.frombytes((root/'enrichment-kernel-right.bin').read_bytes())
                for k,i in enumerate((1,34,67)):
                    for j in range(65):self.assertEqual(right[65*k+j],((17*i+5*(j+1))%29-14)/32 if j<stop else 0.)
                checked=controls(root,compact,trialroot,[65,67],3,stop)
                self.assertEqual(checked['complete_A_and_P'],stop==65)
                self.assertEqual(checked['bilinear_controls'],9)
                for filename in ('enrichment-actions.bin','enrichment-p.bin','enrichment-kernel-left.bin'):
                    path=root/filename;before=path.read_bytes()
                    with path.open('r+b') as stream:array.array('d',[123.]).tofile(stream)
                    with self.assertRaises(ValueError):controls(root,compact,trialroot,[65,67],3,stop)
                    path.write_bytes(before)
                path=root/'enrichment-action.meta';before=path.read_text();path.write_text(before+'stale\n')
                with self.assertRaises(ValueError):controls(root,compact,trialroot,[65,67],3,stop)
                path.write_text(before)
            for name,stop,extra,rank in (('trailing',65,'stale\n',3),('split',63,'',3),('rank',65,'',2)):
                root,done=launch(name,stop,extra,rank);self.assertNotEqual(done.returncode,0);self.assertFalse((root/'enrichment-action.meta').exists())
            (trialroot/'trial-inputs.bin').write_bytes(b'stale');root,done=launch('shape')
            self.assertNotEqual(done.returncode,0);self.assertFalse((root/'enrichment-actions.bin').exists())
