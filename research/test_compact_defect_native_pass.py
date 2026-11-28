import array
from fractions import Fraction as F
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from compact_defect_state import compact as pack
from compact_defect_readback import controls
import test_compact_p_native_pass as first_pass


class CompactDefectNativePassTest(unittest.TestCase):
    def fixture(self,base):
        fixture=first_pass.CompactPNativePassTest();compact,result,q,vectors=fixture.fixture(base)
        prior,done=fixture.run_pass(base,compact,result,'complete-P',0,65)
        self.assertEqual(done.returncode,0,done.stderr)
        research=Path(__file__).resolve().parent
        sources=('compact_defect_io.f90','streamed_defect_core.f90','compact_p_checkpoint.f90',
                 'compact_defect_native_pass.f90','reduced_nonlinear_core.f90')
        subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                        'stubs.f90',*(str(research/x) for x in sources),'main.f90','-llapack','-lblas','-o','defect.x'],
                       cwd=base,check=True,capture_output=True)
        return compact,result,q,vectors,prior

    def run_pass(self,base,compact,result,prior,name,stops=(65,67),fingerprint='c'*64):
        root=base/name;root.mkdir();(root/'seed-control.in').write_text('/unused\n'+'a'*64+'\n')
        fields=['compact-full-defect-v1',str(compact),'3','a'*64,result['padded_candidate_sha256'],'b'*64,
                fingerprint,str(prior),f'{stops[0]} {stops[1]}']
        (root/'compact-defect-control.in').write_text('\n'.join(fields)+'\n')
        return root,subprocess.run([str(base/'defect.x')],cwd=root,capture_output=True,text=True)

    def values(self,path):
        values=array.array('d');values.frombytes(path.read_bytes());return values

    def test_complete_and_partial_against_independent_dense_I_minus_BJ(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);compact,result,q,vectors,prior=self.fixture(base);left,right,n,r=65,67,132,3
            q=[pack(x,[left,right,67],True) for x in q]
            d=pack(vectors[4],[left,right,67],True);z=pack(vectors[3],[left,right,67],False)
            xi=pack(vectors[1],[left,right,67],False);dk=pack(vectors[2],[left,right,67],False)
            w=[k/2*(1.25/2 if x==0 else math.tanh(1.25*abs(x)/2)/abs(x)) for k,x in zip(dk,xi)]
            a=[[0.]*n for _ in range(n)]
            for i in range(right):
                for j in range(left):
                    a[j][left+i]=-((13*(i+1)+7*(j+1))%23-11)/32*w[left+i]/(1+z[j])
                    a[left+i][j]=-((17*(i+1)+5*(j+1))%29-14)/32*w[j]/(1+z[left+i])
            b=[[float(i==j)+math.fsum(q[k][i]*q[k][j]*d[j] for k in range(r)) for j in range(n)] for i in range(n)]
            columns=[[(k,float(k==j)-a[k][j]*d[j]) for k in range(n) if k==j or a[k][j]] for j in range(n)]
            e=[[float(i==j)-math.fsum(b[i][k]*value for k,value in columns[j]) for j in range(n)] for i in range(n)]
            p=self.values(prior/'compact-p.bin')
            expected_c=[float(F(p[j*r+k])-F(q[k][j])) for j in range(n) for k in range(r)]
            for name,stops in (('full',(65,67)),('partial',(64,64))):
                root,done=self.run_pass(base,compact,result,prior,name,stops)
                self.assertEqual(done.returncode,0,done.stderr)
                self.assertIn('COMPACT_DEFECT_COMPLETE' if name=='full' else 'COMPACT_DEFECT_PARTIAL',done.stdout)
                c=self.values(root/'compact-c.bin');self.assertEqual(len(c),n*r)
                for actual,expected in zip(c,expected_c):self.assertLessEqual(abs(actual-expected),1e-13*(1+abs(expected)))
                rows=self.values(root/'compact-defect-rows.bin');self.assertEqual(len(rows),n)
                for i in range(n):
                    if i<left:expected=math.fsum(map(abs,e[i])) if i<stops[0] else 0.
                    else:expected=math.fsum(abs(e[i][j]) for j in (*range(stops[0]),*range(left,left+stops[1])))
                    self.assertLessEqual(abs(rows[i]-expected),2e-12*(1+expected))
                meta=(root/'compact-defect.meta').read_text().splitlines();self.assertEqual(list(map(int,meta[2].split())),list(stops))
                self.assertEqual(float(meta[6].split()[1]),max(rows))
                li=list(map(int,meta[4].split()));ri=list(map(int,meta[5].split()))
                lk=self.values(root/'defect-kernel-left.bin');rk=self.values(root/'defect-kernel-right.bin')
                self.assertEqual(list(lk),[float(((13*i+7*j)%23-11)/32) for j in li for i in range(1,right+1)])
                self.assertEqual(list(rk),[float(((17*i+5*j)%29-14)/32) for i in ri for j in range(1,stops[0]+1)])
                checked=controls(root,compact,prior,[left,right],r,stops)
                self.assertEqual(checked['complete_coverage'],name=='full');self.assertEqual(checked['independent_coefficient_controls'],18)
                self.assertLess(checked['row_max_error_over_bound'],1e-3)
                path=root/'compact-c.bin';original=path.read_bytes()
                with path.open('r+b') as stream:array.array('d',[123.]).tofile(stream)
                with self.assertRaisesRegex(ValueError,'Independent defect'):controls(root,compact,prior,[left,right],r,stops)
                path.write_bytes(original)

    def test_stale_incomplete_predecessor_and_invalid_stops_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);compact,result,_,_,prior=self.fixture(base)
            for name,stops,fp in (('split',(63,64),'c'*64),('wide',(66,67),'c'*64),('identity',(65,67),'d'*64)):
                root,done=self.run_pass(base,compact,result,prior,name,stops,fp)
                self.assertNotEqual(done.returncode,0);self.assertFalse((root/'compact-c.bin').exists())
            path=prior/'compact-p.meta';lines=path.read_text().splitlines();lines[2]='64';path.write_text('\n'.join(lines)+'\n')
            root,done=self.run_pass(base,compact,result,prior,'incomplete')
            self.assertNotEqual(done.returncode,0);self.assertFalse((root/'compact-c.bin').exists())
