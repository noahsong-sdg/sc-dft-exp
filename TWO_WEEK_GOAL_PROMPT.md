# Two-week autonomous research goal: scientifically useful superconducting response on a laptop

## Objective

Work autonomously on `sc-dft-exp` for a fourteen-day research campaign, pursuing the most scientifically consequential contribution justified by our evidence and available hardware. I will be unavailable for routine questions. Use your judgment to research, implement, verify, document, and publish relevant progress to the existing public repository:

https://github.com/noahsong-sdg/sc-dft-exp

The central question is whether reusable microscopic inputs, sound numerical methods, and improved computation can make **reliable superconducting response calculations accessible on commodity hardware**, enabling a specific scientific decision that was previously impractical. Faster reproduction alone is insufficient. A rigorous correction, an independently useful validity map, or a demonstrated limitation may be more valuable than a broad platform.

Treat fourteen days as a maximum campaign duration, not a requirement to consume resources or manufacture a positive result. Record the actual start and end in UTC when execution begins. Work only through execution facilities that actually exist. Do not claim that a prompt, an idle chat, or an unconfigured automation provides continuous background execution. Make the work restartable across sessions, context loss, and machine restarts.

This file is the reusable two-week mandate. It extends the scientific intent of `PROJECT_SPEC.md`; its old twelve-hour deadline is historical when this campaign is explicitly started. Do not reinterpret this prompt-writing request itself as evidence that fourteen days of execution have already been scheduled.

The completed twelve-hour campaign's latest handoff is `CAMPAIGN_STATE.md` and
`research/CAMPAIGN_REPORT.md`, including the held-out grid reversal and final
recommendation. Recover that evidence before treating any earlier starting
hypothesis below as a reason to repeat work or expand compute.

## First action: recover and audit the real state

Read `AGENTS.md`, `PROJECT_SPEC.md`, `RESEARCH_LEDGER.md`, the research documentation, recent commits, and the working-tree diff. The primary checkout is `/Users/noahs/Developer/sc-dft-exp`. Preserve unrelated work and the dirty historical checkout at `/Users/noahs/Developer/flux-pinning`.

Create a compact campaign state file linked from the README and AGENTS entry point. Maintain the current hypothesis, evidence supporting and contradicting it, unresolved questions, compute consumed, active processes, next executable step, and stop conditions. A future agent must be able to resume without relying on conversational memory.

Verify the current Mac model, CPU, RAM, free disk, compiler/toolchain, existing software builds, and competing machine load. Previous observations of Apple Silicon and 32 GiB RAM are leads, not current measurements. Inspect existing processes before launching work. Do not terminate unrelated processes or change system settings to obtain resources.

Audit pending changes before adopting them. Inspect live process ownership and persisted launch watchers before starting native work: a waiting watcher can launch a job later. Existing changes, compiled executables, and passing fixtures do not establish that a method is committed, independently reviewed, or physically qualified.

## Starting evidence and unresolved findings

Revalidate the following against the owning artifacts before making consequential claims:

1. The pinned SCTK `supercurrent` routine showed discrepancies between its normal-reference thermal factors and independently derived expressions. A two-line correction passed initial fixtures but failed 18 of 81 boundary fixtures. A more stable treatment of the saturated thermal branches passed the tested grid. An independent high-precision scalar oracle supplied an additional check. These are synthetic numerical findings; material-level significance remains unestablished.
2. Released V3Si response curves support a slope-route penetration-depth reproduction near 97.6 nm versus a published value near 97 nm after correcting our own unit-conversion error. A peak-route value near 177 nm versus a published 136 nm remains unresolved. Trace definitions, provenance, and assumptions before attributing that difference to the paper or solver.
3. An inspected archived V3Si state file uses a legacy record format without the band-curvature field needed for the current response routine. It is not a complete material replay fixture. Establish whether matching inputs can reconstruct the missing quantities or whether a fresh state dump is necessary.
4. Released workflow logs suggest expensive interaction preparation can dominate the cost of a selected response calculation. Their core counts and mixed-job provenance prohibit treating those timings as Mac forecasts or summing every clock blindly.
5. Current competing methods weaken any unsupported claim that inexpensive superconducting response is an empty field. Review current SCTK, EPW, IsoME, finite-momentum methods, stiffness methods, and relevant reduced models before selecting a contribution.

Use these as falsifiable starting points. Do not inherit a preferred conclusion, extrapolated speedup, claim of unmet demand, or hypothetical model capability as established evidence.

Subsequent campaign evidence provides stronger leads to audit in the ledger and owning artifacts:

6. Full-routine tests extended the thermal finding to the gap-equation right-hand side and exposed a separate zero-energy product boundary in the current routine. Passing numerical tests establish the tested identities and boundaries; they do not establish the size of a material-level correction. Check adjacent zero-energy limits separately, including their temperature domain.
7. A native niobium diagnostic found that squaring a DOS-averaged velocity can differ substantially from retaining its second moment. On the tested grids, a signed second-moment reconstruction matched the corresponding fine-grid constant-gap quadrature to floating-point precision. First-moment results changed markedly with response-grid refinement. Signed integration weights and discarded support complicate interpretation; this is not yet a validated penetration-depth prediction.
8. A compatibility probe using pinned current geometry routines reproduced the historical fully shifted niobium output. This checks a specific execution path, not the complete current SCTK build or every shift convention. Held-out direction and unshifted-band controls remain important qualification steps.
9. Archived niobium gap states matched some geometry and indices but lacked sufficient temperature and convergence provenance; their extracted gap scale did not match the inspected released temperature series. Do not promote those states to qualified microscopic inputs or tune their scale to obtain agreement.

Prioritize qualifying or falsifying the reusable response-moment route before building a general workflow. Determine whether it preserves the intended microscopic response, whether the apparent discrepancy reflects a closure error or different physical approximations, and whether usable equilibrium gap inputs can actually be obtained. Consult `research/PHYSICAL_INTERPRETATION_GATE.md` and the ledger for the latest unresolved gates. These findings are a starting hypothesis, not a commitment to a positive result.

## Choose the consequential scientific question

Identify a concrete user and decision: what quantity do they need, to what accuracy, under which physical conditions, and what would they do differently after receiving it? Distinguish bulk pairing predictions from transport performance, disorder, defects, pinning, grain boundaries, and engineering current limits. Do not imply that a clean bulk calculation answers REBCO tape or fusion-magnet questions without the necessary additional physics.

Compare a small number of plausible contributions using scientific importance, present evidence, novelty, independent verifiability, laptop feasibility, and opportunity cost. Select one primary contribution and at most one supporting line of work. A bounded correctness and material-impact study may outrank an ambitious but unverifiable materials search.

For the selected contribution, write an explicit success thesis: the beneficiary, previously impractical decision, limiting step, proposed intervention, accuracy required, observable demonstration, and evidence that would kill the thesis. Check recent primary literature and current repositories, releases, documentation, and public discussions. Old issues cannot carry a present-demand claim. Separate demonstrated demand from inferred usefulness. Do not contact people without separate authorization.

## Start from raw, inspectable evidence

Prefer original source at pinned revisions; full input decks; raw solver outputs; restart files; convergence histories; exact extraction scripts; compiler and library versions; and experimental records with sample conditions. Read the defining equations and approximations, not only abstracts or summaries.

Record URLs, retrieval dates, revision identifiers, hashes, units, schema, and transformation steps. Keep raw and derived artifacts separate. Inspect listings and use bounded retrieval before downloading large archives. Respect licenses and redistribution conditions. Public documentation may link to restricted or non-redistributable inputs without copying them.

Trace every claimed result from raw input through executable code and numerical extraction to the stated physical observable. Label missing provenance and unavailable inputs explicitly. Never silently substitute an incompatible material, schema, approximation, or temperature to complete a story.

## Correctness before optimization

Before code changes, trace the relevant execution path and state the root cause. Derive the relevant identities independently. Use dimensional analysis, zero-gap and zero-momentum limits, parity, normal-state cancellation, near-degenerate energy limits, and other applicable invariants. Determine which tests are physically necessary for this implementation rather than adding generic checks.

Retain adversarial fixtures that distinguish the original implementation, the minimal candidate, and the stable candidate. Examine cancellation, overflow, underflow, finite-temperature boundaries, precision, and compiler optimization. Use high-precision arithmetic as an independent oracle where practical; document its own assumptions and domain.

Verify changes in the full owning routine and then in a real material workflow if inputs permit. Check serial and relevant parallel behavior. Agreement on a synthetic fixture does not establish a physical correction, and two codes sharing an equation or dataset do not provide fully independent validation.

Make the smallest coherent root-cause fix. Preserve public behavior outside the intended correction. Add meaningful regression tests, including legacy persisted-data cases where relevant. Avoid unrelated refactors and speculative abstractions. Keep each PR single-purpose and below 700 lines of non-test code. Explain the problem, its technical and plain-language cause, the fix, and why it was chosen over viable alternatives.

## Prove whether the laptop can do useful work

Build a measured end-to-end cost model separating electronic structure, phonons and electron–phonon inputs, Coulomb preparation, kernel construction, gap solution, response evaluation, convergence studies, and extraction. Mark measured costs, projections, and unknowns separately.

Establish exactly what can be reused across temperature, momentum, and repeated analyses, and what changes invalidate reuse. Distinguish an approximation that freezes kernels from an exact physical invariance. Include both cold-start and amortized costs. A cheap downstream calculation with inaccessible upstream inputs is not an end-to-end laptop solution.

Start with short representative pilots. Estimate scaling and expected information gain before longer runs. Record wall time, CPU time, thread count, peak memory, storage, and energy only when measurable without intrusive tooling. Do not report fabricated energy estimates or convert cluster core-hours into Mac wall time without a calibrated model.

For this campaign, use an initial budget of four native laptop wall-hours for feasibility pilots. Expand to sixteen cumulative hours only if the pilot demonstrates a credible scientific path. Expand further only when recorded measurements justify the expected scientific return, with a hard campaign ceiling of 100 native compute wall-hours and one heavy job at a time. These are ceilings, not targets. Do not let a forecasted job extend beyond the campaign without a documented checkpoint and termination plan. Reserve memory and disk for normal laptop use; monitor resource pressure and stop the research job if it destabilizes the machine.

No paid APIs, cloud machines, purchases, credentials changes, or system-level installations requiring new trust decisions. Existing tools and reversible project-local dependencies are available within authorized scope. Do not launch huge screening campaigns because they are easy to automate.

## Optimize only the demonstrated bottleneck

Use profiles and representative measurements to choose optimizations. Consider algorithmic reuse, removing repeated work, matrix-free evaluation, better quadrature, controlled interpolation, symmetry, adaptive sampling, vectorization, threading, and reduced representations only where applicable. Bound approximation error in the final observable.

Maintain separate baselines for identical mathematics and changed approximations. Report speedup together with accuracy, problem size, hardware, compiler, memory, setup cost, and reproducibility. Check whether a local acceleration changes total workflow cost using measured fractions. Amdahl's law and missing upstream inputs can invalidate an otherwise impressive kernel benchmark.

Do not assume that model intelligence implies arbitrary speedups or that a three-to-four-order-of-magnitude compute deficit is tractable. Estimate achievable reductions from the actual equations and measurements. Conversely, do not reject a high-value problem solely because the unoptimized implementation is expensive: first test the strongest defensible computational route within the pilot budget.

## Demonstrate scientific benefit

Prefer one deeply verified material-level result over many weak scans. Establish convergence with respect to the parameters that matter for the chosen observable. Separate numerical error, microscopic-input error, functional/model error, extraction assumptions, and experimental sample mismatch. Sensitivity to a fitting window is not automatically a statistical confidence interval.

If investigating response extraction, determine the valid regime of slope-based, peak-based, finite-Q, and reduced-model relations. Trace low-temperature and multiband assumptions. Seek an observable distinction that exceeds justified error bounds. Resolve discrepancies by derivation and provenance rather than tuning conventions to match a published number.

A strong positive result identifies a newly practical scientific decision and reproduces it from documented inputs on the Mac. A strong negative result establishes a bounded impossibility or failure regime, identifies the dominant bottleneck or missing information, and gives others a usable criterion for avoiding wasted work. Failure to obtain inputs or inconclusive runs alone is not a scientific negative result.

## Independent standards for being right

Specify external checks before interpreting outcomes: analytic limits, a separately implemented high-precision reference, independent formulations with understood assumptions, released benchmark data, convergence, and suitable experimental measurements. Identify dependencies shared by supposedly independent checks.

The standard is evidence another researcher can inspect and reproduce, not agreement between agents or confidence in a narrative. State precisely what each check validates and what it leaves open. Do not call results decision-grade until the decision, tolerance, validation domain, and failure conditions are explicit and met.

## Campaign cadence and stopping rules

Use the first two days to audit, reproduce, establish feasibility, and select the strongest thesis. Use the middle period for the decisive implementation and experiments, revising the thesis when evidence requires it. Reserve the final several days for independent checks, clean reproduction, interpretation, and public documentation. These are planning guides; do not wait for calendar milestones to advance or kill a failed route.

At every substantial checkpoint, compare expected scientific value against remaining compute, execution time, and model usage. Prefer informative tests over repetitive literature searches or unchanged monitoring. Persist logs for running jobs and resume intelligently after interruption.

Stop or redirect a line when its result is already adequately available, its distinguishing effect is below justified uncertainty, necessary inputs cannot be obtained within scope, cost exceeds the measured budget, or the result cannot support the stated decision. Document the reason and pursue the strongest remaining bounded alternative. Do not expand into unrelated superconductivity projects to keep working.

## Public deliverables and completion

Publish relevant progress to `sc-dft-exp` after checking for private information, unrelated changes, secrets, and redistribution restrictions. Keep claims proportional to evidence. Do not send outreach, submit a paper, or speak on my behalf without separate authorization.

Deliver a clear README entry point; the campaign state and evidence ledger; a concise scientific report; pinned source and input manifests; reproducible scripts and environment instructions; regression tests and exact check results; measured compute accounting; figures with units and captions; and an explicit verdict on the original thesis. Include failed candidates when they teach a specific reproducible lesson.

At the final gate, inspect the complete changed execution paths and adjacent invariants. Run required repository build and typecheck commands where applicable, plus the narrow scientific and regression checks needed for the claims. Verify the public repository actually contains the intended artifacts. Report limitations and unresolved discrepancies plainly.

Finish with the strongest supported answer to: **What can someone now calculate, decide, or rule out that they could not practically do before, and what independent evidence establishes that?** If that answer is still inconclusive, say so, identify the decisive missing experiment or input, and leave an exact restart point. Do not claim completion merely because the two weeks elapsed.
