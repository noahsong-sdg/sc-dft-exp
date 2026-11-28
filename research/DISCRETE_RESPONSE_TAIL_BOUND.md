# Conditional bound on known high-energy response states

This is our derivation from the scalar expression implemented in
`linear_response.py`, whose hash is pinned in `discrete_response_tail001_result.json`.
It does not derive an electromagnetic vertex or establish a material error bar.
The owning execution path is the state tuple `(xi, gap, weight, a, b)` to
`stiffness`: energy is `hypot(xi,gap)`, the velocity term uses `a*a`, and the
curvature term retains signed `b` and signed quadrature weights. No owning
production/native code or saved weights are changed.

For finite positive beta, put x=abs(xi)>0, E=hypot(x,gap), t(y)=tanh(beta*y/2).
The absolute unweighted state contribution is at most

```
B = 4*beta*a^2*exp(-beta*x) + 4*abs(b)*gap^2/[E*(E+x)].
```

The expression permits a state-dependent, signed gap. The bound depends only
on its magnitude. It is conditional on the audited scalar response functional.

## Proof in exact arithmetic

The velocity contribution is beta*a^2 times
`sech^2(beta*x/2)-sech^2(beta*E/2)`. Since E>=x, this is nonnegative and bounded
by `4*beta*a^2*exp(-beta*x)` using sech^2(z)<=4*exp(-2*z).

The signed curvature bracket is sign(xi) times `t(x)-x*t(E)/E`.
The function t(y)/y is decreasing for y>0: its derivative has numerator
`z*sech^2(z)-tanh(z)<=0`, equivalent to `2*z<=sinh(2*z)`.
Thus the bracket's magnitude is nonnegative. Since t(E)>=t(x), it is at most
`t(x)*(1-x/E)<=1-x/E=gap^2/[E*(E+x)]`. Applying the triangle inequality to
velocity plus curvature yields B. Multiplication by abs(weight), summation and
division by the positive cell volume preserve the upper bound, even for signed
quadrature or curvature. No cancellation is presumed.

For a known tail set with abs(xi)>=L>0 and abs(gap)<=D, a coarser form is

```
abs(S_tail) <= [4*beta*exp(-beta*L)*sum_tail(abs(w)*a^2)
                 + 2*D^2/L^2*sum_tail(abs(w*b))] / volume.
```

Use the statewise expression when available. Rationalizing `1-x/E` as
`(gap/E)*(gap/(E+x))` avoids subtracting two nearly equal numbers. The coarse
bound can be pessimistic and need not certify an economically useful cutoff.

## Numerical falsification and reproduction

The evidence artifact enumerates720 cases: xi=+/-0.001,+/-0.01,+/-0.1,+/-1,+/-10;
beta=2,40,19613.355577892344; gap=0,1e-6,1e-4,0.01; a=0,0.7; b=0,-0.3,0.3.
For each case it records abs(stiffness([(xi,gap,1,a,b)],beta)), B, and a binary64
comparison allowance `64*epsilon*(beta*a*a+8*abs(b))`. All comparisons pass.
The largest unadjusted excess is1.417619379281939e-16; it is explicitly retained,
not rounded into an exact-arithmetic numerical claim. These checks falsify
implementation mistakes in selected cases; the inequalities above supply the
mathematical argument. Ordinary binary64 evaluation is not an outward-rounded
certificate. Include rounding bounds or interval arithmetic before using a
computed B in the registered1% uncertainty budget.

To reproduce, take the Cartesian product of the listed parameter values and use
`linear_response.stiffness` for the slope and the displayed rationalized formula
for B. The complete parameter tuples and intermediate values are public in the
artifact. No native execution or material gap is used by this control.

## Actual scope and next application

After obtaining a qualified gap, this bound could certify omission of a subset
of already represented high-energy states, or transport a justified gap envelope
into a conservative response-tail estimate. It cannot bound the DOS/state support
that was never represented, energy quadrature between nodes, an unknown gap
outside the supplied envelope, low-energy states with xi=0, or errors in band
moments/normalization. A continuum version needs independently bounded absolute
moment measures on the omitted continuum, not just the retained discrete sums.
The band6 normalization finding therefore remains open. No cutoff is applied
and no laptop speedup,1% material certificate or accepted response follows yet.
