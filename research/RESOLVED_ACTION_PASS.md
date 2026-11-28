# Nine-input joint-action variant

The original resolved training rule now supplies9trial inputs; the first3are
bitwise unchanged. To test a60-column inverse, missing full A actions and9extra
projection rows must be computed. This native variant keeps the original
operator/state/normalization/kernel orientations and uses the frozen checked
accumulation core, whose input-rank boundary already permits up to13columns.

Only the native trial count changes3to9 and saved complete held-out rows change
to the prospectively registered set. New sources/Makefile/build owner are distinct
from frozen three-input producers. Existing binaries/outputs stay unchanged.
Control binary sizes and metadata explicitly require9trial columns; old3-column
payloads/consumers cannot pass the new shape checks. Kernel sampling retains
training1/32/64 and fresh held-out left66/16717/50150,right2/16985/50955. Fixture
indices use the same geometry formulas, clamping66to the smaller fixture's end.

resolved_action_readback.py checks9-column action/P shapes, all saved row-action
controls and81bilinear identities. It preserves finite/state-ID/progress/CPU/
zero-unvisited boundaries. These are arithmetic checks with shared inputs, not
independent physical validation. Full inverse and uncertainty gates remain open.

Real native fixtures compare every9-column A/P component with a separately
formed dense nonsymmetric operator for partial64/full65 and final1-row tiles.
All saved kernel entries, corruption/stale shape/control, owner/plan/cache/pin
boundaries are tested. Build recipe freshly compiles19sources and links two
executables against pinned public libraries/Accelerate, with902cache controls.
No historical custom objects or n*n arrays.

## Prospective source build001 only

571pins, raw/resolved-action-build-001,60s build cap,120continuous normal-pressure
seconds,3GiB group/workspace. Priorcharged22596.58254421208s/25200 leaves
2603.4174557879196s; worst60 leaves2543.4174557879196s. Parent stage/plan
0.3315680418163538s separate workflow cost. Old same19-source variant built in
3.75s; actual new build time unmeasured. No native material kernels in this build.
Stop on guard/changed inputs/plan-console/cache failure; no automatic retry,
material pass or resource expansion. Brave/Docker/other study untouched.
A selected material pilot and independent output checks remain necessary before
separate complete-pass admission. Trial buffers add about26MB vs3-input variant;
this is allocation arithmetic, not a measured RSS claim.

Final336testsPASS56.762s incl native builds;315Python sources compilePASS;
moment_refinement exit0; diffcheckPASS. No separate configured typecheck.
Resolved-preparation result1da2cb0 CI46151611559PASS.

## Source build001 accepted; selected pilot prospective admission

Build terminalPASS3.7302835416048765s, maxindividual133152768B (~126.98MiB),
sampled group70107136B.571staged/614accepted closure pins, exact consumed
manifest/receipt/watcher and37output identities checked.19fresh compiles,2links,
exact plan/console and902cache controls PASS. [Build result](resolved_action_build001_result.json).
Source2a065ba CI46151799590PASS. No material kernels in that build.

New resolved_action_material.py accepts the training-only9-input preparation,
requires6newcolumns/bitwise oldprefix, validates the fresh build and frozen
native input lineage, and owns only64rows with explicit partial outputs. It
runs the9-input reader and final input/manifest checks inside the guard. No
new inverse, changed physics, altered heldouts or full pass is admitted.

Admit selected material001 only, raw/resolved-action-material-001,1929pins,
90s/quiet120/3GiB. Currentcharged22600.312827753685s/25200 leaves2599.6871722463147s;
worst90 leaves2509.6871722463147s. Parentstage2.1480775829404593s separate workflow
cost. Prior3-input pilot33.78s/948.05MiB supports this bounded pilot; actual
9-input memory/runtime are unmeasured. Expect54saved-row action controls and
81bilinear checks at the actual geometry, with zero unvisited regions and no
complete_A_and_P claim. Stop on guard/provenance/numeric failure; no automatic
retry, complete pass, inverse adoption or budget expansion. Brave/other study
untouched. Owner regressions cover stale outputs/cwd/console/final pin changes.

Pilot source gate337testsPASS54.941s incl native builds;317Python sources
compilePASS; moment_refinement exit0; diffcheckPASS. No separate typecheck.
