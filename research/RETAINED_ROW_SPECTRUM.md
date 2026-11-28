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

## Accepted material diagnostic001

Terminal guard PASS6.431358041707426s, individual descendant peak281575424B
(268.531MiB); sampled group81510400B, which misses the short native peak.
All1839 staged pins, exact manifest/receipt/watcher/outputs rechecked; accepted
closure1856pins. Numerical readback ran inside the charged owner.
[Result](defect_row_spectrum001_result.json). Public source5444ebf CI46146669175PASS.

On these64 complete left rows, largest1/3/13 directions account for
0.9995342161797829/0.9999841999517176/0.999999999999998 of squared Frobenius
energy. Three exported eigenvalues in ascending order are
0.0017376757891472221,0.017773109133059788,43.33866759332359.
Their squared projections into the current Q span are
1.3146600193764528e-6,2.4241107806445085e-7,1.3043278544934174e-6.
Thus the dominant sampled input direction is almost entirely outside that span.
This establishes a sample input-space mismatch, not a complete causal account
or evidence that three new basis columns will qualify the full inverse.

All64 reconstructed row norms agree with accepted defect output; maximum
304.37575259990825. Independent A-only maximum6.971243858010709.
Q orthogonality error3.5971e-14; V orthogonality1.9632e-11;
Gram eigenpair/independent fsum errors1.9984e-14/1.2101e-14;
sensitivity action6.5765e-13; sampled Q overlap5.1326e-16.
No directions adopted, no new kernel, no full-space/outward/physical certificate.

Charged campaign21989.224320587087s/25200;3210.7756794129127s remain.
All owners terminal. Next: design a bounded enrichment test using orthogonalized
sample sensitivity inputs, with independent rows not used in selecting them.
Computing full A actions on new columns requires a separately admitted pass;
full error control still needs both output orientations and unmeasured rows.
A training-row improvement alone cannot establish that repair is useful.
