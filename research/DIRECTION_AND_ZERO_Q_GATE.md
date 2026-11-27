# Direction and zero-momentum preparation gate

The held-out current-geometry [111] run completed successfully: 72.553 s,
144293888-byte maximum descendant RSS, serial, unchanged 120-second/3-GiB guard.
The physical momentum magnitude matches the original [011] run:
0.00014213149536207326 in the retained native convention. Reciprocal primitive
coordinates differ; directions are stated in physical Cartesian coordinates.

At imposed gap 1.5 meV and 2/4/8 K, signed all-support second moments reproduce
the corresponding direct fine-grid constant-gap quadrature within 4.48e-16
absolute. All three original-path reconstruction controls are exactly zero.
See nb_velocity_moment_current_111_results.json for the output hash and receipt.

The [111] direct values are 0.90646%, 0.90626%, and 0.90605% lower than [011].
This is a measured discrepancy, not established physical anisotropy of cubic Nb.
Agreement of second moments with their own quadrature does not establish cubic
isotropy, fine-grid convergence, or experimental accuracy. Finite-difference
derivatives, integration and band preparation remain possible contributors.

## Separate the zero-Q quadrature

The owning calc_d_xi_q computes directional velocity and curvature contractions,
then overwrites band energies with et0+qCq. Subsequent DOS weights therefore
describe a finite-Q preparation. Linear-response moments should use unshifted
equilibrium bands, while retaining the directional contractions divided by the
appropriate powers of Q. This is a diagnostic extension, not a production fix.

`current_moment_geometry.py --unshifted-bands DESTINATION` now extracts the pinned
current derivative routine as well as compute_dosk and symm_dosk. It changes
only et=et0+qCq to et=et0 in that routine. The default compatibility mode retains
its original finite-Q behavior. Both modes remain fully shifted-grid probes
using retained QE dependencies, not full current-version SCTK builds.

Bounds-checked native compilation passed. The first runtime attempt was stopped
at 53.694 s by host pressure, exit -15, peak 100450304 bytes. It supplies no
accepted scientific result. Build/source/input hashes and the failed receipt
are in unshifted_moment_build_manifest.json. A fresh attempt is tracked in the
restart ledger; inspect its live owner before launching additional native work.
The default finite-Q build also passed in a fresh build directory after the
import change. Final checks: 38 offline unittests pass; moment_refinement.py
replays committed results; compileall reports no Python syntax errors; diff
whitespace check passes. No separate project typecheck is configured for these
Python/Fortran diagnostics.

Next compare unshifted [011] and [111] at matched physical Q, then energy-grid
and momentum-scale controls. Exact Q cancellation in this diagnostic is an
algebraic expectation, not a replacement for checking the native implementation.
