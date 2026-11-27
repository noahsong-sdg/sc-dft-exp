# Research restart ledger

## Current state — 2026-11-27 05:41 UTC

Active twelve-hour campaign; specification in PROJECT_SPEC.md. Previous turn
classification: progress (released finite-Q evidence traced). Current milestone:
durable specification and isolated public checkout created. No solver launched.

Next: pin upstream commit, implement bounded public retrieval and extraction;
analyze saved V3Si curves and reproduce author formulas with analytic controls.
Keep raw downloads ignored pending redistribution-rights review. Record hashes.

Native compute spent this campaign: 0 hours. Native pilot gate remains closed
until saved-data analysis identifies a consequential uncertainty. Full scope
remains active; neither demand nor laptop feasibility has been established.

## 2026-11-27 05:44 UTC checkpoint

Specification published in main commit 4eafc82. Retrieved seven public V3Si
curves plus original extraction/plot scripts; bounded fetch prints hashes.
Implemented deterministic analysis and three analytic/input-validation tests.
All three passed. No native compute. Current public processed data plus author
formula produces 184.44 nm at 1 K, versus published 97 nm: reproduction is NOT
established. Resolve provenance, units and protocol before interpreting window
sensitivity. Next: independently execute original formula, inspect xi.dat and
raw outputs, derive conversions and compare source revision/history.

## Conversion correction

The apparent 184.44 versus 97 nm discrepancy was our missing final plotting
factor 0.529177249, not a demonstrated release discrepancy. Corrected result is
approximately 97.60 nm. Archived xi.dat independently reports ll=1844.38 before
the plot's 0.1*0.529177249 conversion. Regression test now checks this external
reference. Window ratios are unaffected. Next: calculate peak-route conversion,
temperature dependence and physically justified small-Q fitting domains.

## Peak extraction and source concern

Archived xi.dat and fflo.gp independently yield peak-route lambda=177.09 nm at
1 K (xi3=40.8061 before Bohr conversion; sampled jdp=1.25867e-6). This does not
reproduce published 136 nm. Unlike the slope mismatch, its cause remains open.
Analyzer now reproduces this formula too, with an external-reference test.

Source inspection at pinned 4bc883e5 found a potentially consequential issue in
supercurrent's normal-reference algebra: its x_d expression uses tanhe in a
numerator where surrounding factors use tanhx, and the normal branch tests
xi**2+delta**2. Need derive expected normal subtraction and inspect historical
47c06501da8ffd574c87469ddd6d5a2814171796 before claiming a bug. Variables x_d
and d_x may have different roles; do not patch from superficial symmetry.

## Analytic identity progress

Independent shifted-tanh identity confirms two discrepancies in normal x_d:
regular numerator uses superconducting tanhe; saturated boundary includes gap.
Both occur in current and historical source. Added scalar reproducer and three
tests, including a saturation counterexample. See CURRENT_IDENTITY_FINDING.md.
Next gate: paper-equation mapping and minimal Fortran execution, then saved-state
effect. Do not attribute published observable differences to these factors yet.

## Native scalar validation

Standalone Fortran reproduction compiled/executed successfully with GNU
Fortran 16.2.0; nine total tests pass. Hardware rechecked: 32 GiB, 10 logical
CPUs. Native scalar probe uses under one second; no production solver allocation.
Current integrand couples x_d to sign(xi)*curvature, so cancellation under exact
particle-hole symmetry can suppress the effect. Need actual weighted states.
Next: compile the full pinned routine with lightweight modules, compare complete
current to direct identities on synthetic weighted states and normal limits;
then locate saved delta/state data for a material-specific fixed-state check.

## Complete upstream routine reproduced

Full pinned supercurrent fetched with SHA256 check, extracted unchanged and
compiled serially with fixture modules. Symmetric and normal controls pass at
upstream printed precision; asymmetric cases show integrated discrepancies.
Command: python3 research/full_current_probe.py (success). See finding table.
Public archive lists pwscf.scgap for V3Si, but whether this contains sufficient
xi/dxq/d2xq/weights for current replay remains unverified. Next inspect format,
byte size and source IO path before downloading or launching production.

## Saved-state compatibility result

Range/header and historical writer confirm public V3Si scgap has five floats
and omits required curvature d2xq. Current writer adds a sixth float. Replay
from scgap alone is not supported; explicit stale-schema rejection added.
See SAVED_STATE_AUDIT.md. No large download/native job. Heavy unrelated VM is
active; leave it alone. Next: validate narrowly corrected full routine against
direct identities, inspect state reconstruction path, then assess a lightweight
dump or regeneration pilot if justified and resources permit.

## Candidate correction validated

Full-routine harness now builds original and narrowly corrected variants;
both changed asymmetric results agree with direct identities at printed
precision, controls unchanged. Command succeeded. Curvature reconstruction
requires dense band finite differences plus energy-resolved interpolation and
state assignment; velocity-only replay is insufficient. Next: compile broad
parameter-grid validation (including near thresholds) and produce cost/response
figures; investigate a saved-state preparation-only route without kernel solve.
