# Complete public dense-band replay — prospective protocol

Status:897point input staged, no watcher launched while the rank37 full residual
check is active. public_dense_band_manifest.json pins the experiment. This is a
reproduction of the actual32³ band input, not a grid refinement.

## Evidence supporting one bounded run

The corrected public saved-density pilot reproduces eight archived band points,
all208eigenvalues, within9.605e-9Ry without an energy-offset fit. It runs in
1.695s/92MB. Whole-pilot scaling by897/8 gives190s, including repeated setup;
k-dependent iteration costs remain unmeasured. One600s/3GiB action is justified
to verify the entire upstream band input and measure its actual laptop cost.
It stays inside the existing four-hour guarded pilot allowance; no larger
campaign or new material is inferred from this decision.

## Trace and invariants

`read_file_new -> read_a2fsave -> calc_d_xi_q` makes a2Fsave, rather than the XML
band list, the owning dense-band input for response differentiation. Its header
is26bands/897irreducible points, weights sum2, grid32³. The stored Gamma energies
agree with XML within2.11e-13Ry. `read_a2fsave` reads the energies directly in
internal Ry; do not apply XML's Hartree conversion to these reference values.

stage_public_dense_bands.py checks the author-hosted a2Fsave against its original
size/SHA before output creation. It reuses the qualified one-atom Nb cell,
pseudopotential, density/PAW state, cutoffs, FFT grids and tight diagonalization
settings. It replaces only the explicit point card and expected band list in a
fresh generated run. Point weights are1 for this fixed-density bands calculation;
they are not used as a new DOS or Fermi-energy estimate. No original microscopic
file is rewritten. Stale originals cannot be silently adopted while refreshing
the two generated-file hashes; a concurrent-change fixture checks that boundary.

Verify all23,322eigenvalues, their exact point ordering and unchanged input hashes.
The maximum absolute difference must be <=1e-6Ry, with no fitted constant shift.
A passing process guard alone is insufficient. The existing eight-point verifier
keeps its default protocol; the dense wrapper explicitly selects897points/600s.
Tests include the last band of the last point, wrong grid/layout/units,
nonfinite data, stale inputs and wrong point-count protocols.

## Independent execution

From a pinned repository checkout with the documented fresh build and public
input bundle available, stage a new run:

```
python3 research/stage_public_dense_bands.py /absolute/fresh-build/qe/bin/pw.x \
  /absolute/public-input-directory /absolute/new-dense-run
python3 research/macos_native_guard.py bands 600 /absolute/new-dense-run \
  /absolute/new-dense-run/pw.x -in /absolute/new-dense-run/native.in
python3 research/public_dense_band_analysis.py /absolute/new-dense-run \
  /absolute/new-dense-run/run-manifest.json
```

The public guard requires120s normal-pressure observations and checks the staged
manifest before waiting and again before launch. Do not run it concurrently
with another heavy campaign job. Preserve failed attempts in new directories.

## What the result would enable and leave open

A pass would establish a measured saved-density route to the complete original
dense-band input, separately from phonon/Coulomb generation. It would support a
costed derivative-refinement experiment, not prove response convergence or a new
material prediction. A failure must be diagnosed at its actual stage, rather
than assigned to laptop infeasibility.

Source inspection already exposes a refinement constraint: pinned QE declares
npk=40000 in Modules/parameters.f90, and PW/src/pwcom.f90 allocates xk(3,npk).
read_a2fsave expands xk over the full grid.32³ fits;48³ does not. Do not launch a
48³ response initializer against that build. A larger-grid experiment needs a
consistent rebuilt module limit and an unchanged32³ baseline check before a
numerical comparison. This is a compile-time storage bound, not a prediction of
physical cost or an excuse to change the response equations.
