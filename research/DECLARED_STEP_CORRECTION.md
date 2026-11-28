# One sweep for a correction action and actual corrected residual

The accepted compressed correction has maxabs5.502435566805578e-10Ry. The prior
native/checkpoint/readback path hardcodes1e-8Ry. Merely changing its direction
would test an action but would not directly evaluate the proposed corrected gap.
A separate declared-step variant preserves the four existing batches and kernel
order, allowing h=maxabs(correction),v=correction/h without modifying frozen code.

The four unnormalized saved images are A f(d0), A f(d0+h*v), A f(d0-h*v) and
A D(d0)v in the native kernel sign convention. Normalizing by-(1+Z) and subtracting
the corresponding gap gives R(d0),R(d0+h*v),R(d0-h*v); the derivative image minus
v gives native-Jv. Thus the existing plus-image can test actual correction
usefulness without paying for another full kernel sweep. It does not certify
unmeasured directions or a full-space gap/physical-response error.

full-map-step.in has two lines: declared-full-map-step-v1 and a finite positive
binary64-readable step. Native code rejects invalid schema, nonpositive/nonfinite
values and trailing lines. The new checkpoint schema is
`declared-step-full-map-checkpoint-v1; exact active state binding`; restart compares
the saved step bit for bit. The existing exact candidate-bound direction IO is
unchanged. Old fixed-step/checkpoint readers are not permitted to certify this
variant.

Native controls with the actual proposed step pass continuous versus persisted
restart bitwise equality. Independent dense nonlinear sums match base/plus/minus
residuals from saved images in both orientations. Changed step, old checkpoint
schema, invalid/trailing step controls reject. The independent normalization
helper checks padding, dimensions, finite denominators/state/summary and the
unchanged derivative tolerance. Tests reject corrupted plus-images, nonfinite
summaries and incompatible shapes/denominators. Summary readback binds the exact
declared step; its binary input uses compact streamed arrays instead of a tuple
of Python floats. No measured RSS improvement is claimed.

[Prospective source build001](portable_full_step_build001_manifest.json) has566
pins,20fresh compile commands,2links/17distinct pinned archives, no historical
custom objects. Build-only120s/quiet120/3GiB, prior direction build4.413896750193089s
is a forecast aid. Ledger20594.58479271302s leaves1005.4152072869801s; worst build
leaves885.4152072869801s under21600. No material action/automatic retry/budget
increase admitted.243tests/234Python compilations/moment replay passed.

Before any material qualification, independently check all checkpoint occupation
weights using the explicit direction and step, bind original inverse result,
candidate bytes, normalization scale and direction/step files in the immutable
evaluation/restart closure. Report roundoff in h*v relative to the stored
correction and the actual corrected candidate. Repeat microscopic continuous64
versus persisted32+32 equality. Only terminal full-row results can support a
material correction-usefulness claim. Even a successful correction leaves full
conditioning, response functional/uncertainty and2K/4K work open.
