import array
from fractions import Fraction as F
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from compact_defect_state import write
import test_compact_native_tile_probe as native_fixture


class CompactPNativePassTest(unittest.TestCase):
    def fixture(self,base):
        research=Path(__file__).resolve().parent
        (base/'stubs.f90').write_text(native_fixture.STUBS);(base/'main.f90').write_text(native_fixture.MAIN)
        sources=('compact_defect_io.f90','streamed_defect_core.f90','compact_p_checkpoint.f90',
                 'compact_p_native_pass.f90','reduced_nonlinear_core.f90')
        subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                        'stubs.f90',*(str(research/x) for x in sources),'main.f90','-llapack','-lblas','-o','pass.x'],
                       cwd=base,check=True,capture_output=True)
        subprocess.run([str(base/'pass.x'),'export'],cwd=base,check=True,capture_output=True)
        vectors=[[0.]*134 for _ in range(5)]
        for side,count in enumerate((65,67)):
            for i in range(1,count+1):
                xi=0. if i<=2 else i/128;gap=0. if i==2 else .125
                for values,x in zip(vectors,[gap,xi,(1+i%5)/16,(i%7)/16,0.]):values[side*67+i-1]=x
        with (base/'derivative.bin').open('rb') as f:vectors[4]=array.array('d');vectors[4].fromfile(f,134)
        q=[[((7*i+3*k)%17-8)/64 for i in range(1,135)] for k in range(1,4)]
        for values in q:values[65:67]=[0.,0.]
        basis=base/'basis.bin'
        with basis.open('wb') as f:
            for values in q+q:array.array('d',values).tofile(f)
        compact=base/'compact';compact.mkdir()
        result=write(compact,basis,vectors,[float(i==j) for j in range(3) for i in range(3)],
                     [65,67,67],3,1.25,'a'*64,'b'*64)
        return compact,result,q,vectors

    def run_pass(self,base,compact,result,name,completed,stopat,previous='-',mode='segment',fingerprint='c'*64):
        root=base/name;(root/'split').mkdir(parents=True)
        (root/'seed-control.in').write_text('/unused\n'+'a'*64+'\n')
        control='\n'.join(['ordered-compact-P-pass-v1',str(compact),'3','a'*64,result['padded_candidate_sha256'],
                           'b'*64,fingerprint,str(previous),f'{completed} {stopat}',mode])+'\n'
        (root/'compact-P-control.in').write_text(control)
        done=subprocess.run([str(base/'pass.x')],cwd=root,capture_output=True,text=True)
        return root,done

    def test_continuous_split_and_restart_partial_final_tile_against_exact_P(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);compact,result,q,vectors=self.fixture(base)
            qualified,done=self.run_pass(base,compact,result,'qualified',0,64,mode='qualify')
            self.assertEqual(done.returncode,0,done.stderr)
            self.assertIn('all P bits equal',(qualified/'compact-P-qualification.txt').read_text())
            final,done=self.run_pass(base,compact,result,'final',64,65,qualified)
            self.assertEqual(done.returncode,0,done.stderr)
            continuous,done=self.run_pass(base,compact,result,'continuous',0,65)
            self.assertEqual(done.returncode,0,done.stderr)
            self.assertEqual((final/'compact-p.bin').read_bytes(),(continuous/'compact-p.bin').read_bytes())
            from compact_defect_state import compact as pack
            q=[[F(x) for x in pack(values,[65,67,67],True)] for values in q]
            d=[F(x) for x in pack(vectors[4],[65,67,67],True)]
            xi=pack(vectors[1],[65,67,67],False);dk=pack(vectors[2],[65,67,67],False)
            w=[F(k/2*(1.25/2 if x==0 else math.tanh(1.25*abs(x)/2)/abs(x))) for x,k in zip(xi,dk)]
            z=[F(x) for x in pack(vectors[3],[65,67,67],False)]
            expected=[]
            for j in range(132):
                for k in range(3):
                    if j<65:value=sum(q[k][65+i]*d[65+i]*(-F((17*(i+1)+5*(j+1))%29-14,32)*w[j]/(1+z[65+i])) for i in range(67))
                    else:value=sum(q[k][i]*d[i]*(-F((13*(j-64)+7*(i+1))%23-11,32)*w[j]/(1+z[i])) for i in range(65))
                    expected.append(float(value))
            with (final/'compact-p.bin').open('rb') as f:actual=array.array('d');actual.fromfile(f,396)
            for a,b in zip(actual,expected):self.assertLessEqual(abs(a-b),1e-13*(1+abs(b)))

    def test_invalid_coverage_and_predecessor_identity_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);compact,result,_,_=self.fixture(base)
            prior,done=self.run_pass(base,compact,result,'prior',0,64);self.assertEqual(done.returncode,0,done.stderr)
            for name,completed,stopat,previous,mode,context in [
                    ('split',33,65,prior,'segment','c'*64),('end',0,63,'-','segment','c'*64),
                    ('missing',64,65,'-','segment','c'*64),('unexpected',0,64,prior,'segment','c'*64),
                    ('wrong-context',64,65,prior,'segment','d'*64),('unknown',0,64,'-','unknown','c'*64),
                    ('qualification',0,65,'-','qualify','c'*64)]:
                with self.subTest(name=name):
                    root,done=self.run_pass(base,compact,result,name,completed,stopat,previous,mode,context)
                    self.assertNotEqual(done.returncode,0);self.assertFalse((root/'compact-p.meta').exists())
