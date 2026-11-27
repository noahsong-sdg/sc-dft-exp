# Matched-quadrature velocity-moment experiment

## Completed first material test

Attempt 002 PASS: 52.575 s, peak individual RSS 178372608 bytes, exit 0.
Session 32316 is terminal; no owned process remains. All three native control
errors (DOS, mean velocity, mean curvature) are exactly zero in serialized
binary64. `moment_analysis.py` accepts the complete result; see
nb_velocity_moment_results.json and velocity_moment_build_manifest.json.

At 2 K, the two mean-squared active-cell estimates are 0.00327520 and
0.00370208. The direct fine-grid result is 0.00814488517 in the same code
conventions. The all-support second-moment estimates agree with that reference
within 1.43e-16 absolute. Across 2/4/8 K, the maximum discrepancy is 8.27e-16.
The active-support second moments differ slightly from the all-support result;
that support effect is explicitly separate from the much larger closure effect.

There are 1164403 negative fine-grid weights; their absolute sum is 42.8657
out of total absolute mass 801.6764 (these sums are over energy-bin DOS weights,
not a dimensionless electron count). Therefore no positive-weight Jensen
argument is used. Direct signed-quadrature comparisons remain valid.

The existing cell closure retains approximately 40–45% of the direct response
in this imposed-gap test. This establishes a consequential approximation effect
on retained Nb bands, not a converged penetration depth or a prediction for a
physical sample. It requires grid refinement and broader gap/symmetry controls.

An additional control uses the full native-assigned preparation states, including
`store_d3k`'s special interpolation for cells with fewer than two active energy
bins. Its analytic slopes differ from the all-positive-bin K1 diagnostic by at
most 7.9e-9 absolute (nb_assigned_state_slope.json). K1 is therefore a very close
closure diagnostic here, not an exact reproduction of the full state-assignment
exception. Complete native currents at the same nonzero Q also agree with direct
occupations, but their j/Q differs from the analytic limit by temperature-dependent
finite-Q effects (nb_small_q_material_current_results.json). Do not confuse that
finite-Q comparison with exact equality to K1 or a physical convergence test.

## Scientific question

Does the existing coarse-cell velocity closure lose a consequential part of
linear response, and can retaining a second moment recover a direct fine-grid
reference at commodity-hardware cost?

This is a diagnostic of a particular approximation. It is not yet evidence
that the released method is inaccurate after its intended convergence procedure,
or a self-consistent superconducting response prediction.

## Traced path and controlled comparison

Native historical SCTK revision `47c06501da8ffd574c87469ddd6d5a2814171796`:
`calc_d_xi_q -> calc_dosk -> compute_dosk -> symm_dosk`.
`compute_dosk` interpolates DOS-weighted velocity and curvature, symmetrizes,
and divides by DOS. In the current's linear limit the velocity contribution is
quadratic. At fixed energy and gap the microscopic sum thus needs a second
velocity moment. Squaring a first moment is a closure approximation.

`velocity_moment_probe.f90` reads the same native inputs and uses the same
band finite differences, DOS quadrature, interpolation and directional symmetry
subgroup. It accumulates raw DOS, first velocity moment, second velocity moment
and curvature moment separately. First and curvature moments are checked against
a fresh call to the actual owning native `compute_dosk`, with immutable bands
restored and its derivative arrays deallocated before reinitialization. This is
an independent reconstruction control, not a replacement native initializer.

At imposed constant gap 1.5 meV and temperatures 2/4/8 K, it evaluates:

```
K1 = sum dx * [A * M1²/DOS + B * H]       (positive active DOS cells)
K2 = sum dx * [A * M2     + B * H]       (same active cells)
Kall = sum dx * [A * M2  + B * H]        (all signed cells)
Kfine = direct sum on native fine k grid at the SAME energy quadrature
```

All use the same volume/momentum normalization. A and B are the thermal
coefficients derived in LINEAR_RESPONSE_LIMIT.md; M1/M2/H include the corresponding
momentum contractions. K1 and K2 share the native positive-DOS support threshold
1e-12. Kall versus Kfine tests the interpolation partition and symmetry sum
without silently conflating support truncation with moment closure.

The diagnostic counts negative fine-grid weights and records their absolute
mass. Signed optimized-tetrahedron contributions invalidate a blanket
positive-weight variance inequality; measured differences must be interpreted
directly. Constant gap is essential to this particular fine-reference equality:
an anisotropic gap requires a controlled fine/coarse mapping. The directional
subgroup is retained; no full-group scalar averaging replaces a response tensor.

## Build and acceptance gates

Build in a fresh ignored directory using `velocity_moment_probe.mk`, passing
the retained native Makefile as NATIVE_MAKEFILE and the absolute diagnostic
source as MOMENT_SOURCE. Target velocity-moment-probe.x. Native libraries are
not rebuilt or patched. The source is derived in part from GPL SCTK and carries
its own GPL notice; the repository license explicitly preserves that exception.

Run serially with the established 120-second/3-GiB guard and normal-pressure
gate. The diagnostic rejects nonserial native process configuration. First
attempt nb-moments-001 was pressure-interrupted after 51.177 s, peak 110739456
bytes; it produced no result. No numerical or laptop-capacity conclusion follows.
Fresh attempt 002 includes the explicit serial guard and waits for 60 seconds
of normal pressure before launch. See the latest research ledger for its live
handle; do not start a duplicate based on this document.

`moment_analysis.py` requires the complete versioned output, finite values,
native control absolute errors at most 1e-12, and all-second-moment conservation
within 1e-12 + 1e-9*abs(reference). Schema/control/conservation rejection tests
pass. The complete offline suite passes 38 tests. Build succeeded with runtime
bounds checks; only the pre-existing duplicate-BLAS linker warning was observed.
The staged build was subsequently run successfully as reported above.

Even a successful matched-quadrature result must be followed by energy/momentum
refinement and gap/normalization qualification before inferring physical
improvement. The fine-grid reference here shares the band's finite-difference
and energy-integration approximations; it is not an independent DFT calculation.
