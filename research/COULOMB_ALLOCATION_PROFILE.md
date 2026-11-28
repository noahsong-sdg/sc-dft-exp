# Allocation overhead in the current full native checker

Two one-second, read-only macOS stack samples of the owned full-gap003 solver
identify a concrete optimization candidate. No live sources, executable, inputs,
or runtime policy were changed. These samples do not establish a whole-run
timing fraction, a speedup, or the cause of host memory pressure.

Evidence is in `solver_profile001/`: timestamped call-graph excerpts, their
manifest, and exact executable disassembly around allocation/deallocation.
The native executable SHA256 is
`26aeeb8034a2ac34e77d991b46b0990540f926cb3d87f70e15e2502f220df5f3`.

| Observation | Sample 1 | Sample 2 |
|---|---:|---:|
| All sampled main-thread stacks | 90 | 91 |
| Stacks inside cached Coulomb calculation, inclusive | 52 | 61 |
| Within its allocation/free descendants | 12 | 20 |
| Reported physical footprint | 883.2 MiB | 883.2 MiB |

The first sample was taken at20:43:29PST and the second at20:46:42PST on
27November2026. Samples are short and correlated. Dividing these counts gives
sample proportions, not an independently measured fraction of total runtime.
RSS and physical footprint are different accounting measures; a lower RSS
snapshot alone does not demonstrate a reduction in allocated workspace.

## Traced execution path and cause

`full_nonlinear_probe.run_full_map` calls `tiled_operator.build_tile`, which
calls `cached_kel.calc_Kel_cached` once for each left/right state pair.
Its automatic work arrays `Vc1(nmf)` and `mf1(nmf)` have runtime-dependent size.
The exact executable prologue calls `malloc` twice with an allocation size
derived from `nmf`; its return path calls `free` twice. The assembly addresses
match the allocation/free offsets in the live samples. Both buffers are
allocated before the cache lookup, including on a cache hit.

In simple terms, every pair evaluation asks the allocator for two tiny buffers
and gives them back immediately. At this context's nmf10, their combined payload
is only160bytes per call. This is repeated allocation overhead, not an identified
large retained-memory leak. There are66867×67940=4,542,943,980pair evaluations
in a complete map. This count is derived from dimensions, not measured calls.

## Smallest candidate and required evidence

After the current frozen run terminates, test a separately versioned build that
reuses two context-sized scratch arrays. Keep the same MATMUL/DOT_PRODUCT and
evaluation order; invalidate/resize scratch with the existing context lifecycle.
The present tiled path is serial, and the module already maintains mutable
cache state. Any proposed reuse must explicitly retain that scope rather than
claim new thread safety. Inspect all callers before implementation.

This is preferable as a first experiment to reordering the Coulomb contraction,
which changes rounding, or enlarging unrelated caches without measured benefit.
A compiler stack-allocation flag is another possibility, but applies an
unbounded runtime-sized stack requirement unless carefully scoped. No alternative
has been benchmarked, and no optimality or production adoption is claimed.

Require direct upstream and original-cache comparisons, cache hit/miss/collision
cases, changed coefficient and weight vectors, resized/changed contexts, and
assembly evidence that the per-pair allocations disappeared. Then compare a
bounded actual-input tile with identical outputs before using the variant in
another full evaluation. Charge native qualification to the campaign ledger.
No new native run or budget expansion is admitted by this note.

## Verification and scientific limits

Both `/usr/bin/sample PID 1 10 -file PATH` commands exited0. `/usr/bin/otool -tvV`
read the pinned executable; the published excerpt contains its prologue and free
call neighborhoods. Full call graphs are retained through their summary tables;
the unrelated binary-image inventory is omitted and the original file hashes
are recorded. No solver implementation changed, so the existing193-test,
198-source-compilation and moment-refinement gate remains the applicable code
check. Profiling does not accept the full gap, conditioning, or physical response.
