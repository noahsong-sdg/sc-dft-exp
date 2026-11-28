# Native memory reduction decision after the pressure stops

The frozen native path peaks below1GiB individual RSS in the latest failed
attempts, but still fails the global host-pressure policy. This does not prove
that this process caused the host-pressure transition. User-active applications
and the other study must remain untouched. A normal launch interval has not
proved sufficient to finish a segment. No further native retry is admitted.

The source-bound accounting in native_memory_accounting001_result.json follows
`read_saved_coulomb -> read_pairing_files -> Vc0 -> ensure_slab -> build_tile`.
The driver then performs16DGEMVs and verifies serialized checkpoint readback.
Registered binary64 array sizes are:

| Allocation | Formula in bytes | MiB |
|---|---|---:|
| Compact Coulomb Vc0 |8*10*26*26*512*26|686.5625|
| One expanded Coulomb slab |8*10*26*26*512|26.40625|
|32-row two-sided kernel tile |8*67940*32*2|33.173828125|
|16-vector verification baseline |8*67940*2*16|16.5869140625|

These are array-shape sizes, not measured simultaneous resident memory or an
additive physical-memory budget. Other arrays, transient reads, compiler
copies, shared mappings and compression are not included. Input reading already
streams one original q-file at a time, but retains all transformed pairing
coefficients in the686.6MiB array. The slab interface subsequently requires
those coefficients throughout the kernel calculation; they cannot simply be
freed after initialization. Both energy-side actions depend on this path.

Delaying the baseline allocation could save16.6MiB during accumulation, but
that array is needed later for the existing bitwise checkpoint test. Reducing
tile width from32 to16 saves16.6MiB of tile storage. It changes DGEMV partitioning
and may alter rounding or performance, requiring qualification. Neither is an
evidence-backed solution to the unstable global resource window. No patch is
made merely to claim an optimization.

A substantial internal reduction would require bounded residency of the
transformed Coulomb table. This is architecture work rather than a local array
cleanup. If host availability remains limiting, use reviewable slices:

1. Produce a transformed, hash-bound, read-only coefficient artifact with bounded
   conversion memory. Preserve every original header/channel transformation and
   whole-input hash. Reject truncated/stale contexts before consuming it.
2. Add a bounded coefficient accessor to the slab path; test that every selected
   coefficient and expanded slab agrees bitwise with the resident implementation,
   including symmetry averaging, spin-channel and context boundaries. A mapped
   file alone does not prove low physical residency: measure working set and
   repeated-access costs before choosing that implementation.
3. Qualify actual ordered kernel images, checkpoint continuation and uncached
   native sums before replacing the production path. Record setup, disk and
   failure costs; stay inside workspace/resource caps. A lower allocation count
   alone is not a speedup or scientific acceptance.

This proposal is not permission to silently change pinned native sources or
existing manifests. New source/build/run identities and a bounded scientific-value
admission are required. There is currently no measured cost/memory result for a
replacement accessor. The remaining initial pilot1096.2261117064954s cannot
cover the previously selected three420s ceilings. A future run must explicitly
revise its bounded admission or justify a campaign budget expansion; it cannot
reuse the old numerical budget arithmetic.
