# Finite-temperature saturation shortcut also affects the gap RHS

## Root cause and independent reproduction

The current pinned `sctk_gapeq_rhs.f90` has SHA256
`177d0e9738a4accf658aea108b5349a1d392035b3ec4e98c1c5fea82c98ccf73`
at revision `4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33`. Its finite-temperature
thermal block uses the same saturation test as the current routine. It switches
to an energy-ordering shortcut when the product of two tanh factors approaches
one. Both factors can saturate while their energy difference remains thermally
small. In plain terms, large absolute energies do not make their difference cold.

`rhs_thermal_probe.py` retrieves the hash-checked source, extracts the exact
finite-temperature block, compiles it with GNU Fortran, and evaluates controlled
inputs. At xi=0, gap=shift=2 and beta=20 or 100, released chi=0 while the shifted
occupation identity gives 0.5. Scaling both energies to .0002 and beta to 1e6
preserves that counterexample. These values are the dimensionless thermal factor
before multiplication by dk*gap/(2*E), not a full gap residual or material gap.

The zero-temperature branch is a separate intended limit and is not corrected
by this observation. The defect identified here is in the finite-temperature
branch. Near-equality fixtures on either side distinguish a finite thermal
window from a measure-zero equality convention. A regular nonsaturated control
agrees. Results are in rhs_thermal_results.json.

## Implication and scope

A downstream current-only correction cannot certify finite-Q results if the
upstream gap was computed with an inaccurate thermal factor. This expands the
necessary correctness trace within the same response workflow; it does not
justify unrelated solver refactoring. The natural candidate is stable shifted
occupation evaluation in the demonstrated saturation branch, consistent with the
current candidate, followed by full RHS tests and controlled convergence solves.

No production RHS patch has been adopted and no converged gap change measured.
The extracted-block harness intentionally omits interactions, MPI, residual
assembly and gap iteration. Their amplification/cancellation and scientific
significance remain open. Any eventual patch needs its own single-purpose review
and regression qualification; a scalar counterexample alone cannot establish a
new penetration-depth value or explain the released peak-route discrepancy.

## Complete RHS assembly fixture

`full_rhs_probe.py --blas /path/to/libblas.a` compiles the complete hash-checked
`gapeq_rhs`, with small state modules, actual BLAS DGEMV, and serial MPI/clock
stubs. The two grids have unequal counts (2 and 3), distinct interaction matrices,
weights and mass renormalizations. High-energy extrapolation is disabled (xic=-1).
The independent Python reference explicitly assembles each matrix-vector product
from direct thermal identities. The candidate changes only the demonstrated
finite-temperature saturation branch and leaves the regular and zero-temperature
branches untouched; guarded transformation tests cover that boundary.

Released maximum residual-component error is 0.34324189787377124 in this
dimensionless synthetic fixture. The candidate serial (-O0) and four-thread
OpenMP (-O3 -fopenmp) outputs match the direct reference at serialized double
precision, with bounds checks enabled. The run used the retained reference BLAS
library whose SHA256 is recorded in preparation_input_verification.json.
Exact five-component outputs are in full_rhs_results.json.

This proves that the scalar discrepancy survives weighting, interaction
application, mass renormalization and residual subtraction in a controlled full
routine. It does not test actual material interactions, distributed collectives,
xic>0, convergence, or change to a stable physical solution. Those remain separate
gates. No global accuracy or speed claim follows from this fixture.
