# Indexed equivalent-point lookup: prospective qualification

## Problem and owning path

The public response path is read_file_new -> read_a2fsave -> opt_tetra_init.
The optimized-tetrahedron initializer generates a uniform mesh, then searches
all input points and symmetries separately for every mesh point. A second search
checks that every input point was used. read_a2fsave calls this first on
irreducible inputs, then again after constructing the entire ordered identity
mesh. The latter search is quadratic in full point count. In plain terms, it
repeatedly searches for mesh addresses that are already determined by integer
coordinates. The parent tree and equations remain unchanged by this experiment.

Whole-run10ms samples: at32cubed,1087/3278main-thread samples are inside
opt_tetra_init; at48cubed,12074/18842. These approximate sample fractions are not
exact phase wall times. Sampling overhead was not separately calibrated.
They support testing mapping work instead of the deferred DOS arithmetic
candidate, whose32sample fraction was only about9%.

## Exact candidate and domain

mesh_equivalence.f90 scatters each rotated input point onto its nearest uniform
mesh address, retains the original periodic Euclidean comparison and strict eps
inequality, and writes only previously unassigned targets. Visiting input indices
in ascending original order preserves the original first matching input. The
selected symmetry is not persisted by the original routine. Time reversal,
magnetic reversal flags, shifts, non-cubic dimensions and stride are explicit.
A linear seen-array pass preserves reverse-coverage errors and their first
input index. Missing target errors retain their first target index.

The domain requires finite representable reciprocal coordinates and disjoint
mesh matching neighbourhoods: eps*max(grid)<0.5. This is the condition allowing
one candidate address per transformed point. The pinned owning routine itself
generates the uniform reference coordinates. This candidate does not claim to
preserve ambiguous-tolerance meshes outside that domain. No silent fallback is
introduced. The native32/48/64meshes satisfy the domain by a wide margin.

mesh_equivalence_patch.py requires the entire pinned QE tetra.f90 SHA256, then
replaces only the lookup and reverse-coverage blocks. The rest of tetrahedron
construction, transforms, Fermi weights and all response expressions remain.
Generated modified GPL source stays in ignored raw storage. A separately linked
module shadows the original archive member only in the new probe executable;
the original source, libraries and modules remain untouched.

This indexed algorithm is preferable here to a physical approximation, a new
quadrature or broad parallel rewrite: it removes repeated search while retaining
the discrete mapping. It still needs native exact-output qualification. No
speedup follows from asymptotic reasoning or synthetic tests alone.

## Current-source check

On2026-11-27, the official QE develop revision
[61569eb480231b649c47f631df9c5c83537df461](https://github.com/QEF/q-e/blob/61569eb480231b649c47f631df9c5c83537df461/PW/src/tetra.f90)
has exactly the same50575-byte tetra.f90 SHA256 as the pinned native source:
f2b5dde5691d510b613b3e3acef8bb837c549f03082ff7249429469d23d17812.
current_qe_tetra_source.json records acquisition and identity. This verifies the
specific search is present in current owning source. It establishes neither
algorithmic novelty nor absence of unpublished/external alternatives. No outreach
or upstream submission has been sent.

## Acceptance and resource gates

1920compiled cases compare against an independently enumerated brute-force
search. They cover shifts, periodic boundaries, non-cubic meshes, symmetry/TR,
magnetic reversal flags, stride, duplicate/unused/missing inputs and tolerance
edges. Invalid finite-domain, integer-range and ambiguous-tolerance inputs are
rejected. Pinned-source and stale-parent tests reject before output creation.

A180s/3GiB guarded relink completed2.510227s/108249088B; all parent/link inputs
unchanged and generated source matches the prospectively recorded hash. See
public_indexed_mesh_build_result.json. This is reused-library compilation, not a
cold-start build or numerical qualification.

The32cubed native baseline must reproduce all eight original second-order
exports bit for bit, plus context, native controls, cache and input hashes,
before a separate48cubed comparison. Forecast~25s from the observed profile,
120s guard,120normal-pressure seconds. A48attempt needs its own manifest and
exact eight-export comparison to the existing second-order48result. Use actual
accepted-result cost, not a projected search-only speedup. Any mismatch stops
qualification. Larger-grid scientific controls remain conditional on these gates.


##32cubed exact-output result

Native run completed27.205847s/198131712B; all8exports match the unchanged
capacity32baseline bit for bit, and native controls/cache/components/context and
input hashes pass. The observed wall ratio is1.311x versus35.671543s. These are
single unprofiled runs with the same mathematical output, not a repeated timing
study or end-to-end speedup. Native link cost is separate. See
public_indexed_response32_result.json. A prospective48held-out protocol is now
running; qualification does not yet extend to that grid or any physical response.


## Held-out48cubed exact-output result

The separate48run completed85.448508s/444203008B. Every one of the eight
prospectively captured original48exports matches bit for bit; native conservation,
cache/component/context checks and all declared inputs pass. The observed native
wall ratio233.587811/85.448508 is2.734x. These are single unprofiled executions,
not a repeated timing study. See public_indexed_response48_result.json and its
prospective manifest. Only lookup/reverse coverage changes; no physical accuracy
improvement is attributed to that exact acceleration.

This qualifies the tested32/48path. A64mesh could deepen the scientific
convergence test because0.68% two-grid spread is not a continuum error bound,
but needs a separate cost decision, generated bands/serialization qualification,
explicit grid handling and a fourth-order composition control. No64run is queued.


## Explicit fourth-order composition

The original indexed builder always copied second-order parent geometry. That
execution path cannot provide the fourth-order third-grid control. The smallest
extension is `--fourth-geometry-build`: reuse the exact generated geometry of
the existing fourth-order build, verify its source and executable hashes, fourth
order declaration, unchanged curvature declaration and matching capacity, and
include these inputs in the frozen link identities. No source arithmetic is
transformed again and no alternative default is introduced. This avoids another
network extraction or a second independent stencil transformation.

Fixtures exercise the explicit composition and copied-source hash; reject wrong
order, changed geometry, stale capacity and output creation after invalid input.
The resulting build is explicitly numerically unqualified. Before64 response,
it must match all eight existing fourth-order48exports bitwise under a separate
900s native protocol. A passing build is not a passing numerical result.

Verification:125 offline tests passed in10.522s; maintained Python compilation
and diff checks passed. Native composition and64grid remain pending.
