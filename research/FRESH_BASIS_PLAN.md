# Fresh compatible gap basis

The execution path is fresh geometry -> verified finite-temperature Z -> linear
weights -> tiled microscopic pair operator -> block images -> Rayleigh–Ritz
checkpoint -> reduced nonlinear candidate -> independent full residual. The
historical basis and its images are not a compatible fresh calculation.

Two byte-preserved source modules are now public, with hashes and origin recorded
in portable_gap/basis_source_provenance.json. They compiled and ran in the bounded actual-input qualification;
a full image application and Ritz basis remain pending. basis_compile.mk provides the source-only compile target using the
already public operator build. No historical custom object is linked.

block_linear_operator forms the exact finite-temperature Q0 zero-gap derivative,
including the finite xi=0 limit beta*dk/4, applies both tile orientations, and
normalizes by the current 1+Z. It requires serial execution, finite positive beta,
xic<0, zero dxq, valid counts and zero padding. An independent uncached native
row/column oracle must qualify the new actual-input application before its
images are accepted.

tc_subspace generates deterministic fresh energy/band/state trial functions and
orthonormalizes them twice. Its checkpoint combines trial vectors and their
current images, validates the Gram matrix, and solves the nonsymmetric projected
problem. Residuals select a candidate and new projected directions. These are
algorithmic candidates, not a converged gap or an error bound. A positive
conventional Fermi branch must be checked independently of residual size.

First qualify source compilation and an actual-input bounded linear application
with uncached row/column controls. Measure that application on this Mac before
forecasting the full initial16-vector image sweep. Bind the eventual basis to
fresh geometry, physical temperature, full Z, pair coefficients, source/library
identities and the exact trial payload. Reject changed contexts and stale basis
images. A continued basis must preserve its original certified identities.

Only then run bounded full image applications and enrichment as needed. Preserve
the unchanged full nonlinear residual criteria (maximum1e-10Ry and normalized
RMS1e-5); quantify conditioning and gap-to-response error separately. The 8.05K
anchor does not qualify other temperatures. No basis stage is completion of the
response goal.

## Measured qualification and checkpoint decision

basispartial001 passed in 53.081329s at 1,042,350,080B individual peak RSS.
Four64-row block timings were 0.804/0.720/0.830/0.727s. Uncached selected sums
agree within the unchanged bound (error1.6941e-20 vs2.3540e-13). Persisted trial
Gram error2.8755e-14; finite values, exact payload size and padding checked.
See portable_basis_partial001_result.json. This is not a full operator image.

Row-only full16-vector forecast: mean804.755s, sampled752.254–867.181s;
these are scheduling estimates, not bounds. Cold setup and validation add cost.
Use contiguous segments1:16384,16385:32768,32769:49152,49153:66867,
with32-row tiles preserving uninterrupted DGEMV addition grouping. Forecast
roughly250–300s per segment including setup, subject to actual32-row measurement.
Before production, compare uninterrupted1:64 against1:32 + persisted/reloaded
33:64 on actual microscopic inputs, including cache/slab resets. Require bitwise
agreement. No production launch is authorized by a fixture alone.

linear_image_checkpoint.f90 stores unnormalized partial sums, separately from Z
or normalized basis images. It checks context, temperature, both state counts,
column count, completed rows, exact binary size, finiteness and uncomputed/padded
zeros across every column. Standalone compiled tests cover split-order equality
and stale/truncated/nonfinite/padding rejection. Actual-input restart qualification
and its driver/stager remain pending. Normalize by -(1+Z)^-1 only after every left
row is complete, then require the uncached full-row/column oracle before Ritz.

Actual-input restart qualification now PASS: portable_basis_split001_result.json.
The source-built32-row traversal and serialization are bitwise restart-equivalent
for1:64 vs32+32 across all16columns aftercache/slabreset. Complete16-vector
images and independent complete-row/column nativeoracle remain pending.

## Initial complete images accepted; enrichment required

All66867leftrows and16images now complete, normalizedonlyatend; sixuncached
complete row/column samples matchedexactly. Independentbinaryreadback confirms
Gram/projection/residuals. See portable_basis_production005_result.json and
initial_basis001_result.json. No conventionalmodeaccepted atdimension16; largest
positive Ritzvalue0.917756 with0.234relative residual isnotconverged. Applythe
operator to16emittednext-vectors, appendtobasis underunchangedoperatorcontext,
thenrepeatRitz. Distinctbatchidentity mustbindnewtrialpayload/oldbasis/source and
checkpointintervals. Preserveunchanged nonlinearandphysicalacceptancegates.

##32-vector readback accepted; continue to48

Firstenrichment complete withsixsampled uncachedsums passing onfirstnewvector.
32-column Gram/projection andrealRitzresiduals independentlyrecomputed; see
enlarged_basis001_result.json. Same-signFermi-averagecandidate lambda1.00463,
residual0.0274371; selectedindex0, notqualifiedfornonlinearseed.16nextvectors
emitted. Additionalenrichment retainsphysicaloperatorcontext whileusingnew
checkpointbatchidentity. No convergence/responseacceptancegate wasrelaxed.

##48-vector result andregistered64 limit

48-column independentreadbackPASS; same-signcandidate relative residual0.0060520
(previous0.0274371),lambda1.0023979,selectedindex0. Stillnotqualifiedfornonlinear
seed. See enlarged_basis002_result.json. Enrichonce moreto64 underunchanged
physicaloperatorcontext. Ifstillunconverged, evaluate targetedrestart orsolver
strategy againstactualevidence; do not blindlyincreasebasislimit orrelaxgates.


## Fresh geometry/Z bundle for the full nonlinear check

`fresh_gap_context001_result.json` records an exact-copy bundle at
`research/raw/fresh-gap-context-001`: `native-init.meta/bin` from
`fresh-gap-init-001` and `full-z.meta/bin` from`portable-z-sweep-009`.
The four source hashes, original terminal receipts, complete-image parent
identities and six-sum uncached Z oracle were revalidated. Counts, Fermi level,
energy scales and Fermi-weight denominators match. The zero-T geometry
initialization precedes the driver's explicit switch to beta19613.355577892344
(8.05K); the bundle does not reuse retained geometry/Z. No kernel work was run.

The existing `nonlinear_map_probe.f90` full driver reads its geometry and Z
from one `map-control.in` directory, so this bundle avoids a new driver variant.
Once a reduced candidate passes its1e-9 linear-seed gate, create a fresh
verification root, set `map-control.in` to this bundle, and give `seed-control.in`
the candidate directory and unchanged operator context. Its `gap-seed.meta`
point must name this same bundle and carry exact runtime counts/nx/nmf/ne/beta.
Pin all consumed files, source-build provenance and outputs prospectively;
recheck at launch. Do not copy an old gap vector into the new context.

A bundle alone is not native compatibility acceptance. Full runtime must
verify the initialized arrays and Z exactly, preserve the candidate input,
pass occupation/tile/Jacobian controls, and satisfy unchanged residual targets
(1e-10Ry maximum and1e-5 normalizedRMS). Conditioning, discretization,
response mapping and physical normalization remain additional gates.


## Conditioning acceptance, separate from stationarity

See [GAP_CONDITIONING_PROTOCOL.md](GAP_CONDITIONING_PROTOCOL.md) for the
fixed-operator Jacobian/sign convention, a possible reduced inverse, a
sufficient local full-space certificate and transport to stiffness/ratios.
No such bound has been measured yet. A finite set of actions or a compressed
condition estimate does not control the unmeasured complement. The existing
stationary thresholds and registered1% response target remain unchanged.


## Nonlinear handoff within the existing interfaces

Use `fresh-gap-context-001` as the reduced driver's geometry directory as well
as the full checker's point directory. Its native-init arrays are byte-exact
copies of fresh-gap-init001. This matters because subsequent occupation
enrichment requires the full seed's point path and reduced geometry path to
be identical, in addition to exact array/context compatibility.

`reduced_nonlinear_driver.f90` already reads `basis_dir` and `mode_dir` separately.
If48-vector convergence misses the1e-9 seed target but a later64-vector mode
passes it, a same-operator48-column representation may seed from that64-column
mode. The driver checks size/beta/config/context, measures its mode projection
error and solves only a candidate; the full nonlinear residual remains decisive.
Keeping48 rather than64 columns leaves capacity for measured occupation-defect
enrichment under the unchanged64-column cap. This is a prospective handoff,
not acceptance of a mode or nonlinear representation before those results exist.

The existing full checker can be copied as `verify-gap-seed.x` into a fresh
verification root, retaining its certified executable hash. The strict reader
expects that basename and the `moment` receipt label. Set exact native seed
counts/nx/nmf/ne/beta and the shared context-bundle point; pin every copied
input and original build/source proof before launch. No new driver variant or
change to frozen linear-source chains is needed for this path.
