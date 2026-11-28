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
