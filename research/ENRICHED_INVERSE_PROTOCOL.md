# Prospective augmented-inverse gate

Registered before measuring an augmented inverse. Same8.05K base candidate,
D/operator/Z/geometry and original51-column Q/U; append the three accepted
orthogonalized D*v trial inputs and their complete A actions only after full
joint-action acceptance. Original Q/U/P and candidate remain immutable.

Let Q+= [Q,trial], U+= [U,A*trial], P+ stack the accepted old P with extra P.
Choose M+=I-Q+^T*D*U+, W+ by solving M+*W+=I, and
B+=I+U+*W+*Q+^T*D. For arbitrary fixed Q+/U+/W+, not just an exact small inverse,

    C+=W+*(P+-Q+^T)
    I-B+*(I-A*D) = (A+U+*C+)*D.

No dense n*n allocation is needed. Numerical acceptance must check all small
matrix entries independently, both M*W-I and W*M-I, finite solved spectrum and
chosen W, exact parent bindings, and independent selected C coefficients/row
sums with cancellation-aware bounds. A small-matrix singular ratio is not the
full Jacobian condition. A successful small solve is not a certified inverse.

## Fixed rows and decision

Training left1/32/64. Held-out left65/33434/66867 and right1/33970/67940
(global right offsets66867). These were fixed in SENSITIVITY_ENRICHMENT.md before
new A actions or any augmented inverse were measured. Full joint-action pass
retains complete original K1 rows and K2 rows at those indices.

Compute complete ordinary-binary64 row sums of I-BJ for both old B and new B+,
using the same saved full kernel rows and context. Reproduce old training-row
sums against the accepted prior diagnostic. Report all nine results, including
failures, and distinguish training from held-out. Do not tune columns, solve
thresholds, row identities or metrics to these held-out results.

If any held-out row reaches/exceeds one, reject this candidate's unweighted
infinity-contraction route and do not spend a full second sweep on it. A training
failure likewise disqualifies that route. If every tested row is below one,
that only clears this selected rejection gate: a separately admitted full-space
sweep, outward numerical bounds and radius/error-transport argument are still
required. Neither a relative improvement nor sampled agreement suffices.

No adoption of a corrected gap, uncertainty bound, new physical response or
claim that this scheme is generally useful. All physical normalization, grid,
other-temperature, acquisition and independent-reference gates remain open.
This protocol admits no new compute or expansion on its own.
