# Superconducting response on a laptop: evidence and decision

Final bounded campaign report, 27 November 2026. All registered native controls
are terminal and read back. [Acceptance audit](REQUIREMENTS_AUDIT.md),
[cost ledger](WORKFLOW_COSTS.md), [restart state](../CAMPAIGN_STATE.md),
[chronological evidence](../RESEARCH_LEDGER.md).

## Answer supported by the evidence

**Narrow the project to a reproducible numerical-validity study.** Reusable
microscopic inputs make useful response diagnostics and a retained-input gap
stationarity check practical on this 32 GiB Mac. The campaign does **not** establish
reliable material-response prediction, a portable microscopic cold start, or a
new unsaturated market. Those are separate, still-open claims.

The scientific benefit beyond faster reproduction is an executable way to find
misleading numerical agreement before interpreting a material prediction. In
this Nb diagnostic, conservation can pass while grid/stencil sensitivities
remain substantial; a promising two-grid result reverses on a held-out third
grid. Another method developer can reproduce these tests, inspect the failed
inferences and decide which numerical stage needs attention. This is a proposed
use backed by working examples, not demonstrated researcher adoption or proof
that such studies were previously impossible.

## Principal findings

| Test | Verified result | What it establishes |
|---|---|---|
| Public response reproduction | Fresh source build 261.64 s; native 33.24 s / 187 MB; all eight exports bitwise equal to the retained run; 31 inputs unchanged | The response diagnostic has a public source/input path on this Mac |
| Second-moment closure | Squared mean velocities retain only 40–45% of the matched fine-grid sum on tested coarse cells; retained second moments reproduce that discrete sum | Averaging then squaring can discard a large numerical contribution in this approximation |
| Fourth-order velocity, 32→48 | Response spread falls from ~5.52% to~0.68% at 2/4/8 K | Reduced observed two-grid sensitivity; no continuum bound |
| Held-out fourth-order 64³ | 48→64 shift −0.335/−0.337/−0.340%, after the positive 32→48 step | Absolute changes contract, but same-direction continuation fails at every temperature |
| Same-band 64³ stencil control | DOS/curvature/energy axes bitwise equal; F4/F2−1≈1.947%; absolute difference D64/D48≈.4979 rather than frozen .5625 | Isolated velocity-stencil sensitivity remains; leading h² conditional prediction misses by ~11.5% |
| Exact indexed mesh lookup | 1920 compiled brute-force cases; all eight native exports bitwise equal at 32/48; combined fourth 48 takes 83.878 s versus 227.041 s | A qualified exact downstream optimization, single-pair ratio 2.707× |
| Retained-input rank 38 gap | Reduced 1.115 s; full 680.80 s / 938 MB; maximum 3.172e-11 Ry and RMS ratio 7.546e-7 pass unchanged targets | Stationarity for this fixed retained problem, not conditioned gap or material accuracy |
| Matrix-free full action | 908.65 s / 882 MB versus 67.7 GiB dense allocation floor at the inspected state counts | This action fits laptop memory; no paired solve-speed benchmark |
| Same-grid input-regeneration control | Reconstructed 32³ response shifts only 2.19–2.20e-10 relative; 22.419 s / 195 MB | Released versus regenerated bands do not explain the observed grid trend |
| Frozen converged Nb thermal replay | Released currents reproduced; correction changes them by 2.5–2.8 ppm | Synthetic thermal defects do not imply a large demonstrated material correction |

[Third-grid comparison](third_grid_comparison_result.json),
[same-band stencil control](stencil64_control_result.json),
[input-regeneration control](regenerated32_control_result.json),
[gap validation](verify_sixth_occupation_gap_result.json),
[public reproduction](PUBLIC_RESPONSE_REPRODUCTION.md),
[exact lookup](INDEXED_MESH_GATE.md), [figures](figures/README.md).

All response-grid values above use an imposed 1.5 meV gap, the same saved density,
26 bands, 512 response cells and the documented tiny-Q/full-symmetry diagnostic.
They are not self-consistent penetration depths. Curvature is held at its
original stencil when the velocity stencil changes. The observed 64³ reversal
appears in the velocity-squared term; the much smaller curvature term changes
in the opposite direction. That decomposition does not identify all remaining
quadrature or microscopic errors.

## Why these interventions were chosen

The closure issue arises because averaging velocities and then squaring loses
their variance, including cancellation between opposite velocities. Retaining
the second moment preserves the intended matched discrete sum. Signed
tetrahedron weights require direct identities and absolute triangle bounds;
positivity arguments do not apply. This is a controlled numerical statement,
not independent validation of the physical current functional.

The grid experiment tests a distinct derivative error. Changing only the
velocity stencil reduces the original two-grid spread, so a held-out third
grid was registered before its response was inspected. Its reversal blocks a
simple monotone extrapolation. The same-band second-order 64 control then changes
only that stencil: unchanged DOS, curvature and energy axes make the attribution
specific. Neither stencil difference nor contraction is a total-error bound.

Profiling traced a separate performance bottleneck through `read_a2fsave` into
`opt_tetra_init`: repeated mesh searches, including identity-grid cases. An
indexed scatter preserves the original first-match semantics within an explicit
mesh/tolerance domain. Compiled adversarial fixtures and native bitwise exports
qualify that replacement. It was chosen over approximate interpolation because
it removes measured work without changing the mathematical outputs. Timings
are single unprofiled pairs; setup, upstream preparation and timing variability
remain separate.

The nonlinear path avoids a large dense interaction allocation by evaluating
its action in tiles. Reduced occupation/critical-mode enrichment reaches the
registered full stationary residuals at rank 38. Further enrichment merely to
beat the passing threshold is not justified. A small equation residual still
needs conditioning and discretization evidence before becoming a gap-error
bound. The public response build and retained full-gap dependency chain are
not interchangeable; [the portability gate](PORTABLE_GAP_GATE.md) traces that boundary.

The registered same-grid regeneration control closes an input-provenance
confound. Automatic 32³ bands and owning serialization preserve all 897 points,
26 bands and weights; shared energies pass the unchanged 1e-6 Ry test. The new
response differs from the released 32³ result by only 2.19–2.20e-10 relative,
about 3.2e-8 of the original 32→48 absolute difference. The consistent-generation
series still rises ~0.68% and then falls ~0.34%. This excludes this tested
regeneration difference as the explanation, without assigning a physical error.

## Released length-scale extraction

The slope route reproduces a V3Si penetration depth near 97.6 nm versus the
published ~97 nm after correcting our own unit conversion. The peak route remains
near 177 nm versus 136 nm. Local peak interpolation moves 177.09 to 176.24 nm and does
not resolve the discrepancy. At 1 K, first-four-point linear leave-one-out fits
change the length ratio to1.25–1.53 relative to the author's single-point estimate;
odd-cubic alternatives give 1.001 / 1.050. These are window/model sensitivities,
not confidence intervals. [Controls and raw provenance](FINITE_WINDOW_CONTROLS.md).

The released processing script averages two currents before writing the curves,
and only nonnegative momenta are present. Separate-current agreement and
empirical parity cannot be recovered from these processed files. Imposing odd
parity in a fit supplies an assumption, not the missing measurement. Negative
tails alone establish neither a physical instability nor a code defect.
The current functional, normalization, low-temperature GL interpretation and
experimental sample compatibility remain open gates.

## What reuse does and does not buy

Primitive band energies/derivatives and matching geometry support repeated
fixed-context diagnostics. Temperature-dependent gaps and occupations still
change. Changing momentum can change DOS interpolation, active-state counts
and ordering; reusing assigned response states unchanged across Q is not exact.
[Source trace and invalidation boundary](REUSE_BOUNDARIES.md).

Public saved-density band reconstruction is measured: the original897-point
replay takes 98.95 s;48³ bands 359.62 s;64³ bands 826.54 s. The64 input preserves 6273
points / 26 bands, with897 shared reference points agreeing within 4.152e-7 Ry under
the registered 1e-6 Ry test. Owning-QE serialization takes 1.473 s. Shared-point
energy agreement is not derivative accuracy at new points or density convergence.

The full new-material cost remains unknown: relaxed density, converged phonons,
electron–phonon and screened Coulomb preparation, saved Z, fresh basis setup and
physical response qualification are not all measured on this Mac. Historical
cluster clocks cannot be converted to Mac time by multiplying core counts.
The retained basis has historical partial setup accounting and an absent parent
payload. [Complete stage ledger and explicit unknowns](WORKFLOW_COSTS.md).

Final guarded native accounting is 11,357.647 s (189.29 minutes) across 79
terminal attempts: 63 guard passes and 16 failures. This stays below the initial
four-wall-hour ceiling. Quiet gates, unguarded analysis and model use are separate.
Energy and model monetary cost were not measured. No total dollar return or
end-to-end cold-start speedup is claimed. Further sweeps without a better-defined
observable would spend resources without closing the limiting physical gates.

## Opportunity assessment and continuation gate

Current primary-source comparisons identify overlapping finite-Q SCDFT,
extended-GL, DFT stiffness, EPW and IsoME work. The broad response-access pathway
is not shown to be unsaturated, and no interviews or outreach establish unmet
demand. [Current landscape](CURRENT_LANDSCAPE.md), [upstream audit](UPSTREAM_STATUS_AUDIT.md).
The inspectable exact lookup and numerical regressions may be independently
useful; novelty, adoption and publication significance remain unproved.

Continue only as a focused methods/reliability project. Preserve the public
regression harness, raw-source retrieval manifests, held-out negative result
and exact optimization. Stop broad materials screening and unsupported claims
of decision-grade penetration depth. The most ambitious justified next step is
one **portable, physically qualified finite-temperature anisotropic response
case**, with a concrete scientific decision and accuracy target fixed first.

That continuation has three reviewable gates: rebuild the custom gap dependencies
from inspectable licensed source without retained objects; reconstruct or release
rights-cleared compatible microscopic/Z/basis inputs and measure complete setup;
then qualify a held-out response with conditioning, discretization, functional
normalization and a suitable independent benchmark. If these gates cannot be
specified and verified, stop the material-access thesis rather than compensate
with more optimization. Commodity hardware has not been shown to be the decisive
remaining barrier; nor has the complete workflow been shown to fit it.
