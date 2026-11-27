# Small-momentum symmetry selection has an absolute-scale boundary

## Verified root cause

The pinned `symm_dosk` routine selects symmetries using
`dot_product(S*q-q,S*q-q) < 1e-15`, in fractional reciprocal coordinates.
The execution path is `calc_d_xi_q -> compute_dosk -> symm_dosk -> division by
DOS -> current`. The scalar first velocity moment is averaged over this selected
subgroup before the current uses its square.

For inversion S=-I the test accepts inversion when `4*sum(q*q) < 1e-15`.
For q=(a,0,0), this occurs below |a|=1.58114e-8. Inversion does not preserve
any nonzero q. Averaging an odd velocity over k and -k cancels the first moment.
Plainly: making the momentum smaller changes which operations the code treats
as direction-preserving, even when its direction is unchanged.

This is independent of the thermal and moment-closure findings. It means an
arbitrarily-small-Q extrapolation is not automatically a safer calculation.
It does not establish an error at the published q values or explain the measured
[011]/[111] discrepancy at q around 1e-4.

## Owning-routine regression

[Source manifest](symmetry_source_manifest.json) identifies the full source hash,
revision and unmodified extracted routine. The GPL fixture is checked against the
hash-verified upstream file, including its imports. Minimal modules provide two
symmetries (identity and inversion), even unit DOS, an odd periodic velocity,
zero curvature, and 3-cubed unshifted and half-shifted grids. No material bands,
gap, or fitted constants enter this control.

[Full compiled results](symmetry_scale_results.json) show:

| q=(a,0,0) | Released subgroup size | Released squared-moment retention | Relative candidate |
| --- | --- | --- | --- |
| 1e-4, 1e-7 | 1 | 1 | subgroup 1, retention 1 |
| 1e-8, 1e-10, 1e-12 | 2 | below 6e-32 | subgroup 1, retention 1 |
| exactly 0 | 2 | below 6e-32 | subgroup 2, same cancellation |

The expected symmetry subgroup follows algebraically from S*q=q. The odd-field
cancellation is a separate analytic check on the actual averaging routine.
Both response-grid shifts pass. This is not a material response calculation.

## Minimal candidate and its boundary

The diagnostic candidate divides the residual S*q-q by max(abs(q)) before
forming its squared norm when q is nonzero. It leaves exactly zero q unchanged.
The threshold becomes relative to momentum scale; no new arbitrary momentum
cutoff is introduced. Its angular tolerance remains the existing approximately
sqrt(1e-15) convention in this max-component normalization. This is not proof
that that angular tolerance is optimal for every lattice or input convention.

This choice addresses the root cause with one conditional normalization. Merely
lowering the fixed absolute threshold would move the failure to another scale;
forbidding small q would reject a physically legitimate response limit.
Exactly zero is a real domain boundary because its symmetry group differs from
that of a directed nonzero momentum. The current's division by |Q| still requires
a separate zero-Q limit; this candidate does not make that expression defined.

No production solver patch is installed. The full current-version build,
general non-cubic lattices, near-special directions and material-level effects
remain unqualified. This bounded finding is an additional validity criterion
for reusable response calculations, not evidence of experimental accuracy.

## Reproduction

```sh
python3 -m unittest discover -s research -p 'test_symmetry_scale_probe.py' -v
python3 research/symmetry_scale_probe.py
```

Requires gfortran; no network, external microscopic inputs or heavy native job.
Both variants use -O0 -std=f2008 -fcheck=all. The regression verifies the released
failure and corrected nonzero-scale invariance, plus the exact-zero boundary.

## Material geometry control and next qualification

The later unshifted-band Nb controls now demonstrate the same selection failure
in real material-derived geometry: q1e-4 retains4 operations and62850/64662
states; q1e-12 retains48 and66867/67940. The latter matches the Q0 layout, but
its squared-mean current coefficient collapses while the matched fine reference
and all-support second-moment sum remain unchanged to floating-point precision.
See response_assignment_symmetry_result.json and response_symmetry_moment_result.json.
These impose a constant gap; no physical self-consistent response is qualified.

The existing tested `relative_selection` normalization is now applied to the
same unshifted geometry source, with no other change. A retained-native
boundschecked build passes. relative_symmetry_material_manifest.json prepares
one120s/3GiB run atq1e-12 after the current owners terminate. It must retain4
symmetries and match the q1e-4 baseline's energies, weights and indices; normalized
velocity/curvature must agree within1e-10 normwise relative. Its moment sums
must also preserve the existing matched-quadrature identities. No candidate
material run has launched yet. This extends qualification of a specific bug
candidate, not a full current-version build or a physical response claim.

`response_assignment_analysis.compare_scales` reuses strict assignment parsing
to compare the two geometry exports and their derivatives divided byQ/Q².
It keeps exact shape/index and64eps energy/weight criteria. It reports input
direction unverified: the caller must bind that separately from the input decks,
as the binary schema stores only momentum norm. The prospective manifest pins
both directional decks. Tests distinguish correctly scaled arrays, a scale
failure and normalization underflow; existing stale-data gates remain intact.
The public reader before this extension is50d8bb3; historical manifest hashes
are not rewritten. All77regressions pass5.398s, Python compilation and diff
checks pass. The native candidate build uses the actual exporter and retained
libraries, not only the scalar fixture.
