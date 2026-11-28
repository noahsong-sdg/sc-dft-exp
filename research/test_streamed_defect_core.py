"""Real 32-row contractions against a separate exact dense I-BJ construction."""
import array
from fractions import Fraction as F
from functools import lru_cache
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


@lru_cache(maxsize=1)
def oracle():
    left,right,r=35,39,3;n=left+right
    weights=[F(1,2)+F(i%5,16) for i in range(1,n+1)]
    z=[F(i%7,16) for i in range(1,n+1)];d=[F(i%9,8) for i in range(1,n+1)]
    q=[[F((7*i+3*k)%17-8,64) for k in range(1,r+1)] for i in range(1,n+1)]
    u=[[F((11*i+5*k)%19-9,128) for k in range(1,r+1)] for i in range(1,n+1)]
    small=[[1+F(i,32) if i==j else F(i-j,64) for j in range(1,r+1)] for i in range(1,r+1)]
    a=[[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(1,right+1):
        for j in range(1,left+1):
            a[j-1][left+i-1]=-F((13*i+7*j)%23-11,32)*weights[left+i-1]/(1+z[j-1])
            a[left+i-1][j-1]=-F((17*i+5*j)%29-14,32)*weights[j-1]/(1+z[left+i-1])
    p=[[sum(q[k][i]*d[k]*a[k][j] for k in range(n)) for j in range(n)] for i in range(r)]
    c=[[sum(small[i][k]*(p[k][j]-q[j][k]) for k in range(r)) for j in range(n)] for i in range(r)]
    # Independently construct B and J, then multiply: do not reuse (A+UC)D.
    uw=[[sum(u[i][k]*small[k][j] for k in range(r)) for j in range(r)] for i in range(n)]
    b=[[F(i==j)+sum(uw[i][k]*q[j][k]*d[j] for k in range(r)) for j in range(n)] for i in range(n)]
    columns=[[(k,F(k==j)-a[k][j]*d[j]) for k in range(n) if k==j or a[k][j]] for j in range(n)]
    defect=[[F(i==j)-sum(b[i][k]*x for k,x in columns[j]) for j in range(n)] for i in range(n)]
    rows=[sum(map(abs,row)) for row in defect]
    same_left=sum(abs(defect[i][j]) for i in range(left) for j in range(left))
    same_right=sum(abs(defect[i][j]) for i in range(left,n) for j in range(left,n))
    assert same_left>0 and same_right>0
    return [float(p[i][j]) for j in range(n) for i in range(r)]+[float(c[i][j]) for j in range(n) for i in range(r)]+list(map(float,rows))


class StreamedDefectCoreTest(unittest.TestCase):
    def compile(self,root,framework=False):
        compiler=shutil.which('gfortran');self.assertIsNotNone(compiler)
        research=Path(__file__).resolve().parent
        link=['-lblas']
        if framework:
            sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
            link=[str(Path(sdk)/'System/Library/Frameworks/Accelerate.framework/Accelerate.tbd')]
        subprocess.run([compiler,'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                        str(research/'streamed_defect_core.f90'),str(research/'streamed_defect_fixture.f90'),
                        *link,'-o','fixture.x'],cwd=root,check=True,capture_output=True)

    def readback(self,root):
        result=subprocess.run([str(root/'fixture.x'),'normal'],cwd=root,check=True,capture_output=True,text=True)
        self.assertIn('DIAGNOSTIC ONLY',result.stdout)
        self.assertEqual(list(map(int,result.stdout.split()[2:8])),[35,39,3,36,36,40])
        data=array.array('d');data.frombytes((root/'defect-fixture.bin').read_bytes());expected=oracle()
        self.assertEqual(len(data),518)
        self.assertTrue(all(map(math.isfinite,data)))
        for start,end in ((0,222),(222,444),(444,518)):
            error=max(abs(a-b) for a,b in zip(data[start:end],expected[start:end]))
            scale=max(1.,max(map(abs,expected[start:end])))
            self.assertLess(error,3e-12*scale)

    def test_native_first_second_and_both_same_side_blocks_against_dense_rational(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.compile(root);self.readback(root)

    @unittest.skipUnless(sys.platform=='darwin','Mac framework binding')
    def test_framework_same_actual_32row_strided_layout_against_dense_rational(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.compile(root,True);self.readback(root)

    def test_incomplete_duplicate_stale_shape_nonfinite_and_normalization(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.compile(root)
            for mode in ('skip','duplicate','stale','incomplete','nonfinite','normalization','wide','shape',
                         'rows-stale','rows-duplicate','right-duplicate','omit'):
                with self.subTest(mode=mode):
                    cwd=root/mode;cwd.mkdir()
                    result=subprocess.run([str(root/'fixture.x'),mode],cwd=cwd,capture_output=True,text=True)
                    self.assertNotEqual(result.returncode,0)
                    self.assertFalse((cwd/'defect-fixture.bin').exists())
