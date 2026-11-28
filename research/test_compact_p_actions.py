import array
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest

from compact_p_actions import compare


class CompactPActionsTest(unittest.TestCase):
    def fixture(self,root):
        n=7;r=2
        q=[[F(i+2*k+1,11) for k in range(r)] for i in range(n)]
        a=[[F((i+1)*(j+2)*(-1)**j,31) if (i<3)!=(j<3) else F(0) for j in range(n)] for i in range(n)]
        d=[F(i+1,9) for i in range(n)];v=[F((-1)**i*(i+2),13) for i in range(n)]
        adv=[sum(a[i][j]*d[j]*v[j] for j in range(n)) for i in range(n)]
        p=[[sum(q[i][k]*d[i]*a[i][j] for i in range(n)) for j in range(n)] for k in range(r)]
        for name,values in (('q',[q[i][k] for k in range(r) for i in range(n)]),('p',[p[k][j] for j in range(n) for k in range(r)])):
            with (root/name).open('wb') as stream:array.array('d',map(float,values)).tofile(stream)
        return root/'q',root/'p',list(map(float,d)),list(map(float,v)),list(map(float,adv)),r

    def test_independent_fraction_identity_and_wrong_action(self):
        with tempfile.TemporaryDirectory() as directory:
            args=self.fixture(Path(directory));result=compare(*args)
            self.assertEqual(result['controls'],2);self.assertLess(result['max_error_over_bound'],1e-4)
            for index in (2,4):
                changed=list(args);changed[index]=[x*1.01 if i==0 else x for i,x in enumerate(changed[index])]
                with self.assertRaisesRegex(ValueError,'mismatch'):compare(*changed)
            with args[1].open('r+b') as stream:array.array('d',[123.]).tofile(stream)
            with self.assertRaisesRegex(ValueError,'mismatch'):compare(*args)

    def test_stale_shape_and_nonfinite_data(self):
        with tempfile.TemporaryDirectory() as directory:
            args=self.fixture(Path(directory))
            for path in args[:2]:
                original=path.read_bytes();path.write_bytes(b'stale')
                with self.assertRaisesRegex(ValueError,'shape'):compare(*args)
                path.write_bytes(original)
                with path.open('r+b') as stream:array.array('d',[float('nan')]).tofile(stream)
                with self.assertRaisesRegex(ValueError,'Nonfinite'):compare(*args)
                path.write_bytes(original)
