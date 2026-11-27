# Reuse boundary: primitive bands versus assigned response states

## Verified native execution path

Historical pinned source:
https://github.com/mitsuaki1987/sctk/blob/47c06501da8ffd574c87469ddd6d5a2814171796/src/sctk_ini_delta.f90

`calc_d_xi_q` constructs the directional first derivative and Hessian from an
immutable local copy `et0`, then overwrites module `et` with `et0 + qCq`, where
`qCq = Q^T H Q / 8`. Its velocity shift is linear in Q and `d2_et=qCq` is
quadratic. For fixed bands and direction, those primitive contractions can be
scaled algebraically. This observation is about the implemented finite-difference
approximation, not exact shifted band energies.

The fresh-state path subsequently runs DOS interpolation using the shifted `et`.
`compute_dosk` weights derivative arrays with energy-resolved DOS, interpolates,
symmetrizes and divides by DOS. `compute_d3k` selects active energy states using a
DOS threshold and `store_d3k` assigns xi, dk, indices and derivative averages.
The two grids use shifts zero and one half. Consequently changing Q can change
interpolation weights, averages, active counts and ordering, even though the
primitive derivatives have simple scaling.

## Consequence for an accessible response workflow

Caching immutable band energies plus primitive derivative tensors is a plausible
preparation optimization. Reusing the final assigned response state unchanged
across Q is a separate approximation and has not been qualified. Matching grids
and state indices is necessary before transferring a saved gap. An energy- or
band-dependent gap may require controlled remapping and a new solution.

Do not repeatedly call the initializer against already shifted `et`: the routine
copies its current contents, and its derivative arrays are also allocated anew.
A new-Q implementation must restore immutable bands and manage array ownership.
No production cache or restoration patch has been implemented here.

Temperature reuse at fixed Q is structurally different: thermal occupations and
the converged gap change, while the geometry preparation may remain compatible.
That does not prove temperature independence of every interaction/kernel object.
Each cache requires explicit keys for physical inputs, approximation, grid,
source revision and numerical settings, supported by an invalidation test.

This trace rejects a simplistic speedup thesis; it does not establish that a
properly designed reuse scheme is unhelpful. Measure the preparation fraction
and remapping error before implementing one.
