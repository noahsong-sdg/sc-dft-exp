# Full native validation of an explicit nonlinear candidate

The existing map probe always overwrote delta with its arbitrary diagnostic
seed. That path cannot validate a reduced candidate. `gap_seed_io.f90` adds an
explicit input path, selected only by the `verify-gap-seed.x` target. Default
selected-row and full arbitrary-seed targets retain their behavior.

The ordering is deliberate: fresh native initialization, declared numerical
compatibility and unchanged saved-Z checks complete first. Only then load the
new delta. Gap reuse does not substitute a grid or alter the initialization gate.
The seed metadata binds dimensions, grid parameters, physical beta, exact source
point path and declared operator context. Binary size, finite values, exactzero
padding and positive conventional Fermi support are checked. The manifest and
launcher must additionally bind all files by hash before execution.

A nonzero conventional seed usually has no exact E=0 products. The diagnostic's
requirement to include zero products therefore applies only to its old arbitrary
seed, while the verified-seed path retains safe occupation evaluation and a real
Fermi-support check. It does not manufacture zeros in the loaded vector. The
original thermal boundary regressions remain applicable to the owning formula.

The compiled loader fixture proves exact binary preservation and rejects stale
schema, dimensions, temperature, source point, context, trailing metadata,
truncated/nonfinite payload, nonzero padding and zero/negative Fermi gaps.
The boundschecked native target builds; it has not validated a material seed.
Default selected and full targets also build after this integration change.

`verify_gap_candidate.py DIRECTORY MANIFEST` performs the terminal readback.
It binds runtime inputs to their prospective hashes, requires a passing receipt
with the declared executable and working directory, and runs the full-map
binary/summary, tile-sum and Jacobian checks. It then compares the persisted
input-vector prefix bitwise with the declared seed and computes both residual
targets. A numerically unsuccessful candidate is a valid reported result,
not an execution failure. Conditioning and physical-response flags remain false
even when both stationary-residual targets pass. The regression fixture covers
both numerical outcomes, a changed evaluated vector and failed/stale receipts.

## Prospective numerical gate

Require terminal guard PASS, strict full result readback and bitwise equality
of its persisted input delta with the declared seed. Full residuals must be
finite. For point-level stationary-residual certification, target infinity norm
at most1e-10Ry and RMS residual/gap ratio at most1e-5. Report actual residuals
when those targets fail; a low reduced residual never overrides them.

Those tests alone are not a bound on gap or response error. Near-transition
conditioning, changes under basis/solver refinement, integration and physical
response-functional uncertainties remain separate gates. Do not promote a
point-level residual check into a decision-grade response prediction.

The complete full pass also retains explicit tile-sum and analytic-Jacobian
finite-difference controls. Its retained microscopic coefficient hashes, source
point and saved Z must remain the ones declared in the experiment manifest.
Use a fresh run directory and the established1200s/3GiB guard only after the
current amplitude job terminates and a reduced candidate passes readback.

## Possible next improvement, not implemented here

For F=A0*f, U=A0*Q and a reduced root delta=U*c, the omitted occupation component
e=f(delta)-Q*c satisfies R=A0*e, up to the reduced residual and operator reuse
error. Computing this known direction's linear action during full validation
could check the identity and provide a new basis image for enrichment without
another kernel pass. It needs a separate tested output schema and native control;
this loader change does not implement or establish that method.

## First material candidate: full targets failed

The explicit-candidate run completed in 785.634 s with 904052736-byte peak RSS.
Terminal guard, initialized-state/Z checks, exact candidate preservation and
strict full-map readback pass. Tile-sum discrepancy is 4.38e-15 and analytic
Jacobian/finite-difference discrepancy is 3.39e-9, below its declared bound.

The full residual infinity norm is 8.95904547e-8 Ry, and RMS residual/gap is
0.00236268943. Both fail the prospective thresholds. The reduced coefficient
residual of 2.09e-17 therefore did not qualify a full-space gap. This is a
representation failure at the tested point, not a native execution failure or
evidence that all reduced methods fail. See verify_reduced_gap_result.json,
which includes the terminal receipt and prospective-manifest hash.

`occupation_enrichment.py` implements the algebraic next step, independently
tested on a nonsymmetric dense operator. With p=Q^T*f, form e=f-Q*p and
A0*e=F(delta)-U*p from the measured full image. Orthogonalize both vectors using
matching Q/U subtractions, normalize them together and append one column.
This reuses the validation rather than spending a kernel pass merely to obtain
the new image. Unresolved directions are rejected. No inherited-action
consistency or new material result follows from that identity; a subsequent
candidate still needs a fresh native check. File-bound material preparation
and the next reduced solve are not implemented at this checkpoint.
