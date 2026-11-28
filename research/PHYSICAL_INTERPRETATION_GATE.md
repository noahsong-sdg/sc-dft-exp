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


## Prospective external comparison conditions (checked27November2026)

[SCDFT v2, S67/S79 and TableS2](https://arxiv.org/html/2603.05123v2)
freezes the momentum dependence of K and Z, and lists its mass-enhanced
normal-state estimate separately from the current-slope result. For Nb its
calculated Tc is8.09K versus experimental9.50K in that table. This is evidence
about that calculation, not a measured Tc for our current run. The table does
not justify inserting its normal-state mass factor into our current slope.

[Hiorth et al. v1, SectionIII.1 and Table1](https://arxiv.org/html/2603.10955v1)
reports Nb15nm with uniform pairing at zero temperature. Its comparison near
16–19nm rescales experimental values by1/sqrt(Z), with Z approximately2.1.
Thus that comparison is not a direct uncorrected experimental benchmark for our
finite-temperature anisotropic result. Their conventional/geometric split and
strong-coupling comparison must remain distinct; we have not matched their DFT
inputs or independently derived their correction for our functional.

[McFadden et al., published abstract](https://journals.aps.org/prb/abstract/10.1103/2nsw-n8gf)
reports intrinsic lambda_L=29.1(10)nm from oxygen-doped Nb with nonlocal screening
analysis. The [author-hosted manuscript dated4November2025](https://misportal.jlab.org/sti/publications/25858/attachments/21075/lem-sims-nbV3.pdf),
Figure2 and Equations3–10, describes Meissner profiles at3K, a finite-mean-free-path
and stopping-distribution model, surface dead layer and demagnetization, and
fixed Tc9.25K/gap1.53meV in its joint fit. TableII selects the nonlocal weighted
estimate. Its parameter is not simply a fitted exponential screening distance.
The published abstract agrees on29.1(10); full final publication conditions have
not been independently checked against that manuscript.

Our resulting comparison protocol is prospective, not an accepted result:

1. Keep the registered2/4/8.05K calculations and report physical temperatures.
   Any reduced-temperature comparison must disclose each independently obtained
   Tc and remain a separate diagnostic. Do not shift Tc to fit a measured curve.
2. Compare intrinsic q->0 stiffness/London length with a matched intrinsic
   quantity, distinguishing it from a finite-q field profile or dirty-sample
   exponential length. Do not infer the missing corrections from agreement.
3. Keep numerical1% uncertainty separate from current-functional, strong-coupling,
   sample and extraction mismatch. A common scalar normalization cancels in a
   ratio only if it is actually common; state/temperature-dependent vertices
   cannot be assumed to cancel.
4. Accept no physical length comparison until mass/current assumptions and
   matched conventions are derived and independently checked. These sources
   identify useful external checks; none closes that gate by itself.


## Conditional unit/spin normalization control

CURRENT_UNIT_CONTROL.md derives a separate continuum identity for the audited
Q0 formula: in a parabolic band the Rydberg slope equals paired two-spin density
minus thermal normal-fluid density, with an explicit finite-cutoff boundary.
All12 artificial finite-temperature cases agree within6.94e-18; independent
regressions check normal/low-temperature limits and S_Hartree=S_Rydberg/2.
This provides a conditional unit ledger without fitting a niobium scale.
The two native arrays are quadrature estimates, not separate spin factors.
It does not execute the native current/stencil, qualify the released arithmetic,
normalize the actual Nb quadrature, bound gap/response error, or justify a mass
vertex. No physical material length is accepted.193tests/198source compilations
and moment final checks pass; source/input identities are in the resultJSON.
