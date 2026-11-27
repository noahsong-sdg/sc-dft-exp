# Qualifying an anisotropic gap for response

The current full native validation concerns a Q=0 gap at 8.05 K. The existing
moment diagnostic imposes the same constant 1.5 meV gap everywhere at 2/4/8 K.
Replacing that scalar by a vector without matching the native state assignment
would introduce an uncontrolled approximation. No response calculation with the
new candidate has yet been accepted.

## Owning path and observed layout

The retained `sctk_ini_delta.f90` path is `ini_delta -> ... -> store_d3k`.
`store_d3k` resolves a band/cell over positive-DOS energy nodes when at least two
nodes exceed its 1e-12 threshold. Otherwise it creates one interpolated band
state with weight 1/nqbz. Both records carry k-cell and band indices; only the
first class is indexed by the energy quadrature. This is why vector position
alone cannot safely connect the two representations.

`gap_response_mapping_audit.json` records a read-only exact grouping audit of
the same retained Q=0 initialization used in the candidate experiment:

| Class | Side 1 | Side 2 |
|---|---:|---:|
| Resolved band/cell groups | 1024 | 1024 |
| Resolved states | 54579 | 55652 |
| Single-state groups | 12288 | 12288 |

Every resolved state's energy is exactly an xi0 node, with no duplicate energy
within a band/cell group. Every single state is off that grid and has exactly
weight 1/512. Its smallest absolute energy is 0.02747/0.03619 Ry. Large energy
does not by itself justify discarding its response contribution.

Reproduce with `python3 research/gap_response_mapping_audit.py PREPARE SOURCE`,
using the paths and SHA256 identities in the JSON. This groups the actual native
snapshot; it does not certify that an arbitrary source file generated it.

## Required next experiment

After full gap qualification, keep its native 8-cubed cells and exact Q=0 bands
for the first anisotropic response test. Map resolved states using side, cell,
band and exact energy index; require native ordering, energy and weight agreement.
Retain the original single-state branch separately. Reconstruct the native
first-moment and curvature path before evaluating second moments on the same
support and gap. Require a constant-gap replay and the existing native controls.

The constant-gap fine-grid equality does not extend automatically to an
anisotropic gap: a fine-grid gap interpolation changes the question. A cellwise
second moment can audit the within-cell closure at a fixed gap representation,
but cannot establish fine-grid anisotropic convergence. Changing response cells
requires an explicit gap-transfer/refinement study, rather than silently reusing
the old vector. Physical normalization and response vertices remain the separate
gates in PHYSICAL_INTERPRETATION_GATE.md.

## Optional native assignment export built

The constant-gap diagnostic previously wrote only scalar moment sums, which
cannot establish compatibility with a vector gap. The optional
`response_assignment_dump.f90` path now calls the owning native `store_d3k`
with freshly checked DOS/mean-velocity/curvature arrays. It uses the original
state-count rule and writes energy nodes, weights, assigned energies, directional
derivatives and band/cell indices. It never loads or interpolates a gap.

Set `ASSIGNMENT_DUMP_SOURCE` to this module when building
`velocity_moment_probe.mk`; this explicitly enables `ASSIGNMENT_DUMP`. Leaving
it unset preserves the original diagnostic path. Both variants build against
the retained native libraries with bounds checks. Use the unshifted geometry
source for the proposed Q=0 comparison; the export does not itself remove a
band shift or certify the input geometry.

`response_assignment_analysis.py DIRECTORY PREPARE_DIRECTORY` validates schema,
size, finite values, padding and index ranges, then compares shape and exact
band/cell indices with the gap initialization. Energies and weights use the
already declared 64eps elementwise relative compatibility criterion, including
exact zeros. Shape or numerical incompatibility is a reported failed mapping,
not a reason to interpolate silently. Gap-transfer and physical-response flags
remain false even for a compatible layout. The regression covers a compatible
layout, changed indices and stale/truncated persisted data.

The new export has not run on material inputs yet. Its next runtime must wait
until the rank33 full-validation owner is terminal and use a separate measured-cost
decision, normal-pressure gate and single heavy owner. Historical moment
manifests refer to the source before this optional extension (available at
bf3c155); do not rewrite their hashes to the new source.

## Prospective material assignment pilot

`response_assignment_manifest.json` pins the already built exporter and a new
input deck with the gap initializer's nx100/nmf10/ne50/temp0 controls. The
unshifted derivative diagnostic uses nonzero directional Q without shifting
bands. Its 8-cubed response grid matches the saved initializer. A previous
matched moment run took 63.891 s / 181.5 MB; the planned guard is 120 s / 3 GiB
after 120 continuous normal-pressure seconds. No launcher is active for this
pilot. It must wait behind full-validation owner57262, and all pinned inputs
must be rechecked at launch. Passing assignment compatibility would authorize
only investigation of gap reuse, not a physical response claim.

## First material export: direct layout reuse fails

The export completed in34.924s with195280896-byte individual peak RSS. Its
62,850/64,662 states differ from the Q0 initializer's66,867/67,940 despite
matching nx/nmf/ne/temp and the unshifted bands. Strict readback reports
`mapping_compatible=false`; no gap was transferred. See
response_assignment_result.json with its terminal receipt and prospective
manifest hash. This rules out direct positional reuse for this tested pair,
not every controlled state-transfer method.

Owning source `symm_dosk` selects symmetries preserving q_fflo before averaging
DOS and directional moments. Runtime logs select48 operations at Q0 but4 for
the response direction. A causal geometry-only control is prepared in
response_assignment_symmetry_manifest.json: same executable and unshifted
bands, with q magnitude1e-12 so the documented absolute symmetry threshold
admits all48 operations. That threshold defect is deliberately exercised here
to isolate assignment behavior. It must not be presented as a physically valid
response or a recommended way to choose Q. If the layout then matches, the
symmetry-selection dependence is demonstrated; otherwise investigate the other
initialization differences. Do not add interpolation or relax the gate.
