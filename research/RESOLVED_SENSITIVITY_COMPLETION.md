# Complete the original resolved training span

The54-column candidate failed its fixed complete-row gate. It is not adopted and
will not receive a full defect sweep. Saved E*v controls show that it annihilates
its three selected sensitivity directions; large remaining row sums therefore
justify assessing omitted training directions before spending more kernels.

The original64-row training spectrum, before the failed candidate was measured,
had9eigenvalues above1e-10 times its largest. The initial export was capped at3
for a bounded pilot. Complete that original fixed resolution rule, rather than
choosing a cutoff or directions from failed held-out residuals. This preparation
reads only the original training spectrum/row matrix and the old accepted
three-input preparation. It does not read any enriched-inverse row result.

## Preparation algorithm and error checks

resolved_sensitivity_prepare.py reconstructs the six omitted right sensitivity
vectors E^T*l/sqrt(lambda) from saved training E and left eigenvectors, with
scalar fsum and bounded column chunks. It checks their Gram error<=1e-4 and
all64 E*v components against sqrt(lambda)*l, with256*eps*lambda_max/sqrt(lambda)
as the absolute arithmetic diagnostic bound. The relatively loose Gram limit
reflects roundoff amplification near the fixed eigenvalue threshold; these
vectors are not an outward spectral certificate. No tiny unresolved eigenvalue
is inverted and no new eigensolve or native kernel is run.

The frozen twice-reorthogonalized preparation helper maps D*v against original
51-column Q plus the accepted3trial columns and previous extras. It verifies
orthogonality and target reconstruction. The original trial prefix must remain
bitwise identical. Combined9inputs would give a60-column candidate only after
full A actions and projection rows are separately acquired and checked.

Fixtures recover an exact omitted mode under the fixed rule, verify derivative
mapping/reconstruction and bitwise prefix, and reject rank overflow, zeroed
training payload, stale spectrum/outputs, wrong cwd and changed pins. These
are input preparation controls, not evidence for a useful inverse.

## Fresh complete-row holdouts for a possible next candidate

Training remains original left1:64. New complete held-out rows, fixed before
any new candidate or kernel result: left66/16717/50150 and
right2/16985/50955 (right global offsets66867). Uniform quarter-grid anchors
and the next untested prefix row replace the previous held-out row set.
Old tested rows/results remain public validation history. Neither their metric
values nor new held-out values select directions or adjust the threshold.
Reused microscopic data and shared inputs are not independent physical validation.

Any next candidate must report complete old/new row sums on all new heldouts
and training controls; any tested row>=1 rejects that candidate's unweighted
contraction route. Sample success still needs full-space/outward/radius and
physical response gates. No adaptive addition chosen from these new holdouts.

## Prospective preparation001 only

Fresh raw/resolved-sensitivity-prepare-001;120s owner including all numeric work,
120continuous normal-pressure seconds,3GiB group/workspace cap. Current charged
22575.04157867035s/25200 leaves2624.958421329651s; worst120 leaves2504.958421329651s.
Native kernel work, new inverse and resource expansion are not admitted here.
Forecast about100MiB working storage for Q/vectors and bounded row chunks;
actual RSS/runtime unmeasured. All input hashes checked before/after and owner
manifest fixed. Stop on guard, provenance or numerical check failure; no automatic
retry or substitute directions. Brave/Docker/other study untouched.

Staged1865pins; parent validation/stage4.685455750208348s separate workflow cost.
Final333testsPASS54.039s incl native fixture builds;311Python sources compile
PASS; moment_refinement exit0; diffcheckPASS. No separate configured typecheck.
Rejected candidate result5d51a2c CI46150971899PASS.

## Accepted preparation001

TerminalPASS21.540965541731566s, maxindividual/sampled group119046144B
(~113.53MiB).1865staged/1872accepted closure pins, terminal receipt/watcher,
exact manifest and trial output hash checked. [Result](resolved_sensitivity_prepare001_result.json).
Six omitted vectors reconstruct with Gram error2.5807085046736233e-7 and action
error1.3411674757591717e-10. Mapped targets have old54-column squared projections
6.78e-6–5.12e-5; all six remain outside that span. After reorthogonalization,
maxorthogonality1.5912384906882327e-17 and maxreconstruction4.0780352630996467e-16.
Combined trial count9, original3prefix bitwise unchanged. No A actions/new inverse.
Sourcec33d133 CI46151286367PASS.

Charge22596.58254421208s/25200 leaves2603.4174557879196s. All owners terminal.
Next source/fixture-qualify a nine-input joint-action variant with the fresh
held-out rows above, then a selected material pilot. Only after those pass may
a separate complete pass be admitted. All original kernel contexts/physics and
old producer artifacts remain unchanged. No new kernel run admitted here.
