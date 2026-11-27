# Current grid mismatch and next scientific action

The strict retained-candidate check remains failed. A new source-built diagnostic
identifies one transformed weight difference, not a broad failure of the energy
grid: dx0[52] is `0x1.d0271d8bffaf8p-22`, versus retained
`0x1.d0271d8bffb05p-22`. The absolute difference is 6.88214269644119e-22,
13 ULPs. All 100 transformed energy nodes and the other 99 weights match bitwise.
The diagnostic takes 0.592295 seconds including its small compile/link, with
96,747,520 bytes individual peak RSS. This is not full initialization cost.

The execution path is upstream `energy_grid -> weightspoints_gl`: cosine seeds,
Legendre/Newton iteration, raw weights, then the exponential grid transform.
All SCTK Fortran source files compared byte-equal between the public source-built
tree and retained native source tree. A prior saved platform investigation reports
the same entry and exact values; this is supporting historical evidence, not a
new controlled intervention proving the current platform cosine implementation.
No comparator values were injected into the current diagnostic or production code.

An independent Decimal calculation uses 75-digit arithmetic, Taylor cosine seeds,
Legendre recurrence and Newton steps below 1e-65. All polynomial moments through
degree 199 differ from their analytic integrals by at most 1.036e-73. This is a
numerical self-consistency check, not interval arithmetic. Compared with its
binary64-rounded results, the public upstream raw nodes differ by at most one ULP;
raw weights differ by up to 1.060e-14 absolute / 1.443e-11 relative. The native
binary64 quadrature's worst absolute polynomial moment error is 2.404e-14.
These bounds concern scalar quadrature tests, not the superconducting solution
or its response uncertainty. The independent rule is not installed as a new
production grid.

The exact check correctly prevents silently combining different numerical
contexts. Relaxing it would not regenerate the corresponding Z or establish a
conditioned solution. The next route is to export the genuine initialized Mac
state, generate compatible Z and a basis from that state, and solve/check its
gap independently. Keep the original retained problem and its failed exact
reproduction separate. This costs more than accepting a tolerance but directly
addresses the public, internally consistent laptop calculation that is required.

Evidence: `portable_grid_probe_manifest.json`, `portable_grid_probe_result.json`,
`gauss_decimal_reference.py`, and `gauss_decimal_reference_result.json`. The probe
result includes all 600 binary64 values as hexadecimal strings for readback.
Postrun hashes, public/consumed manifest identity, receipt command/cwd/deadline
and executable identity were checked. Native source build and execution passed;
no gap state or physical response was accepted. All 140 offline tests passed in
13.313 seconds; maintained-source compileall, moment replay and diff checks passed.
