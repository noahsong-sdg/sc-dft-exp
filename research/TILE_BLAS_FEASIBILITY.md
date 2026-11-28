# Measure the contraction cost before a full conditioning pass

The original fixed inverse still lacks a full-space defect bound. A fitted
rank-one update failed its separate probe and was rejected. The streamed norm
identity avoids a145GB dense matrix, but still requires about2.78T floating
operations in two low-rank contractions. A dimensional count does not establish
laptop wall time. The actual inverse build plan links the public build's
reference `libblas.a`; no current measurement justified assuming its throughput
or replacing it. This is the traced computational uncertainty addressed here.

The bounded probe compares that same archive with the built-in Mac Accelerate
library via its pinned SDK link stub. It does not change any accepted solver,
source, input or library. Both fresh executables use the same Fortran source,
compiler/flags, rank51, signed inputs and fixed32timed repetitions, following one
untimed warm-up. Tile shapes are256x384,512x768 and1024x1024. It measures exactly
the two intended layouts: P=(QTD)A as transpose/no-transpose and UC as
no-transpose/no-transpose. No dense material matrix or kernel is generated.

The native program saves the input and output of two small nonsymmetric signed
controls. Independent Fraction arithmetic checks every one of their80output
entries against the exact represented products. It also checks nine sampled
entries of each of six timed products, giving54sampled entries per library.
Native finiteness checks cover the full timed outputs. Sampled agreement is not
exhaustive numerical qualification of a replacement BLAS implementation.

The arithmetic allowance is gamma_(2k)*sum(abs(a_l*b_l)), evaluated exactly as
rational numbers, with unit roundoff2^-53. This tests a conventional elementary
rounding model on these inputs. It is **not** a proof of the internals of an
opaque library or an outward kernel/global norm enclosure. Future full-space
acceptance still needs all kernel, product, coefficient, row-sum and radius
errors bounded and the ball inequality satisfied.

For each tile shape, rates project first-pass contraction work
2*51*9085887960 and second-pass work2*51*134807^2 separately. These are
contraction-only forecasts. Kernel evaluation, source/input loading, coefficient
IO, memory movement outside the warmed calls, full absolute row sums, rounding
enclosures, radius variation and integration are excluded. Do not add a guessed
kernel time or report the projection as a measured full norm runtime.

The runner pins the reference source-build lineage/terminal receipt, compiler,
archive, SDK link stub, OS version plist and its own sources. Two explicit compile
commands and dynamic `otool -L` bindings are retained. The system framework's
runtime comes from macOS; the SDK stub is not a hash of that runtime binary.
Results must state the OS/toolchain and cannot claim bitwise portability.
Requested OMP/OPENBLAS/VECLIB thread limits are1; this does not independently
prove the framework's worker count. Process CPU time and elapsed wall are both
recorded. The own fresh cwd/command/outputs and immutable closure are enforced;
raw acceptance waits for the separate owning guard receipt.

This narrow same-shape library comparison is preferable to rewriting the
scientific kernel or admitting a full pass from a FLOP count. It answers which
contraction backend, if any, makes the proposed method computationally plausible
without treating a fast benchmark as a physical or conditioning result.

The initial tiny fixture used one multiplication and intermittently measured
zero elapsed ticks on this system, despite the clock reporting1GHz. Fixed128
repetitions make the fixture long enough to observe; repeated fresh fixture
launches now check this boundary. Production benchmarking remains fixed32calls.
No fabricated minimum time or retry is substituted for a zero-time observation.

Tests compile/run actual reference-linked signed controls, transpose/layout and
sample checks, stale format/shape/nonfinite/wrong-value rejection, and fresh output
boundaries. A Mac-specific fixture also compiles directly against the actual SDK
stub and checks its Accelerate dynamic binding. Owning tests cover baseline
source/receipt/closure/library changes, both exact compile plans, terminal
withholding, fresh outputs, changed command and final input mutation. Synthetic
runner fixtures do not qualify a real timing run.

Final source gate:274offline tests PASS37.845s, including actual native fixture
builds/run and the Mac SDK binding;257maintained Python sources compilePASS;
Fortran syntax-only checkPASS; moment_refinement exit0; diffcheckPASS. No separate
configured typecheck. No timing pilot is admitted by this source checkpoint.

## Actual pilot001: contractions are plausible, integration is open

[Result](tile_blas_feasibility001_result.json) passed its owning guard in
3.7081837086007s, individual descendant maximum66568192B (~63.48MiB), sampled
group41811968B. The maximum covers build and benchmark descendants, not a
separately measured per-library memory comparison. All44pins, terminal receipt,
consumed/public manifest, exact compile plans and dynamic bindings checked.
Hardware: AppleM5,10logicalCPU,32GiB; macOS26.6.2build25G83, GCC16.2.0.

| Buffered tile | Reference P / UC, GFLOP/s | Accelerate P / UC, GFLOP/s | Reference contraction forecast,s | Accelerate contraction forecast,s |
|---|---:|---:|---:|---:|
|256x384|4.26 /6.78|293.29 /352.60|490.89|8.42|
|512x768|3.70 /7.17|285.91 /321.35|508.78|9.01|
|1024x1024|3.29 /7.04|288.63 /285.90|545.04|9.69|

These forecasts apply the measured rates to926760571920first-pass and
1853638579398second-pass operations. Their ratios are56.2–58.3, a library/tile
comparison on this one pilot. This is neither an observed full-norm speedup nor
a speedup of the existing inverse/solver. Reference runs preceded framework
runs; the small warmed benchmark is not a thermal/contended-load study.

Each backend passed all80signed exact-rational control outputs and54timed
samples. Both maximum small-control errors1.737079286361358e-22 lie below their
5.479991460657078e-15maximum allowances; each entry passed its own bound. Timed
sample max error1.6201866220578965e-16. Both sample payloads are bitwise equal,
while control payloads have different hashes. Therefore do not infer full bitwise
library equivalence. The framework's opaque internal arithmetic and actual
worker count remain separate assumptions despite requested thread limits1.

The [committed synthetic evidence](evidence/tile-blas-feasibility-001) contains
summaries, small input/output arrays, timed samples, build plans, dynamic
bindings, raw readback and guard receipt, with hashes in the public result.
It includes no third-party archive, framework or executable. The offline suite
replays every committed product control with Fraction arithmetic without
requiring a Mac, material inputs or rerunning hardware timings.

Postread independently derives work from66867/67940active side counts, checks
all hashes/source pins/receipt/build plans, replays the rational analysis, and
recomputes projections from FLOPs and raw elapsed times. Postread0.1567553337663412s,
process peak27475968B, is observed separately from guarded wall. Whole-workflow
setup, IO, energy and accepted physical-result cost remain unmeasured.

**Next: test actual layout before a full pass.** The accepted kernel producer
emits32left rows per block. This pilot measures larger buffered contractions,
so no direct production drop-in has been established. Compare32-row processing
against explicitly accounted buffering, qualify both orientations/layout/row
coverage and rigorous error controls, and forecast kernel plus contraction plus
IO work before admission. These results support testing Accelerate for that
new path, not changing any frozen accepted producer.

Charged guarded total21352.417154796272s/21600 leaves247.58284520372763s.
All owners terminal; no next run, fullnorm/kernel pass, retry or budget increase
admitted. All conditioning/radius/physical-response/other-temperature gates remain.

Final evidence-publication gate:275offline tests PASS38.915s, including committed
arithmetic replay and native builds/run;257maintained Python sources compilePASS;
moment_refinement exit0; diffcheckPASS. Native source unchanged since its earlier
syntax/build checks. No separate configured typecheck.
