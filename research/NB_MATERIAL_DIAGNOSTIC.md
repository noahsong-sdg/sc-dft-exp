# First material-derived current diagnostic

## Measured preparation feasibility

Attempt 005 completed native Nb geometry preparation on the 32-GiB Mac in
49.783 s. Guard receipt: exit 0, peak individual RSS 199,573,504 bytes,
sampled group peak 198,492,160 bytes. The 120-second/3-GiB limits and normal
host-pressure requirement were unchanged. It launched after 60 continuous
seconds of normal pressure. No interaction matrix or nonlinear gap solve ran.
The watch and child are terminal; no solver remains running from this attempt.

The custom state SHA256 is
`dddc4eb0d79e2762d5b8c978564cefbd43b1625321a2ad2f46fb92c4bb6f2cde`.
Both grids pass the strict preparation-only schema/finite-value checks, with
62,850 and 64,662 states. Every state has nonzero curvature; 61,149 and 63,054
have nonzero velocity contractions. Metadata/initial-gap diagnostics are in
nb_preparation_diagnostic.json. Raw state/receipts remain ignored locally.

This demonstrates affordable reconstruction of missing response arrays from
retained microscopic inputs. It does not demonstrate an affordable cold-start
DFT/phonon/Coulomb workflow or an accurate superconducting gap.

## A correction can survive material quadrature

`material_current_probe.py` validates the prepared file, fetches/hash-checks
the pinned current source, compiles its complete released and thermal-candidate
routines, and loads all prepared integration states. It imposes a constant
1.5-meV gap at 2, 4 and 8 K on the same finite-Q geometry. Independent Python
evaluation sums shifted occupation identities with `math.fsum`.

At 2 K the released currents are 8.95893e-7 and 1.04303e-6 in code atomic
units; corrected values are 9.42423e-7 and 1.16670e-6. Released errors relative
to the direct reference are approximately -4.94% and -10.60%. Corrected values
match the direct reference within 2.4e-14 absolute across these imposed-gap cases.
The discrepancy is much smaller at 4 and 8 K. Full values and nonfinite controls
are in nb_material_current_results.json. Thus the effect is not confined to two
invented states, but neither these temperatures nor the imposed gap describe a
qualified self-consistent Nb solution. The two integration grids also disagree
substantially; convergence is indispensable before physical interpretation.

## Newly exposed boundary and reuse failure

The exactly zero-gap controls yield nonfinite native current on both released
and thermal-candidate routines. Some material states have xi=0, producing E=0;
the source forms xi/E before multiplying its vanishing thermal factor. The
continuous occupation identity gives zero normal current. Results encode
nonfinite native values as null, explicitly marked false for finiteness;
they are failures, not passing controls. A separate narrow root-cause fix and
regression are needed before claiming normal-state robustness.

Prepared counts differ from the archived gap's 66,867/67,940. Direct statewise
gap transfer is rejected. The source's DOS symmetrization retains only operations
conserving Q (four here versus the zero-Q group), in addition to shifted energies
and thresholded support. Attribution of the count difference requires controlled
comparison. There is also an absolute squared-Q symmetry tolerance of 1e-15:
arbitrarily shrinking Q eventually changes the accepted symmetry group. A naive
numerical Q→0 sweep therefore cannot qualify the analytic response route alone.

## Reproduce and next gate

```
python3 research/preparation_analysis.py research/raw/nb-preparation-005/response-state.txt
python3 research/material_current_probe.py research/raw/nb-preparation-005/response-state.txt
python3 -m unittest discover -s research -p 'test_*.py'
```

The first two commands require the locally generated preparation artifact; its
source wrapper, build path and input provenance are documented in
PREPARATION_PILOT.md. They are not a portable raw-input download/install command.
The offline suite passes 33 tests. Complete native material-current probe passed
its nonzero-gap reference comparisons and explicitly exposed failed zero-gap
controls. Next: isolate/fix that singular product, then a controlled geometry
reuse/convergence test and compatible qualified gap. Full campaign incomplete.
