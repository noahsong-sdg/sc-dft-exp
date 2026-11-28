# A32-row native-layout contraction core for the full defect diagnostic

The buffered BLAS pilot established contraction throughput, but its256–1024row
tiles were not a demonstrated fit for the accepted producer. The owning
`block_linear_operator` path emits K(right,left,orientation) blocks and applies
K1 transposed and K2 untransposed before dividing by the output row's1+Z.
`full_nonlinear_step_probe` fixes the left block width at32. K2 is not symmetric.
A generic matrix benchmark therefore left a real layout/normalization gap.

`streamed_defect_core.f90` is a separate diagnostic core consuming that exact
32-row block shape. It changes no frozen solver, kernel, source or accepted
result. Inputs use compact active order: all left states followed by all right
states. The future material adapter must source-bind and validate the conversion
from the padded two-side basis/derivative arrays. That adapter is not provided
or qualified by this fixture checkpoint.

For arbitrary fixed Q,U,W and D, put B=I+U W Q^T D and J=I-A D. The identity
I-BJ=(A+UC)D with P=Q^T D A and C=W(P-Q^T) does not require U=AQ or W to be an
exact inverse. The core implements that identity in bounded tiles:

| Routine | Operation and coverage |
|---|---|
|`accumulate_p`|Consumes contiguous native left blocks; accumulates right columns of P from `(D Q)_left^T A01` and writes each left-column block from `(D Q)_right^T A10`. Uses both separate kernels and correct input weights/output Z.|
|`make_c`|Requires complete left-row P coverage, then forms W(P-Q^T).|
|`defect_left`|Forms UC for current left rows against **all** active columns, adds A01 only in the cross block and multiplies each column by D. Also adds right-row contributions from the current left columns using separate A10.|
|`defect_same_right`|Adds every remaining right-row/right-column UC contribution in contiguous32column batches. No native A term exists in this same-side block.|

Omitting the last routine would leave a finite but wrong norm. Both same-side
blocks are generally nonzero even though A has zero same-side blocks. Independent
left-kernel and right-same-side coverage counters must reach left+1 and right+1
before the caller can report a complete row norm. Incomplete P cannot form C;
skipped, repeated or out-of-range tiles are rejected before their products.
Stale initial P/left rows, malformed shapes, nonfinite data and1+Z<=0 are rejected.

For the prospective Nb active counts, the largest left defect work array is
32*134807doubles=34510592bytes (~32.91MiB). A normalized native cross block is
32*67940doubles=17392640bytes (~16.59MiB). These are shape-based payload counts,
not measured material RSS. Rank-by-active matrices, native kernel storage, BLAS
work, logical/expression temporaries and allocator retention still contribute.
No dense active-by-active matrix is allocated by this core. `make_c` separately
uses a rank-by-active difference matrix. The complete simultaneous peak remains
unmeasured until the material driver is integrated and guarded.

The independent native fixture has35left and39right states, rank3,32-row blocks
with final widths3 and7, and retains the producer's nonunit left-index lower
bounds. It uses unequal output Z, nonuniform input weights, signed asymmetric
K1/K2, nonuniform D including zeros, and arbitrary Q,U,W. A Python Fraction
oracle constructs the full B and J separately and multiplies I-BJ. It compares
all P/C entries and all74absolute row norms against the real compiled core,
using tight floating arithmetic controls. This oracle does not compute its
expected norm through the core's `(A+UC)D` formula. Both same-side exact blocks
are checked nonzero, so the fixture detects their omission.

The generic BLAS link and explicit Mac SDK Accelerate link both pass the dense
oracle. Linux CI supplies its generic BLAS fixture; the Mac binding is local and
explicitly platform-specific. They are link configurations, not an assertion
that the Mac generic link is an independent implementation. Separate fixtures
reject duplicate/skipped coverage, stale P/rows, incomplete coefficient formation,
nonfinite/shape/normalization errors, widths above32, and omitted right-side
coverage. These are synthetic layout/arithmetic controls, not a material norm.

The row sums are ordinary floating-point diagnostics. They are **not** outward
rounding enclosures, a ball contraction, a gap-error bound or a physical response.
Kernel definition/replay/error, products and row-sum rounding, D variation and
eta/ball invariance remain required. This slice establishes the actual strided
32-row algebra without inventing a global certificate from fixture agreement.

Next integrate the compact/padded state bridge and source-built native producer
under a fresh owning receipt; qualify selected actual tiles and timings before
admitting a full pass. This source checkpoint admits no material run, kernel
pass or budget expansion. Existing guarded total21352.417154796272s/21600 leaves
247.58284520372763s; all owners remain terminal. Full response/other-temperature
and discretization/physical gates remain open.

Verification performed:

- `/opt/homebrew/opt/python@3.13/bin/python3.13 -m unittest discover -s research -p 'test_streamed_defect_core.py' -v`:3PASS,5.468s.
- `/opt/homebrew/opt/python@3.13/bin/python3.13 -m unittest discover -s research -p 'test_*.py'`:278PASS,42.086s, including native compilation/execution.
- Python `compile` over all258maintained `research/*.py` files:PASS.
- `/opt/homebrew/bin/gfortran -O2 -ffp-contract=off -fcheck=all -ffree-line-length-none -J /tmp -fsyntax-only research/streamed_defect_core.f90 research/streamed_defect_fixture.f90`:PASS.
- `/opt/homebrew/opt/python@3.13/bin/python3.13 research/moment_refinement.py`:exit0.
- `git diff --check`:PASS. No separate configured typecheck.

These checks cover code/layout/arithmetic and rejection boundaries. They do not
measure a native Nb norm, source-bind a new material driver or establish any
physical uncertainty contribution. The three new files form one purpose, with
213non-test Fortran lines and no changes to pinned producers.
