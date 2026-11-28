# Independent full-P saved-image control

The complete first pass accumulates P=Q^T D A, with A the two-orientation native
linear kernel carrying finite-temperature input weights and output(1+Z) factors.
D is the normalized occupation derivative. Its use on both sides below is required:

    P(Dv) = Q^T D (A D v).

The accepted older full correction sweep saved the original raw fourth native
linear image for its declared correction direction v. Its existing normalization
routine gives residual Jacobian action ADv-v=-image4/(1+Z)-v. Therefore ADv is
independently available as -image4/(1+Z), without new kernels or finite differences.
Comparing all rank51 components checks complete P against a separately executed
full native image. It is one direction and cannot bound the full operator norm,
prove inverse conditioning or validate superconducting response.

`compact_p_actions.py` uses math.fsum rather than the native BLAS accumulation.
It streams P in1024-column chunks (at rank51,417792payload bytes), retains only
per-rank chunk sums and streams one Q column at a time. It does not transpose or
load complete P/Q. Left and right sums are compared with the diagnostic bound
1e-28+1e-10*(sumabs(left products)+sumabs(right products)). This is a conservative
ordinary floating-point control, not an outward-rounded certificate. Both Dv and
DADv products, all matrix entries, sums/errors and bounds must be finite.

`compact_p_action_readback.py` first replays accepted complete-segment provenance,
recorded output equality and pins. It separately certifies the old complete native
correction sweep and recorded result, checks the same native source/geometry and
declared direction, removes padding in the original two-side order and reads D
from the accepted compact state. Original full sweep and checkpoint/seed/direction
files must be in the accepted closure. Input and helper identities are recorded
and rechecked after all arithmetic. The result has its own acceptance flags and
does not modify earlier pinned segment producers/results. The accepted complete-P
result itself retains independent_full_P_action_controls_passed=False; only this
separate validated artifact can establish the additional directional control.

Fixtures independently construct a signed nonsymmetric cross-side A and nonuniform
Q/D/v using exact Fraction sums for P and ADv. All control components pass;
wrong D/action, finite P corruption, stale shapes and nonfinite Q/P fail. Owner
regression rejects incomplete/stale public full-P parents and invalid timing
metadata before using a saved image. Targeted3PASS0.003s. Actual material action
control remains pending complete native coverage, terminal readback and publication
of the current helper sources. Native/physical response goals remain incomplete.
Final source gate:312testsPASS45.022s,285Python compilationsPASS; actual native
fixture builds/runsPASS via full suite; moment_refinement.py exit0; diffcheckPASS.
No separate configured typecheck. These checks ran after the material native
pass completed, with independent checkpoint postread concurrent with unit tests.
Complete P segment001 accepted; material saved-image control remains pending.
