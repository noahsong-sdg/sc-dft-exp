# Registered methods

## Scientific question

The primary question is how specified superconducting approximations change the
continuous conventional pairing-onset temperature, and what additional public
interaction information is required for an isotropic Migdal–Eliashberg model to
agree with SCTK.

The study separates three claim levels:

1. implementation and numerical validation;
2. agreement between specified models;
3. predictive accuracy against experiment.

Passing one level does not establish the next.

## Cohort

The frozen cohort is Nb, Al, Ta, SOC-Pb, beta-Sn, and V3Si, using their released
bulk structures and public inputs. V3Si is retained as a resource and structure
stress case rather than silently excluded if capacity fails.

## Nb interaction bridge

The Nb factorial keeps electron–phonon pairing and renormalization in every arm:

| Arm | Spin fluctuations | Electronic Coulomb Z | Pairing coefficients | Electronic Z coefficients |
|---|---|---|---|---|
| A | on | on | C+S | S-C |
| B | off | on | C | -C |
| C | on | off | C+S | S |
| D | off | off | C | omitted |

Each arm and temperature requires its own initialization, Z, and context.

## Scalar panel

For every material, the scalar diagnostic evaluates bare `mu` values 0.20,
0.30, and 0.40 at 7000 and 9000 meV cutoffs. The electronic scale is 10000 meV
and the electronic density of states is constant. These are sensitivity arms,
not fitted ab-initio Coulomb inputs.

## Acceptance rules

The observable is the continuous conventional pairing instability at Q=0,
defined by the largest eligible algebraic eigenvalue crossing one.

Accepted native endpoints require:

- full residual no greater than `1e-10`;
- consecutive eligible eigenvalue change no greater than `1e-8`;
- distance from one greater than `1e-8`;
- registered phase, sign, node, and higher-mode checks;
- a fresh complete native operator action;
- independent full-space reconstruction and uncached sums.

Failures and ambiguous channels are never classified as normal-state points.

For a paired comparison, define

`d = max(0.20 K, 0.10 * T_ref)`.

Each transition bracket and numerical-control endpoint shift must be no wider
than `min(0.10 K, d / 5)`.

## Resource boundary

Runs use bounded process groups, normal host-memory pressure, fixed free-disk
floors, supervised stages, immutable output namespaces, and explicit accounting.
Resource-held, censored, failed, and unrun cases are reported as such and never
converted into physical scores.

