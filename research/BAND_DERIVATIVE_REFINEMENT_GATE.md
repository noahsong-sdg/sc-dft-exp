# Prospective48cubed derivative-grid study

Latest:48band diagonalization PASS359.615s/109MB, but its original required
a2Fsave output protocol FAILED. The complete XML has2769points;145shared
reference points agree within4.6133e-8Ry. `disk_io=nowf` makes QE punch return
before a2Fsave even when la2F is requested. Preserve public_band_grid48_result.json
as that failure. The separate native serialization protocol below is the fix;
it does not retroactively pass the original protocol.


## Scientific question

The tested32cubed constant-gap response changes about9% when only its velocity
stencil changes from second to fourth order. That unresolved sensitivity exceeds
the measured moment-averaging effects. Test whether refining the underlying band
grid reduces it, using reusable saved charge density rather than recomputing
phonons or Coulomb matrices. This is a numerical validity experiment, not a
material penetration-depth prediction or a new equilibrium gap solve.

## Evidence and cost decision

The complete original897-point/26-band32cubed input reproduces from public saved
density: all23322 absolute eigenvalues within4.152e-7Ry, target1e-6, no fitted
shift,98.947s/96MB. Grid-volume scaling to48cubed predicts334s; differing
irreducible-point counts and iteration costs remain uncertain. One1200s/3GiB
band action after120s normal pressure is justified, only after the larger
capacity build passes the exact32cubed eight-export response baseline.

The fresh consistent npk300000 build is separately qualified in
POINT_CAPACITY_REBUILD_GATE.md. No48cubed response may use the old npk40000
build. One heavy job at a time; do not queue watchers behind an active one.
The initial four-hour guarded native pilot ceiling remains in force.

## Band-generation invariants and readback

`stage_public_band_grid.py` retains the exact qualified one-atom Nb cell,
pseudopotential, density/PAW state, cutoffs40/320Ry, FFT32/24,26bands and tight
1e-10 diagonalization control. Only the explicit k-point card becomes an
unshifted48cubed automatic grid. The original la2F request proved ineffective:
`PW/src/punch.f90` returns for io_level<0 before its a2Fsave call. A separate
`read_file_new(needwf=false) -> a2Fsave` action now writes the owning format in
internal Ry from completed XML, without redoing diagonalization.
The density is fixed; the coarse-density convergence problem remains separate.

`public_band_grid_analysis.py` requires exact staged input hashes and terminal
guard success. It verifies all generated coordinates and26-band energies agree
between XML (Hartree) and a2Fsave (Ry), checks grid48cubed, finite values,
nonnegative weights with sum2, and compares absolute energies at common32/48
reference coordinates. Require at least100 shared irreducible points and max
energy difference<=1e-6Ry, without fitting an offset. This is a preregistered
shared-point check, not independent accuracy at all newly generated points.
The last band/point, stale input/receipt, duplicate coordinates and uniform
energy-offset cases have readback tests.

Consumed-copy hashes are checked at launch; only the consumed XML may become
native output. Original public files remain immutable. Generated a2Fsave is a
new derived artifact: preserve its hash, source input/command and output metadata.
Do not relabel it as an original author-hosted input.

## Subsequent response controls

If band readback passes, stage a separate input bundle combining the unchanged
public XML/density/PAW/pseudopotential and26phonon/elph files with the new48cubed
a2Fsave. Explicitly record which file is derived. Keep response-cell grid8,
full48-symmetry tiny-Q diagnostic, imposed1.5meV gap and2/4/8K coefficients fixed.
Predict about112s from33.24s*48cubed/32cubed; use240s/3GiB guard,120s normal gate.
Measure actual cost and re-evaluate before another run. No temperature/kernel
reuse claim follows from this fixed-gap experiment.

Compare direct fine-quadrature and reconstructed second-moment responses,
signed-weight audits and native first-moment replay. Distinguish derivative-grid
change from cell interpolation, energy quadrature and Fermi-energy estimation:
read_a2fsave recomputes the dense-grid Fermi energy, so a32->48 change is a
combined band-grid sensitivity, not an isolated stencil truncation error.
A fourth-order48-grid control needs a separately pinned, consistently linked
probe and identical generated inputs. A64-grid extension requires a new measured
cost decision. If changes persist, report non-convergence rather than choosing
the preferred value or fitting normalization to experiment.

## Runnable stages after the observed writer boundary

Use fresh destinations and the exact environment recorded by each manifest.
Do not launch stages concurrently. Build the small serializer against the same
qualified source tree, using a fresh directory and the supplied make target:

```
make -C /absolute/fresh-serializer-build -f /absolute/repository/research/a2f_serialization.mk QE_ROOT=/absolute/capacity-build/qe a2f-serialize.x
python3 research/stage_public_band_grid.py /absolute/capacity-build /absolute/public-inputs /absolute/new-band48
python3 research/macos_native_guard.py bands 1200 /absolute/new-band48 /absolute/new-band48/pw.x -in /absolute/new-band48/native.in
python3 research/stage_band_serialization.py /absolute/fresh-serializer-build/a2f-serialize.x /absolute/new-band48 /absolute/new-band48/run-manifest.json /absolute/new-serialized48
python3 research/macos_native_guard.py serialize 120 /absolute/new-serialized48 /absolute/new-serialized48/a2f-serialize.x -in /absolute/new-serialized48/native.in
python3 research/verify_band_serialization.py /absolute/new-serialized48 /absolute/new-serialized48/run-manifest.json
python3 research/stage_refined_response.py /absolute/capacity-build /absolute/public-inputs /absolute/new-serialized48 /absolute/new-band48/run-manifest.json /absolute/new-response48 --serialization-manifest /absolute/new-serialized48/run-manifest.json
SCTK_MOMENT_GRID=8 python3 research/macos_native_guard.py response 240 /absolute/new-response48 /absolute/new-response48/velocity-moment-probe.x -in /absolute/new-response48/native.in
python3 research/verify_refined_response.py /absolute/new-response48 /absolute/response48-manifest.json
```

The build is also guarded in this campaign; public_a2f_build_manifest.json records
its exact command/inputs/receipt. The original direct-band analyzer remains
available for runs which actually produced native a2Fsave. The separate
serialization route is explicitly selected; it does not silently fall back after
an error. It validates all coordinates,26-band energies, weights and grid against
the parent XML, both terminal receipts and the original shared-energy targets.
A regression changes the final band, balanced point weights and an immutable
consumed copy; each is rejected. The actual native serializer is its integration
gate. Original source/consumed manifests and failed protocol remain preserved.

The refined-response stager repeats the selected validation before destination
creation. It constructs a separate consumed bundle, preserving original public
identities and explicitly labeling a2Fsave as derived. No invented download URL
or replacement author-hosted checksum is used. Both generated source and consumed
copy stay bound to the readback hash if a later change occurs. A stale or failed
band gate rejects staging; a concurrent-change fixture verifies that new
identities are never silently adopted.

## Separately linked fourth-order control

`build_fourth_order_response.py` reuses the freshly source-built QE/SCTK and
reference LAPACK/BLAS libraries; it does not claim another cold-start build.
It fetches the same SHA-pinned geometry source and applies the existing
`fourth_order=True` velocity-only extraction, leaving curvature unchanged.
A new probe directory prevents old module/object adoption. All parent archives,
modules, make.inc, probe sources and generated geometry are hash-recorded;
LAPACK/BLAS outside the QE subdirectory are included. A changed or pre-capacity
parent is rejected before output creation. The native link/run is still the
integration gate.

After48band/response controls terminate, one180s/3GiB guarded link is justified,
expected seconds plus bounded source retrieval. Require120s normal pressure and
no other heavy owner. Then stage separate original32 and derived48 response
controls with that probe, retaining the exact tiny-Q/full48 diagnostic and
response-cell grid8. Use120s and240s guards respectively. Require unchanged
inputs, native first-moment replay, and second-moment conservation on each grid.
Compare all2/4/8K fine-quadrature values to the corresponding second-order run;
report differences without treating them as a certified truncation bound.

```
python3 research/build_fourth_order_response.py /absolute/capacity-build /absolute/new-fourth-build
```

The command itself is a build, so execute it through the documented guard and a
prospective input manifest. Subsequent staging uses `/absolute/new-fourth-build`
as its build argument. The parent remains untouched. A successful link is not
response qualification; retain all failed attempts and measured cost.

## Attribution without another native solve

`constant_moment_components.py` contracts the raw cache on all support, including
negative or zero DOS cells, and separates the computed thermal velocity-squared
and curvature terms. Their sum must reproduce the native direct fine-grid value
at2/4/8K. The32cubed baseline agrees within4.78e-16 in the native diagnostic units.
The curvature term is only about20–31ppm of the total in these imposed-gap cases;
the velocity-squared term dominates. This supports the velocity-stencil control,
without assigning separately validated physical meanings to those terms.
A signed/zero-support fixture prevents accidental support filtering.

```
python3 research/constant_moment_components.py /absolute/response-run
```

This decomposition shares the native thermal approximation. It is an attribution
of a discrete computed sum, not independent physical validation or a truncation
error certificate. Preserve component source/input hashes alongside comparisons.


## Why this fix is chosen

The problem is an I/O control-flow boundary, not a failed band calculation.
Technically, nowf maps to io_level=-1 and punch returns before the writer call.
In plain terms, the requested small output sits behind the setting that suppresses
wavefunction output. Directly calling the unchanged QE reader/writer in a small
serial postprocessor is the smallest coherent way to preserve the native format
and recover the completed work. Enabling broader wavefunction output would add
unneeded storage; repeating diagonalizations would add no information. No solver,
thermal expression, numerical threshold or band energy is changed.


Native serialization checkpoint: separate action completed in1.243783s with
108068864B peak individual RSS. All2769 coordinates,26 bands and point weights
match the parent XML within1e-12;145 shared reference points differ at most
4.613280e-8Ry, below the unchanged1e-6Ry criterion. See
`public_a2f_serialize48_result.json`. This does not make the original missing-output
protocol pass. The next experiment is the independently staged48cubed response,
with imposed gap and unchanged512 response cells; no physical accuracy claim.


### Actual48 response cost revision

The first48cubed response failed its predeclared240s deadline:240.128889s,
405143552B peak RSS, exit-15; all consumed inputs unchanged. It produced no
accepted diagnostic. The112s grid-volume forecast was inadequate. A one-second
near-deadline sample observed all769 main-thread stacks in calc_dosk, including
array-allocation/free activity. This is an interval profile, not total phase
attribution or proof of an optimization opportunity.

A distinct900s/3GiB attempt with identical mathematics and inputs is justified
within the original four-hour pilot allowance: terminal guarded work to this
point totals8678.137533s, leaving about95min. The900s limit is a bounded cost of
answering the central grid comparison, not a predicted completion time. Preserve
both prospective manifests and the first failure. No64cubed run is justified by
this evidence. Use the explicit --guard-seconds 900 readback only for the new
protocol; the default240s reader rejects it. A passing computation still needs
all native conservation/cache checks and the fourth-order stencil controls.


### Completed48 baseline and next scientific control

The separate900s-protocol retry completed233.587811s/401113088B; strict hashes,
native moment controls, full110592point/512cell context and cache contractions
passed. At2/4/8K, the fine diagnostic increases5.5207/5.5218/5.5244% versus32.
See public_response_grid48_retry002_result.json and public_response_grid_sensitivity.json.
This resolves neither integration convergence nor physical response accuracy.
The first240s protocol stays failed. Its112s forecast was too optimistic.

The retry's late one-second sample captured opt_tetra_init in read_a2fsave,
while the original late sample captured calc_dosk. These intervals do not prove
which phase dominates total cost. A separately staged support-only DOS candidate
therefore remains deferred until phase timings justify it. The fourth-order
velocity control is the next scientific priority. Use a distinct900s48 protocol
and retain the marginal240s failure; do not silently extend an existing run.

Portability note: the first refined verifier imported the Mac guard's runtime
while only needing its input hash check. Linux CI rejected that import. The fix
uses the existing portable postrun hash checker, preserving receipt/context
validation and leaving the Mac launcher unchanged. A subprocess regression
forbids loading a native library during import. The successful retry was checked
before this source edit; its original manifest retains the dcf39b3 code identity.
