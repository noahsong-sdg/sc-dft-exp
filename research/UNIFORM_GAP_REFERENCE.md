# Independent uniform-gap response control

Checked 27 November2026. The prior landscape survey inspected the published
abstract; we now inspected the [authors' full preprint, Eq.4 and SectionsII–III](https://arxiv.org/html/2603.10955v1).
Their conventional response uses velocity products; their practical calculations
assume uniform pairing and zero temperature, separate a geometric contribution,
and discuss strong-coupling/nonlocal comparisons. Finite temperature and nonuniform
pairing are stated extensions. Therefore its Nb length is not our finite-temperature
anisotropic acceptance value. We have not reproduced their DFT inputs or geometric
calculation, and found no implementation link in the inspected text.

## Derivation in our existing code convention

This is our integration-by-parts check, not a claim of new response theory.
For a smooth periodic band, constant real gap, and directional derivatives
v=partial_k xi, c=partial_k² xi, the current-code coefficients are a=v/2 and b=c/8.
Set E=sqrt(xi²+gap²), t(E)=tanh(beta E/2), s(E)=sech²(beta E/2).
The existing normal-subtracted integrand is

```
beta*v²/4 * [s(xi)-s(E)] + c/2 * [t(xi)-xi/E*t(E)].
```

The integrated normal terms vanish as the periodic total derivative
partial_k[v*t(xi)]/2. Integrating the remaining curvature term by parts gives

```
S = integral weight * v²*gap²/(2*E³) * [t(E)-beta*E*s(E)/2] / volume.
```

The one-half converts the reference conventional kernel to our pair-momentum
slope convention. It follows from the displayed algebra; electromagnetic/SI
conversion remains governed by RESPONSE_NORMALIZATION.md. No fitted factor enters.

uniform_gap_reference.py evaluates the velocity expression without using the
existing curvature implementation. Its small-energy series controls cancellation.
Tests compare independently evaluated integrals for a periodic cosine band at
beta2/8/40, and check zero-gap and analytic small-energy limits. These tests do
not use experimental targets or fitted normalization.

## Material validation still required

Use the same converged bands, derivative direction, integration measure, constant
gap, temperature and volume in both formulations. Discrete quadrature need not
obey integration by parts exactly: their difference is a diagnostic that must
converge, not a license to choose whichever matches experiment. The actual native
state/derivative mapping and band crossings remain to be qualified. Do not apply
this constant-gap identity to a momentum-dependent gap without retaining its
additional derivative terms. Geometric, mass and vertex contributions are outside
this scalar control. No accepted material uncertainty follows yet.
