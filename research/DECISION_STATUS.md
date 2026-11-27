New measured feasibility evidence: a complete retained-input Q0 nonlinear
residual and Jacobian action now pass in908.65s at882MB peak RSS, without the
67.7GiB dense allocation. See [full nonlinear gate](FULL_NONLINEAR_MAP_GATE.md).
The tested seed is unconverged; no new gap or response prediction follows.
The subsequent amplitude pass independently reproduced the stored conventional
mode action and located a projected sign change between 0.10 and 0.15 meV.
A retained-basis nonlinear candidate then converged in 1.07 s / 113 MB peak RSS,
with mean Fermi gaps 0.1663/0.1653 meV at 8.05 K. Its full native validation
completed in 785.63 s / 904 MB but failed both stationary-residual targets:
8.96e-8 Ry infinity norm and 0.00236 RMS residual/gap. Exact input preservation
and native controls pass. A tiny coefficient residual did not certify a
full-space gap. See REDUCED_NONLINEAR_GATE.md and GAP_SEED_VERIFY_GATE.md.

# Scientific decision checkpoint

[Documented converged Nb replay](ARCHIVED_NB_FINITE_Q_GATE.md) now reproduces
both released currents with reconstructed curvature. The correction changes
this real frozen state by only 2.5–2.8 ppm; large imposed-gap errors must not be
presented as demonstrated material impact. Reuse is cheap after compatible inputs
exist, but no corrected nonlinear solve or qualified Q=0 material prediction
has been established.

New method evidence: [velocity-moment study](VELOCITY_MOMENT_METHOD.md) reproduces
native geometry arrays exactly and preserves direct same-energy quadrature using
second moments. [Response-cell refinement](MOMENT_REFINEMENT_RESULT.md) changes
the first-moment result substantially; signed-support selection is a separate
source of bias. The pinned current-geometry compatibility runtime also passes.
Both [unshifted-band directions](DIRECTION_AND_ZERO_Q_GATE.md) now pass native
controls and moment conservation, but retain a ~0.906% direction discrepancy.
Their accepted runtimes are 63.9 and 60.9 s, below 182 MB peak RSS. This excludes
the tested finite-Q band shift as its main cause; it does not identify the cause.
The paired fourth-order control increases the direct result by about9% and
does not reduce the direction discrepancy (~1.04% versus~0.91%). Derivative,
energy-grid, tensor/gap mapping and physical normalization gates remain open.
A [separate exact-source symmetry regression](SYMMETRY_SCALE_FINDING.md) also
shows why arbitrarily reducing momentum can change the selected symmetry group;
its relative-tolerance candidate is not yet a material-qualified production fix. No full current-version SCTK build is implied.
[Physical interpretation](PHYSICAL_INTERPRETATION_GATE.md) is separately gated:
numerical improvement cannot alone establish experimental accuracy.

Latest material gate: [Nb geometry diagnostic](NB_MATERIAL_DIAGNOSTIC.md).
Preparation succeeded in 49.8 s / 200 MB peak RSS. Complete current on imposed
1.5-meV-gap material geometry shows roughly 5–11% released error at 2 K versus
direct occupations, but no self-consistent physical prediction. Both native
variants initially failed exactly zero-gap controls through xi/E at E=0.
The [combined correction](ZERO_ENERGY_FINDING.md) now passes those controls,
with nonzero-gap currents unchanged. The paragraph below
describes the earlier fixture milestone; the stronger geometry evidence remains
limited by the explicitly imposed gap and unconverged integration estimates.

## What is established

The strongest currently supported contribution is a reproducible numerical
correctness study of the finite-Q response workflow. Two normal-reference
expressions in the current routine disagree with direct occupation identities.
A separate finite-temperature saturation shortcut affects both current and the
upstream gap RHS. Complete-routine synthetic fixtures show that the discrepancies
survive integration or residual assembly. Narrow candidates pass the tested
references, including optimized OpenMP builds. These are numerical findings;
no corrected self-consistent material response has been established. The
[reviewable patch](patches/README.md) also includes tested exact finite-T
zero-energy product limits in current and RHS; zero-T RHS behavior is unchanged.

The public released V3Si slope extraction is reproduced near 97.6 nm after
correcting our own conversion error. The peak extraction remains inconsistent
with its published table value under the inspected archive/script combination.
That unresolved discrepancy is not attributed to the numerical bugs. Theory,
sampling, and provenance remain separate possibilities.

## What this could enable

If material-level tests show a consequential effect, a qualified correction would
let users compute finite-temperature finite-Q gaps and currents without the
demonstrated thermal-boundary error. That is a scientific reliability benefit,
distinct from faster reproduction. Its importance depends on how much real
quadrature weight lies in the affected region and how the gap solution responds.
Synthetic error magnitudes cannot answer those questions.

An accessible response workflow has a narrower possible advantage: repeated,
validated finite-temperature or anisotropic decisions from compatible reusable
microscopic inputs. Efficient stiffness and reduced-model methods already
compete with generic penetration-depth screening. No evidence currently supports
a broad unsaturated-platform or validated-user-demand claim.

## What prevents a positive feasibility verdict

New evidence: [the older saved Nb gap](NB_LEGACY_ALIGNMENT.md) aligns in all
134,807 band/k indices with retained Q=0 native geometry. Its temperature and
convergence are still unknown. [Dense interaction allocation](MEMORY_FLOOR.md)
would require 67.7 GiB even at these smaller counts, so a new unmodified dense
solve cannot fit 32 GiB RAM. Reuse or qualified memory reduction is necessary.

Legacy released state files omit curvature. The existing native inputs support
a preparation route now measured at 49.8 s and 200 MB peak RSS. Its first launched
attempt exposed a wrapper argument-contract bug, now corrected and regression-tested.
Two later runs were interrupted by host pressure before attempt 005 succeeded.
The finite-Q preparation counts differed from archived gap counts. A later Q=0
preparation matches the smaller legacy gap geometry, but [gap provenance and
scalar consistency](NB_GAP_CONSISTENCY.md) still reject assigning it to the
inspected temperature series. Matching indices alone do not qualify transfer.

Even after preparation succeeds, its imposed initial gap is not a self-consistent
material state. A predictive demonstration needs matching gap provenance,
convergence, thermal-factor consistency upstream and downstream, and validated
units/extraction. Reuse also cannot blindly preserve final state weights across
momentum: the source shifts energies before DOS interpolation. No cold-start
Mac runtime forecast is justified by the cluster logs alone.

## Next decisive evidence, in order

1. Evaluate the prepared rank34 reduced candidate after the response-assignment
   owner terminates. Rank33 full validation finished in 599.93 s / 952 MB and
   failed unchanged targets: infinity residual 4.58e-8 Ry, RMS ratio 0.00213.
   A second source-bound occupation enrichment is prepared; its reduced solve
   is cheap, but another full pass requires a new cost/information decision.
   See verify_critical_gap_result.json and second_occupation_reduced_manifest.json.
2. Qualify conditioning and refinement of a successful gap. A point residual
   alone cannot bound gap error near the transition.
3. Resolve the failed direct response assignment before connecting a gap:
   directional preparation gives62850/64662states versusQ0gap66867/67940.
   A geometry-only symmetry-selection control is prepared. Preserve far-band
   single states; do not infer a fine-grid gap from the constant-gap experiment.
4. Resolve derivative/integration, physical normalization and functional gates,
   then quantify a selected observable against those uncertainties. Choose a
   response demonstration, focused correction/method report, or bounded negative
   result from that evidence. A public cold-start reproduction remains separate.

Further synthetic examples are lower priority now that the complete RHS effect
is demonstrated. Do not expand the platform or launch a material screen before
these gates. The full goal remains incomplete; this checkpoint does not replace
it with the work already finished.

Evidence entry points: [RHS finding](RHS_THERMAL_FINDING.md),
[current finding](CURRENT_IDENTITY_FINDING.md),
[preparation pilot](PREPARATION_PILOT.md), [reuse boundary](REUSE_BOUNDARIES.md),
[workflow costs](WORKFLOW_COSTS.md), and [current alternatives](CURRENT_LANDSCAPE.md).
