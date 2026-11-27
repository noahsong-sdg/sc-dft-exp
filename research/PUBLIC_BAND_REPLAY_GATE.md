# Fixed-density public band reconstruction: pilot protocol

Status: corrected eight-point replay **PASS**. Fresh PW build004 with the public
saved density reproduces all208archived eigenvalues within9.60504e-9Ry, without
an energy-offset fit, versus the unchanged1e-6Ry target. Guard1.694869s/91,963,392B
peak RSS. All declared originals remain unchanged. See public_band_pilot_result.json
and public_band_pilot_retry_manifest.json. This is a limited fixed-density replay,
not a completed dense-band or response-refinement study.

## Why this is relevant

The response derivative-stencil sensitivity is about9%, much larger than the
measured anisotropic moment-averaging effect. We need to distinguish a reusable
band-sampling limitation from an expensive need to redo all microscopic inputs.
A saved-density band calculation is one directly measurable upstream substage;
it is not a full electronic/phonon/Coulomb cold start.

An initial hypothesis based on the XML's1024points was corrected by tracing
`read_file_new -> read_a2fsave -> calc_d_xi_q`. The second routine discards the
XML eigenvalues, reads26bands/897irreducible points from `pwscf.a2Fsave`, and
expands its32³ grid before differentiation. The XML's two8³ grids are therefore
not the derivative grid. Changing that XML alone cannot refine the response.
This boundary must remain explicit in any follow-up implementation.

The bounded first experiment instead asks whether the public saved charge, PAW
state and pseudopotential reproduce eight archived XML band points, and how much
that costs. If they do, a later measured protocol can target the actual dense
bands. No denser response calculation is authorized by this pilot manifest.

## Exact protocol

`stage_public_band_pilot.py` checks the four author-hosted source files against
the existing acquisition manifest before creating a run directory. It copies
those files into a new scratch tree and preserves the originals. It supports
only this pinned nonmagnetic one-atom Nb context,26bands,40/320Ry cutoffs and
32/24FFT grids. It renders the first eight archived tpiba points with the
original primitive cell and alat. CELL_PARAMETERS uses dimensionless alat
vectors with explicit celldm(1), rather than specifying a Bohr cell and lattice
scale twice. This is required by pinned QE cell_base_init; Cartesian vectors
round-trip to the original values in the regression. No cell optimization, SCF iteration, gap solve,
phonon or Coulomb calculation is requested.

The Hartree/Ry conversion is traced to pinned QE
`PW/src/pw_init_qexsd_input.f90` (cutoffs divided by e2),
`PW/src/pw_restart_new.f90` (eigenvalue readback multiplied by e2), and
`Modules/constants.f90` (e2=2). Thus XML20/160 corresponds to PW40/320Ry.
Use `startingpot='file'`, `startingwfc='atomic+random'`, fixed occupations,
`diago_thr_init=1e-10`, `diago_full_acc=.true.`, and `disk_io='nowf'`.
The native integration run must test whether these reconstruction choices work;
synthetic rendering tests do not establish that.

Prospective acceptance: exactly eight matching k points and26bands, maximum
absolute eigenvalue difference <=1e-6Ry across all208values, **no fitted energy
offset**, exact original input hashes preserved, and one matching terminal guard
receipt. This is a reconstruction tolerance, not a physical response-error bound.
Guard180s/3GiB, OMP/BLAS threads1,120continuous normal-pressure seconds before
launch. The manifest must pin the actual newly built PW executable and input
before launch. Count failures, compilation and acquisition separately.

## Commands after a qualified fresh build exists

```
python3 research/stage_public_band_pilot.py \
  /absolute/fresh-build/qe/bin/pw.x \
  /absolute/public-input-directory /absolute/new-band-pilot
```

The emitted run-manifest records command/cwd/environment and input hashes.
The public macOS guard retains the qualified process-control implementation,
adds the120s normal-pressure gate, and writes receipts under the declared fresh
run directory. It checks command/cwd and every staged hash before waiting and
immediately before launch. It rejects an existing watcher instead of overwriting
a prior attempt. Use absolute paths matching the emitted manifest:

```
python3 research/macos_native_guard.py bands 180 /absolute/new-band-pilot \
  /absolute/new-band-pilot/pw.x -in /absolute/new-band-pilot/native.in
```

Then verify with:

```
python3 research/public_band_pilot_analysis.py \
  /absolute/new-band-pilot /absolute/new-band-pilot/run-manifest.json
```

Tests cover conversion, exact point mapping, untouched originals, stale-input
rejection before output creation, missing terminal receipts, and detection of a
constant energy offset rather than fitting it away. Native output readback and
resource measurements now pass for the eight-point pilot.

A successful pilot would justify estimating a32³ dense-band replay cost from
measured work, with setup and k-dependent diagonalization uncertainty. It would
not justify an uncalibrated cluster-to-Mac extrapolation or establish a converged
response. Reassess the information gain before any full-grid or refinement run.


Attempt001 failed in0.480s before diagonalization because the initial input
specified lattice scale twice. public_band_pilot_attempt001_result.json preserves
the receipt, log, input and old manifest hashes. The normalized-cell retry uses
a new directory and unchanged energy acceptance target. No cost or material
conclusion follows from that input-format failure.


The actual a2Fsave header is26bands/897irreducible points on32³; its weights sum
to2 and its Gamma energies agree with the XML within2.11e-13Ry. A full replay
would compare all23,322eigenvalues at those exact coordinates, not substitute
XML's two8³ grids. Scaling the entire1.695s pilot by897/8 gives190s as a rough,
setup-inclusive forecast; k-dependent iteration counts are unknown. A proposed
full replay would use a600s cap, still require the same absolute energy tolerance,
and measure actual cost before authorizing a denser derivative-grid study.

## Consumed-copy provenance boundary

The band calculation reads copied restart files under its own scratch directory,
not the original public directory. The initial stager pinned only the originals.
That left a changed consumed copy outside prelaunch verification, even when the
original remained correct. The regression now requires catalog-bound entries for
all four consumed copies; it fails on the old stager because those entries are
absent. The existing guard checks those exact bytes before and after its quiet
window, without a new guard or fallback path.

The XML copy is both input and native output. Its entry explicitly marks that
single known path as rewritten by native execution. Postrun analysis permits
that XML rewrite and validates its output bands, while requiring the density,
PAW, pseudopotential and all originals to remain unchanged. A test changes the
consumed density and rejects it; attempting to mark it mutable is also rejected.
This handles the actual file lifecycle rather than weakening all hash checks.

The completed dense001 run's three persistent consumed copies were compared
against the public originals after execution and match bit for bit; only XML
was rewritten, as expected. Historical consumed manifests remain intact. New
runs use fresh manifests including the copy entries and the updated verifier.
