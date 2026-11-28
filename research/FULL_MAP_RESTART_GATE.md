# Ordered full-map restart qualification

The pressure-stopped full-gap003 run completed44064/66867rows but produced no
final map. The owning `full_nonlinear_probe.run_full_map` retained all four image
batches in RAM until every left row finished. A progress log contains row counts,
not the right-side partial sums, so it cannot reconstruct or resume that work.
In simple terms, the solver lost its working answer when the guard stopped it.

The versioned `full_nonlinear_checkpoint_probe.f90` keeps the same module/API and
the frozen weight construction,32-row tiles, DGEMV calls, explicit-sum checks,
normalization, finite-difference test and final binary format. It adds ordered
segment controls and an unnormalized checkpoint. The original source and all
old manifests remain unchanged. A fresh build must explicitly select the variant;
the existing full-link makefile does not do so.

## State and boundaries

`full-map-segment.in` has exactly these lines:

```text
ordered-full-map-control-v1
<64 lowercase hex evaluation identity>
<qualified predecessor directory, or - for a fresh start>
<completed left rows> <last left row for this segment>
segment
```

A fresh start requires completed0 and predecessor `-`; a restart requires a
predecessor and completed>0. Restart boundaries and intermediate endpoints must
be multiples of32, preserving the original tile partition and floating-point
accumulation order. The last segment may end at the full left-state count.
Missing/stale state is an error. There is no automatic restart or retry.

The checkpoint contains:

- The existing ordered-linear-image schema for all four unnormalized batches,
  including completed rows, counts, beta and evaluation identity.
- A separate versioned full-map metadata file with exact derivative step,
  accumulated explicit-sum discrepancy and cumulative kernel CPU time.
- Exact active-state gap, xi, dk, Z and all four weight arrays, in that order.
  Inactive padding is set to zero for the state binding.

On restart, the native reader compares every bound state bit and rejects changed
context, temperature, dimensions, row range, finite-state data, payload size,
step, or invalid diagnostics. The prospective evaluation identity must also bind
the candidate, operator inputs, source/build and geometry/Z provenance; runtime
array equality alone cannot identify changed kernel interactions. Any stager must
derive that identity from immutable content and pin all predecessor outputs.
The guard and independent certifier must require a terminal PASS receipt; files
from an interrupted/failed writer are never accepted merely because they exist.

Only complete left-row coverage emits `full-map.txt/bin`. Intermediate output
is a partial sum, not an accepted gap or residual. Normalization and subtraction
of the seed happen once, after all rows. Diagnostic errors are carried by maximum
and CPU time by addition across segments. The existing stationary thresholds
and separate conditioning/response gates remain unchanged.

The optional `qualify` control instead requires a fresh1:64row experiment. It
compares continuous64rows against32rows, persisted/reloaded state, cache reset,
and the next32rows. All four images must agree bitwise. A fresh `split/` directory
must exist. It writes only a checkpoint, never a final full-map result.

## Why this split

This is a reliability fix, not a memory reduction or a speedup. It bounds how much
completed work is lost on a host-pressure stop, while preserving the operator and
sum order. Repeated full replays have already failed. Weakening the pressure rule
would violate the user's laptop-usage constraint. A bounded Coulomb accessor
could substantially reduce retained memory but is a larger independent change,
with its own IO/symmetry/equality qualification; see NATIVE_MEMORY_ACCOUNTING.md.
Do not mix it or the profiled work-array optimization into this change.

The additional checkpoint payload at current counts is13,044,480bytes, excluding
small metadata. State-binding scratch is8,696,320bytes and exists only during
read/write; it is not retained through kernel accumulation. These are source
shape calculations, not measured peak RSS or file-cache pressure.

## Current evidence and next gate

Four native regression tests compile the frozen and versioned routines with
independent rectangular kernel stubs. Continuous execution and three separate
processes over1:32,33:64,65:67 produce byte-identical final binaries; all summary
fields except CPU time match. The last short tile and inactive left padding are
covered. Internal split qualification also passes. Persisted stale/pre-migration
schema, changed active gap/xi/dk/Z/weights/beta, context, discontinuous boundaries,
truncation, changed state bits, nonfinite images, invalid diagnostics and trailing
control/metadata are rejected. Narrow suite:4tests PASS3.634s.

Actual microscopic-input compilation, split equality, strict hash/readback
certification and production segments remain pending. No full residual is accepted,
no native launch is admitted by this document, and the5h pilot is not expanded.

Final offline gate: `python3.13 -m unittest discover -s research -p 'test_*.py' -v`
passed202tests in24.247s, including both owning native implementations and
stale-parent build staging. All203maintained Python sources compile;
`python3.13 research/moment_refinement.py` exited0; `git diff --check` passed.
No separate configured typecheck. Native fixture builds use gfortran-O2,
-fcheck=all and-ffp-contract=off.

One source-only build is separately admitted in RESEARCH_LEDGER.md. Its
prospective manifest is portable_full_checkpoint_build001_manifest.json.
It selects full_checkpoint_link.mk explicitly, retaining the public QE/SCTK
source-only archive/interface inventory and unchanged902cache controls.
This build admission does not launch the full microscopic solver.
