# Conditional current normalization from a continuum control

This qualifies an analytic normalization identity for `linear_response.stiffness`,
not a niobium penetration depth. It does not execute the native current or
finite-difference stencil; their end-to-end projection/unit checks remain open.
No runtime formula, empirical factor, native
input or acceptance tolerance changes.

## Source conventions checked

The pinned QE constants use Rydberg energies, `RYDBERG_SI=HARTREE_SI/2`.
Native `calc_d_xi_q` contracts the band gradient with Q/2 and curvature with
Q Q/8. `ini_delta` labels its DOS per spin; the two native arrays are shifted
quadrature estimates, not the two spins. They must not be summed as a spin factor.
The released current routine also has the separately documented normal-reference
arithmetic defect; this control concerns the audited formula, not that release.

The [SCDFT supplement](https://arxiv.org/html/2603.05123v2), S19/S21 and S60/S69,
uses Hartree kinetic energy, pair momentum Q and single-particle shifts Q/2;
S19 states the slope-to-London-length convention. These establish conventions,
not validation of our material response or an additional response vertex.

## Independent parabolic-band identity

Choose dispersion xi=k²-mu in Rydberg/Bohr units, a uniform real gap d, and
one-spin continuum measure d³k/(2pi)³. Set E=hypot(xi,d),
tx=tanh(beta*xi/2), te=tanh(beta*E/2). Along x, the half-shift gives a=kx
and b=1/4. Our audited slope therefore reads

    S_R = integral [beta*kx²*(sech²(beta*xi/2)-sech²(beta*E/2))
                    + tx-xi/E*te] d³k/(2pi)³.

Integration by parts of the NORMAL reference, using dxi/dkx=2kx, gives

    integral beta*kx²*sech²(beta*xi/2) = integral (1-tx),

with a boundary term if the domain is cut off. Consequently

    S_R = n_pair - n_normal,
    n_pair = integral [1-xi/E*te],
    n_normal = beta*integral kx²*sech²(beta*E/2).

The density expression already counts both spin states. At zero gap the two
terms cancel; at low temperature in a gapped continuum n_normal vanishes and
the slope approaches paired electron density. This result follows from a
normal-reference density identity, not differentiating the current formula
again or calibrating a niobium number.

For a radial cutoff K the omitted boundary is exactly
`K³*(1-tanh(beta*(K²-mu)/2))/(6*pi²)`. The regression subtracts that term and
uses the same finite domain for both integrals. It does not claim convergence
of the paired-density tail to an infinite domain. The radial one-spin measure
is k² dk/(2pi²), with angular average kx²=k²/3.

## Unit ledger, conditional on the functional

Changing energy units from Ry to Hartree halves xi,d,a,b and doubles beta.
The slope then satisfies S_H=S_R/2, exactly by dimensional covariance; a separate
regression verifies it. The scalar computed in code has physical dimension
energy/length, before charge/hbar converts it to electric-current slope.
With Q in inverse Bohr and volume in Bohr cubed,

    d j_SI / d Q_SI = e*Ry_J/(hbar*a0) * S_R.

Combining that relation with the pair-phase London convention gives

    lambda^(-2)_SI = (4*pi*alpha²/a0²)*S_R,
    lambda = a0/sqrt(4*pi*alpha²*S_R),

provided S_R is positive and is the intended physical current slope. Equivalently,
in Hartree units the factor is 2*(4*pi*alpha²)*S_H. This is a conditional unit
conversion, not authorization to report a material length. The parabolic
control recovers the expected two-spin density at low temperature and supplies
an independent check on the factor, rather than an arbitrary rescaling.

For niobium, mass/current vertices, the frozen K/Z approximation, state support,
quadrature, derivatives, gap stationarity and conditioned error remain open.
Neither a factor1+lambda_ep nor a fitted scale is introduced. The two shifted-grid
responses remain separate estimates until their numerical combination is justified.

## Evidence and reproduction

`test_parabolic_current_normalization.py` compares the audited slope to the
independent density/normal-fluid identity with mu0.93Ry, cutoff4/Bohr,
8192 Simpson intervals, beta4/12/40/120Ry^-1 and gap0/0.15/0.4Ry. All12 cases
pass; maximum measured absolute difference6.938893903907228e-18. Separate
checks cover the energy-unit change, exact normal-state cancellation, and the
low-temperature paired-density limit. These artificial scales are analytic
controls, not material parameters or a numerical uncertainty bound.

Run `python3.13 -m unittest discover -s research -p test_parabolic_current_normalization.py -v`.
The3 tests pass0.299s. `parabolic_current_normalization001_result.json` records
all cases and owning source hashes. Final repository checks after the native owner terminated:193tests PASS19.855s,
198maintained Python sources compiled, moment_refinement exited0, and
git diff --check passed. Native fixture compilation is included in the suite;
there is no separately configured typecheck.
