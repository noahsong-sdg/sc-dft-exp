# Test a saved-action rank-one inverse update

The current low-rank inverse B has a0.6411 relative inverse defect on the actual
useful correction direction. It approximates only a compressed part of the full
Jacobian. A residual pass therefore leaves the conditioning gate open. In plain
terms, the correction helped, but our tool for translating residual into gap
error is still inaccurate in a direction we have actually measured.

Before another full kernel sweep, test a specific fixed inverse update using
already accepted saved full actions. Put z=J(d0)v, u=v-Bz, w=z/(z^T z), and
Bnew=B+u w^T. For nonzero z, w^T z=1 and Bnew z=v exactly in real arithmetic.
Each changed row must have dot product u_i with z. Cauchy–Schwarz gives its
minimum squared length u_i^2/(z^T z), attained by u_i z^T/(z^T z). Thus this
update is the minimum Frobenius-norm matrix change satisfying that one equation.
This is elementary secant algebra, not a novelty claim or an inverse-error bound.

A perfect fitted-direction result is expected by construction. The decisive
separate diagnostic is the original pre-existing probe, whose native J action
and original B Jv-v are already saved. Its direction does not determine the
update. It is a separate control, not an unseen experimental holdout: its prior
result is public. Also report the updated inverse actions on base and actual
plus-point residuals. No new nonlinear residual evaluation is implied.

`secant_inverse_action.py` forms two vectors and applies their outer product
without a dense matrix or basis copy. Scaling z before its squared norm avoids
unnecessary overflow/underflow; zero action and nonfinite values are rejected.
`secant_inverse_run.py` binds the complete accepted streamed diagnostic, its
terminal receipt, saved answers and full original source/correction closure.
It reuses the frozen full-context validator, checks the source diagnostic's
recorded metrics against its binary, and reconstructs the original probe with
the required addition of its saved direction. The original binary stores a
defect, not the inverse action. Base residual equality binds the separate probe
to the same candidate. The own command/cwd, fresh outputs, immutable pins and
manifest are checked before an unaccepted raw readback is written.

The output binary has six n-double blocks: u,w, updated B Jv, updated B Jv_old,
updated B R(base), updated B R(plus). The current inverse and seed stay frozen.
Even improving both probes cannot bound the unmeasured complement, derivative
variation, kernel/rounding error or physical response. The global norm route
would need to include this extra rank-one term throughout if it is adopted.

This is the smallest update directly informed by the observed defect. It is
preferable as an inexpensive falsification test to regenerating the same
kernel, pretending a fitted direction is a global certificate, or rewriting the
accepted inverse producer. A failed separate test argues against adopting it;
a pass only justifies further assessment. No budget expansion follows.

Tests independently construct an exact rational nonsymmetric dense updated
matrix, check another RHS and the minimal-norm identity, exercise extreme
finite scaling, and retain a case where the fitted direction improves while a
separate direction worsens. Owning tests cover binary order/terminal withholding,
source/receipt/metric/closure changes, nonfinite equation bounds, stale base
residuals, changed final pins, owner/command and fresh outputs. No material result
or admission is asserted by this source checkpoint.

Final source gate:268offline tests PASS38.066s including native compilation/run;
253maintained Python sources compilePASS; moment_refinement exit0; diffcheckPASS.
No separate configured typecheck. Initial attempt used macOS system Python3.9,
which lacks contextlib.chdir used by existing owning fixtures; rerun with the
project Python3.13 passed. No runtime/source compatibility change was needed.

## Material result: reject this update

[Secant001](secant_inverse_action001_result.json) passed its owning execution
guard in21.248003708198667s, individual peak92323840B (~88.05MiB), sampled group
peak89849856B. All1597pins/source/receipt/public-consumed manifest checks passed.
This is a small saved-data diagnostic, not a controlled memory comparison.

| Diagnostic | Original B | Rank-one updated B |
|---|---:|---:|
| Fitted direction inverse defect |0.6410778371097358|1.1102230246251565e-16|
| Separate original probe inverse defect |0.48070172169141706|15.233333612168108|
| Base residual inverse action, Ry |5.502435566805601e-10|1.438905105618171e-10|
| Plus residual inverse action, Ry |3.5273124350480197e-10|4.2587019897976185e-10|

The apparent training success is imposed by the update. The separate probe
worsens by about32x and its defect exceeds1, while the plus residual action also
worsens. Reject this update for the intended unweighted infinity-norm contraction
route; do not promote its smaller base correction as a gap-error estimate. A
single measured direction above1 already fails the necessary directional test
for a global norm below1 on these saved actions. This is an algorithmic rejection,
not an impossibility result for superconducting response or the original inverse.
The global scientific gate still needs a genuine full-space/radius certificate.

Independent70digit Decimal readback reconstructed u and w from the saved v,Jv,BJv
and checked every entry of all four updated actions against a separately
computed dot product and update. Maximum absolute action errors were1.11e-16,
1.78e-15,5.17e-26,5.17e-26, below3.28e-13,3.04e-12,1.10e-22,8.52e-23 controls.
Maximum w relative difference4.45e-16; u agrees exactly. Binary shapes/finiteness,
output hashes, original/current base gap and residual equality, all diagnostic
norms and strict terminal receipt also checked. This arithmetic check is
independent of the update helper, but shares saved native inputs and is not a
kernel/physical validation. Postread4.7563805831596255s/93552640B process peak
observed separately, excluded from guarded wall; whole-workflow cost remains open.

Original inverse and seed remain unchanged. All owners terminal. Charged guarded
total21348.708971087672s/21600 leaves251.291028912328s; no next run, retry or budget
increase admitted. The next feasible conditioning experiment is a bounded
source-built tile-throughput/error-control test for the original fixed inverse's
full streamed norm route, rather than another fitted-direction update. That
experiment requires its own source qualification, forecast and admission.
