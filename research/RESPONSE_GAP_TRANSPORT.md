# Conditional finite-temperature gap error transport

The execution path `linear_response.stiffness` evaluates a fixed-state response
but previously supplied no finite-ball gap sensitivity bound. A small stationary
residual cannot fill that gap: an independent full-space conditioning analysis
must first bound the gap error. The existing conditioning protocol identifies
this missing transport step explicitly.

The separate helper `response_gap_transport.infinity_gap_lipschitz` supplies
one conservative real-arithmetic bound without changing the response routine.
In simple terms, once an independently justified maximum gap error is available,
this coefficient gives an upper bound on how much that error can change the
fixed discrete stiffness. It does not produce the gap-error bound itself.

## Derivation in the audited routine's conventions

For one state, write E=sqrt(xi²+d²), u=beta E/2, and retain fixed signed weight w,
velocity coefficient a, curvature coefficient b, and positive volume V. The
gap-dependent part of the response has derivative

    dS_state/dd = w/V * [
        beta² a² (d/E) sech²(u) tanh(u)
      + 4 b xi d/E³ * (tanh(u) - u sech²(u)) ].

This is a derivative with respect to the real gap, with all other state data
fixed. The formula has a continuous zero-energy extension. No gap-gradient,
band-derivative, weight, temperature, or functional variation is included.

For u>=0, set t=tanh(u). Then t(1-t²)<=2/(3sqrt(3)) and |d|/E<=1.
Also g(u)=tanh(u)-u sech²(u) is nonnegative: g(0)=0 and
g'(u)=2u sech²(u)tanh(u)>=0. Since g(u)<=tanh(u)<=u and
|xi d|<=E²/2, the second derivative term in absolute value is at most
beta |b|. Thus a global per-state derivative bound is

    |w|/V * [2 beta² a²/(3sqrt(3)) + beta |b|].

Summing absolute bounds gives L and the mean-value inequality gives

    |S(d+e)-S(d)| <= L * ||e||_infinity.

The norm is over represented active state gaps, with fixed state layout.
Negative integration weights are handled by their absolute values; dropping
that absolute value would invalidate a bound. The global bound covers finite
perturbations, including changes of gap sign, rather than only a derivative at
the candidate. It is deliberately conservative; a failed1% test is inconclusive.

The helper requires finite states and positive finite beta/volume, and rejects
a nonfinite result. It returns a floating-point evaluation of a mathematical
coefficient, **not outward-rounded interval arithmetic**. A production numerical
certificate must include rounding and response-evaluation errors separately.
Do not call L*r a material error bound unless r is independently justified in
the same norm, and the functional/state mapping and other error sources pass.

## Controls and scope

`test_response_gap_transport.py` checks240 finite perturbations against a
70-digit Decimal response evaluated through exponentials, independently of the
production tanh/sech implementation. Cases cover beta0.5/4/40/20000, xi0 through
2, gaps0 through0.3, signed weights, and perturbations1e-12 through0.2. The
zero-energy continuous extension is included in that analytic control; this
does not alter the original routine's explicit zero-energy rejection.
Additional checks cover positive-volume scaling, empty support, and invalid or
nonfinite domains. The narrow three-test suite passed in0.057s.

This closes a conditional algebraic step, not the full conditioning requirement.
No native gap error, physical response, numerical1% acceptance, mass/current
vertex, missing-state support, or experimental agreement is certified. The
choice of a simple global bound avoids an unqualified interval optimizer or
new state-dependent approximation; sharper bounds can be considered only if
this sufficient test is too conservative for an actual certified gap radius.

Final gate: `python3.13 -m unittest discover -s research -p 'test_*.py' -v`
passed196tests in20.967s, including native fixture compilation. All200maintained
Python sources compile; `python3.13 research/moment_refinement.py` exited0 and
`git diff --check` passed. No separate configured typecheck. Source identities
and explicit unaccepted material flags are in response_gap_transport001_result.json.
