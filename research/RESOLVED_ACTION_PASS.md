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
