# Retained-row sensitivity diagnosis — prospective admission

The current chosen inverse worsens three independently checked complete row
norms relative to A-only, and those A-only rows also exceed one. The cause is
not yet established. Before another kernel pass, diagnose whether the existing
64 complete left defect rows share a small number of input directions and how
those directions overlap the current orthonormal Q basis.

This is a diagnostic of E=(A+UC)D on the saved 64-row sample, not a full-space
norm, inverse qualification, conditioning certificate or physical response.
Its squared singular spectrum measures sample Frobenius energy; concentration
alone does not establish a useful repair or an infinity-norm improvement.
No exported direction is adopted into a new inverse.

## Exact path and memory

Fresh standalone Fortran reads the accepted compact U,Q,C,state and the two
original 32-row kernel tiles; reconstructs all 64 complete rows; forms a 64x64
Gram matrix with BLAS; diagonalizes with LAPACK DSYEV; and exports at most three
resolved right sensitivity directions. U and C are freed before the eigensolve.
No N x N matrix, new microscopic kernel, installation or material sweep.
Estimated peak live numerical arrays about275MB; this is an allocation forecast,
not measured RSS. Three BLAS thread environment variables are fixed to one.

An independent Python reader streams the row matrix in1024-column chunks,
reproduces all64 accepted row norms and all64 A-only baselines, and checks six
Gram entries, all Gram eigenpairs, direction orthogonality and E*v actions.
It independently checks Q overlaps at first/middle/last basis columns and
requires the complete native Q Gram to equal identity to1e-8. Fractions use raw
eigenvalues, with small negative roundoff permitted only within1e-10 of the
largest. Only eigenvalues above that threshold can generate directions.
Existing accepted parent provenance, input/output hashes and guard receipts
are rechecked before staging; final input hashes are checked inside the owner.

The native regression recovers an exact two-mode spectrum (8,32), both in-basis
and out-of-basis directions. It rejects corrupted Gram data, trailing controls
and stale binary shapes. Owner regressions reject stale output, incorrect cwd,
changed input pins and missing terminal console. The initial owner fixture used
a macOS /var alias while cwd resolves /private/var; resolving the temporary test
root fixes that test mismatch while preserving the ownership boundary.

## Admission and stop conditions

One fresh90s analysis owner in raw/defect-row-spectrum-001, launched by the
existing guard after120continuous normal-pressure seconds, with3GiB group cap.
At admission21982.79296254538s charged of25200s;3217.20703745462s remain.
Worst-case90s leaves3127.20703745462s. Parent validation is a separately recorded
read-only workflow cost. Compilation, material math and independent numerical
readback are all inside the90s charge. Stop on pressure, deadline, changed
provenance, nonfinite output or any independent check failure. No automatic
retry, budget expansion or full second sweep of the failed inverse.

Brave, Docker and the separate study are untouched. A concentrated unexplained
sample spectrum would justify only a future prospective repair/held-out plan;
it is not evidence that the laptop response goal is achieved.

Source gate:321 offline regressions PASS49.854s, including native fixture builds;
295 Python sources compile; moment_refinement exit0; git diff --check PASS.
Parent replay/staging42.795815207995474s is a separate read-only workflow cost.
