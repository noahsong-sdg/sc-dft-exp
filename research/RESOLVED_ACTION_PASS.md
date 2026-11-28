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

## Selected pilot accepted; complete pass admission

Pilot001 terminalPASS35.162074375431985s, maxindividual1019789312B
(~972.55MiB), sampledgroup927350784B.1929staged/1941closure pins, exact
receipt/watcher/output identities checked.54saved-row action and81bilinear
controls PASS, maxabsoluteerror1.3530843112619095e-16, maxerror/bound
7.064800253562975e-5; only64rows, complete_A_and_P=false.
[Result](resolved_action_material001_result.json). Sourcef2f9fac CI46152124120PASS.

A separate resolved_action_complete.py replays the accepted pilot checks,
requires identical compact state, nine trials, dimensions and binary, then
promotes a fresh control endpoint64to66867. It keeps the ordered kernel pass,
scalar readback and final input/manifest checks. Earlier producers stay frozen.
Owner regressions cover wrong cwd, stale outputs, incomplete console and changed
input pins; nine-input native fixtures already cover full/partial/final-short tiles.

Admit complete001 only,1950pins,900s/quiet120/3GiB, one heavy owner.
Charged22635.474902129117s/25200 leaves2564.525097870883s; worst900 leaves
1664.525097870883s. Separate parent stage6.06026658276096s. Prior3-input full
pass507.83s/967.67MiB and nine-input pilot35.16s/972.55MiB support this bounded
run; forecast roughly550s, actual full9runtime/RSS unmeasured. Expect all66867
left rows and81saved-action/81bilinear controls, no inverse adoption or physical
response. Stop on guard/provenance/numeric failure; no automatic retry, fullnorm
pass or budget expansion. Brave/Docker/separate study untouched.

Complete-owner final gate:338testsPASS56.945s including native fixture builds;
319Python sources compilePASS; moment_refinement exit0; git diff --check PASS.
No separate configured typecheck.

## Complete pass001 accepted

TerminalPASS507.71250912500545s, maxindividual1045757952B (~997.31MiB),
sampledgroup1053851648B (~1005.03MiB).1950staged/1962accepted closure pins,
receipt/watcher/exact manifest and all six output identities checked. All66867
left rows/final19-row tile covered, complete_A_and_P=true.81action/81bilinear
controls PASS, maxabsoluteerror1.97758476261356e-16, maxerror/bound
7.635352844779993e-5. Kernel/contraction CPU445.7703519999983/26.174540999999635s.
[Result](resolved_action_complete001_result.json). Source449248e CI46152668968PASS.
No inverse, full norm, gap radius or physical response accepted by this pass.
Charge23143.187411254123s/25200 leaves2056.812588745877s.
