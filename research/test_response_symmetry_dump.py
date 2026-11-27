from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from gap_symmetry_audit import read_rotations
from cell_moment_cache import read_pair


class ResponseSymmetryDumpTest(unittest.TestCase):
    def test_actual_export_module_matrix_order_and_legacy_assignment(self):
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler)
        source = Path(__file__).parent/'response_assignment_dump.f90'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'stubs.f90').write_text('''
module kinds
 use iso_fortran_env,only:dp=>real64
end module
module sctk_val
 use kinds
 integer,parameter::nx=2,nqbz=1,fbee=1,lbee=1
 real(dp)::q_fflo(3)=[.01_dp,0._dp,0._dp]
 real(dp)::xi0(2)=[-1._dp,1._dp],dx0(2)=[.5_dp,.5_dp]
end module
module el_phon
 integer,parameter::elph_nbnd_min=1,elph_nbnd_max=1
end module
module disp
 integer,parameter::nq1=1,nq2=1,nq3=1
end module
module symm_base
 integer,parameter::nsym=2
 integer::s(3,3,2)=reshape([1,0,0,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1],[3,3,2])
end module
module sctk_ini_delta
 use kinds
contains
 subroutine store_d3k(dos,velocity,curvature,shift,n,x,w,k,band,v,h)
 real(dp),intent(in)::dos(:,:,:),velocity(:,:,:),curvature(:,:,:),shift
 integer,intent(in)::n
 real(dp),intent(out)::x(n),w(n),v(n),h(n)
 integer,intent(out)::k(n),band(n)
 x=[-1._dp,1._dp];w=.5_dp;v=2;h=3;k=1;band=1
 end subroutine
end module
''')
            (root/'driver.f90').write_text('''
program test
 use kinds
 use response_assignment_dump
 real(dp)::dos(2,1,1,2),v(2,1,1,2),h(2,1,1,2)
 dos=1;v=2;h=3
 call dump_assignment(dos,v,h,.01_dp,10._dp)
 call dump_cell_moments('raw',dos,v,4*v,h,.01_dp,10._dp)
 call dump_cell_moments('averaged',dos,v,4*v,h,.01_dp,10._dp)
end program
''')
            subprocess.run([compiler, '-fcheck=all', '-ffree-line-length-none', 'stubs.f90',
                            str(source), 'driver.f90', '-o', 'test'], cwd=root, check=True, capture_output=True)
            subprocess.run([str(root/'test')], cwd=root, check=True, capture_output=True)
            dims, physical, raw, averaged = read_pair(root)
            self.assertEqual(dims, [2, 1, 1, 1, 2])
            self.assertEqual(physical, [.01, 10., .01, 0., 0.])
            self.assertEqual(list(raw['second']), [8.]*4)
            self.assertEqual(list(raw['curvature']), [3.]*4)
            self.assertEqual(raw, averaged)
            size, rotations = read_rotations(root/'response-symmetry.txt')
            self.assertEqual(size, 1)
            self.assertEqual(rotations[1], ((1, 1, 0), (0, 1, 0), (0, 0, 1)))
            self.assertEqual((root/'response-assignment.txt').read_text().splitlines()[0],
                             '# response-assignment-v1; native geometry only; NOT a gap transfer')
            self.assertEqual((root/'response-assignment.bin').stat().st_size, 16*2+80*2)


if __name__ == '__main__':
    unittest.main()
