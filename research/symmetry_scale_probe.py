"""Compile the pinned owning symmetry routine against a scale-invariance control.

The fixture has identity and inversion, even DOS, and an odd velocity field.
For any nonzero Q, inversion must be excluded; Q=0 retains both symmetries.
This tests symmetry selection, not a material response or gap functional.
"""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

FIXTURE = Path(__file__).parent / 'fixtures/pinned_symm_dosk.f90'


def relative_selection(source):
    anchor = '     qnorm = DOT_PRODUCT(q_fflo2, q_fflo2)'
    if source.count(anchor) != 1:
        raise ValueError('Expected symmetry selector changed')
    return source.replace(anchor, '''     IF(MAXVAL(ABS(q_fflo)) > 0.0_dp) &
     & q_fflo2 = q_fflo2 / MAXVAL(ABS(q_fflo))
''' + anchor)


STUB = '''module kinds
 integer,parameter :: dp=kind(1.d0)
end module
module symm_base
 integer :: nsym=2,s(3,3,2)
end module
module disp
 integer :: nq1=3,nq2=3,nq3=3
end module
module el_phon
 integer :: elph_nbnd_min=1,elph_nbnd_max=1
end module
module io_global
 integer,parameter :: stdout=6
end module
module sctk_val
 use kinds
 integer :: nqbz=27,nx=1
 real(dp) :: q_fflo(3)
end module
module elph_tetra_mod
 integer,parameter :: lshift_q(3)=[1,1,1]
end module
module owning
contains
'''

DRIVER = '''end module
program probe
 use owning
 use kinds
 use symm_base
 use sctk_val
 implicit none
 real(dp) :: dos(1,1,27,2),velocity(1,1,27,2),curvature(1,1,27,2)
 real(dp) :: scales(6)=[1.e-4_dp,1.e-7_dp,1.e-8_dp,1.e-10_dp,1.e-12_dp,0._dp]
 real(dp) :: before(2),q,field
 integer :: axis,trial,g,k,i
 s=0
 do axis=1,3
 s(axis,axis,1)=1;s(axis,axis,2)=-1
 end do
 do trial=1,size(scales)
 q=scales(trial);q_fflo=[q,0._dp,0._dp]
 dos=1;curvature=0
 do g=1,2
 do k=1,27
 i=(k-1)/9
 field=sin(2*acos(-1._dp)*(real(i,dp)+real(g-1,dp)/2)/3)
 velocity(1,1,k,g)=max(q,1.e-100_dp)*field
 end do
 before(g)=sum(velocity(:,:,:,g)**2)
 end do
 call symm_dosk(dos,velocity,curvature)
 write(*,'(a,3es25.16)')'SCALE ',q, &
 sum(velocity(:,:,:,1)**2)/before(1),sum(velocity(:,:,:,2)**2)/before(2)
 end do
end program
'''


def run():
    compiler = shutil.which('gfortran')
    if not compiler:
        raise RuntimeError('gfortran is required for the owning-routine regression')
    source = FIXTURE.read_text()
    results = {}
    with tempfile.TemporaryDirectory(prefix='sctk-symmetry-') as directory:
        root = Path(directory)
        for label, routine in (('released', source), ('relative', relative_selection(source))):
            path = root / (label + '.f90')
            path.write_text(STUB + routine + DRIVER)
            exe = root / label
            subprocess.run([compiler, '-O0', '-std=f2008', '-fcheck=all',
                            str(path), '-o', str(exe)], cwd=root, check=True,
                           capture_output=True, text=True, timeout=30)
            output = subprocess.run([str(exe)], check=True, capture_output=True,
                                    text=True, timeout=10).stdout
            counts = list(map(int, re.findall(r'q_FFLO\s*:\s*(\d+)', output)))
            values = [list(map(float, line.split()[1:])) for line in output.splitlines()
                      if line.startswith('SCALE ')]
            if len(counts) != 6 or len(values) != 6:
                raise AssertionError('Missing full-routine symmetry output')
            results[label] = [dict(q_fractional=row[0], retained_symmetries=count,
                                   first_moment_squared_retention=row[1:])
                              for count, row in zip(counts, values)]
    return dict(fixture_sha256=hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
                source_revision='4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33',
                compiler=subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
                flags=['-O0', '-std=f2008', '-fcheck=all'], results=results,
                scope='Complete symmetry routine; identity/inversion odd-velocity fixture; no material prediction')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, allow_nan=False))
