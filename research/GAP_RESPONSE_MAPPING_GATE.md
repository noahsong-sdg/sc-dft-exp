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

## Symmetry isolation result and interpretation

The control passes in34.147s/195362816-byte peak RSS. Selecting48 operations
restores66867/67940states. Every energy node, assigned energy and band/cell
index matches the Q0 snapshot exactly. Maximum weight difference3.31e-23 and
energy-grid weight difference6.88e-22 pass the unchanged64eps gate. See
response_assignment_symmetry_result.json. With the same executable, unshifted
bands and grids, the deliberate change to symmetry selection restores layout
compatibility. This identifies the cause for this tested pair; no interpolation
or tolerance relaxation was used.

The technical cause is that `symm_dosk` averages scalar DOS and directional
first/second derivatives over the momentum-preserving subgroup before the
positive-DOS support threshold determines state assignment. At Q0 the group
contains48 operations; at the tested direction it contains4. In plain terms,
the two paths average different collections of cells before choosing the states.
The unshifted energy bands alone do not make the representations identical.

Do not fix this by choosing an artificially tiny Q. The paired moment readback
(response_symmetry_moment_result.json) shows why: averaging an odd directional
velocity over full symmetry cancels it before it is squared. At2K the full-group
squared-mean diagnostic is about-1.58e-7 instead of the direct0.00814488.
These are diagnostic code units with an imposed1.5meV gap, not physical material
response. Both groups' all-support second moments still match their fine-grid
reference; changing Q changes that reference by less than5e-16 relative.

A candidate next method is a Q0-compatible tensor/second-moment representation,
with transformation of directional quantities treated consistently. This is
preferred for investigation over silent vector interpolation because it retains
the matched scalar layout and the measured moment identity. It is not yet an
implemented or qualified fix. An anisotropic gap requires a demonstrated crystal
symmetry condition, correct resolved/single-state treatment, and convergence;
the constant-gap identity alone does not supply those. Mass/vertex and functional
accuracy remain independent gates.

## Scalar-gap symmetry audit implemented; material run pending

Before applying full-group averaging to a cell-dependent gap, test the gap and
geometry on the corresponding native cell orbits. Otherwise a matching layout
can still conceal a changed response integrand. For an invariant scalar factor
C(k), permutation of cells proves sum C(k)*average_group[M(k)] = sum C(k)*M(k).
This is linear in the DOS-weighted second moment or curvature. Squaring an
averaged first moment does not satisfy that identity. The proof does not
establish convergence of the underlying band derivatives or quadrature.

The optional assignment exporter now also writes `response-symmetry.txt` with
the actual native integer rotation matrices, cubic cell grid, and the fully
shifted second-grid convention. Its previous version is pinned at0d2ea1b;
historical build/launch manifests continue referring to that immutable version.
Existing assignment payload/schema and the default target are unchanged.

`python3 research/gap_symmetry_audit.py CANDIDATE PREPARE SYMMETRY_FILE` first
performs strict reduced-candidate and native-state readback. It maps cell indices
using exact doubled integers, including the half-shifted second grid. Like
native symm_dosk, it skips rotations that do not preserve the shifted grid.
Resolved states match by band, cell and exact energy-node index; single states
remain a separate class. Missing counterparts, incompatible energies/weights,
and scalar-gap variation are reported separately. Geometry uses64eps relative
with exact zeros; the prospective scalar-gap tolerance is1e-10 times its global
maximum. These are diagnostic symmetry criteria, not full-gap or observable
error bounds. Fixed band labels follow this native representation; degeneracy
or band-permutation ambiguities would require investigation, not a physics
claim based only on failed label matching.

Tests cover shifted/inverted cells, a nonsymmetric matrix that detects transpose
errors, an asymmetric gap, missing records, geometry violations, stale/truncated
rotation metadata, wrong grids and file-bound candidate readback. A compiled
fixture executes the actual exporter and confirms native matrix order and the
unchanged assignment schema. The retained-native boundschecked optional target
builds; all77regressions pass5.215s, compileall/diff checks pass. No standalone
project typecheck exists.

response_symmetry_build_manifest.json pins this build. response_orbit_manifest.json
prepares one120s/3GiB export using the measured34.147s/195MB geometry cost, after
120 quiet normal-pressure seconds. It must wait behind full owner17667. The
material gap symmetry audit has not run. No production response fix is claimed.

## Material scalar-gap orbit result

The fresh export passes in34.947s/195346432-byte peak RSS and restores the
strict Q0-compatible layout. response_orbit_result.json binds its inputs,
receipt and actual native-matrix payload. The rank34 orbit audit takes17.25s
and86999040-byte peak RSS. All6,470,736 comparisons across134,807states and
48rotations find exact energies and weights, with no missing or off-grid records.
The gap itself fails the prospective1e-10-relative symmetry criterion: maximum
orbit difference7.00139e-9Ry, or0.000294718 of its global maximum (0.0295%).
See rank34_gap_symmetry_result.json.

This rejects exact scalar-gap invariance at the tested tolerance, not the whole
response-reuse thesis. The observed variation could arise from unfinished
convergence, basis error or discrete-operator symmetry breaking; these causes
are not yet separated. It also does not establish a scientifically significant
response error. Next compare the independently measured linear mode or full-map
image on the same orbits, or propagate the variation through a clearly defined
response before judging its importance. Do not silently symmetrize the gap or
relax the recorded test. A bounded approximate moment route remains possible,
but requires an explicit observable-error assessment.
