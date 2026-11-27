"""Compile the actual wrapper against tiny dependency stubs; no physics claim."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

STUBS = """
module environment
contains
subroutine environment_start(name)
character(*) :: name
end subroutine
subroutine environment_end(name)
character(*) :: name
end subroutine
end module
module input_parameters
character(20) :: calculation='scdft', restart_mode='from_scratch'
end module
module elph_tetra_mod
logical :: lshift_q
end module
module sctk_stdin
contains
subroutine stdin_control()
end subroutine
subroutine stdin_scdft()
end subroutine
end module
module sctk_read_file
contains
subroutine degenerated_band()
end subroutine
subroutine read_a2Fsave()
end subroutine
subroutine read_elph()
end subroutine
end module
module sctk_ini_delta
contains
subroutine energy_grid()
end subroutine
subroutine ini_delta(allocate_state)
logical :: allocate_state
end subroutine
end module
module sctk_val
use iso_fortran_env, only: dp=>real64
real(dp) :: xi(2,2)=.1_dp, delta(2,2)=.01_dp, dk(2,2)=1._dp
real(dp) :: dxq(2,2)=.001_dp, d2xq(2,2)=.0001_dp
real(dp) :: q_fflo(3)=[.001_dp,0._dp,0._dp], beta=100._dp
integer :: ngap(2)=[1,2], kindx(2,2)=1, bindx(2,2)=2
end module
module cell_base
use iso_fortran_env, only: dp=>real64
real(dp) :: omega=1._dp, bg(3,3)=0._dp, tpiba=1._dp
end module
subroutine read_file_new(needwf)
logical, intent(inout) :: needwf
if (needwf) error stop 'Expected initial false argument'
needwf=.true.
end subroutine
"""


@unittest.skipUnless(shutil.which('gfortran'), 'gfortran unavailable')
class PreparationWrapperTests(unittest.TestCase):
    def test_mutable_qe_argument_and_complete_state_serialization(self):
        wrapper = Path(__file__).with_name('prepare_response_state.f90')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'stubs.f90').write_text(STUBS)
            subprocess.run(['gfortran','-std=f2008','-fcheck=all',
                            str(root/'stubs.f90'),str(wrapper),'-o',str(root/'probe')],
                           cwd=root,check=True,capture_output=True,text=True)
            subprocess.run([str(root/'probe')],cwd=root,check=True,
                           capture_output=True,text=True)
            lines=(root/'response-state.txt').read_text().splitlines()
        self.assertIn('NOT self-consistent',lines[0])
        self.assertEqual(list(map(int,lines[1].split())),[1,2])
        self.assertEqual(len(lines),8)
        self.assertEqual([list(map(int,line.split()[-3:])) for line in lines[5:]],
                         [[1,1,2],[2,1,2],[2,1,2]])
        for line in lines[5:]:
            values=list(map(float,line.split()[:5]))
            self.assertEqual(values,[.1,.01,1.,.001,.0001])


if __name__ == '__main__':
    unittest.main()
