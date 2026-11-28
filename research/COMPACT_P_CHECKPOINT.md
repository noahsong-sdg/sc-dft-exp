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

Ordered-P build001 now terminalPASS3.6561458753421903s, maxindividual
133152768B (~126.98MiB), sampled group68927488B. All577pins,19fresh compiles,
37outputs, exact source-plan/compiler prefix and902cache controls checked.
[Build result](compact_p_build001_result.json). Source/admission77e3c16 public
CI46141075791PASS. No material P-pass or restart accepted by a successful build.

The actual accepted Q/state/executable/SDK files now register P context
43be64148f45cab2975254ad80a543945a60423745b226bdbf77a09b8cf79cca.
[Registration](compact_p_context001.json) records exact derivation fields,
content identities, source helper identity and accepted preparation/build result
identities. This registration validates both parents and input hashes, not native
restart behavior; those flags remain false. Registration is preflight hashing
separate from guarded native cost. A future owning qualification must pin this
registration, recompute it from accepted inputs and bind the checkpoint outputs.
Charged total21413.48604350429s/21600;186.51395649570986s remain. No budget expansion.

## Streaming independent checkpoint readback

`compact_p_readback.py` now checks the persisted native metadata and P payload
without allocating either complete matrix. It scans binary64 values in blocks of
at most512KiB, verifies dimensions/rank/coverage/context, timing syntax, finite
values, exact byte count and zero unvisited left columns. Qualification additionally
checks the continuous/split records and cumulative timing relationship, and requires
an externally accepted partial-P SHA256. This last comparison detects finite
corruption in already visited entries that metadata and finiteness cannot detect.
The accepted hash must come from a separately validated parent result, never from
the new checkpoint itself. The split output still needs its owning output hash
and native replay record; the Python reader cannot independently reconstruct the
native replay from a32-row payload alone.

This closes a readback component, not material admission: the helper does not
validate guard receipts, input closures or executable/control provenance, and
returns no terminal acceptance flag. Its future owning qualifier must perform
those checks and recompute the registered dependency fingerprint. Keeping these
responsibilities explicit preserves the immutable earlier native producers and
avoids loading two55MB P arrays merely to compare them. Actual readback RSS has
not been measured. Public build/context commit580a7c7 CI46141345023PASS.

Three new regression tests cover stale persisted metadata/schema/shape/context,
Fortran slash tokens, overflowing timings, nonfinite data, changed unvisited
columns, initial/final short-tile rules and finite visited-entry corruption against
an accepted hash. Targeted3PASS0.004s. No material run or budget expansion;
charged native total21413.48604350429s/21600 remains unchanged.
Final gate for this readback source:304testsPASS47.727s,277Python compilations
PASS, actual native fixture builds/runsPASS via full suite, moment_refinement.py
exit0, git diff --check PASS. No separate configured typecheck.

## Owning material restart qualification admission001

`compact_p_material.py` connects the strict readback to accepted provenance. The
prior fixture/readback alone left a real acceptance gap: a valid-looking persisted
matrix could belong to a different executable or operator, and a self-reported
replay claim could describe a different partial P. The owner replays the earlier
selected-material independent controls, validates preparation/build receipts and
closures, requires the19-compile ordered-P build with902cache controls, recomputes
the registered dependencies from the actual bound files and verifies registration
producer/parent identities. It stages fresh copies and exact controls for the
continuous64 versus checkpoint32+32 native qualifier. No old pinned source changes.

Postread requires exact consumed manifest, parent closure, executable/input copies,
controls, guard receipt, terminal watcher, native marker and independent streaming
readback against the previously accepted selected-material P hash. All six produced
checkpoint/qualification/progress outputs are content-bound for prospective reuse.
The qualification record is from the validated native executable; the streaming
reader independently verifies continuous output identity and checkpoint invariants.
This tests actual cache reset/restart, not a complete P pass or operator norm.

Two new tests check registration/file identity, build gates, fresh control staging,
accepted receipt and stale over-budget receipt, plus finite persisted-P corruption.
Targeted2PASS0.030s. Preflight real parents reproduce registered fingerprint
43be64148f45cab2975254ad80a543945a60423745b226bdbf77a09b8cf79cca.
Admission001:90s guarded native wall,120continuous normal-pressure seconds before
launch,3GiB process-group/workspace caps, one owner, original32-row native tiles.
Before launch21413.48604350429s/21600 leaves186.51395649570986s; worst90s leaves
96.51395649570986s. The full guarded wall includes both continuous and replay
work. Parent hashing/independent postread remain separate workflow costs. No
budget expansion/full-sweep admission. Brave and the separate study stay untouched.
Final source gate:306testsPASS43.509s;279Python compilationsPASS; actual Fortran
fixture builds/runsPASS via full suite; moment_refinement.py exit0; diffcheckPASS.
No separate configured typecheck. Actual staged manifest has1735pins, native
counts66867/67940/rank51 and exact registered fingerprint.

Material qualifier001 now terminalPASS30.05208083288744s, maxindividual
1076133888B (~1026.28MiB), sampled group1041268736B. The actual native
continuous64 versus checkpoint32+32 comparison passed every binary64 bit.
Independent readback verified1735pins, exact consumed manifest/receipt/watcher,
registered context, six output identities, finite/untouched-column invariants and
continuous64 SHA25646131b24daf1d2f98d72f59b54cf22fcdf8af52821ffe76cdcca94c7682cb035
against the accepted selected-material output: all6,875,157entries identical.
Continuous kernel/contraction CPU0.4446070000000013/0.03196799999999911s;
replay0.46574799999999783/0.030307000000000528s. These section timers do not
replace30.052s guarded cost. Readback14.913044875022024s/55492608B
(~52.92MiB) is separate workflow cost. [Result](compact_p_material001_result.json).
Source/admission8a3a29c public CI46142133013PASS.
Charge21443.538124337178s/21600;156.461875662822s remain. All owners terminal.
Material restart for these two native tiles is now qualified; complete P, second
pass, full norm/radius, conditioned gap error and physical response remain open.
No budget expansion or full sweep follows automatically from this result.
