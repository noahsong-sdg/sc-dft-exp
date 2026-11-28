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
