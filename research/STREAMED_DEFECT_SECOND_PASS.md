# Streamed second-pass defect diagnostic

The accepted full P and one saved-direction identity do not bound the unmeasured
complement. At the fixed base state, the chosen B=I+U W Q^T D has
I-B(I-AD)=(A+UC)D with C=W(P-Q^T). A norm calculation must include both native
cross orientations and both same-side UC blocks. Omitting a same-side block
understates the row sum, even though A itself has only cross blocks.

The separate compact_defect_native_pass.f90 uses the frozen strict compact reader,
complete-P checkpoint reader, core contractions and original native32-row builder.
It validates original native fields and normalized D, constructs C from complete P,
releases P/Q/W, then accumulates left rows/cross-right columns and same-right
columns with explicit separate coverage counters. Full and selected stops must be
native tile boundaries except actual final rows. Full fixture stops65/67 exercise
one- and three-row final tiles. A complete marker requires both side counts;
partial output is explicitly NOT a full-space norm. Coefficients, row sums, six
selected kernel rows, progress and metadata are saved for independent readback.

The new reader streams C in1024-column chunks, obtains six U rows from streamed
columns and independently computes selected row sums with math.fsum and saved
original kernels. It separately checks C=W(P-Q^T) at six columns for every rank
component. All produced C/rows/kernels are finite and correctly shaped; unvisited
left rows must be zero. Max row sum must equal metadata. Diagnostic tolerances
use1e-28+1e-10sumabs scales and are not outward bounds. No norm/radius or physical
response certificate follows, even if a diagnostic maximum is below one.

The compiled fixture independently builds dense B and J and compares every132
row sums for full and selected coverage. It checks every396C entries against a
Fraction difference oracle, both saved kernel orientations and both same-side
contributions. The exact general-U/W I-BJ oracle remains in the frozen core suite.
Wrong coverage/context, incomplete persisted P and finite C corruption fail.
Native fixture+reader2PASS4.735s; build-owner2PASS0.024s; material-owner2PASS0.008s.

## Source build001 admission

New compact_defect_build.py/make variant preserves pinned P/selected producers.
Fresh source plan/compiler stdout must agree exactly, expected19compiles and two
links, explicit SDK-first BLAS, pinned archives and902bitwise cache checks. Stage
has577pins. [Manifest](compact_defect_build001_manifest.json).60s guard cap,
120normal-pressure seconds,3GiB caps, one owner; no native kernels in this build.
Charge before build21949.621570962332s/25200 leaves3250.378429037668s;
worst60s leaves3190.378429037668s. No budget expansion or full second-pass run.

## Selected material gate, not yet admitted

compact_defect_material.py will bind the accepted complete-P result/provenance,
reuse the separately accepted51-component saved-image action by exact unchanged
bindings and serialized control checks, and require a fresh19-compile defect build.
It does not recompute that old saved-action sum on every staging/readback; unchanged
published artifact/source/input hashes preserve the existing evidence. It merges
closures with conflicts rejected, stages fresh exact native inputs/control and
admits only64left/64same-right columns. Native left rows1:64 are complete row sums;
right rows contain only selected left/right-column contributions. All remain
ordinary finite diagnostics. Six sample row sums and306coefficient controls are
independently checked; exact consumed manifest, terminal receipt/watcher, original
copies, fingerprint, partial marker and four progress records required.

This selected gate can avoid an expensive full sweep if independently checked
stored-operator rows already substantially exceed one. It cannot qualify full
contraction when rows pass; unseen rows/columns still matter. A row above one is
evidence against this particular unweighted infinity-norm route, not failure of
the material or every possible inverse/metric. Numerical outward certification
and nonlinear radius/observable error transport remain separate requirements.
The material90s admission requires the actual accepted source build first; it is
not launched by this source work. A full second sweep needs a separate measured
scientific-value decision. Brave and unrelated study stay untouched.
Final gate:318testsPASS49.875s;291Python compilationsPASS; actual compiled
Fortran native fixtures/dense controls and persisted-state regressionsPASS;
moment_refinement.py exit0; diffcheckPASS. No separately configured typecheck.
New non-test code448lines across driver, make variant, source-build owner,
material owner and independent readback; all earlier pinned sources unchanged.
Prior public185d785 CI46143964798PASS. No material result claimed.

Source build001 now terminalPASS3.7740026665851474s, maxindividual134643712B
(~128.41MiB). Independent acceptance checks all577pins, consumed manifest/receipt/
terminal watcher,19fresh compiles,37output hashes, explicit SDK and902cache
controls. [Build result](compact_defect_build001_result.json). Source8e19886
CI46144804164PASS. Charged total21953.395573628917s/25200 leaves
3246.604426371083s; no budget expansion. Actual material qualifier still requires
its own prospective manifest and publication before launch.

## Selected material001 admitted

Actual staging revalidated complete P, unchanged saved-action bindings, accepted
new build and merged1824pins. [Manifest](compact_defect_material001_manifest.json).
Only64left/64same-right columns;90s cap,120continuous normal-pressure seconds,
3GiB caps, one owner. Charge21953.395573628917s/25200 leaves3246.604426371083s;
worst90s leaves3156.604426371083s. No budget expansion/full second pass admitted.
This gate produces complete first64left row sums and partial right sums, with
six independent samples and306coefficient controls. Native resource/coverage
receipt plus independent arithmetic required. Above-one rows are diagnostic
evidence against this stored unweighted-contraction route, not an outward proof
or a statement about superconductivity. A passing selection leaves full rows
unqualified. On failure the guard terminates its own group; no automatic retry.
Brave/otherstudy untouched. All owners terminal before prospective publication.
