# Anisotropic gap: measure observable error before requiring exact symmetry

## Problem and traced path

The rank34/35 gap-orbit tests measure departures from exact scalar symmetry.
Their 1e-10 identity criterion is a diagnostic, not a response-error tolerance.
A failure alone cannot tell us whether averaging directional moments materially
changes a response. Conversely, near symmetry alone does not certify accuracy.

The traced path is `velocity_moment_probe`: fine-grid `calc_dosk` weights are
interpolated into cell DOS and first/second directional velocity and curvature
moments; `symm_dosk` averages each scalar array; `compute_dosk` independently
checks DOS, mean velocity, and curvature; `store_d3k` retains positive-DOS
energy states and uses a separate single-state branch elsewhere. Previous
exports retained assigned means but discarded the second moment and the
pre-averaging arrays. That loss prevents a gap-dependent averaging-error test.

The opt-in `MOMENT_CACHE=1` export preserves those arrays before and after
averaging. It changes no solver arithmetic. The default build and assignment
binary schema remain unchanged. This is preferable to symmetrizing the gap,
loosening an identity threshold, or assuming a variance theorem for signed
quadrature weights. Historical exporter sources are preserved at dc8a6f2;
older manifests identify earlier exact versions and must not be rewritten.

## Discrete observable and error control to implement

For each retained resolved energy/cell/band state let

- E = hypot(xi, delta), T = beta[sech²(beta xi/2) - sech²(beta E/2)],
- H = 4[tanh(beta xi/2) - xi/E tanh(beta E/2)],
- m2 and h be the weighted second velocity and curvature moments.

The fixed-quadrature resolved contribution is
`S = sum dx0 * (T*m2 + H*h) / (volume*Qnorm²)`.
Replacing m2 with m1²/DOS gives the corresponding mean-velocity closure.
These are candidate diagnostics; a stationary gap, discretization convergence,
current-functional interpretation, and absolute material normalization are
separate requirements.

For a verified uniform cell-orbit averaging operator P, compare both `S(raw)`
and `S(P moments)` at the *same unmodified candidate*. Replay the native
averaging from the raw cache; validate its action, the rotation convention,
and invariant retained-support mask rather than assuming them. On each orbit,
`|S(Pm)-S(m)|` is bounded by the sum over raw entries of
`abs(dx0)/(volume*Qnorm²) * (abs(m2)*range(T) + abs(h)*range(H))`.
A sharper bound may use each entry's maximum distance to the orbit coefficient
range endpoints. This follows the triangle inequality and self-adjoint uniform
orbit averaging; it needs no positivity of tetrahedron weights. Report both
actual difference and the absolute bound, with cancellation/denominator scales.
No bound is valid until the averaging and support checks pass.

The candidate is defined on the initialized native state layout. Match exact
energy labels/cell/band and verified quadrature weights; reject missing states.
Do not interpolate a gap onto negative or discarded DOS support. Report that
omitted support and the separate single-state branch explicitly. A bound for
retained resolved states is not a bound for the entire current or continuum.
Constant-gap fixtures must give zero coefficient range and averaging error;
an asymmetric signed-weight fixture must satisfy the absolute bound. Include
stale phase/context and incorrect native averaging fixtures.

## Resource and interpretation gates

One opt-in cache export is prepared in response_moment_cache_manifest.json.
Launch only after full native owner2285 is terminal, then after the normal
120-second pressure window. Deadline120s/RSS3GiB; earlier same-geometry run
34.95s/195MB. Raw+averaged caches add about13MB at the present dimensions.
The q1e-12/full48 setup deliberately exercises the documented absolute selector
fault to match Q0 geometry. It is a rotational-averaging diagnostic, not a
qualified physical small-Q prescription or a replacement for the relative fix.

No threshold on observable error is silently inferred from the 1e-10 symmetry
identity test. Quantify the result first. Any later accuracy claim must name
its observable, support, denominator, tolerance, and scientific decision.
