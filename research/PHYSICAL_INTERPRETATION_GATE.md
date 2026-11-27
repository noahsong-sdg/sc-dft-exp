# Numerical improvement is not yet physical validation

The velocity-moment experiment establishes a matched-quadrature numerical
effect. It does not establish that the resulting penetration depth is closer
to experiment. This distinction is especially consequential for the Nb test.

The [source paper](https://arxiv.org/html/2603.05123v2) reports a slope-derived
Nb penetration depth of 34 nm, an electron–phonon coupling constant 1.34, and
a normal-state estimate incorporating the mass enhancement (its Eq. S79).
The reported experimental values vary by probe/sample. The response-cell grid
used for Nb is 8 cubed (Table S1). These are published comparison points,
not provenance for our imposed gap or an experimental acceptance interval.

Our matched-energy constant-gap test changes stiffness by factors about
2.20–2.49 when replacing the squared first moment with the second moment.
If a common normalization applied, penetration lengths would change by square
roots of those factors, about 1.48–1.58. These ratios are independent of the
unknown overall unit normalization. The paper's mass enhancement 1+1.34=2.34
is numerically similar to those stiffness ratios. Similarity is not evidence
that the effects are equivalent or that either implementation accounts for the
other. It motivates a check for compensating approximations, rather than using
experimental agreement alone to choose the numerical path.

Before a physical claim:

1. Establish moment-cell convergence and an unshifted-band limit, rather than
   extrapolating the present finite-Q geometry.
2. Trace where response mass/vertex renormalization belongs in the SCDFT current
   functional and where it is actually included. Gap renormalization alone does
   not prove a particular response-current renormalization.
3. Verify overall current/spin/projection units and the pair-momentum convention.
4. Use compatible converged gap data and separate band, gap-functional,
   quadrature and experimental sample effects.

Do not add a fitted factor to recover the published or experimental number.
Do not infer that the paper's physical conclusion is wrong from this diagnostic.
A useful outcome may instead be an auditable separation of numerical coarsening
from physical approximation—an accuracy benefit that a speedup alone cannot give.

## External constraint on a mass-factor shortcut

Raines, Zhang and Chubukov, [Phys. Rev. B 109, 144505
(2024)](https://doi.org/10.1103/PhysRevB.109.144505), establish within their
Eliashberg framework that current-vertex corrections can change stiffness,
including compensating suppression in specific interaction regimes. This is
theoretical context, not evidence of present user demand. It prevents treating
a scalar 1+lambda_ep correction as universally justified. The paper does not
validate our SCDFT approximation or prescribe a niobium correction for it.

The SCDFT source paper's S67 freezes Q dependence of K and Z as a long-wavelength
approximation; S78 defines the auxiliary-energy current, while S79 includes a
mass factor in a separate normal-state estimate. Our inference is that numerical
moment closure and physical response renormalization must be audited separately.
We have not derived an additional response vertex consistent with that functional.
Do not insert a fitted mass factor into the diagnostic cache.
