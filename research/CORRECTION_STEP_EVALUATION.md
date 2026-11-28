# Bind correction preparation to native evaluation and restart

The declared-step native driver and arithmetic reader alone did not establish
which verified inverse correction a run consumed. A different direction/step
could pass arithmetic checks while answering a different question. The new
versioned evaluation schema binds the accepted preparation, candidate, source
build and their complete input closures. Frozen historical readers are unchanged.

`correction_direction_artifact.py` rechecks the guarded preparation's exact
producer, consumed manifest, terminal receipt, outputs and immutable upstream
inputs. It independently reconstructs correction/maxabs(correction), candidate
bytes, padding, step and normalization roundoff. The exhaustive inverse replay
remains in the original guarded preparation; it is not repeated at each segment.
This is reuse of checked immutable evidence, not a new inverse calculation.
It reads only the correction block, avoiding an additional full inverse-payload
allocation. Actual material preflight:2.7161237499676645s, process peak33521664B;
this is a separate inexpensive preflight, excluded from guarded-native wall.
No controlled before/after memory or speedup claim follows from that observation.

`stage_full_step_qualification.py` checks the exact declared-step builder and
pinned sources, its terminal build/902 cache controls, seed identity and accepted
preparation before creating a fresh root. The evaluation recipe uses
`declared-step-full-map-evaluation-v1`. It copies exact preparation payloads and
pins all ancestors and sources. It stages only; it does not launch anything.

`full_step_segment_analysis.py` checks the owning native receipt, evaluation
identity, ancestor pins and closure, exact prepared payload copies, source
candidate/geometry/Z, range and controls. The independent explicit-step reader
then checks all persisted state/occupation batches. Qualification requires the
native continuous64-versus-persisted32+32 equality assertion and matching state.
Partial output cannot be presented as a complete full residual. No physical
response or full-space conditioning flag is granted.

Regression controls include rehashed altered direction/candidate/step/roundoff,
stale receipt/deadline/consumed manifests, absent closure, changed preparation,
old schema, native checkpoint corruption, missing split marker, wrong source
builder and excessive recorded resource peaks. Native fixtures exercise the
real driver and checkpoint modules; artifact-evidence tests use synthetic data.
The evaluation fixture mocks only preparation certification, which is tested
separately. This is not a material qualification.

Final checks:251 offline tests PASS32.932s, including native fixture builds and
execution;242 maintained Python sources compilePASS; moment_refinement exit0;
diffcheckPASS. No separate configured typecheck. No new native job admitted here.
Guarded ledger remains20645.51788821336s/21600s,954.4821117866413s available.
Next publish a prospective actual-input qualifier before admission. Production
segment lineage and corrected residual certification remain to be connected.
