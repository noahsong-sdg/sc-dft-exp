# Held-out boundary grid rejects minimal correction as sufficient

`python3 research/threshold_probe.py` compiles the complete two-line-corrected
routine on 81 synthetic combinations of beta=(2,20,100), shift=(.2,1,2),
x=shift+(-.01,0,.01), gap=(0,.1,1), and asymmetric weights. Eighteen cases
exceed 5e-5 absolute tolerance against independent direct shifted occupations.
At x=d=2, gap=.1, beta=20, candidate current=4.1011 while direct=0.0517828263.
These are dimensionless fixtures, not material error predictions.

Root cause: the saturation criterion tests tanh(beta*x/2)*tanh(beta*d/2)
near one, but x and d can both be large while x-d is thermally small. The
shortcut discards this finite difference and jumps to a zero-temperature branch;
at equality the omitted half-occupation is especially clear. The same issue
can affect superconducting energy E versus d. This failure justifies testing
a wider thermal-factor correction, not adopting the two-line candidate.

Next candidate: evaluate shifted sums/differences stably in saturated branches,
retaining the quotient away from them. Compare current, continuity, normal limit
and runtime. Direct tanh differences can lose tiny tails, so specify absolute
error targets and test extremes. The original four fixtures remain valid but
are insufficient evidence of general correction. No production fix adopted.

## Stable saturated-branch candidate

The next candidate retains corrected regular quotients and replaces only the
saturated shortcuts by direct shifted tanh sums/differences. On the same frozen
81-case grid it has zero failures at an absolute current tolerance 1e-7;
maximum difference is 2.1711e-8. The harness expands WRITE precision to 16
digits for this comparison; that diagnostic-only edit does not change arithmetic.
Exact results are in threshold_results.json. This tolerance is a fixture-level
numerical criterion, not a physical error bound or a preregistered material
acceptance tolerance. The residual discrepancy comes from the retained quotient
near saturation and needs high-precision/continuity checks.

No whole-solver speedup or physical accuracy is claimed. This candidate is wider
than the two-line fix because a demonstrated independent threshold defect made
that fix insufficient. The next held-out tests should include smaller gaps,
extreme inverse temperatures, threshold crossings, independent high-precision
occupation evaluation and OpenMP execution where supported.
