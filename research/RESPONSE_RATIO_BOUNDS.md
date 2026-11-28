# Conditional normalized-response enclosure

The campaign requires uncertainty on S(T)/S(Tref), not just each stiffness.
The conditioning protocol already requires a denominator interval excluding
zero, but supplied no executable arithmetic check. The new separate
`response_ratio_bounds.stiffness_ratio_interval` implements that requirement
without changing the stiffness routine or assuming common errors cancel.

Given independently justified absolute errors eN,eD >= 0 around finite binary64
centers N,D, form the exact rational intervals [N-eN,N+eN] and [D-eD,D+eD].
Reject the denominator interval if it contains zero. Otherwise N/D is continuous
and monotone in each coordinate with the other fixed; its extrema over this
rectangle occur among the four endpoint ratios, including signed numerators
and negative denominator intervals. Evaluate those corners with Python Fraction
and convert the extrema to binary64, moving one adjacent float outward when
nearest rounding would exclude the rational endpoint. Overflow is rejected.
Subnormal endpoints and underflow to signed zero receive the same treatment.

In simple terms, this keeps division from concealing uncertainty in the reference
stiffness. It encloses all pairs in the supplied intervals; shared errors may
make it conservative, but no undocumented cancellation is taken. A denominator
interval containing zero gives no finite ratio enclosure under these assumptions.

Exact rational corner arithmetic was selected because only four divisions are
needed: it avoids a new interval dependency or an unqualified epsilon margin.
It does not make the preceding floating Lipschitz coefficient outward-rounded,
produce a gap-error radius, certify a stiffness interval, or account for missing
physics. Only the propagation of the supplied binary64 interval data is enclosed.
No material normalized-response or1% acceptance follows from this helper alone.

Three regression tests compare signed numerator/denominator intervals against
100-digit Decimal corner/interior evaluations (1350 points), check exact rational
containment and tight outward rounding for1/3 and subnormal quotients, exact
representable ratios, zero numerators, and reject zero-crossing/touching, negative
errors, nonfinite inputs and binary64 overflow. Narrow suite PASS in0.008s.

Final gate:214tests PASS24.137s including native fixture builds;212maintained
Python sources compile PASS; moment_refinement exit0; git diff --check PASS.
No separate configured typecheck. No native production source changed.
