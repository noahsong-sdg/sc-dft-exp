# Prospective augmented-inverse gate

Registered before measuring an augmented inverse. Same8.05K base candidate,
D/operator/Z/geometry and original51-column Q/U; append the three accepted
orthogonalized D*v trial inputs and their complete A actions only after full
joint-action acceptance. Original Q/U/P and candidate remain immutable.

Let Q+= [Q,trial], U+= [U,A*trial], P+ stack the accepted old P with extra P.
Choose M+=I-Q+^T*D*U+, W+ by solving M+*W+=I, and
B+=I+U+*W+*Q+^T*D. For arbitrary fixed Q+/U+/W+, not just an exact small inverse,

    C+=W+*(P+-Q+^T)
    I-B+*(I-A*D) = (A+U+*C+)*D.

No dense n*n allocation is needed. Numerical acceptance must check all small
matrix entries independently, both M*W-I and W*M-I, finite solved spectrum and
chosen W, exact parent bindings, and independent selected C coefficients/row
sums with cancellation-aware bounds. A small-matrix singular ratio is not the
full Jacobian condition. A successful small solve is not a certified inverse.

## Fixed rows and decision

Training left1/32/64. Held-out left65/33434/66867 and right1/33970/67940
(global right offsets66867). These were fixed in SENSITIVITY_ENRICHMENT.md before
new A actions or any augmented inverse were measured. Full joint-action pass
retains complete original K1 rows and K2 rows at those indices.

Compute complete ordinary-binary64 row sums of I-BJ for both old B and new B+,
using the same saved full kernel rows and context. Reproduce old training-row
sums against the accepted prior diagnostic. Report all nine results, including
failures, and distinguish training from held-out. Do not tune columns, solve
thresholds, row identities or metrics to these held-out results.

If any held-out row reaches/exceeds one, reject this candidate's unweighted
infinity-contraction route and do not spend a full second sweep on it. A training
failure likewise disqualifies that route. If every tested row is below one,
that only clears this selected rejection gate: a separately admitted full-space
sweep, outward numerical bounds and radius/error-transport argument are still
required. Neither a relative improvement nor sampled agreement suffices.

No adoption of a corrected gap, uncertainty bound, new physical response or
claim that this scheme is generally useful. All physical normalization, grid,
other-temperature, acquisition and independent-reference gates remain open.
This protocol admits no new compute or expansion on its own.

## Diagnostic001 implementation and prospective admission

Fresh standalone enriched_inverse_rows.f90 appends accepted trial inputs/actions,
forms54x54 M with BLAS, solves M*W=I with DGESV and checks both inverse products.
DGESVD supplies a small-matrix diagnostic, not full-space conditioning. It stacks
old/new P, forms C and computes all nine old/new complete row vectors from saved
K1/K2 rows. It retains the chosen W and C as diagnostic outputs; no candidate,
basis or previous inverse is overwritten. Counts, finite shapes, positive Z
normalization, fresh files and versioned controls are enforced.

Independent enriched_inverse_readback.py streams old/new Q columns, checks every
M entry by fsum against full U/D, checks M*W and W*M, singular ordering/Frobenius
identity and Q Gram. It checks all rank components of C at six fixed columns,
then every element and full absolute row sum of all nine baseline/new defect
rows using chunked C. Original three training norms must match accepted data.
The native fixture separately forms full B and J and multiplies I-BJ; it does
not reuse the streamed identity as its expected oracle. It compares native M/W
and complete rows. Altered M/W/C/rows/norms, trailing controls and stale shapes
fail; owner fixtures reject wrong cwd/stale outputs/control/console/changed pins.
A fixture-caught array/list comparison mismatch in singular ordering was fixed
before any material run; valid ordering and corruption tests now pass.

Owner enriched_inverse_run.py replays the accepted full-action parent checks,
requires old P/C/native-state lineage and unchanged old/new context, fresh-builds
the standalone program against pinned compiler/Accelerate SDK, runs native and
independent reader, then checks final pins and manifest. Three thread variables
are one. No historical object file or new kernel pass.

Admit only diagnostic001 in raw/enriched-inverse-001:1958pins,240s total including
compilation/math/numeric readback,120continuous normal-pressure seconds,3GiB cap.
Charged22544.771201837193s/25200 leaves2655.228798162807s; worst240 leaves
2415.228798162807s. Parent replay/staging3.2256356249563396s separate workflow cost.
Prior exhaustive51-column inverse diagnostic44.32s supports investigating this
54-column version with more row checks; new actual runtime remains unmeasured.
Forecast native live-array peak about300MB; no Coulomb store is loaded here.
This is an allocation estimate, not measured RSS or a same-workload speedup.
Stop on guard/input/numerical check failure; no automatic retry, inverse adoption,
new sweep or budget expansion. A scientifically negative row-gate result is
still a successful diagnostic execution and must be published as a rejection.
Brave and the separate study remain untouched.

Final source gate331testsPASS53.854s including native fixture builds;309Python
sources compilePASS; moment_refinement exit0; diffcheckPASS. No separate
configured typecheck. Full-action result6a5ad60 CI46150039062PASS.
