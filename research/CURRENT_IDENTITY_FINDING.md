# Normal-reference thermal-factor audit

## Verified algebraic discrepancy

The released supercurrent routine at current pinned commit
4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33 and historical output commit
47c06501da8ffd574c87469ddd6d5a2814171796 contains the same normal-reference
factor x_d. Its regular branch uses tanhe=tanh(beta*sqrt(xi^2+delta^2)/2)
in the numerator while all surrounding factors use tanhx=tanh(beta*abs(xi)/2).

For x=abs(xi), d=abs(dxq), the required normal factor from the sum of shifted
normal-state occupations is

    X = [tanh(beta*(x+d)/2) + tanh(beta*(x-d)/2)] / 2
      = b*(1-a^2)/(1-a^2*b^2),
    a=tanh(beta*d/2), b=tanh(beta*x/2).

The released regular branch instead evaluates e*(1-a^2)/(1-a^2*b^2),
where e depends on delta. A normal reference at fixed x,d,beta must not depend
on delta. At x=.4,d=.2,beta=2 and gap=1 this fails by more than .1 in a
dimensionless thermal factor. Replacing that numerator e by b restores the
identity across the tested nonsaturated grid.

The saturation shortcut has a second issue: it chooses its normal-reference
branch using x^2+delta^2>d^2. The corresponding normal-state boundary is x^2>d^2.
For x=1,d=2,gap=2,beta=100, direct normal X=0 but the released branch returns
approximately 1. Direct shifted tanh expressions avoid the near-singular
addition-form denominator in this scalar check.

Plain meaning: the subtraction intended to remove the normal-state current
contains superconducting-gap information. Two copied expressions retain terms
from the superconducting branch. This is a specific algebraic discrepancy,
not merely evidence of finite-sampling sensitivity.

## Scope and next gate

Eight unit tests across this and response extraction currently check analytic
identities and archive conversions. No upstream Fortran patch is adopted yet.
An initial 1e-9 equality check also exposed cancellation in the quotient form
near saturation (7.6e-9 difference); regular-branch identity tests now use a
well-conditioned grid. Stable evaluation near saturation needs separate tests.
Need independently map the paper's current equation to these factors, compile
a minimal Fortran reproduction, and determine the observable effect on fixed
saved states. The identity discrepancy does not quantify changes to total
current, penetration depth, or the published peak/slope difference: integrations
can cancel, and source/output provenance still needs checking.

No claim that correcting two lines alone certifies the entire current routine.
Examine its companion d_x factor, normal limit, sign conventions, threshold
continuity, and zero-Q behavior before preparing a narrowly scoped upstream
patch. Public reporting remains local; no maintainer contact authorized.

## Compiled reproduction

`current_probe.f90` reproduces the normal-reference branches in standalone
Fortran, compiled with GNU Fortran 16.2.0, `-std=f2008 -Wall -Wextra
-fcheck=all -O0`. All three counterexample/control cases pass their assertions.
The full suite has nine passing tests, including native compilation/execution.
This rules out Python-specific evaluation as the explanation; it is not yet a
compiled test of the complete upstream routine.

The current integrand contains `4*d2xq*sign(xi)*x_d`. A changed x_d therefore
changes this term whenever curvature is nonzero. Its error is odd in xi if all
other factors and the gap are symmetric. Exact cancellation is possible in a
particle-hole symmetric integral. Real material weights/asymmetry must be
measured before estimating an observable correction. The companion d_x term
uses tanhx consistently in its regular branch, but shares the gap-dependent
saturation boundary. Both normal-reference factors need treatment together.

The direct shifted-tanh sum is stable for X at large beta. For the companion
difference, direct subtraction can lose tiny contributions when both terms
saturate; do not replace the complete stable algorithm without accuracy and
performance comparisons over the actual physical parameter range.

## Complete routine test

`python3 research/full_current_probe.py` retrieved the pinned source and checked
SHA256 1062c2a6656455b223111928fbc37996fce564d6dcf0a3acc945b973a9101598.
It compiled the complete unmodified routine against synthetic modules, serially
with bounds checks. Both integration-grid outputs are identical in this fixture.

| Case | Released printed current | Direct thermal identities |
|---|---:|---:|
| Particle-hole symmetric weights | 0.075565 | 0.075564665 |
| Asymmetric weights | 0.47540 | 0.116898877 |
| Zero gap | 0 | 0 |
| Asymmetric saturated case | 0.49751 | 4.597507764 |

The tiny symmetric-case difference is output rounding. The asymmetric cases
demonstrate the discrepancy survives summation in the full routine. Synthetic
energies, weights, volume and curvature are unit fixtures, not a material model;
these magnitudes or ratios cannot be assigned to V3Si. OpenMP directives are
ignored in this serial build, so this does not qualify parallel behavior.
