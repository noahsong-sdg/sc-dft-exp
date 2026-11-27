# Analytic small-momentum limit: a narrower reuse opportunity

The complete pinned current routine agrees with an analytic Q→0 expression on
synthetic controls. This offers a way to evaluate linear response from a Q=0
gap and directional band derivatives, without a separate nonlinear solve at
every small Q. It is not yet a material result or a novelty claim.

## Derivation and boundary

Use the audited routine's conventions: dxq=aQ, d2xq=bQ², E=hypot(xi,gap),
Tx=tanh(beta*abs(xi)/2), and TE=tanh(beta*E/2). Expanding its corrected
shifted thermal occupations gives

```
lim j(Q)/Q = sum weight/volume * {
  beta*a²*[sech²(beta*xi/2)-sech²(beta*E/2)]
  + 4*b*[sign(xi)*Tx-xi/E*TE]
}
```

This is a derivation of the code's scalar limit. Overall physical sign,
spin/projection factors and conversion to penetration depth remain separate
qualification gates. `linear_response.py` implements it, using an exponential
thermal tail rather than subtracting a rounded tanh from one.

For a smooth time-reversal-symmetric branch, gap(Q), xi(Q), and weights(Q)
are even in Q. Their O(Q²) changes affect j/Q only at O(Q²); their Q=0
values therefore suffice for the leading limit. This argument does not certify
discrete active-state changes, nonsmooth or unstable branches, zero-energy
nodes, or an inadequately converged integration grid. The implementation
explicitly excludes E=0. Directional a and b are still required; an archived
gap alone is insufficient. See REUSE_BOUNDARIES.md for the finite-Q boundary.

At fixed finite beta and Q→0 the finite-Q saturation shortcut does not trigger:
its shifted-energy difference tends to zero. The previously found finite-Q RHS
shortcut discrepancy therefore does not itself imply a wrong Q=0 gap. A
qualified saved gap could be useful even while finite-Q nonlinear behavior
remains unresolved.

The released regular normal-reference error does survive this limit. Its bias is

```
sum 4*weight*b*sign(xi)*(TE-Tx)/volume
```

Exact particle-hole-symmetric pairs cancel this bias; realistic cancellation
must be measured rather than assumed.

## Independent checks actually run

`python3 research/linear_response_probe.py` downloads and hash-checks the pinned
complete current routine, then compiles released and narrowly corrected variants.
Only diagnostic output precision is increased. Twelve cases use six momenta
from .03 to .0001 and two prescribed gap paths, delta=1 and delta=1+3Q².
Unequal weights prevent accidental particle-hole cancellation. Both integration
grids receive identical synthetic inputs and must agree.

Analytic slope: 0.6689372637280748. At Q=.0001 the corrected slope differs by
2.58e-9 for the constant gap and 2.09e-8 for the varying gap. Reducing Q tenfold
reduces error approximately one hundredfold. Released slopes instead approach
the independently predicted biased limit, 1.0398697978915403.
Machine-readable results: linear_response_results.json.

These checks establish algebra and a full-routine implementation comparison,
not physical accuracy. The next decisive test is material-derived directional
coefficients, matching qualified Q=0 gap data, and integration/convergence checks.
If successful, this avoids the dense finite-Q nonlinear allocation documented
in MEMORY_FLOOR.md for this linear observable. It does not enable critical
current, pair-breaking scans, or arbitrary finite-Q reuse by itself.
