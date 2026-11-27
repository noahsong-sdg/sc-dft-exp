"""Compile an unmodified pinned upstream routine against synthetic state modules."""
import hashlib
import json
import math
import pathlib
import re
import subprocess
import tempfile
from urllib.request import urlopen

REVISION = "4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33"
SHA256 = "1062c2a6656455b223111928fbc37996fce564d6dcf0a3acc945b973a9101598"
URL = "https://raw.githubusercontent.com/mitsuaki1987/sctk/" + REVISION + "/src/sctk_broyden.f90"
STUB = """
module kinds
 use iso_fortran_env, only: dp=>real64
end module
module io_global
 use iso_fortran_env, only: stdout=>output_unit
end module
module cell_base
 use kinds
 real(dp) :: omega=1, bg(3,3)=0, tpiba=1
end module
module sctk_val
 use kinds
 real(dp) :: xi(2,2),delta(2,2),dxq(2,2),dk(2,2),d2xq(2,2),q_fflo(3),beta
 integer :: ngap(2)=2
end module
program probe
 use kinds
 use cell_base
 use sctk_val
 implicit none
 integer :: n
 bg(1,1)=1; bg(2,2)=1; bg(3,3)=1
 q_fflo=[1._dp,0._dp,0._dp]
 do n=1,4
   xi(1,:)=.4_dp; xi(2,:)=-.4_dp
   delta=1; dxq=.2_dp; d2xq=.3_dp; dk=1; beta=2
   if(n==2) dk(2,:)=.25_dp
   if(n==3) delta=0
   if(n==4) then
     xi(1,:)=1; xi(2,:)=-1
     dxq=2; delta=2; beta=100; dk(2,:)=.25_dp
   end if
   write(*,'(a,i0)') 'CASE ',n
   call supercurrent()
 end do
end program
"""


def expected(case):
    x, d, gap, beta, weight = (.4,.2,1.,2.,1.)
    if case == 2:
        weight = .25
    elif case == 3:
        gap = 0.
    elif case == 4:
        x,d,gap,beta,weight = 1.,2.,2.,100.,.25
    e = math.hypot(x,gap)
    def factors(energy):
        plus = math.tanh(.5*beta*(energy+d))
        minus = math.tanh(.5*beta*(energy-d))
        return .5*(plus+minus), .5*(plus-minus)
    ed,de = factors(e)
    xd,dx = factors(x)
    return sum(w*(2*d*(dx-de)+4*.3*(sign*xd-sign*x/e*ed))
               for sign,w in ((1.,1.),(-1.,weight)))


def run():
    with urlopen(URL, timeout=45) as response:
        data = response.read(1_000_001)
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Pinned source hash mismatch")
    match = re.search(r"(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent", data.decode())
    if not match:
        raise ValueError("Routine not found")
    with tempfile.TemporaryDirectory(prefix="sctk-full-current-") as folder:
        root = pathlib.Path(folder)
        source = root / "probe.f90"
        source.write_text(STUB + "\n" + match.group())
        subprocess.run(["gfortran","-O0","-std=f2008","-fcheck=all",
                        str(source),"-o",str(root/"probe")],cwd=root,check=True,
                       capture_output=True,text=True)
        result = subprocess.run([str(root/"probe")],check=True,capture_output=True,text=True)
    values = re.findall(r"Super current \[a.u.\] :\s+(\S+)\s+(\S+)", result.stdout)
    if len(values) != 4:
        raise ValueError("Expected four current outputs")
    rows = []
    for i, pair in enumerate(values,1):
        direct = expected(i)
        rows.append(dict(case=i, released=list(map(float,pair)), direct=direct,
                         absolute_error=abs(float(pair[0])-direct)))
    # Upstream writes only five significant digits: compare controls at its
    # printed precision, not at full internal floating-point precision.
    if rows[0]["absolute_error"] > 5e-6 or rows[2]["absolute_error"] > 5e-6:
        raise AssertionError("Symmetric/normal controls failed")
    if rows[1]["absolute_error"] < .3 or rows[3]["absolute_error"] < 4.:
        raise AssertionError("Expected asymmetric counterexamples missing")
    return dict(revision=REVISION,source_sha256=SHA256,cases=rows,
                scope="Synthetic weighted states, serial build; no material prediction")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,allow_nan=False))
