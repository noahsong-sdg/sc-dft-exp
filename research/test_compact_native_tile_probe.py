"""Actual probe with synthetic native modules; exact partial-P oracle and mismatches."""
import array
from fractions import Fraction as F
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from compact_defect_state import compact,write

STUBS='''module sctk_val
 use iso_fortran_env,only:dp=>real64
 implicit none
 integer::ngap(2)=[65,67],ngapmax=67
 real(dp)::beta=1.25_dp,delta(67,2),xi(67,2),dk(67,2),z(67,2)
end module
module cached_kel
contains
 subroutine reset_kel_cache()
 end subroutine
end module
module cached_phonon
contains
 subroutine reset_phonon_cache()
 end subroutine
end module
module slab_operator
contains
 subroutine clear_slab()
 end subroutine
end module
module tiled_operator
 use iso_fortran_env,only:dp=>real64
contains
 subroutine build_tile(first,last,block,slab_width)
 integer,intent(in)::first,last,slab_width
 real(dp),intent(out)::block(67,first:last,2)
 integer::i,j
 do j=first,last
  do i=1,67
   block(i,j,1)=real(mod(13*i+7*j,23)-11,dp)/32
   block(i,j,2)=real(mod(17*i+5*j,29)-14,dp)/32
  end do
 end do
 end subroutine
end module
'''
MAIN='''program test
 use sctk_val
 use full_nonlinear_probe
 implicit none
 integer::i,g
 character(32)::mode
 call get_command_argument(1,mode)
 delta=0;xi=0;dk=0;z=0
 do g=1,2
  do i=1,ngap(g)
   delta(i,g)=.125_dp;xi(i,g)=real(i,dp)/128
   dk(i,g)=real(1+mod(i,5),dp)/16;z(i,g)=real(mod(i,7),dp)/16
  end do
 end do
 if(mode=='state')delta(1,1)=.25_dp
 if(mode=='geometry')ngap(1)=64
 call run_full_map(delta)
end program
'''


class CompactNativeTileTest(unittest.TestCase):
    def test_selected_both_orientations_dense_partial_P_and_context_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);research=Path(__file__).resolve().parent
            (base/'stubs.f90').write_text(STUBS);(base/'main.f90').write_text(MAIN)
            subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                            'stubs.f90',str(research/'compact_defect_io.f90'),str(research/'streamed_defect_core.f90'),
                            str(research/'compact_native_tile_probe.f90'),'main.f90','-lblas','-o','probe.x'],
                           cwd=base,check=True,capture_output=True)
            counts=[65,67,67];n=132;rank=3
            vectors=[[0.]*134 for _ in range(5)]
            for side,count in enumerate(counts[:2]):
                for i in range(1,count+1):
                    at=side*67+i-1;gap=.125;xi=i/128;dk=(1+i%5)/16;z=(i%7)/16
                    e=math.hypot(xi,gap);t=math.tanh(1.25*e/2)
                    d=dk/2*((xi/e)**2*t/e+1.25/2*(gap/e)**2*(1-t*t))
                    for values,v in zip(vectors,[gap,xi,dk,z,d]):values[at]=v
            basis=base/'basis.bin'
            q=[[((7*i+3*k)%17-8)/64 for i in range(1,135)] for k in range(1,4)]
            for values in q:
                values[65:67]=[0.,0.]
            with basis.open('wb') as stream:
                for values in q+q:array.array('d',values).tofile(stream)
            state=base/'state';state.mkdir()
            result=write(state,basis,vectors,[float(i==j) for j in range(3) for i in range(3)],counts,rank,1.25,'a'*64,'b'*64)
            control='selected-compact-native-tiles-v1\n'+str(state)+'\n3\n'+'a'*64+'\n'+result['padded_candidate_sha256']+'\n'+'b'*64+'\n'
            def run(name,mode='',text=control,seed='a'*64):
                root=base/('case-'+name);root.mkdir();(root/'compact-tile-control.in').write_text(text)
                (root/'seed-control.in').write_text('/unused\n'+seed+'\n')
                return root,subprocess.run([str(base/'probe.x'),mode],cwd=root,capture_output=True,text=True)
            root,done=run('normal');self.assertEqual(done.returncode,0,done.stderr)
            self.assertIn('incomplete P',done.stdout)
            checks=[line.split() for line in (root/'compact-tile-checks.txt').read_text().splitlines() if line.split()[0] in ('left','right')]
            self.assertEqual(len(checks),30)
            self.assertTrue(all(len(line)==6 for line in checks))
            with (root/'compact-partial-p.bin').open('rb') as stream:
                actual=array.array('d');actual.fromfile(stream,3*n)
            packed=[[F(x) for x in compact(values,counts,True)] for values in q]
            w=[F(x) for x in compact(vectors[2],counts,False)];z=[F(x) for x in compact(vectors[3],counts,False)]
            d=[F(x) for x in compact(vectors[4],counts,True)]
            expected=[]
            for j in range(n):
                for k in range(3):
                    if j<64:
                        value=sum(packed[k][65+i]*d[65+i]*(-F((17*(i+1)+5*(j+1))%29-14,32)*w[j]/(1+z[65+i])) for i in range(67))
                    elif j==64:value=F(0)
                    else:
                        value=sum(packed[k][i]*d[i]*(-F((13*(j-64)+7*(i+1))%23-11,32)*w[j]/(1+z[i])) for i in range(64))
                    expected.append(float(value))
            for a,b in zip(actual,expected):self.assertLessEqual(abs(a-b),1e-14*(1+abs(b)))
            self.assertEqual((root/'compact-kernel-1.bin').stat().st_size,67*32*2*8)
            for name,mode,text,seed in [('state','state',control,'a'*64),('geometry','geometry',control,'a'*64),
                    ('operator','',control,'c'*64),('stale','',control.replace('tiles-v1','tiles-v0'),'a'*64),
                    ('rank','',control.replace('\n3\n','\n3 extra\n'),'a'*64),
                    ('long','',control.replace('a'*64,'a'*64+' '*256+'extra'),'a'*64),
                    ('candidate','',control.replace(result['padded_candidate_sha256'],'c'*64),'a'*64),
                    ('source','',control.replace('b'*64,'c'*64),'a'*64),
                    ('trailing','',control+'extra\n','a'*64)]:
                with self.subTest(name=name):
                    bad,done=run(name,mode,text,seed);self.assertNotEqual(done.returncode,0)
                    self.assertFalse((bad/'compact-kernel-1.bin').exists())
            statepath=state/'compact-state.bin';original=statepath.read_bytes()
            changed=array.array('d');changed.frombytes(original);changed[4*n]+=1
            statepath.write_bytes(changed.tobytes())
            bad,done=run('derivative');self.assertNotEqual(done.returncode,0)
            self.assertIn('derivative',done.stderr)
            self.assertFalse((bad/'compact-kernel-1.bin').exists())
            statepath.write_bytes(original)
