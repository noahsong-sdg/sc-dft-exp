# Fixed-density public band reconstruction: pilot protocol

Status: staged code and synthetic checks only; no band calculation launched.
The fresh response build remains the only heavy job. Do not launch this pilot
until that owner is terminal and the normal-pressure launch gate passes.

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
original primitive cell and alat. No cell optimization, SCF iteration, gap solve,
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
Run it only through the campaign guard protocol, then verify with:

```
python3 research/public_band_pilot_analysis.py \
  /absolute/new-band-pilot /absolute/new-band-pilot/run-manifest.json
```

Tests cover conversion, exact point mapping, untouched originals, stale-input
rejection before output creation, missing terminal receipts, and detection of a
constant energy offset rather than fitting it away. Native output readback and
actual resource measurements remain pending.

A successful pilot would justify estimating a32³ dense-band replay cost from
measured work, with setup and k-dependent diagonalization uncertainty. It would
not justify an uncalibrated cluster-to-Mac extrapolation or establish a converged
response. Reassess the information gain before any full-grid or refinement run.
