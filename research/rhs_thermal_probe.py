"""Compile the pinned finite-temperature RHS thermal block, not the full RHS."""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile
from urllib.request import urlopen

REVISION = "4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33"
URL = "https://raw.githubusercontent.com/mitsuaki1987/sctk/" + REVISION + "/src/sctk_gapeq_rhs.f90"
SHA256 = "177d0e9738a4accf658aea108b5349a1d392035b3ec4e98c1c5fea82c98ccf73"
CASES = ((0., 2., 2., 20.), (0., 2., 2., 100.),
         (0., .0002, .0002, 1.e6), (0., 1.99, 2., 100.),
         (0., 2.01, 2., 100.), (.4, .1, .2, 2.))


def extract(data):
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Pinned RHS source differs")
    text = data.decode()
    start = text.index("        tanhe = TANH")
    end = text.index("      END DO", start)
    return text[start:end]


def reference(x, gap, shift, beta):
    energy = math.hypot(x, gap)
    return .5 * (math.tanh(.5*beta*(energy+shift)) +
                 math.tanh(.5*beta*(energy-shift)))


def run():
    with urlopen(URL, timeout=45) as response:
        data = response.read(1_000_001)
    block = extract(data)
    header = """program probe
use iso_fortran_env, only: dp=>real64
implicit none
real(dp) :: xi(1,1), delta(1,1), dxq(1,1), chi(1,1), beta, tanhe, tanhd
integer :: igap=1, ii=1
"""
    driver = [header]
    for x, gap, shift, beta in CASES:
        driver.append("xi=%s_dp; delta=%s_dp; dxq=%s_dp; beta=%s_dp" %
                      (x, gap, shift, beta))
        driver.extend((block, "write(*,'(es25.16)') chi(1,1)"))
    driver.append("end program")
    with tempfile.TemporaryDirectory(prefix="sctk-rhs-thermal-") as folder:
        root = Path(folder)
        source = root / "probe.f90"
        source.write_text("\n".join(driver))
        subprocess.run(["gfortran", "-O0", "-std=f2008", "-fcheck=all",
                        str(source), "-o", str(root/"probe")], check=True,
                       capture_output=True, text=True)
        output = subprocess.check_output([str(root/"probe")], text=True)
    actual = [float(line) for line in output.splitlines()]
    if len(actual) != len(CASES):
        raise AssertionError("Incomplete thermal fixture output")
    rows = [dict(x=x, gap=g, shift=d, beta=b, released=a,
                 direct=reference(x,g,d,b), error=abs(a-reference(x,g,d,b)))
            for (x,g,d,b),a in zip(CASES,actual)]
    if any(row["error"] < .49 for row in rows[:3]):
        raise AssertionError("Expected finite-temperature counterexample absent")
    if any(row["error"] < .25 for row in rows[3:5]):
        raise AssertionError("Expected non-equality thermal-window failure absent")
    if rows[-1]["error"] > 1e-14:
        raise AssertionError("Regular control differs")
    return dict(revision=REVISION, source_sha256=SHA256, cases=rows,
                scope="Exact extracted finite-T block; no full RHS or gap solution")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, allow_nan=False))
