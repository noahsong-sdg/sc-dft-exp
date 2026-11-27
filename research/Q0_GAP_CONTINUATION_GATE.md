# Does a linear current slope require finite-Q gap solves?

This is a conditional scalar-current result, not a qualified material response.
The source equations checked are [S60, S67, S69 and S76–S78 of the SCDFT
supplement](https://arxiv.org/html/2603.05123v2). S67 freezes K/Z with respect to
pair momentum. S69 expands shifted band energies, and S76–S78 specify the
normal-subtracted current and auxiliary-energy representation. Those choices
remain physical approximations; this limit does not add a vertex or mass factor.

## Limit in the audited routine's convention

For a state let d=aQ, the even band shift be bQ^2, E=hypot(xi,Delta), and use
A(y,d) and D(y,d) defined in PAPER_EQUATION_MAP.md. The scalar current is the
weighted sum of

    j(Q,Delta) = {2|d|[D(|xi|,|d|)-D(E,|d|)]
                  +4bQ^2[sign(xi)A(|xi|,|d|)-xi*A(E,|d|)/E]}/Q.

Its analytic slope is implemented in linear_response.py. At fixed positive
finite temperature and a nonzero quasiparticle-energy neighborhood, the thermal
functions are smooth and j(Q,Delta)/Q approaches S(Delta) locally uniformly.
Consequently any continuous branch Delta(Q)->Delta0 has the same limit
S(Delta0), even if its first derivative is nonzero. For a differentiable branch
this also follows because j(0,Delta)=0 for every gap, so the chain-rule term
partial_Delta j * Delta'(0) vanishes. This is our mathematical inference from
the scalar expression, not an independent derivation of electromagnetic response.

An even, continuous change in band energies or quadrature weights does not
change that leading coefficient. The proof does not justify replacing a
momentum-dependent gap by a constant, nor replacing the square of a velocity
by the square of its average. It also does not address a discontinuous branch,
the order of T->Tc and Q->0 limits, or zero-energy nodal limits without their
own continuous-extension argument.

## Numerical falsification controls

`test_q0_gap_continuation.py` compares the analytic slope against independently
evaluated finite-Q exponential occupations at60-digit Decimal precision.
It uses nonuniform gaps, signed weights, positive/negative/zero xi, beta2/8/40,
even band/weight shifts, and fixed/even/linear gap paths. Q is refined from
1e-3 to1e-6; convergence and a fixed final absolute-error threshold are checked.
An even gap path preserves the signed-Q slope. A discontinuous gap path tends
to the alternate gap's slope and must disagree with the original gap's slope.

Development controls: Q=1e-5 was insufficient for the declared2e-5 absolute
comparison for two beta40 linear paths. Adding1e-6 retains the threshold.
Direct binary64 thermal subtraction then reached a roundoff floor for a
beta2 even path, motivating the independent high-precision exponential oracle.
These are finite-step/reference-precision findings, not a production solver bug.
Targeted command: `python3.13 -m unittest discover -s research -p test_q0_gap_continuation.py`.
All3 tests pass; they do not execute the native material initialization/current.

## What this could save, and the remaining gate

Within the stated scalar functional, a qualified Q0 equilibrium gap could
suffice for its linear slope, avoiding additional finite-Q equilibrium solves.
No measured end-to-end saving is claimed. The auxiliary-energy/state assignment
must represent the same continuous integral. Existing native evidence shows
that selecting different symmetry subgroups changes the discrete state layout;
this test does not repair or qualify that mapping. Crystal symmetry, moment
closure, native finite-Q replay, derivatives, quadrature, conditioning, units
and the current-functional interpretation remain separate requirements.
