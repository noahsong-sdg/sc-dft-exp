# Nonlinear equilibrium-gap reuse gate

## Question and traced path

Can the retained matrix-free operator produce a new, provenance-qualified Q=0
finite-temperature gap on this Mac, rather than only replay an archived state?
The dense-memory bound alone cannot answer that question.

The retained native code already has `tiled_operator.build_tile` and
`gapeq_rhs_tiled`, in addition to the linear Tc block operator. At fixed T,
geometry and microscopic inputs, build_tile's kernel is independent of delta.
The nonlinear dependence enters the occupation vector chi. Consequently the
same bounded tile can act on a nonlinear vector and several derivative vectors.
This is an execution-path property, not a measured acceleration or novelty claim.

The prior complete native actions took approximately500–765s at below1GiB.
Those are historical linear-action anchors, not a nonlinear-solve forecast.
Repeatedly rebuilding the kernel for many nonlinear iterations could still be
expensive. Building the full dense matrix remains outside laptop memory.

## Staged selected-row pilot

`nonlinear_map_probe.f90` initializes the real Nb state, uses the saved-Coulomb
reader with coefficient hashes, and requires exact initialized-state agreement
with a retained8.05K preparation. That preparation used zero-T initialization
before setting physical beta; initialization temperature is not physical T.
It then reads the full saved Z with its temperature/shape/Fermi checks. The
manifest binds the source input (nx100,nmf10,ne50) because the Z metadata alone
does not encode all input parameters. No saved Z is accepted merely by filename.

The imposed0.2meV energy-dependent seed is explicitly not a solution. Exact
xi=0 states have delta=0 to exercise the finite-T product limit. The pilot checks
occupation factors against a separate exponential form, constructs three
8-column tiles spanning the left state range, checks sampled kernel entries
against the uncached native_pair routine, and compares selected complete left
row sums with BLAS. It records selected residuals without calling them converged.
It does not compute a complete right-side image or full residual norm.

The build uses immutable retained dependency objects and native libraries;
new sources, objects and executable stay in the ignored isolated build directory.
`nonlinear_map_build_manifest.json` records their current hashes. This is a
retained-build experiment; a fresh public reconstruction of these custom native
dependencies is not yet packaged. The portable output reader/regressions do not
claim to reproduce the full microscopic experiment independently.

The launch owner and result status are in the restart ledger. The pilot retains
the120s/3GiB guard and normal-pressure prerequisite. A failed compatibility gate
must be diagnosed before any new solve; do not weaken saved-state checks merely
to obtain a result.

## Conditional next experiment

Only after this pilot passes, qualify the complete nonlinear map and its
Jacobian, with a new explicit measured-cost decision before longer execution.
For finite positive T and Q=0, xic<0, the owning map is

    E = sqrt(xi^2 + delta^2)
    chi = dk/2 * delta/E * tanh(beta*E/2)
    R(delta) = -K*chi/(1+Z) - delta.

Its pointwise derivative for E>0 is

    dchi/ddelta = dk/2 * [xi^2/E^3 * tanh(beta*E/2)
                         + beta/2 * delta^2/E^2 * sech^2(beta*E/2)].

At xi=delta=0, chi=0 and dchi/ddelta=dk*beta/4. These limits must be tested
against independent high-precision values and complete owning-routine controls.
The full Jacobian image is -K*(dchi/ddelta*v)/(1+Z)-v. This gives a possible
batched Newton/subspace route with independent full residual acceptance.
No projected residual alone can certify a solved gap. Preserve the nonzero
superconducting branch; convergence to delta=0 below Tc is not the desired state.

A complete native map, temperature/discretization compatibility, nonlinear
convergence, independent residual, branch checks, response extraction and physical
interpretation remain separate gates. No new gap or end-to-end feasibility
verdict follows from this plan.

The scalar occupation/Jacobian formulas pass125 cases against80-digit Decimal
central differences of the direct exponential occupation, including signed gaps,
exactzero energy and a range of temperatures/energies. Run
`python3 research/nonlinear_weight_probe.py`; summary is in
nonlinear_weight_reference_summary.json. In particular, setting the derivative
to zero at xi=delta=0 would be wrong even though chi itself iszero. This is
scalar qualification only; it does not verify a full native Jacobian action.

Attempt001 was stopped by the unchanged host-pressure guard after68.175s, peak
777437184 bytes; no accepted map result. Buffered console output obscured the
stopping stage. One fresh retry uses120s quiet-normal prerequisite and unbuffered
logging, with the same120s runtime/3GiB cap. Inspect the ledger's live owner.

## Exact compatibility gate rejected the retry

Attempt002 reached initialized-state verification and exited after48.295s, peak
912670720 bytes. Counts66867/67940 match and the xi0 node comparison passes,
but dx0 differs. The saved Z was not accepted and no selected map was produced.
The earlier native portability diagnosis records a13-ULP difference in one
transformed Gaussian weight between platforms; that is a lead, not a freshly
verified description of every difference in this run. No tolerance is relaxed.

Next audit: serialize the newly generated grid for comparison, then consider a
separate explicit saved-quadrature-input experiment. Reusing a declared numerical
grid alongside compatible saved renormalization data is a different experiment
from independently regenerating that grid. It must retain the old failed exact
gate, identify the grid input by hash, and require exact agreement of all newly
prepared state arrays before accepting Z. The old common-seed causal diagnostic
is expressly test-only and must not be linked into this calculation. A newly
computed Mac Z is the alternative if compatible input reuse cannot be established.

## Fresh audit and explicit numerical-compatibility mode

The fresh grid audit finds exactly one changed weight, dx0[52],13ULP; all nodes
match. The saved-quadrature proposal is superseded by an existing, independently
tested cross-platform state checker. Four regression tests passed, including
stale/truncated state, remapping, NaN/Inf, zero and over-bound rejection.
The driver now supports an explicit compile-time mode; the default stays strict.
It changes checker selection only, preserving native quadrature generation and
the saved-Z checker. This avoids an unnecessary new input-injection path.
The prior exact-mode failure remains valid. A selected map passing this mode
would qualify only its declared numerical compatibility and selected rows.
See nonlinear_map_cross_platform_manifest.json for prospective hashes/bounds.

Verification at this checkpoint:56 offline unittest cases PASS(2.246s);
compileall PASS; committed moment_refinement replay PASS; git diff --check PASS.
Original strict-mode build manifest hashes refer to source at581f71f; the new
explicit-mode manifest pins current source separately. Native outcome pending.

## Native selected-map result

Explicit compatibility mode PASS:49.182736s,935133184-byte peak RSS. Fresh
initialization and saved Z checks pass. All three8-row tiles have zero observed
BLAS/explicit-sum and sampled uncached-coefficient differences. The1425 exact
zero-energy product cases are finite; exponential reference error2.65e-23.
Result and terminal receipt are pinned in nonlinear_map_cross_platform_result.json
and the mode manifest. This supports a full matrix-free evaluation experiment;
it is not full residual, gap convergence, independent operator acceptance, or
physical response validation. Prospective1200s single fullpass budget is recorded
in the ledger from measured selected-tile costs, within the4h pilot allowance.


The retained rank38problem now passes its specified full stationary residuals.
[PORTABLE_GAP_GATE.md](PORTABLE_GAP_GATE.md) records the inspected dependency
chain and exact public-reproduction boundary. Do not reinterpret residual
acceptance as fresh input/basis generation or physical-response validation.
