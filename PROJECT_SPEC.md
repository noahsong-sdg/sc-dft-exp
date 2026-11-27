# Autonomous superconducting-response research specification

## Mandate and duration

User-authorized twelve-hour research window. The earlier two-week proposal is
adapted to twelve hours, not an instruction to wait two weeks. Initial durable
checkpoint: 2026-11-27 05:41 UTC (26 November in America/Los_Angeles).
Target window end: 2026-11-27 17:41 UTC. Time is a ceiling, not proof of success.

Work autonomously on sc-dft-exp, pursuing the most scientifically consequential
contribution supported by evidence and available hardware. Continue research,
implementation, verification, and public documentation without routine user
input. Determine—and if justified demonstrate—whether reusable microscopic
inputs and improved computation make reliable superconducting response
calculations accessible on commodity hardware, with scientific benefit beyond
reproducing existing results faster. Preserve this full objective across restarts.

Use actual execution facilities; never imply work continues while inactive.
Maintain restartable evidence and checkpoints. Keep the thread goal active until
the complete objective and deliverables are verified or a genuine blocker meets
the goal system's repeated-blocker threshold.

## Workspace and starting evidence

Public owner: https://github.com/noahsong-sdg/sc-dft-exp . Local checkout:
/Users/noahs/Developer/sc-dft-exp . Historical research checkout:
/Users/noahs/Developer/flux-pinning (dirty; preserve unrelated changes).

Read historical benchmarks/isome-sctk-broader-v1/optimization-frontier-v1/
REPORT.md, OPPORTUNITY_AUDIT.md, FINITE_Q_TRACE.md, analyzer/tests, source
manifests and relevant native receipts. Historical documents are evidence leads,
not proof of present behavior. Verify current hardware, available resources,
inputs and upstream revisions. Expected hardware: Apple Silicon, 32 GiB RAM.

Primary method: https://doi.org/10.1103/lrhl-j9bt ; inspectable supplement:
https://arxiv.org/html/2603.05123v2 . Data:
https://mkawamura.ynu.ac.jp/data/ and
https://arim.mdx.jp/nextcloud/s/zqS4RXS8zaD26p5 . Code:
https://github.com/mitsuaki1987/sctk .

## Questions and scientific gates

1. What complete workflow fits this laptop, at what accuracy, wall time, memory,
   storage and energy cost where measurable?
2. Which inputs can be reused across temperature/momentum, and which changes
   require regeneration?
3. How robust are coherence-length and penetration-depth extractions to sampling,
   fitting, convergence and theoretical assumptions?
4. When does a small-momentum calculation resolve the same question as a scan?
5. Separate microscopic-input, functional, solver, extraction and experimental
   uncertainty. Does the predicted difference exceed those uncertainties?
6. What specific scientific decision is newly practical, compared with current
   SCTK, EPW, IsoME and competing response methods?
7. Is there current evidence of an important gap? Old issues cannot carry demand.
8. What strongest independently supportable contribution can fit this window?

Success requires a specific question, a valid method, an actual practical barrier,
a demonstrated improvement, and external verification. Do not assume speed,
novelty, demand, or publication significance. Kill avenues failing value,
identifiability, novelty or feasibility; record why and pursue the strongest
remaining evidence-supported avenue. No forced materials-discovery story.

## Saved-data work first

Pin code revisions and retrieved evidence with dates, URLs and SHA256 hashes.
Keep raw and derived evidence separate. Bound downloads and inspect listings.
Reconstruct original extraction conventions, units, current estimates,
zero-momentum limits, temperature assumptions and GL relationships. Reproduce
published values without silently changing definitions to force agreement.

Test one-point versus multi-point slopes, fitting intervals, parity constraints,
separate current estimates, peak interpolation when justified, sample removal,
temperature dependence, residual-to-observable implications, far-tail behavior,
and compatibility of experimental definitions/disorder/sample conditions.
Use analytic/synthetic controls. Sensitivity ranges are not statistical confidence
intervals. Do not infer physical errors from NaN zero-Q current, negative tails,
or slope/peak differences without derivation and controls.

Leading hypothesis: a reproducible validity map for finite-Q extraction and
cost amortization. Existing records indicate shared kernels across Q, a single
sample slope estimator, and public V3Si multi-temperature response files.
The nonlinear response route differs from our linearized Tc anchor. Verify all.

## Full resource accounting

Ledger stages: relaxation, ground state, dense electronic sampling/velocities,
phonons, electron–phonon matrices, screened Coulomb/spin fluctuations, kernel
construction, nonlinear solve, current, scans, convergence controls/readback,
retrieval/storage/preprocessing. Record hardware and MPI/thread layout.
Distinguish CPU, wall, allocated and accepted-result cost. Never extrapolate
laptop time by multiplying cluster wall time by cores. Model both new-material
and reusable-input costs. Unknown remains unknown until measured or bounded.

Initially authorize up to four laptop wall-hours for a justified native pilot;
another twelve hours is conditional on a useful target and validation route.
The prior cumulative 100-hour allowance is an absolute ceiling, not permission
to exceed the twelve-hour campaign or run uncontrolled concurrent jobs. Expand
only after a recorded decision establishes question, validity, bounded forecast,
no cheaper answer, acceptance/stop conditions and worthwhile information gain.

Keep laptop usable; inspect active jobs first. Avoid swap, uncontrolled storage,
heavy concurrent jobs and repeated failures. Checkpoint bounded jobs. No cloud
purchases or new paid services. Use available models/tools thoughtfully.

## Implementation and optimization

Trace bottleneck before edits. Consider exact reuse, setup deduplication,
parallelism, contractions, continuation, and better algorithms based on measured
fractions. Approximate compression needs error controls. Do not count existing
gains again or multiply overlapping microbenchmarks. Measure complete accepted
scientific-result cost including setup, failures and validation.

Freeze baseline/protocol; compare appropriate outputs; check invariants and
edge cases; validate held-out momentum/temperature/material; report time,
memory and accuracy. Explain problem, technical/plain causes, fix and chosen
alternative. Small coherent changes, regression tests, stale-data cases when
needed, narrow iteration checks and final required build/typecheck.

## Novelty, rights and validation

Inspect current papers, docs, source, examples, applications and data across
alternative tools. No unsupported first/unique/decision-grade/no-cluster claims.
No outreach without explicit authorization; drafts are permitted. Absence of
researcher interviews limits demand claims. Conventional SCDFT does not solve
REBCO tape engineering performance.

Validate with analytic limits, published numerical reproduction, unmodified
upstream comparisons, independent extraction, cross-code checks where physical
approximations overlap, matched experiments and preregistered held-out cases.
Shared inputs do not establish independent experimental agreement. Do not tune
to holdouts. Log hypothesis and acceptance changes.

Publication of relevant progress is authorized. Exclude private data, credentials,
unrelated work and third-party files without redistribution rights. Prefer
retrieval scripts, links, hashes and derived results if rights are uncertain.

## Required durable deliverables

1. Clear question and current decision.
2. Reproducible retrieval/evidence manifest.
3. Complete workflow map and cost ledger (explicit unknowns permitted).
4. Tested analysis code and runnable commands.
5. Standalone figures with units/provenance.
6. Reproduction and sensitivity findings.
7. Any qualified improvements with held-out validation, or an evidence-based
   decision that no improvement is justified.
8. Comparison with current alternatives.
9. Negative results and unresolved uncertainties.
10. Final continue/narrow/pivot/stop recommendation.

Commit coherent milestones and synchronize verified public progress. Final
report must explain what was learned, what it enables, who could use it, evidence
and limitations. An acceptable terminal result is either a validated contribution
to accessibility/reliability of a specific response study, or a rigorous,
reproducible explanation for stopping with the limiting stage and strongest
alternative. Do not redefine success to a small passing subset. Verify every
deliverable before claiming completion. Optimize information per token/hour;
avoid redundant planning and reviews.
