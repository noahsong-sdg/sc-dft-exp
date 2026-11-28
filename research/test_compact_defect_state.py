"""Padded-source compaction, strict native readback and independent chosen-W actions."""
import array
from fractions import Fraction as F
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from compact_defect_state import FILES,actions,compact,inverse,write


class CompactDefectStateTest(unittest.TestCase):
    def fixture(self,base):
        q=[[1.,2,0,4,5,6],[-1.,3,0,2,4,7]];u=[[.1,.2,0,.4,.5,.6],[-.2,.3,0,.2,.4,.7]]
        basis=base/'basis.bin'
        with basis.open('wb') as stream:
            for values in q+u:array.array('d',values).tofile(stream)
        vectors=[[1e-5,2e-5,0,4e-5,5e-5,6e-5],[1.,2,99,4,5,6],[2.,3,99,5,6,7],
                 [.1,.2,99,.4,.5,.6],[.8,.7,0,.6,.5,.4]]
        root=base/'run';root.mkdir();result=write(root,basis,vectors,[2.,1,3,4],[2,3,3],2,1.25,'a'*64,'b'*64)
        return root,basis,q,u,vectors,result

    def compile(self,base):
        compiler=shutil.which('gfortran');self.assertIsNotNone(compiler)
        source=Path(__file__).with_name('compact_defect_io.f90')
        (base/'reader.f90').write_text('''program test
 use compact_defect_io
 use iso_fortran_env,only:dp=>real64
 implicit none
 real(dp),allocatable::q(:,:),u(:,:),state(:,:),w(:,:)
 character(512)::root
 character(64)::candidate
 integer::unit
 call get_command_argument(1,root)
 call get_command_argument(2,candidate)
 call read_compact_defect(trim(root),[2,3,3],2,1.25_dp,repeat('a',64),candidate,repeat('b',64),q,u,state,w)
 open(newunit=unit,file='echo.bin',status='new',access='stream',form='unformatted')
 write(unit)q,u,state,w
 close(unit)
end program
''')
        subprocess.run([compiler,'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',str(source),'reader.f90','-o','reader.x'],cwd=base,check=True,capture_output=True)

    def test_native_roundtrip_compaction_order_and_exact_dense_actions(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root,basis,q,u,vectors,result=self.fixture(base);self.compile(base)
            subprocess.run([str(base/'reader.x'),str(root),result['padded_candidate_sha256']],cwd=base,check=True,capture_output=True)
            expected=b''.join((root/name).read_bytes() for name in FILES[1:])
            self.assertEqual((base/'echo.bin').read_bytes(),expected)
            self.assertEqual(result['padded_candidate_sha256'],hashlib.sha256(array.array('d',vectors[0]).tobytes()).hexdigest())
            self.assertEqual(list(compact(vectors[1],[2,3,3],False)),[1,2,4,5,6])
            self.assertFalse(result['conditioned_gap_error_bounded'])
            w,errors=inverse([2.,1,3,4],2)
            for got,want in zip(w,[.8,-.2,-.6,.4]):self.assertAlmostEqual(got,want)
            self.assertLess(max(errors),1e-14)
            rhs=[1.,-.5,.25,.125,-.25];got=actions(root,5,2,[rhs])[0]
            d=list(compact(vectors[4],[2,3,3],True));qc=[list(compact(x,[2,3,3],True)) for x in q];uc=[list(compact(x,[2,3,3],True)) for x in u]
            # Exact represented chosen W, Q, U and D, explicitly form full B.
            b=[[F(i==j)+sum(F(uc[k][i])*F(w[l*2+k])*F(qc[l][j])*F(d[j]) for k in range(2) for l in range(2)) for j in range(5)] for i in range(5)]
            target=[float(sum(x*F(y) for x,y in zip(row,rhs))) for row in b]
            self.assertLess(max(abs(a-b) for a,b in zip(got,target)),1e-14)
            with self.assertRaisesRegex(ValueError,'Fresh'):write(root,basis,vectors,[2.,1,3,4],[2,3,3],2,1.25,'a'*64,'b'*64)

    def test_native_stale_legacy_context_trailing_shape_and_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);root,_,_,_,_,result=self.fixture(base);self.compile(base)
            saved={name:(root/name).read_bytes() for name in FILES}
            for mode in ('legacy','counts','extra-count','temperature','operator','long-operator','candidate','source','trailing','size','nonfinite','z'):
                with self.subTest(mode=mode):
                    for name,data in saved.items():(root/name).write_bytes(data)
                    lines=(root/FILES[0]).read_text().splitlines()
                    if mode=='legacy':lines[0]='gap-seed-v1; binary64 Fortran order'
                    if mode=='counts':lines[1]='3 2 3 2'
                    if mode=='extra-count':lines[1]+=' extra'
                    if mode=='temperature':lines[2]='1.5'
                    if mode in ('operator','candidate','source'):lines[{'operator':3,'candidate':4,'source':5}[mode]]='c'*64
                    if mode=='trailing':lines.append('extra')
                    if mode=='long-operator':lines[3]+=' '*256+'extra'
                    (root/FILES[0]).write_text('\n'.join(lines)+'\n')
                    if mode=='size':(root/'compact-q.bin').write_bytes(saved['compact-q.bin'][:-8])
                    if mode in ('nonfinite','z'):
                        path=root/('compact-q.bin' if mode=='nonfinite' else 'compact-state.bin');values=array.array('d');values.frombytes(path.read_bytes())
                        values[0 if mode=='nonfinite' else 15]=float('nan') if mode=='nonfinite' else -1.;path.write_bytes(values.tobytes())
                    run=subprocess.run([str(base/'reader.x'),str(root),result['padded_candidate_sha256']],cwd=base,capture_output=True)
                    self.assertNotEqual(run.returncode,0)
                    self.assertFalse((base/'echo.bin').exists())

    def test_padding_nonfinite_shape_and_singular_boundaries(self):
        for values,counts in (([1.,2,3,4],[1,2,2]),([1.,float('nan'),0,4],[1,2,2]),([1.],[1,2,2])):
            with self.assertRaises(ValueError):compact(values,counts,True)
        for matrix,rank in (([0.]*4,2),([1.,2.,3.],2),([1.],0),([float('nan')],1)):
            with self.assertRaises(ValueError):inverse(matrix,rank)
        with tempfile.TemporaryDirectory() as directory:
            root,basis,q,u,vectors,result=self.fixture(Path(directory));data=array.array('d');data.frombytes(basis.read_bytes());data[2]=1.
            basis.write_bytes(data.tobytes());fresh=root.parent/'fresh';fresh.mkdir()
            with self.assertRaisesRegex(ValueError,'padding'):write(fresh,basis,vectors,[2.,1,3,4],[2,3,3],2,1.25,'a'*64,'b'*64)
            self.assertFalse((fresh/'compact-state.meta').exists())
            data[2]=0.;basis.write_bytes(data.tobytes());vectors[3][0]=-1.
            with self.assertRaisesRegex(ValueError,'normalization'):write(fresh,basis,vectors,[2.,1,3,4],[2,3,3],2,1.25,'a'*64,'b'*64)
