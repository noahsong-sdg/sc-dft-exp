import array
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from stream_inverse_action import solve_small
from resolved_inverse_readback import check


def put(path,values):
    with path.open('wb') as stream:array.array('d',values).tofile(stream)


def get(path):
    result=array.array('d');result.frombytes(path.read_bytes());return result


def fixture(base):
    left,right,oldr=65,67,2;n=left+right;r=oldr+9
    compact=base/'compact';trialroot=base/'trials';full=base/'full';previous=base/'previous';oldc=base/'oldc'
    for p in (compact,trialroot,full,previous,oldc):p.mkdir()
    w=[.5+(i%5)/16 for i in range(n)];z=[(i%7)/16 for i in range(n)];d=[.5+(i%3)/16 for i in range(n)]
    a=[[0.]*n for _ in range(n)];kl=[];kr=[]
    for j in range(left):
        for i in range(right):
            k1=((13*(i+1)+7*(j+1))%23-11)/256;k2=((17*(i+1)+5*(j+1))%29-14)/256
            a[j][left+i]=-k1*w[left+i]/(1+z[j]);a[left+i][j]=-k2*w[j]/(1+z[left+i])
    positions=[0,1]+list(range(left,left+9))
    q=[[float(i==j) for i in range(n)] for j in positions];u=[[a[i][j] for i in range(n)] for j in positions]
    p=[[d[pos]*a[pos][j] for j in range(n)] for pos in positions]
    def small_inverse(rank):
        m=[float(i==j)-d[positions[i]]*u[j][positions[i]] for j in range(rank) for i in range(rank)]
        inv=[x for j in range(rank) for x in solve_small(m,[float(i==j) for i in range(rank)])]
        c=[[math.fsum(inv[k*rank+i]*(p[k][j]-q[k][j]) for k in range(rank)) for j in range(n)] for i in range(rank)]
        return m,inv,c
    oldm,oldw,oldcoeff=small_inverse(oldr);m,inv,c=small_inverse(r)
    put(compact/'compact-q.bin',[x for col in q[:oldr] for x in col]);put(compact/'compact-u.bin',[x for col in u[:oldr] for x in col])
    put(compact/'compact-state.bin',[0.]*n+[0.]*n+[2*x for x in w]+z+d)
    (compact/'compact-state.meta').write_text('fixture\n65 67 67 2\n2\n'+'a'*64+'\n'+'b'*64+'\n'+'c'*64+'\n')
    put(trialroot/'trial-inputs.bin',[x for col in q[oldr:] for x in col]);put(full/'enrichment-actions.bin',[x for col in u[oldr:] for x in col])
    put(previous/'compact-p.bin',[p[i][j] for j in range(n) for i in range(oldr)])
    put(full/'enrichment-p.bin',[p[i][j] for j in range(n) for i in range(oldr,r)])
    put(oldc/'compact-c.bin',[oldcoeff[i][j] for j in range(n) for i in range(oldr)])
    li=[0,31,63,64,16,47];ri=[1,15,49]
    put(full/'enrichment-kernel-left.bin',[((13*(i+1)+7*(j+1))%23-11)/256 for j in li for i in range(right)])
    put(full/'enrichment-kernel-right.bin',[((17*(i+1)+5*(j+1))%29-14)/256 for i in ri for j in range(left)])
    control='resolved-inverse-rows-v1\n'+'\n'.join(map(str,(compact,trialroot,full,previous,oldc)))+'\n65 67 2\n'
    (base/'enriched-inverse-control.in').write_text(control)
    indices=li+[left+i for i in ri]
    expected=[]
    for rank,winv in ((oldr,oldw),(r,inv)):
        rows=[]
        for row in indices:
            # Form B explicitly, then I-BJ: independent of (A+UC)D identity.
            b=[float(row==j)+math.fsum(u[k][row]*winv[l*rank+k]*q[l][j]*d[j] for k in range(rank) for l in range(rank)) for j in range(n)]
            support=[k for k,x in enumerate(b) if x]
            rows.append([float(row==j)-math.fsum(b[k]*(float(k==j)-a[k][j]*d[j]) for k in support) for j in range(n)])
        expected.append(rows)
    accepted=[0.]*64
    for i,j in enumerate((0,31,63)):accepted[j]=math.fsum(map(abs,expected[0][i]))
    put(oldc/'compact-defect-rows.bin',accepted)
    return dict(compact=compact,trials=trialroot,full=full,previous=previous,oldc=oldc,counts=[65,67,2],q=q,u=u,d=d,p=p,m=m,w=inv,c=c,expected=expected,control=control)


class ResolvedInverseRowsTest(unittest.TestCase):
    def test_native_small_inverse_and_complete_rows_against_dense_BJ(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);f=fixture(base);source=Path(__file__).resolve().parent/'resolved_inverse_rows.f90'
            subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',str(source),'-llapack','-lblas','-o',str(base/'inverse.x')],check=True,capture_output=True)
            done=subprocess.run([str(base/'inverse.x')],cwd=base,capture_output=True,text=True);self.assertEqual(done.returncode,0,done.stderr)
            for name,key in (('enriched-m.bin','m'),('enriched-w.bin','w')):
                self.assertLess(max(abs(x-y) for x,y in zip(get(base/name),f[key])),1e-12)
            for name,rows in zip(('baseline-rows.bin','enriched-rows.bin'),f['expected']):
                expected=[rows[i][j] for j in range(132) for i in range(9)]
                self.assertLess(max(abs(x-y) for x,y in zip(get(base/name),expected)),1e-12)
            checked=check(base,f['compact'],f['trials'],f['full'],f['previous'],f['oldc'],f['counts'])
            self.assertFalse(checked['inverse_adopted'])
            for name in ('enriched-m.bin','enriched-w.bin','enriched-c.bin','enriched-rows.bin','baseline-rows.bin','enriched-norms.bin'):
                path=base/name;before=path.read_bytes()
                with path.open('r+b') as stream:array.array('d',[123.]).tofile(stream)
                with self.assertRaises(ValueError):check(base,f['compact'],f['trials'],f['full'],f['previous'],f['oldc'],f['counts'])
                path.write_bytes(before)
            bad=base/'bad';bad.mkdir();(bad/'enriched-inverse-control.in').write_text(f['control']+'stale\n')
            done=subprocess.run([str(base/'inverse.x')],cwd=bad,capture_output=True,text=True);self.assertNotEqual(done.returncode,0)
            (bad/'enriched-inverse-control.in').write_text(f['control'].replace('resolved-inverse-rows-v1','enriched-inverse-rows-v1'))
            done=subprocess.run([str(base/'inverse.x')],cwd=bad,capture_output=True,text=True);self.assertNotEqual(done.returncode,0)
            (bad/'enriched-inverse-control.in').write_text(f['control'])
            trial=f['trials']/'trial-inputs.bin';trial.write_bytes(trial.read_bytes()[:8*132*3])
            done=subprocess.run([str(base/'inverse.x')],cwd=bad,capture_output=True,text=True);self.assertNotEqual(done.returncode,0);self.assertFalse((bad/'enriched-m.bin').exists())
