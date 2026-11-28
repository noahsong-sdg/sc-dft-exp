# The proposed correction improves the actual full residual

The complete correction-sized native sweep at8.05K is certified, covering all
66867left rows and67940right states in both orientations. The exact inverse
correction is useful on this candidate; this is a measured nonlinear residual
improvement, not a full-space gap-error or physical-response certificate.

| Evaluated point | Maximum residual (Ry) | Normalized RMS residual/gap | Original targets |
|---|---:|---:|---|
| Unchanged base d0 |6.09669437161189e-11|1.0312693411116765e-6|PASS|
| d0+h*v |1.5375314641797623e-11|2.843395985000644e-7|PASS|
| d0-h*v |1.1214212172330003e-10|1.853456444901352e-6|FAIL maximum|

The original targets remain1e-10Ry maximum and1e-5 normalized RMS. The plus
point improves them by factors3.965248525736243 and3.6268931466168715,
respectively. The negative step is retained as a sign/falsification control.
No accepted seed is overwritten or automatically replaced.

h=5.502435566805578e-10Ry and v is the verified normalized inverse correction.
Although normalization has observed maxabs(h*v-c)=5.169878828456423e-26Ry,
independent binary64 reconstruction finds **d0+h*v equals d0+c bitwise** across
all135880stored entries, including padding. Its gap SHA256 is
c5ad7e2a2d1e18debacd22e4162db2256193b344e29e90cf84e70967d43cc507.
The whole unchanged base gap/residual block also equals original full016
bitwise. These are identity/roundoff controls, not solution-error bounds.

## Evidence and cost

[Final result](portable_full_step_segment002_result.json) verifies1577pins,
matching public/consumed manifests, owning terminal receipts and recursive
qualifier/first-half lineage. Prepared candidate/direction/h/operator/beta and
all ancestor input closures are unchanged. Native continuous64 versus saved
32+32 was qualified before production. Checkpoint state is unchanged through
both production halves, and final stored direction equals the prepared one.

Independent checkpoint normalization has maxdiff0. Independent plus/minus FD
error7.487899536529063e-10 <=1.9600885669402079e-7. All four independently
reconstructed occupation/Jacobian batches agree within6.938893903907228e-18,
below1e-14. Explicit-sum discrepancy3.294348301097205e-16 is below its registered
6.9621535069987366e-12bound. The full base summary separately agrees with binary
output and preserves its original stationary thresholds.

Production half001:311.66590004134923s/913653760B terminalPASS.
Half002:310.0547899999656s/922468352B terminalPASS.
Combined production621.7206900413148s; cumulative kernelCPU549.426167s.
Qualifier36.70167237473652s/931561472B is separate. Full postread14.195769042242318s
and process peak75923456B are separately observed, outside guarded-native wall.
Quiet waits, staging and other pre/postchecks also do not disappear from whole
workflow cost; no complete accepted-response wall/energy claim is available.
Different direction/step/build and segment layout prevent treating the older
four-segment timing as a controlled speedup baseline.

Guarded campaign total21303.94025062941s/21600s, remaining296.05974937059s.
No owner, retry, auxiliary action or budget increase is admitted. Host pressure
remained normal; Brave and the other study were untouched. Source gate remains
258tests PASS38.008s,247Python compilationsPASS and moment replay exit0; no code
changed for this result. Result/document diffcheck is the publication gate.

Reproduce the core readback with Python3.13:
`python3.13 research/full_step_segments.py certify research/portable_full_step_segment002_manifest.json`.
Raw inputs/artifacts remain identified by the prospective manifests; this does
not claim every upstream acquisition/redistribution/reconstruction gate is closed.
The extra base comparison reads the first16*n bytes of each full-map file;
corrected-point identity compares binary64 arrays d0+h*v and d0+c, with n=135880.

## What this enables next

We now have a checked full J action on the actual useful correction and its
actual nonlinear residual in one sweep, rather than only a compressed estimate
or an unrelated probe. The separate streamed inverse-action helper can examine
that direction without another resident105.74MiB basis copy, after binding a
proper owning source/receipt/preparation closure. No material use is admitted yet.

The unmeasured complement is still the load-bearing gap in conditioning. An
[exact streamed-defect identity](STREAMED_FULL_DEFECT_ROUTE.md) suggests a way to
compute a full induced-norm bound without storing a145GB matrix. Its2.78trillion
contraction-operation estimate is not a measured runtime. A bounded source-built
tile benchmark, complete same-side block treatment and rigorous kernel/product/
row-sum/radius-variation error controls are needed before any full admission.
Neither a favorable probe nor the fourfold residual reduction supplies that bound.
Functional/current normalization, response grids/derivatives, physical reference,
2K/4K and the registered1% scientific decision remain open. The full goal is active.
