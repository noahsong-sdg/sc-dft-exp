# Geometry controls for a reusable linear-response route

Two further guarded native preparations completed using the same executable,
microscopic inputs and numerical settings, changing only q_fflo:

| q_fflo first component | State counts | Wall seconds | Peak individual RSS bytes |
|---|---|---|---|
| .001 (attempt 005) | 62850 / 64662 | 49.783 | 199573504 |
| .0001 (attempt 006) | 62850 / 64662 | 51.631 | 113590272 |
| 0 (attempt 007) | 66867 / 67940 | 50.587 | 189956096 |

All receipts report PASS/exit 0 under the unchanged 120-second/3-GiB guard.
These are warm retained-input preparations, not cold-start electronic-structure
workflows. Session 19837 is terminal, with neither child nor watcher remaining.

The two nonzero-Q runs match all state indices in order. Their diagnostic
initial-gap analytic slopes differ by about 9e-6 relative, but some individual
normalized derivative coefficients differ appreciably. Matching counts alone
does not justify reusing every array. nb_geometry_limit_controls.json records
maximum differences; nb_preparation_small_q_diagnostic.json records the smaller-Q
state summary. No finite-Q gap was computed.

The fresh Q=0 preparation recovers the archived gap's exact counts and all
134807 ordered band/k indices; geometry differences are recorded in
nb_zero_q_alignment.json. Its response contractions are zero, as expected at
Q=0. The old gap's temperature/convergence remains unknown. This confirms a
practical Q=0 geometry reconstruction path, not an accepted physical restart.

The directional symmetry subgroup contains four operations for both nonzero-Q
controls; Q=0 uses 48. Scalar DOS symmetrization, energy shifts and support
thresholding precede state assignment. The controls support a directional-limit
versus exactly-zero-Q distinction; they do not individually attribute every
count difference to one of those operations.

## Next substantive method question

Source inspection finds another potential obstacle to accurate reusable linear
response. `compute_dosk` accumulates DOS-weighted first derivatives, then divides
by DOS. The current's small-Q expansion subsequently squares the resulting mean
derivative. A microscopic quadrature of that expansion instead involves the
second derivative moment, <a²>, when energy/gap are held within the same cell.
In general <a>² differs from <a²>. This is a coarsening/closure hypothesis, not
yet a diagnosed upstream bug: the intended approximation and convergence must
be checked before judging it.

A useful experiment would preserve both first and second velocity moments from
the same unshifted microscopic bands, then compare linear response at matched
gap and quadrature settings. An exactly reproduced old path is the control.
For anisotropic materials, tensor components and symmetry transformations must
be explicit; averaging signed directional velocities under the full zero-Q
group would erase useful information. A scalar fixed-direction shortcut must
not silently replace that tensor problem. Optimized tetrahedron contributions
also need a sign audit before invoking positive-weight variance arguments.

Acceptance requires agreement with a direct fine-grid reference, convergence
under energy/momentum refinement, correct normal cancellation and physical
normalization. This could connect reusable microscopic inputs to a scientifically
better observable, rather than just executing the old approximation faster.
No moment-preserving implementation or improved prediction is claimed yet.
