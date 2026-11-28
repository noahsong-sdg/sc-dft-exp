# Ordered complete-P pass and strict checkpoints

The first-pass algebra accumulates P=Q^T D A. Each native left tile writes its
left-column P block once and adds contributions to **all** right columns. A
restart that restores only the most recent left block loses the right-side
history. Restarting under different Q/D/weights/Z/kernel context mixes operators.
The existing in-process tile counter cannot protect persisted state by itself.

The separate compact_p_checkpoint module stores the complete rank-by-active P,
completed left-row count, dimensions/rank, a64hex context fingerprint and two
cumulative CPU counters. Metadata is versioned, size-bounded and rejects extra
records/fields, noncanonical integer syntax (including Fortran slash/null tokens),
stale dimensions/coverage/identity and nonfinite or negative timings. Binary size
is checked before reading, all values must be finite and every unvisited left P
column must be zero. Boundaries must be native32-row endpoints except the actual
last row. An initial zero-coverage checkpoint must have zero P and CPU. Writers
require fresh metadata and binary paths; an incomplete write has no accepted
owning receipt and is never an automatic restart source.

The native pass is a new source variant, preserving the frozen selected-tile
producer and results. It retains the original initialized driver, compact native
field and normalized-D checks, finite-T weights and original32-row build_tile.
It restores P/cumulative CPU only from the exact declared predecessor and resumes
at completed+1. Coverage must increase and end on a valid tile boundary; only the
actual final row can produce a complete P. Progress is flushed at bounded row
intervals. It writes no coefficient matrix or defect norm.

Qualification mode computes continuous rows1:64, then independently resets caches,
computes1:32, writes/reads the checkpoint, resets caches and computes33:64. Every
P entry must have identical binary64 bits. A qualification record retains both
continuous and replay CPU counters; the final checkpoint carries continuous CPU.
The future owning receipt must charge **all** actual work, including replay.
These CPU counters never substitute for guarded wall cost. Generic segment mode
also supports the final short tile.

The fingerprint is opaque to native I/O: a future owning manifest must derive it
from the actual P dependencies (Q, D, native state/linear weights/Z/kernel inputs,
producer/compiler/library and normalization convention) and bind parent/output
hashes separately. Counts or a caller-supplied label alone are insufficient. P
has no U/W dependency; changing those inverse factors does not mathematically
require another kernel first pass, although the inverse and provenance gates must
still be revalidated. This source slice does not yet implement that manifest
protocol or admit reuse. Full second-pass kernel identity/replay and outward
rounding/radius controls remain separate requirements.

Regression fixtures compile the real checkpoint, core and pass driver. The
checkpoint test uses35left/39right/rank3: continuous versus32+3restart matches
bitwise and every P entry matches the independent exact dense oracle. The pass
fixture obtains D from the actual frozen inverse producer, uses65left/67right,
qualifies32+32, then restarts for the final one-row tile. Its complete P equals
continuous65rows bitwise and all396entries agree with separate Fraction sums.
Stale persisted metadata, schema/context/coverage/shape, nonfinite values,
untouched-column changes and invalid owner transitions fail. These are synthetic
native modules; material cache/restart behavior still needs a fresh source build
and guarded material qualification.

This is a source-only checkpoint. No new material run or budget expansion is
admitted. Current charge21409.829897628948s/21600 leaves190.17010237105205s.
The goal prompt permits a documented measured scientific-value expansion, but
no automatic increase or full-pass admission follows from these fixture results.
The full superconducting response objective remains incomplete.

Final verification:

- `/opt/homebrew/opt/python@3.13/bin/python3.13 -m unittest discover -s research -p 'test_compact_p*.py' -v`:5PASS4.700s; actual checkpoint/core/pass compile and execute.
- `/opt/homebrew/opt/python@3.13/bin/python3.13 -m unittest discover -s research -p 'test_*.py'`:297PASS45.185s, after final source edits.
- Python `compile` over271maintained research/*.py files:PASS.
- `/opt/homebrew/opt/python@3.13/bin/python3.13 research/moment_refinement.py`:exit0.
- `git diff --check`:PASS. No separate configured typecheck.

Three Fortran files and the make variant total357lines, including the synthetic
fixture. P payload remains rank-by-active (55MB at current Nb dimensions), not a
dense active-by-active matrix. New material runtime/RSS remain unmeasured.

## Ordered-P source build and dependency binding

The new compact_p_build.py is a separate owning source variant: the earlier
compact_tile_build.py and its pinned selected-tile outputs remain unchanged. It
requires the checkpoint and ordered-pass sources in addition to reader/core,
checks the exact dry plan/compiler console, local fresh objects and pinned
archives, explicit SDK-first link, both executables,902cache controls and final
input equality. Actual staged plan has19compiles and577pins.

compact_p_context.py hashes the explicit P dependencies: Q and the five compact
state columns, native grid/counts/beta, operator/candidate identities, executable
and SDK content identities, platform and normalization convention. Paths are
excluded from content identity so relocation alone does not invalidate P. Beta
is encoded as exact binary64 hex. Changed Q/D/state/operator/executable/library
inputs invalidate the fingerprint; changed U/W do not. The helper is not a parent
validator: its caller must validate receipts/pins and the relationship between
those supplied descriptors and the accepted artifacts. No material reuse or
restart is accepted by a fingerprint alone.

Four new regression tests check missing/duplicate checkpoint compilation, owner,
stale object, console/cache and final-pin failures; dependency changes, relocation,
U/W independence and stale shape/context rejection. Narrow P-related suite9PASS
4.817s; full suite301PASS44.966s;275Python compilationsPASS; actual Fortran
fixtures compile/executePASS; moment refinement exit0; diffcheckPASS. No separate
configured typecheck. Source build001 admits60s only,120quiet seconds,3GiB caps,
no kernels. Before launch21409.829897628948s/21600 leaves190.17010237105205s;
worst60s leaves130.17010237105205s. No budget increase or full sweep admitted.
[Manifest](compact_p_build001_manifest.json).
