# Complete coverage before interpreting the correction

The explicit-step qualification proves restart behavior on64rows, not the
residual of the corrected material gap. `full_step_segments.py` is a separate
version of the ordered segment owner. It preserves recursive contiguous-row
lineage, immutable predecessor outputs, qualification origin, state equality,
nondecreasing diagnostics and complete left-row coverage before full readback.
It also carries the exact direction/step/preparation recipe into every segment.

At complete coverage, `verify_gap_candidate_step.py` uses the independently
step-bound summary reader and unchanged1e-10Ry/1e-5 residual thresholds. It uses
binary arrays and streamed hashes to avoid tuple-float payload expansion and
whole-file hashing allocations. No measured before/after RSS claim is made.
Independent normalization checks the saved base residual and native J action
against unnormalized checkpoint images. The saved plus/minus batches are then
normalized independently at d0±h*v, producing actual nonlinear residual
statistics at the proposed Newton correction and its negative. Both signs are
retained because an improved linear estimate alone does not verify the step.

These checks still cannot bound the unmeasured complement, prove full-space
conditioning or qualify physical response. The accepted base candidate is never
overwritten. A synthetic passing residual substituted into full-map output is
rejected against checkpoint normalization. Other tests cover native restart,
complete coverage, changed source step/image/receipt/result, invalid row/deadline
admission and perturbed residual/FD summaries. Native fixtures use the real
versioned driver; preparation certification is separately tested and mocked in
the small synthetic geometry. No microscopic production segment is admitted by
this document or by fixture success.

Final gate:255offline tests PASS36.891s, including native fixture compilation
and execution;245maintained Python sources compilePASS; moment_refinement exit0;
diffcheckPASS. No separate configured typecheck. Actual-input qualifier001
separately terminalPASS36.70167237473652s/931561472B,1533pins and native
continuous/restart equality verified. No production full-coverage claim yet.
