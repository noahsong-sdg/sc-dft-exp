# Scientific decision checkpoint

Latest material gate: [Nb geometry diagnostic](NB_MATERIAL_DIAGNOSTIC.md).
Preparation succeeded in 49.8 s / 200 MB peak RSS. Complete current on imposed
1.5-meV-gap material geometry shows roughly 5–11% released error at 2 K versus
direct occupations, but no self-consistent physical prediction. Both native
variants fail exactly zero-gap controls through xi/E at E=0. The paragraph below
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
no corrected self-consistent material response has been established.

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
Prepared counts differ from archived gap counts, preventing direct gap transfer.

Even after preparation succeeds, its imposed initial gap is not a self-consistent
material state. A predictive demonstration needs matching gap provenance,
convergence, thermal-factor consistency upstream and downstream, and validated
units/extraction. Reuse also cannot blindly preserve final state weights across
momentum: the source shifts energies before DOS interpolation. No cold-start
Mac runtime forecast is justified by the cluster logs alone.

## Next decisive evidence, in order

1. Fix and regression-test the newly exposed E=0 current product boundary.
2. Qualify geometry reuse/convergence after the completed preparation and
   fixed-gap diagnostic, separating those from physical predictions.
3. Obtain a compatible converged gap, or justify a bounded new solve, then compare
   corrected and original workflows under the same numerical controls.
4. Quantify changes in a selected physical observable and compare them with
   convergence and extraction effects. Only then choose a response demonstration,
   a focused correction report, or an evidence-bounded negative result.

Further synthetic examples are lower priority now that the complete RHS effect
is demonstrated. Do not expand the platform or launch a material screen before
these gates. The full goal remains incomplete; this checkpoint does not replace
it with the work already finished.

Evidence entry points: [RHS finding](RHS_THERMAL_FINDING.md),
[current finding](CURRENT_IDENTITY_FINDING.md),
[preparation pilot](PREPARATION_PILOT.md), [reuse boundary](REUSE_BOUNDARIES.md),
[workflow costs](WORKFLOW_COSTS.md), and [current alternatives](CURRENT_LANDSCAPE.md).
