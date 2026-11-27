# Released V3Si extraction: additional finite-window controls

## Question and raw evidence

Can point selection or local peak discretization explain the discrepancy between
released extraction routes? This is a saved-data analysis, not a new solver or
a validated experimental prediction. Seven original curves and fflo_j.sh are
checked against retrieval_manifest.json before analysis. The processing script
averages the two current estimates into column4; column3 is the filename's
momentum parameter, not another current. Only nonnegative Q is released in these
curves. Separate-current agreement and empirical odd parity therefore cannot be
recovered from this processed artifact. No synthetic reflection counts as data.

## Method and independent controls

Run `python3 research/finite_window_controls.py`. It records every source hash
and returns deterministic first-four-point leave-one-out origin-constrained
linear slopes, three/four-point odd-cubic fits j=aQ+bQ^3, and local three-point
quadratic interpolation of the sampled current maximum. Cubic Q is scaled by
the window endpoint before solving the two-parameter normal equations. A local
peak is accepted only for a concave parabola with its vertex inside the adjacent
sampled bracket. Analytic linear/cubic and irregular-grid parabola fixtures
validate these numerical operations, not the physical fitting assumptions.

All length ratios use the same conversion lambda proportional to slope^(-1/2).
The odd-cubic model imposes parity. Its fitted intercept is a model-dependent
Q-limit estimate, not empirical evidence that the cubic truncation is adequate.
Point removal checks leverage and window dependence; it is not statistical
resampling and produces no confidence interval. Raw negative-tail values are
reported without classifying them as physical instability or a code error.

## Result and implication

At1K, leave-one-out first-four linear length ratios span1.25159–1.52618
relative to the author's single-point result. Three/four-point odd-cubic ratios
are1.00115/1.04963. Across seven temperatures, three-point cubic ratios range
0.97824–1.00115 and four-point ratios0.95670–1.05308. Agreement of the smaller
fit with the first point does not establish asymptotic accuracy.

At1K, local peak interpolation gives Q=0.0090607195Ang^-1 and current
1.27087764e-6reportedau, versus the sampled1.25867e-6. With the existing
half-gap estimate held fixed, the peak-route length scales by0.99519: roughly
177.09nm becomes176.24nm. This local interpolation does not reconcile136nm.
It does not rule out other extraction/functional/sample/provenance explanations.

The1Kcurve has two negative-current tail samples and the other six each have
one. The files alone do not identify their numerical/physical cause. Resolving
that needs raw separate currents, convergence histories and compatible states.

This analysis makes a concrete reliability decision possible without another
SCDFT run: local peak interpolation is not a sufficient explanation of this
released discrepancy, and broader linear-window fits are not robust replacements
for the initial slope without a justified model. Future native effort should
address compatible states and theoretical extraction definitions rather than
tuning a fit to the published number.

Verification: `python3.13 -m unittest discover -s research -p 'test_*.py'`
passes130tests in10.371s. Maintained-source compileall excludingraw,
`python3.13 research/moment_refinement.py` and `git diff --check` pass.
The new fixtures include changed persisted input rejection.
