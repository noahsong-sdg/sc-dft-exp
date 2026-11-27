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

## Source-bound enrichment prepared

`prepare_occupation_enrichment.py` now binds the original basis/geometry hashes,
strict reduced readback, exact full-evaluated candidate, temperature and context.
It creates a fresh directory only after these gates and numerical checks pass.
The file fixture uses an independent exponential occupation and exact A0=2I;
it verifies the appended image and rejects changed persisted inputs before output.

For the failed material candidate, the omitted occupation has norm 8.43608e-6
and relative norm 0.00197856. The added direction has norm 1 and old-basis overlap
6.42e-19. Preparation takes 13.78 s / 176701440-byte peak RSS, measured separately
from native guarded attempts. See enrichment_preparation_result.json. This does
not freshly qualify every inherited operator image or establish a new gap.

The unchanged reduced executable is copied into a fresh directory, with the new
32-column basis and the same 0.15 meV conventional-mode seed. The prospective
enriched_reduced_manifest.json pins all runtime inputs; the launcher rechecks
their hashes immediately before execution after 120 quiet normal seconds.
Keep the existing 120 s / 3 GiB guard and one heavy owner. A qualifying candidate
would justify considering one fresh full check at unchanged acceptance targets.

## Rank33 full native result

The occupation-plus-critical-mode candidate also fails the unchanged stationary
targets. Terminal guard PASS599.926s,951713792-byte individual peak RSS. Exact
input gap preserved. Infinity residual4.58440815e-8Ry and RMS residual/gap
0.00212817009 exceed1e-10Ry/1e-5. Tile sum difference4.9083e-15 and analytic
Jacobian/finite-difference difference3.4433e-9 pass their native controls.
See verify_critical_gap_result.json with terminal receipt and prospective
manifest hash. This is not a converged gap, despite exact representation of the
measured critical mode and a tiny reduced coefficient residual.

The new full image permits a second exact occupation-defect enrichment without
another kernel pass. Preparation rank33->34 took13.20s /178307072-byte RSS;
relative occupation defect0.000636889, new direction norm1 and old-basis overlap
4.08e-19. This qualifies the measured enrichment algebra, not the inherited
operator globally. A cheap reduced pilot is prepared, not yet launched.

## Rank34 full native result: contraction, not acceptance

Terminal guard PASS524.858s/934281216-byte individual peak RSS. Strict readback
and exact seed preservation pass. Infinity residual5.00949e-9Ry and RMS ratio
0.000112069 still fail1e-10Ry/1e-5. Relative to rank33, the RMS ratio contracts
about19-fold and infinity norm about9-fold. Tile error3.9439e-15 and Jacobian
finite-difference error3.4150e-9 pass the native controls. See
verify_second_occupation_gap_result.json with receipt/manifest binding.

This supports another cheap measured enrichment rather than changing tolerances.
Rank34->35 preparation took13.22s/180436992-byte peak RSS; relative occupation
defect0.000132615, new norm1, old-basis overlap6.96e-19. A rank35 reduced pilot
is prepared in third_occupation_reduced_manifest.json, not launched. It must
wait behind the material response controls. A further full pass still needs a
source-bound candidate and explicit measured-cost decision. No conditioned gap
or physical response has been established.

## Rank37: unchanged maximum target still fails narrowly

Full native check513.389230s/926105600B passes its process guard, tile-sum
error3.963e-15 and analytic-Jacobian difference3.405e-9. Exact input preservation
passes. Rinf1.099906719e-10Ry remains above1e-10; RMSratio2.025058e-6 passes1e-5.
The candidate is therefore unaccepted. No threshold is rounded or relaxed.
`verify_fifth_occupation_gap_result.json` binds the original prospective manifest.
Rank36->37 mean gaps change about -0.019%; the same-cache anisotropic diagnostic
changes about -0.038%, while derivative/integration/physical gates remain open.

The measured next occupation defect has relative norm2.053155e-6. Preparing
rank38 takes9.75s/194854912B, without another kernel pass. A roughly one-second
reduced follow-up is staged in sixth_occupation_reduced_manifest.json. It is not
queued behind the active897point band replay; inspect owners before launch.
A stationary residual pass, if obtained later, still will not bound conditioned
gap error or establish physical response accuracy.


## Rank38 meets unchanged stationary-residual targets

Full native check680.801683s/937721856B passes its guard. All prospective
external/local identities remain unchanged after the run; the exact input seed
is preserved. Maximum residual3.171891839e-11Ry≤1e-10 and RMSratio
7.546354472e-7≤1e-5 both pass. Tile error4.7825e-15 and Jacobian difference
3.4183e-9 pass their native controls. No threshold changed between candidates.

This certifies stationary residual accuracy for one fixed retained Q0problem,
not conditioned gap error, uniqueness, discretization or physical current.
The rank38 reduced solve took1.115s; full independent validation680.802s and
historical/retained basis setup must be included in any practical solve cost.
Do not report a subsecond complete solve or infer a speedup against an absent
equivalently qualified full-solver baseline. No additional enrichment is needed
merely to drive this residual below an already satisfied arbitrary threshold.

Owning result: verify_sixth_occupation_gap_result.json; frozen prospective
protocol: verify_sixth_occupation_gap_manifest.json. Run verify_gap_candidate.py
with those inputs to reproduce the strict residual readback.
