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

## Unshifted runs completed

Attempt 003 [011] passed in 63.891 s / 181452800-byte peak, and unshifted [111]
attempt 001 passed in 60.889 s / 166477824-byte peak. Both pass all native
controls and signed moment conservation. Their result JSONs contain hashes and
resource receipts. The [011] change from finite-Q preparation is only
-1.72e-7 relative; the unshifted direction discrepancy remains approximately
-0.90646%/-0.90626%/-0.90605% at 2/4/8 K. The tested band shift does not explain it.

An independent analytic BCC-periodic band control, derivative_symmetry_probe.py,
uses exact derivatives and primitive-coordinate finite differences. Exact
velocity-squared quadrature is cubic isotropic within 2e-14; the second-order
stencil introduces direction differences, reduced by fourth-order differences
on the tested grids. This is a counterexample to assuming stencil isotropy,
not a niobium model or proof of the native discrepancy's cause. The Gaussian
weight is only an invariant analytic test weight, not superconducting response.

The generator now has a diagnostic --fourth-order-velocity option. It changes
only the first derivative to the centered four-point stencil, including private
OpenMP indices and periodic wrapping; curvature stays unchanged. Native build
with bounds checking passes. A paired [011]/[111] run is owned in the restart
ledger. Runtime and accuracy conclusions await those results.

First fourth-order [011] runtime passed: 64.738 s, peak 145735680 bytes. Native
reconstruction and signed moment conservation pass. Direct response increases
by 8.978% at all three temperatures relative to the second-order unshifted run;
see nb_velocity_moment_fourth_order_011_results.json. This is derivative-order
sensitivity, not an error bar or proof of improved physical accuracy. Curvature
was unchanged. The paired [111] comparison is still pending. Neither stencil is
accepted as a converged material prediction.

## Additional small-Q symmetry gate

[The complete symmetry routine](SYMMETRY_SCALE_FINDING.md) fails a nonzero-Q
scale-invariance control below its fixed absolute tolerance. A relative-residual
candidate passes both grid shifts and preserves the distinct exactly-zero
subgroup. This does not explain the direction discrepancy at the tested larger Q,
but forbids treating arbitrary momentum reduction as a safe convergence strategy.

## Paired fourth-order control completed

Fresh [111] attempt002 passed in75.927s, peak142311424 bytes, with unchanged
120s/3GiB guard. All original-path reconstruction errors are exactlyzero; signed
second moments preserve direct quadrature. See
nb_velocity_moment_fourth_order_111_results.json. Relative to the second-order
[111] result, direct response rises8.8304–8.8306%. Relative to fourth-order[011],
[111] is1.0407/1.0405/1.0402% lower at2/4/8K. Thus the direction discrepancy
does not improve with this stencil change, despite the independent smooth-band
control's improvement. Neither derivative order is qualified as a converged
material response; fine-grid, band-crossing and quadrature effects remain open.

A bounded nx100-to200 pilot now isolates energy discretization while retaining
the unshifted second-order executable and response8cube/fine32cube grids. Its
live owner and stop conditions are in the latest restart ledger.

## Energy-grid doubling completed

The nx200 unshifted second-order [011] pilot passed in77.020s at274808832-byte
peak RSS. All native reconstruction errors arezero and all-support second
moments conserve direct quadrature. See nb_velocity_moment_energy200_results.json.
Relative direct changes fromnx100 are+0.013595%,+0.006945%,+0.003706% at2/4/8K.
Energy discretization has a much smaller observed sensitivity than derivative
order in these specific fixed-band, imposed-gap controls. Two resolutions do
not certify convergence, and these are not an error budget for the different
archived finite-Q real-gap state. The native owner46661 is terminal SUCCESS.
