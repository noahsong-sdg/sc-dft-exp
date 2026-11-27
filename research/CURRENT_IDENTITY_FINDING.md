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
Need independently map the paper's current equation to these factors, compile
a minimal Fortran reproduction, and determine the observable effect on fixed
saved states. The identity discrepancy does not quantify changes to total
current, penetration depth, or the published peak/slope difference: integrations
can cancel, and source/output provenance still needs checking.

No claim that correcting two lines alone certifies the entire current routine.
Examine its companion d_x factor, normal limit, sign conventions, threshold
continuity, and zero-Q behavior before preparing a narrowly scoped upstream
patch. Public reporting remains local; no maintainer contact authorized.
