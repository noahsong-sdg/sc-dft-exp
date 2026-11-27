# Variable-gap algebra control

The existing uniform-gap velocity reference cannot be extended by replacing its
constant gap with a state vector: the integration-by-parts step differentiates
the gap as well as the band. This is a missing independent validation case,
not evidence of a bug in the curvature-based anisotropic implementation.

Trace: `linear_response.stiffness` evaluates the frozen-gap scalar current's
small-Q curvature expression. `anisotropic_moment_analysis` uses that expression.
`uniform_gap_reference.stiffness` eliminates curvature only for constant gap.
For smooth periodic xi(k) and real Delta(k), in the same direction let
v=partial_k xi, c=partial_k v, d=partial_k Delta, E=hypot(xi,Delta),
t=tanh(beta E/2), and s=sech²(beta E/2). The normal terms cancel after integration
as partial_k[v*tanh(beta xi/2)]/2. The remaining expression is

```
integral [-beta*v²*s/4 - c*xi*t/(2*E)].
```

Integrating the curvature term by parts gives v*partial_k[xi*t/E]/2. Using
partial_k E=(xi*v+Delta*d)/E then yields

```
S = integral Delta*(v²*Delta-v*xi*d)/(2*E³) * [t-beta*E*s/2].
```

Thus simply inserting Delta(k) into the uniform-gap velocity formula drops
the term proportional to its gradient. In plain terms, the band curvature
formula accounts for a changing gap through the integrand; removing curvature
moves that dependence into an explicit derivative.

`anisotropic_velocity_reference.py` evaluates this expression independently of
the curvature implementation. It handles the E=0 thermal limit with its series,
and accepts smooth signed real gaps. Tests compare periodic two-harmonic bands
and variable gaps at beta2/8/40, require that omitting the gradient gives a
detectable disagreement, and check constant-gap reduction, global sign and
small-energy limits. This small separate control preserves all pinned production
sources and directly tests the missing algebra without introducing gap transfer.

These are synthetic identities for the existing frozen-gap scalar functional.
They do not derive an electromagnetic vertex, prove that this functional is
the exact anisotropic physical response, or validate material state mapping.
No fresh niobium gap gradient or material stiffness has been accepted. Applying
the control to a discrete material representation requires a qualified derivative
and measure; discrete integration-by-parts error must be assessed separately.
