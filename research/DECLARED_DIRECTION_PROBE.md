# Candidate-bound full native direction

The fixed probe used for the accepted8.05K residual does not test the actual
compressed correction. Both its native implementation and independent checkpoint
reader construct a prescribed signed energy-dependent direction. Changing a
Python label would not change that mathematical test.

A separate source variant now loads direction-state.meta/bin before forming the
same four occupation/Jacobian batches. Kernel calls, accumulation order, finite
step1e-8Ry, original residual targets and normalization are unchanged. The
frozen full_nonlinear_checkpoint_probe.f90 and its reader are untouched. Native
fixtures verify equivalence to that source except the declared input, avoiding
an unrelated refactor of already-pinned scientific code.

Metadata is exactly four lines: declared-full-map-direction-v1; three counts
(left,right,maximum); finite beta;64hex operator context matching seed-control.in.
Binary contains the full padded candidate followed by the full padded direction,
both native binary64 Fortran order. Candidate must equal the loaded native gap
bit for bit, including signed zero. Direction must be finite, have unit infinity
norm and zero inactive padding. This representation allows a normalized actual
correction without overwriting the accepted gap. The normalization scale belongs
in the separately pinned preparation recipe; a unit direction alone does not
preserve the correction magnitude.

Native controls pass: declared old direction gives bitwise identical full output;
continuous and persisted32+remainder outputs match; a changed direction cannot
resume the prior checkpoint. A different signed direction matches independent
dense nonsymmetric Jacobian sums in both orientations. Stale temperature/operator/
counts/trailing metadata, truncated payload, candidate mismatch/signedzero,
nonfinite values, padding and zero/nonunit directions reject. These are arithmetic
and input controls, not microscopic material qualification.

The source-only build stages from the qualified full-checkpoint parent, verifies
its consumed manifest, owning guard/receipt/resource fields and902cache controls,
and binds the new files without changing that parent. Prospective
[build001 manifest](portable_full_direction_build001_manifest.json):556pins,
20fresh compile commands,2links,17distinct archives including resolved-l devXlib.
All compiler commands, actual Clang driver and Fortran compiler/f951 are pinned.
No historical custom object input. Build-only120s/quiet120/3GiB; previous source
build7.60056541627273s is a forecast aid, not a guarantee. Ledger20590.170895962827s
leaves1009.8291040371732s; worst build leaves889.8291040371732s under21600.

Before a material action is admitted, qualify an independent reader that uses
these explicit direction bytes, bind candidate/direction/normalization scale in
the evaluation identity and restart closure, and repeat microscopic continuous64
versus persisted32+32 qualification. The old reader hardcodes its old direction
and must not certify the new action. A full action on the correction can falsify
its predicted usefulness; it does not bound unmeasured directions or establish a
full-space gap/physical-response error certificate. No material run admitted.
