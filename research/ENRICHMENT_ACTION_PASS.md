# Joint interaction-action and extra-projection pass

The chosen inverse fails the selected complete-row contraction test. Saved-row
spectrum and derivative-mapped preparation identify three trial inputs almost
outside old Q. Their full interaction actions are missing; without them there
is no justified augmented inverse. This variant computes A*trial and
trial^T*D*A from the same ordered kernel tiles, avoiding a separate kernel pass
for the extra projection rows. It is a diagnostic step toward conditioning,
not an accepted gap-error bound or physical response.

## Execution path

Fresh full driver/native initialization, unchanged strict compact state reader,
then enrichment_action_native_pass.f90. It checks delta/xi/dk/Z against the
initialized native state and independently recomputes normalized occupation D.
It reads exactly three finite trial columns, and processes32-row tiles in order,
including the final short tile. enrichment_action_core.f90 reuses the existing
checked projection accumulator and applies each orientation separately:
A01=-K1^T*w_right/(1+Zleft), A10=-K2*w_left/(1+Zright).
A01 writes current left output rows; A10 accumulates right output rows.
Full action storage is n*3, extra P is3*n. No n*n array or stored full kernel.
U/W are released after context validation. Old Q is released after trial input
loading; the production context, old basis/inverse and existing outputs are untouched.

The pass retains the fixed training/held-out K1 rows1/32/64/65/33434/66867 and
full K2 rows1/33970/67940, with corresponding geometry-derived indices in fixtures.
Partial64-row outputs explicitly remain incomplete, including zero unvisited
sample rows. Future material acceptance must enforce exact coverage and verify
those samples independently; merely seeing the terminal marker is insufficient.

## Evidence and boundaries

Real native fixtures compare every component of both A*trial and trial^T*D*A
against a separately formed dense nonsymmetric operator, using nonuniform D,
weights and Z, both64-row partial and65-row full coverage and a final1-row tile.
All saved sample kernels are checked entrywise. Trailing controls, wrong rank,
split end and stale trial payload are rejected. Source build-owner fixtures
reject missing/duplicate source commands, stale objects, changed pins, wrong
cwd, mismatched build console and incomplete cache checks.

Fresh enrichment_action_link.mk source-links19compiles/2executables, explicitly
binding the pinned Mac Accelerate SDK before public static reference archives.
Inherited source-only public libraries and902bitwise cache controls are required.
No historical custom objects/modules are linked. New build owner is a distinct
variant of the frozen prior build path; no pinned producer was edited.

## Prospective build001 admission

One60s build owner in raw/enrichment-action-build-001,571pins,
120continuous normal-pressure seconds,3GiB group/workspace cap. Prior charged
21999.40743792042s/25200 leaves3200.592562079579s; worst60 leaves3140.592562079579s.
Parent validation/stage0.19919287506490946s separate workflow cost. No material
kernels or inverse adoption in this build. Stop on guard/input/plan/cache failure;
no automatic retry, full material pass or budget expansion. Brave/other study
untouched. Future selected material pilot and independent readback required.

Final source gate327testsPASS53.213s including actual native fixture builds;
300maintained Python sources compilePASS; moment_refinement exit0; diffcheckPASS.
No separately configured typecheck. New non-test executable/build code306lines.

## Accepted source build001

TerminalPASS3.7499855835922062s, maxindividual133201920B (~127.03MiB), sampled
group46366720B (short compiler peak missed). All571staged/614accepted closure
pins, exact consumed manifest/receipt/watcher and37output identities checked.
19fresh compiles,2links,902cache controls PASS, exact build plan equals console.
[Result](enrichment_action_build001_result.json). Sourcec888baf CI46148038612PASS.
No material kernel executed. Charged22003.157423504013s/25200 leaves
3196.8425764959866s. All owners terminal. No retry or material pass admitted.

Next implement independent material checks on complete saved A rows and
Pextra*trial = trial^T*D*(A*trial), with scalar fsum and cancellation-aware
bounds, plus state/D/provenance/coverage/finite-output checks. Then stage a
selected64-row material pilot before considering the separately admitted full
pass. Partial action/P outputs must remain explicitly partial. Shared-kernel
bilinear consistency is an arithmetic check, not independent physical evidence.

## Selected material001 prospective admission

New enrichment_action_material.py verifies accepted trial-preparation and source
build receipts/output identities and their merged closure, preserves copied native
inputs, and stages exactly64rows in a fresh root. It owns the native subprocess
with all three thread environment variables set to one, requires exact partial
console coverage and runs independent readback before final pin checks.

enrichment_action_readback.py enforces versioned metadata, exact state identities,
finite binary sizes, ordered progress and cumulative CPU, zero unvisited left
A/P and K2 sample regions. Scalar fsum independently reproduces selected complete
left A*trial rows and selected right rows over the processed64columns. Nine
bilinear controls compare Pextra*trial with trial^T*D*(A*trial), using bounds
scaled by the sum of absolute terms on both sides. Shared kernels mean this is
an arithmetic consistency check, not an independent physical/operator derivation.
Native fixtures compare every A/P component against the dense oracle separately.
Corruption controls alter action/P/kernel payloads and persisted metadata; owner
controls reject wrong cwd, stale output, changed input pins and console mismatch.

One90s selected pilot in raw/enrichment-action-material-001,1921pins,
120continuous normal-pressure seconds,3GiB cap. Current charged22003.157423504013s
of25200 leaves3196.8425764959866s; worst90 leaves3106.8425764959866s. Parent
validation/stage2.815651709213853s separate workflow cost. Native execution and
numerical readback are both charged inside owner. Prior selected diagnostic took
29.40s near1.1GiB; this new combined path's actual runtime/memory are unmeasured.
Stop on any guard/provenance/coverage/control failure. No automatic retry,
full pass, new inverse or further budget expansion. Brave/other study untouched.

Pilot source gate328testsPASS53.222s,303Python sources compilePASS, native
fixture builds/moment_refinement/diffcheck PASS. Build result06cccbc
CI46148272267PASS. No separate configured typecheck.

## Accepted selected material001

TerminalPASS33.78485658345744s, individual peak994099200B (~948.05MiB), sampled
group906903552B. All1921staged/1933accepted closure pins, exact consumed manifest,
terminal receipt/watcher and six output hashes checked. [Result](enrichment_action_material001_result.json).
18scalar saved-row A-action controls and9bilinear P controls PASS;
maxerror7.112366251504909e-17, maxerror/bound7.064800253562975e-5.
Normalized derivative maxdifference4.440892098500626e-16. Native kernel/
contraction CPU0.44558999999999926/0.02290400000000048s are partial sections,
not whole-result timings. Native initialization dominates this64-row pilot.
All outputs finite; unvisited left actions/P and saved sample suffixes zero.
Exactly64rows: complete_A_and_P=false. No augmented inverse or physical response.
Sourcec080ec4 CI46148570348PASS.

Charged campaign22036.94228008747s/25200 leaves3163.057719912529s.
All owners terminal. Next separately implement/admit a complete ordered pass
using the same accepted binary, trial inputs and frozen contexts, enforcing all
66867left rows and fixed held-out kernel rows. Measured original complete P pass
506.08s supports a bounded900s forecast ceiling; this is not a measured full
joint-action runtime. A full result must pass all saved-row and bilinear checks,
finite/coverage/ownership/lineage and unchanged inputs. A later augmented inverse
must be tested on the fixed held-out rows before considering a full defect pass.
No full pass, retry or budget expansion admitted by this checkpoint.
