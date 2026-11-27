# Review candidate against pinned SCTK

`sctk-4bc883e-thermal-candidate.patch` targets revision
`4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33`. It is not installed into the retained
native build and has not been submitted upstream. The patch contains GPL-derived
code; see ../../licenses/GPL-2.0.txt. The manifest records both original and
candidate file hashes and the patch hash.

The current routine mixes a superconducting thermal factor into its normal
reference. Its saturated branches also replace smooth occupations with steps,
losing the half occupation at the energy/shift boundary. In simple terms, the
subtraction compares inconsistent references and prematurely rounds away a
physically relevant transition. The candidate restores the normal factor and
uses shifted tanh identities only where the original quotient becomes unstable.
This retains the existing regular branch and avoids a tuned saturation cutoff.

The current accumulation additionally evaluates xi/E at xi=gap=0. Its finite-T
product has a continuous zero limit even though the literal quotient is 0/0.
The exact-zero product branch implements that limit without perturbing nearby
nonzero states. The RHS thermal saturation branch receives the same occupation
identity correction. No interaction kernel or response normalization changes.

This is a bounded candidate, not a claim that every solver boundary is repaired.
In particular, the RHS later divides delta by E and its zero-energy boundary
still needs a separate regression and domain-aware fix. Zero-temperature limits,
the positive high-energy-cutoff branch, self-consistent solutions, and material
accuracy are not qualified by these fixtures.

Existing evidence: complete-current 81-case thermal controls, nine zero-energy
and two-sided normal-state controls in serial/OpenMP, an independent high-
precision scalar oracle, and complete-RHS synthetic-interaction residual tests
using real BLAS. These test numerical expressions, not experimental agreement.
See ../THERMAL_BOUNDARY_RESULT.md, ../ZERO_ENERGY_FINDING.md, and
../RHS_THERMAL_FINDING.md for results and limits.

Recreate the package in a new ignored directory:

```sh
python3 research/package_thermal_patch.py research/raw/thermal-patch-new
```

The generator rejects either upstream file if its full hash changes. It uses
the same transformations as the compiled harnesses; it does not include their
diagnostic output-precision changes. An isolated `patch --dry-run -p1`, actual
application, and both applied-file hash comparisons passed for this package.
Review the diff before applying to any scientific workflow.
