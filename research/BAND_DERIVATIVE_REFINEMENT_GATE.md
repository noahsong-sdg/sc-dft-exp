# Prospective48cubed derivative-grid study

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
unshifted48cubed automatic grid, and la2F is enabled to serialize the owning
band input. `PW/src/punch.f90 -> a2Fsave` writes that file in internal Ry.
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

## Runnable stages

Use fresh destinations and the exact environment recorded by each manifest.
Do not launch these stages concurrently or skip the preceding qualification:

```
python3 research/stage_public_band_grid.py /absolute/capacity-build /absolute/public-inputs /absolute/new-band48
python3 research/macos_native_guard.py bands 1200 /absolute/new-band48 /absolute/new-band48/pw.x -in /absolute/new-band48/native.in
python3 research/public_band_grid_analysis.py /absolute/new-band48 /absolute/new-band48/run-manifest.json
python3 research/stage_refined_response.py /absolute/capacity-build /absolute/public-inputs /absolute/new-band48 /absolute/new-band48/run-manifest.json /absolute/new-response48
SCTK_MOMENT_GRID=8 python3 research/macos_native_guard.py moment 240 /absolute/new-response48 /absolute/new-response48/velocity-moment-probe.x -in /absolute/new-response48/native.in
python3 research/moment_analysis.py /absolute/new-response48/velocity-moments.txt
```

The refined-response stager repeats the band validation before destination
creation. It constructs a separate consumed bundle, preserving original public
identities and explicitly labeling a2Fsave as derived. No invented download URL
or replacement author-hosted checksum is used. Both the generated source and
consumed copy stay bound to the readback hash if a later change occurs. A stale
or failed band gate rejects staging; a concurrent-change fixture verifies that
new identities are never silently adopted. The copied bundle is immutable for
this read-only response diagnostic, unlike the band-generation XML lifecycle.

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
