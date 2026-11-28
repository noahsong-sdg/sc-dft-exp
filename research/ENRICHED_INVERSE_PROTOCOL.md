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

## Accepted diagnostic001: enriched candidate rejected

TerminalPASS30.27037683315575s, maxindividual328024064B (~312.83MiB), sampled
group118308864B (short native peak missed).1958staged/1974accepted closure pins,
exact consumed manifest/receipt/watcher and ten output identities checked.
[Result](enriched_inverse001_result.json). Sourceb93c140 CI46150551746PASS.
All independent checks passed: all2916 M entries (maxerror8.304468224196171e-14,
maxerror/bound0.00026164815258147465), two-sided inverse1.7293459157869913e-13,
324 C samples maxerror2.42861286636753e-16 and every old/new saved row element
maxerror3.122502256758253e-17. Small-matrix singular ratio2328.1414351593335
is not full-space conditioning.

| Row | Role | Old defect sum | Enriched defect sum |
|---|---|---:|---:|
| left1 | training |272.463383|25.689839|
| left32 | training |205.758588|19.468015|
| left64 | training |123.741233|11.668872|
| left65 | held-out |147.831350|13.936707|
| left33434 | held-out |220.100539|20.753940|
| left66867 | held-out |172.168725|16.080739|
| right1 | held-out |245.730778|23.546274|
| right33970 | held-out |203.334158|19.278254|
| right67940 | held-out |155.813816|14.731376|

Every tested row still exceeds one. This54-column candidate fails the registered
unweighted contraction gate despite roughly tenfold improvement. No full defect
sweep will run on it; no inverse/gap or physical result adopted.
Charged22575.04157867035s/25200 leaves2624.958421329651s. All owners terminal.

### Saved-direction postread, separate workflow cost

[Read-only postread](enriched_inverse001_direction_postread.json) independently
sums E*v using saved old/new nine-row matrices and the original three exported
sensitivity directions. All27 enriched components have magnitude<=3.88e-15;
old leading-direction components reach1.12228. Thus mapped-direction repair works
on those directions; the large remaining row sums cannot be attributed simply
to failure to annihilate them. This is not a full complement bound or a causal
proof of every remaining error. Input identities match before/after; wall
0.27378129167482257s separate from guarded ledger. Reproduce the numeric arrays:

```python
from pathlib import Path
import math
from defect_spectrum_readback import matrix
from stream_inverse_action import column
n=134807
v=matrix(Path('research/raw/defect-row-spectrum-001/sensitivity-directions.bin'),n,3)
for filename in ('baseline-rows.bin','enriched-rows.bin'):
    parts=[[[] for _ in range(9)] for _ in range(3)]
    with (Path('research/raw/enriched-inverse-001')/filename).open('rb') as stream:
        for first in range(0,n,1024):
            width=min(1024,n-first);values=column(stream,9*width)
            for k in range(3):
                for i in range(9):
                    parts[k][i].append(math.fsum(a*b for a,b in zip(values[i::9],v[k][first:first+width])))
    print(filename,[list(map(math.fsum,col)) for col in parts])
```

Run from repository root with PYTHONPATH=research; recorded JSON includes all
three source binary hashes. No new kernels, inverse or physical acceptance.
The original training spectrum has9directions above the already fixed1e-10
relative-eigenvalue threshold; only3were exported for the first pilot. Any future
candidate must be based on training data and a prospectively fixed rule, with
fresh held-out rows; current held-out results are now validation history and
cannot be reused as an untouched test. No new candidate or compute admitted here.
