# Complete public dense-band replay — prospective protocol

Status: complete native replay and strict readback PASS. All23322 eigenvalues
agree within4.151893e-7Ry against the declared1e-6Ry target, without a fitted
offset. Wall98.947410s/96403456B peak RSS; original inputs unchanged.
public_dense_band_result.json binds the original manifest/receipt/output.
This reproduces the actual32³ band input; it is not a grid refinement.

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


## Concurrent original-file change boundary

A post-run review found that the stager initially rehashed the original a2Fsave
while assembling its final manifest, after it had already checked the catalog
and read the reference. If that original changed during staging, the manifest
could adopt new bytes while reference.json still described the old file. In
plain terms, the source identity and derived reference could disagree.

The fix preserves the catalog size/SHA for this original, just as for the saved
density files. The prelaunch guard then rejects any concurrent change. The
regression changes both density and a2Fsave after their checks and verifies that
neither new identity is adopted. This is smaller than adding copies or new
fallback paths and enforces the existing immutable-original requirement.

The completed001 experiment used the original stager at94a6326; its consumed
manifest is preserved unchanged and strict readback passed before this code
change. Reproduce its historical hash-bound readback at that revision. New runs
must stage fresh manifests with the fixed source. No evidence showed a change
during001: all original catalog hashes matched on its final readback.
