import array
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from defect_spectrum_readback import check


class DefectRowSpectrumTest(unittest.TestCase):
    def write(self,path,values):
        with path.open('wb') as stream:array.array('d',values).tofile(stream)

    def read(self,path):
        values=array.array('d');values.frombytes(path.read_bytes());return values

    def test_exact_two_mode_spectrum_and_basis_overlap_and_stale_input(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);source=Path(__file__).resolve().parent/'defect_row_spectrum.f90'
            subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',str(source),'-llapack','-lblas','-o',str(base/'spectrum.x')],check=True,capture_output=True)
            n=128;r=2
            for inside in (False,True):
                root=base/str(inside);root.mkdir();compact=root/'compact';compact.mkdir();defect=root/'defect';defect.mkdir();tiles=root/'tiles';tiles.mkdir()
                (compact/'compact-state.meta').write_text('fixture\n64 64 64 2\n1.25\n')
                u=[0.]*(n*r);u[0]=u[1]=1.;u[n]=1.;u[n+1]=-1.
                q=[0.]*(n*r);q[0]=q[n+1]=1.
                state=[0.]*(n*5);state[4*n:]=[.5]*n
                c=[0.]*(n*r);j=0 if inside else 64;c[2*j]=8.;c[2*(j+1)+1]=4.
                for name,values in (('compact-u.bin',u),('compact-q.bin',q),('compact-state.bin',state)):self.write(compact/name,values)
                self.write(defect/'compact-c.bin',c)
                for tile in (1,2):self.write(tiles/f'compact-kernel-{tile}.bin',[0.]*(64*32*2))
                control='retained-defect-row-spectrum-v1\n'+str(compact)+'\n'+str(defect)+'\n'+str(tiles)+'\n64 64 2 64\n'
                (root/'spectrum-control.in').write_text(control)
                done=subprocess.run([str(base/'spectrum.x')],cwd=root,capture_output=True,text=True);self.assertEqual(done.returncode,0,done.stderr)
                lines=(root/'row-spectrum.txt').read_text().splitlines();self.assertEqual(list(map(int,lines[1].split())),[64,64,2,64,2])
                eig=list(map(float,lines[2:]));self.assertEqual(len(eig),64);self.assertAlmostEqual(eig[-2],8.);self.assertAlmostEqual(eig[-1],32.)
                e=self.read(root/'row-errors.bin');self.assertEqual(e[64*j:64*j+2],array.array('d',[4.,4.]));self.assertEqual(e[64*(j+1):64*(j+1)+2],array.array('d',[2.,-2.]))
                overlap=self.read(root/'basis-overlap.bin');self.assertAlmostEqual(math.fsum(x*x for x in overlap),2. if inside else 0.,places=12)
                vg=self.read(root/'direction-gram.bin');self.assertLess(max(abs(x-float(i in (0,3))) for i,x in enumerate(vg)),1e-12)
                self.assertTrue(all(x==0 for x in self.read(root/'row-baselines.bin')))
                self.write(defect/'compact-defect-rows.bin',[6.,6.]+[0.]*126)
                checked=check(root,compact,defect,tiles,[64,64,2])
                self.assertAlmostEqual(checked['retained_energy_fractions']['1'],.8)
                self.assertAlmostEqual(sum(checked['basis_projection_squared_norms']),2. if inside else 0.)
                self.assertFalse(checked['adopted_directions'])
                path=root/'row-gram.bin';before=path.read_bytes()
                with path.open('r+b') as stream:array.array('d',[123.]).tofile(stream)
                with self.assertRaises(ValueError):check(root,compact,defect,tiles,[64,64,2])
                path.write_bytes(before)
            # Fresh bad runs reject stale payloads and invalid persisted control.
            bad=base/'bad';bad.mkdir();(bad/'spectrum-control.in').write_text(control+'extra\n')
            done=subprocess.run([str(base/'spectrum.x')],cwd=bad,capture_output=True,text=True);self.assertNotEqual(done.returncode,0)
            (bad/'spectrum-control.in').write_text(control);(compact/'compact-u.bin').write_bytes(b'stale')
            done=subprocess.run([str(base/'spectrum.x')],cwd=bad,capture_output=True,text=True);self.assertNotEqual(done.returncode,0);self.assertFalse((bad/'row-spectrum.txt').exists())
