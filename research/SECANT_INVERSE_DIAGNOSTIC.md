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
