# Actual-input ordered restart test

The source-only checkpoint build and rectangular fixtures passed. They do not
by themselves establish equality after cache reset and persisted readback on the
actual Nb interactions. The next bounded experiment uses the same fresh8.05K
candidate, geometry/Z, interactions and32-row arithmetic as full-gap003, with
the separately source-built checkpoint executableSHA90c072ebc2c8df205ddc358155b22bdc29756ae091fefebb81f08fa12f58e3d9.

## Prospective experiment

`stage_full_map_qualification.py` verifies both parent input inventories, the
source-only build receipt/result and candidate identity. It derives an evaluation
identity from the seed manifest, checkpoint build manifest/result, executable,
candidate and operator hashes. The identity is independent of the new run's
directory and row bounds, so later qualified segments can retain it.

The native `qualify` mode computes continuous rows1:64, then resets caches and
compares rows1:32 plus persisted/reloaded checkpoint plus rows33:64. All four
unnormalized images must agree bitwise. All67940right states participate in
each selected row. The split checkpoint records32completed rows; the final
partial checkpoint records64. Neither emits a full-map result or accepts a gap.
This tests selected rows, not an exhaustive independent operator recomputation.

`full_map_segment_analysis.py` independently requires:

- Matching terminal PASS receipt, exact command/cwd/guard/deadline and valid
  resource fields; exact public/consumed manifest equality and every input hash.
- Evaluation identity, candidate, operator and native geometry/seed controls;
  complete inclusion of both ancestor input inventories.
- Exact checkpoint schemas, row counts, beta and derivative step; finite data,
  exact binary sizes and zero inactive/uncomputed image rows.
- Bitwise active gap/xi/dk/Z equality with the declared source files, and all
  four occupation/derivative weight batches checked with an exponential form.
  The existing1e-14absolute occupation tolerance is retained.
- Native continuous-versus-restarted equality assertion; identical split/main
  state bytes; nondecreasing carried error/CPU diagnostics; no full-map output.

The partial explicit-sum discrepancy must also satisfy
`2e-13 + 2e-12*max(abs(unnormalized_partial_images))`. This is a preliminary
partial-image control, not a replacement for the frozen final normalized-map
sum bound, finite-difference gate or stationary residual thresholds.

The geometry schema reports nx, number of cells, bands and fine-grid points.
It does not report nmf/ne. A staging trial caught and corrected a mistaken
comparison of those different fields before any native launch; a real-layout
regression fixture now prevents recurrence. Seed nmf/ne remain bound by the
seed/operator metadata and checked by the native owning driver.

## Evidence and admission boundary

Three new native-backed regression tests exercise the independent checker and
stager. They reject pre-migration schema, truncated/nonfinite/changed state,
wrong weight batches, oversized explicit-sum error, missing equality assertion,
stale receipt/manifest/input, premature full output and uncomputed image rows.
The baseline native fixture also uses the actual geometry-header field meanings.
The narrow suite passes3tests in6.336s.

Staging draft001 was never admitted or launched. It was superseded before
admission by002, adding the explicit partial-sum control and binding the frozen
final checker source. Its raw draft remains separate; it has no native cost.
Only the prospective002manifest identifies the current experiment.

The separately recorded admission is180s/3GiB with the unchanged120continuous
normal-pressure gate and versioned streaming guard. Prior actual runs suggest
initialization roughly80–110s plus a few seconds for128row evaluations; this is
a forecast, not a runtime bound. No automatic retry, production segment or pilot
expansion follows. Independent strict readback must pass before another decision.

Full-space nonlinear stationarity, conditioning, response normalization/functional,
grid uncertainty, other temperatures and physical validation remain open.

Final gate: `python3.13 -m unittest discover -s research -p 'test_*.py' -v`
passed205tests in34.774s, including native fixtures. All206maintained Python
sources compile; `python3.13 research/moment_refinement.py` exited0 and
`git diff --check` passed. No separately configured typecheck.
All1064prospective pins and public/consumed manifest equality passed before
publication. No maintained native solver source changed in this slice.
