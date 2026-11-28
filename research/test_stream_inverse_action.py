"""Exact rational dense control, stale small system, finite domain and allocation."""
import array
from fractions import Fraction
from pathlib import Path
import tempfile
import tracemalloc
import unittest

from stream_inverse_action import apply, solve_small


def exact_solve(matrix,rhs):
    rows=[[Fraction(str(x)) for x in row]+[Fraction(str(b))] for row,b in zip(matrix,rhs)]
    n=len(rows)
    for k in range(n):
        p=next(i for i in range(k,n) if rows[i][k]);rows[k],rows[p]=rows[p],rows[k]
        pivot=rows[k][k];rows[k]=[x/pivot for x in rows[k]]
        for i in range(n):
            if i!=k:
                factor=rows[i][k];rows[i]=[a-factor*b for a,b in zip(rows[i],rows[k])]
    return [float(row[-1]) for row in rows]


class StreamInverseActionTest(unittest.TestCase):
    def fixture(self,root):
        q=[[1.,0,0,0],[0,1.,0,0]];u=[[.1,.2,.3,0],[.2,-.1,.2,.1]];d=[.8,.7,.6,.5]
        m=[float(i==j)-sum(q[i][k]*d[k]*u[j][k] for k in range(4)) for j in range(2) for i in range(2)]
        path=root/'basis.bin'
        with path.open('wb') as out:
            for col in q+u:array.array('d',col).tofile(out)
        return path,q,u,d,m

    def test_nonsymmetric_dense_rational_control_and_multiple_rhs(self):
        with tempfile.TemporaryDirectory() as directory:
            path,q,u,d,m=self.fixture(Path(directory));rhss=[[1.,-2.,3.,4.],[.2,.1,0.,-.3]]
            result=apply(path,d,m,rhss)
            full=[[float(i==j)-sum(u[k][i]*q[k][j]*d[j] for k in range(2)) for j in range(4)] for i in range(4)]
            self.assertNotEqual(full[0][1],full[1][0])
            for answer,rhs,error,bound in zip(result['answers'],rhss,result['independent_action_max_errors'],result['independent_action_bounds']):
                expected=exact_solve(full,rhs)
                self.assertLess(max(abs(a-b) for a,b in zip(answer,expected)),2e-15)
                self.assertLessEqual(error,bound)
            self.assertFalse(result['conditioned_gap_error_bounded'])
            self.assertFalse(result['physical_response_verified'])
            changed=list(m);changed[0]+=.01
            with self.assertRaisesRegex(ValueError,'action differs'):apply(path,d,changed,rhss)

    def test_pivot_and_singular_nonfinite_shape_boundaries(self):
        self.assertEqual(solve_small([0.,1.,1.,0.],[2.,3.]),[3.,2.])
        for matrix,rhs in (([0.]*4,[1.,1.]),([1.,float('nan'),0.,1.],[1.,1.]),([1.],[float('inf')]),([] ,[])):
            with self.assertRaises(ValueError):solve_small(matrix,rhs)
        with tempfile.TemporaryDirectory() as directory:
            path,_,_,d,m=self.fixture(Path(directory))
            for diagonal,small,rhss in ((d,m,[]),(d,m,[[1.]]),([float('inf')]*4,m,[[1.]*4]),(d,[1.]*3,[[1.]*4]),([1e308]*4,m,[[1e308]*4])):
                with self.assertRaises(ValueError):apply(path,diagonal,small,rhss)
            original=path.read_bytes();path.write_bytes(original[:-8])
            with self.assertRaisesRegex(ValueError,'inputs'):apply(path,d,m,[[1.]*4])
            a=array.array('d');a.frombytes(original);a[0]=float('nan');path.write_bytes(a.tobytes())
            with self.assertRaisesRegex(ValueError,'basis column'):apply(path,d,m,[[1.]*4])

    def test_allocations_do_not_hold_a_full_basis_payload(self):
        n,rank=1024,32
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'basis.bin'
            with path.open('wb') as out:
                for scale in (1.,.1):
                    for j in range(rank):
                        col=array.array('d',[0.])*n;col[j]=scale;col.tofile(out)
            small=[.9*float(i==j) for j in range(rank) for i in range(rank)]
            diagonal=array.array('d',[1.])*n;rhs=array.array('d',[0.])*n;rhs[0]=1.
            tracemalloc.start()
            try:
                result=apply(path,diagonal,small,[rhs]);_,peak=tracemalloc.get_traced_memory()
            finally:tracemalloc.stop()
            self.assertAlmostEqual(result['answers'][0][0],1/.9)
            self.assertLess(peak,3*path.stat().st_size/4)
