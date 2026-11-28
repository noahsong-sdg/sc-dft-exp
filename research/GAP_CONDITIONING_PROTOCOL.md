# From a stationary residual to a response error

This is a prospective acceptance protocol, not a measured bound. It closes no
scientific gate by itself. It applies to the registered fixed-geometry,
fixed-K/Z/beta real conventional branch. Other temperatures require their own
operator and solution. The existing native residual checks remain necessary.

## Owning path and the missing quantity

`reduced_nonlinear_core.f90` solves a compressed equation using Q and U=A0 Q.
`full_nonlinear_probe.f90` evaluates the full residual and one analytic Jacobian
action, with a central-difference check. Neither routine bounds the inverse of
the full Jacobian. `verify_gap_candidate.py` correctly leaves its conditioned
error flag false even if both stationary-residual thresholds pass.

In plain terms, a nearly flat equation can have a small residual while the gap
is still wrong. The small compressed coefficient residual and a successful test
in one direction do not rule out another sensitive direction. Near a transition
this distinction is especially relevant. No numerical condition estimate for
the current fresh solution has been accepted.

## Exact fixed-operator equations

Use H(d)=d-A0 f(d), with the occupation ratio f already defined in
REDUCED_NONLINEAR_GATE.md. Let D(d) be its diagonal derivative and
J(d)=I-A0 D(d). Padding is excluded from the active vector space; do not let
identically zero padded states alter norms or conditioning estimates.

The full native output uses the opposite residual sign, R=-H. Its Jacobian
output is -J applied to its declared direction. Preserve these signs when
forming a Newton correction or testing an inverse. Signed quadrature weights
and the nonsymmetric operator prohibit assuming a positive-definite metric or
using an eigenvalue distance as a smallest-singular-value bound.

For the compressed approximation, an available inverse candidate is

    B = (I-U Q^T D)^(-1)
      = I + U (I-Q^T D U)^(-1) Q^T D.

This identity requires the displayed small matrix to be invertible; its
conditioning must be checked. It does not establish that B approximates the
full inverse. D is evaluated at the candidate, and a changed candidate changes
this construction. A dense nonsymmetric control can check the algebra, but
material qualification requires full-operator evidence.

## Sufficient local certificate

Fix an induced norm on the active states and freeze B at the candidate d0.
Suppose, on a closed radius-r ball about d0, independently justified bounds give

    eta >= ||B H(d0)||,
    q   >= sup_ball ||I-B J(d)||,
    q < 1,  eta + q*r <= r.

Then T(d)=d-B H(d) maps that ball into itself and is a contraction. With
nonsingular B its unique fixed point is a zero of H, and

    ||d_star-d0|| <= eta/(1-q).

Finite-precision evaluation error must be included in eta and q. The ball must
remain inside the declared nonzero conventional branch. If using a bound q0
at d0 and a Lipschitz bound L for B J in that ball, q0+L*r is a sufficient q.
A failed sufficient test is inconclusive; it does not prove a physical solution
is absent. This protocol does not require accepting this particular certificate
if another independently justified full-space error analysis is stronger.

Crucially, Q/U and a finite set of Jacobian probes cannot supply q by themselves:
the operator can differ on their unmeasured complement. Reduced singular values,
observed residual contraction, or sampled matrix actions must be labelled as
estimates or diagnostics, never substituted for that missing bound. Computing
an exhaustive matrix merely to certify a bound also needs a cost/value decision.

## Practical evidence before a certificate is available

After a fresh full residual evaluation, a candidate correction may be formed
using B. Check its full J action, its sign, and the actual nonlinear residual
at a refined candidate before interpreting a predicted correction. Compare an
independently enriched representation on the same operator and retain changes
in the gap and observable. These are useful falsification and sensitivity tests;
their agreement alone is not a rigorous full-space bound. Record which source
of evidence supports any eventual numerical uncertainty claim.

Do not weaken the registered1e-10Ry maximum or1e-5 normalized-RMS stationary
targets because an inverse estimate seems favorable. Conversely, passing those
targets cannot bypass error transport. A full Jacobian finite-difference test
checks implementation of an action, not invertibility or stability of the root.

## Transport to the response

Only after state mapping and the response functional are qualified, let S(d)
be the corresponding fixed-band discrete stiffness. A justified radius r and a
bound on its derivative throughout the same ball give

    |S(d_star)-S(d0)| <= r * sup_ball ||grad S(d)||_dual.

The norm and its dual must match the gap certificate. If the response is a sum
of scalar state contributions at fixed band moments, interval bounds on each
contribution are another route; retain signed integration weights when combining
intervals. A derivative evaluated only at d0 is a linear sensitivity, not a
bound on a finite ball. Crystal-symmetry averaging must remain valid throughout
the allowed perturbations or its error must be treated separately.

For a normalized ratio S(T)/S(Tref), propagate numerator and denominator bounds
with a denominator interval excluding zero. Treat a common normalization as
cancelling only after establishing that it is common. Conditioning evidence at
8.05K does not qualify2K or4K. Solver/conditioning, band/energy/response grids,
interpolation and band derivatives remain separate contributions to the1%
numerical uncertainty target. Functional and experimental mismatch remain
outside that numerical budget.

`RESPONSE_GAP_TRANSPORT.md` now derives a conservative global derivative bound
for the fixed discrete `linear_response.stiffness` observable and infinity gap
norm, with independent high-precision finite-perturbation controls. Its helper
is a floating-point coefficient, not an interval certificate. No justified
material gap radius has yet been supplied; full conditioning remains open.
