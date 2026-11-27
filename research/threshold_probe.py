"""Held-out boundary cases for the complete corrected upstream routine."""
import hashlib
import json
import re
from urllib.request import urlopen
from full_current_probe import URL, SHA256, STUB, compile_run, correction, stable_correction, direct_current


def run():
    with urlopen(URL, timeout=45) as response:
        data = response.read(1_000_001)
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("Source hash mismatch")
    routine = re.search(r"(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent",data.decode()).group()
    # Diagnostic output precision only; arithmetic is unchanged by this edit.
    if routine.count("2e15.5") != 1:
        raise ValueError("Output format changed")
    routine = routine.replace("2e15.5", "2es25.16")
    cases = [(x,d,g,b,.25) for b in (2.,20.,100.) for d in (.2,1.,2.)
             for x in (d-.01,d,d+.01) for g in (0.,.1,1.)]
    driver = [STUB.split("program probe")[0], "program probe", "use kinds",
              "use cell_base", "use sctk_val", "implicit none",
              "bg(1,1)=1; bg(2,2)=1; bg(3,3)=1",
              "q_fflo=[1._dp,0._dp,0._dp]"]
    for x,d,g,b,w in cases:
        driver += ["xi(1,:)=%s_dp; xi(2,:)=-%s_dp" % (x,x),
                   "dxq=%s_dp; delta=%s_dp; beta=%s_dp" % (d,g,b),
                   "d2xq=.3_dp; dk(1,:)=1; dk(2,:)=%s_dp" % w,
                   "call supercurrent()"]
    driver += ["end program"]
    values = compile_run(correction(routine), "\n".join(driver))
    stable_values = compile_run(stable_correction(routine), "\n".join(driver))
    if len(values) != len(cases):
        raise ValueError("Incomplete native output")
    rows = []
    for case,value,stable in zip(cases,values,stable_values):
        direct = direct_current(*case)
        actual = float(value[0])
        rows.append(dict(x=case[0],d=case[1],gap=case[2],beta=case[3],
                         stable=float(stable[0]),stable_error=abs(float(stable[0])-direct),
                         corrected=actual,direct=direct,error=abs(actual-direct)))
    stable_failures = sum(r["stable_error"] > 1e-7 for r in rows)
    if stable_failures:
        raise AssertionError("Stable candidate failed %s boundary cases" % stable_failures)
    return dict(cases=len(rows),worst_cases=sorted(rows,key=lambda r:r["error"],reverse=True)[:12],
                stable_failures_over_print_tolerance=stable_failures,
                stable_max_absolute_error=max(r["stable_error"] for r in rows),
                failures_over_print_tolerance=sum(r["error"]>5e-5 for r in rows),
                scope="Synthetic boundary grid; diagnostic precision expanded; stable absolute tolerance 1e-7")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,allow_nan=False))
