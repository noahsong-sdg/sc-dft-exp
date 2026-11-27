# Twelve-hour campaign acceptance audit

This audits [PROJECT_SPEC.md](../PROJECT_SPEC.md), not a scheduled two-week run.
All registered native controls are terminal and strictly read back.
Open physical gates are limitations of the scientific answer, not passed tests.

## Questions answered within the available evidence

| Question | Evidence inspected | Verdict |
|---|---|---|
| Laptop workflow, accuracy and cost | WORKFLOW_COSTS.md; native receipt ledger; public source/input runs; PORTABLE_GAP_GATE.md | Several downstream actions fit this M5 / 32 GiB Mac. Full microscopic cold start, fresh Z/basis, energy/billing and total physical error remain unknown. Rank 38 stationary residuals pass. No global hardware-impossibility claim. |
| Reuse and invalidation | REUSE_BOUNDARIES.md; GAP_RESPONSE_MAPPING_GATE.md; input/context/stale-state tests | Fixed-context diagnostics reuse bands/caches. Assigned state reuse across Q is not exact; layout, DOS and gap changes require qualification. |
| Length-scale extraction | Original curves/scripts and hashes; response_analysis.py; FINITE_WINDOW_CONTROLS.md | Slope reproduction succeeds; peak discrepancy remains. Window sensitivities are measured; positive-Q averaged curves cannot establish empirical parity or separate-current agreement. |
| Small-Q versus scans | LINEAR_RESPONSE_LIMIT.md; SYMMETRY_SCALE_FINDING.md; DIRECTION_AND_ZERO_Q_GATE.md | Analytic limits and selector defect tested. Full production directional small-Q response is unqualified. |
| Error separation | Moment/anisotropic bounds; full residuals; grid/stencil and held-out 64 controls | Specific numerical operations and sensitivities separated. Total material error is not bounded. Third-grid reversal blocks simple monotone extrapolation. |
| Newly practical decision | Public native diagnostics and CAMPAIGN_REPORT.md | A working numerical-validity audit can reject misleading convergence/closure claims. New reliable material prediction and previously impossible access are not demonstrated. |
| Current alternatives and demand | CURRENT_LANDSCAPE.md; UPSTREAM_STATUS_AUDIT.md; current QE source identity | Direct overlapping methods exist. No empty-field, novelty or unmet-demand claim; no interviews/outreach. |
| Strongest supported contribution | Public regressions; exact 32/48 exports; rank 38 full check; registered 64 holdout | Narrow to reproducible numerical reliability plus a qualified exact downstream optimization. Further material work is gated on portable inputs and physical qualification. |

## Required deliverables

| # | Deliverable and owning evidence | Acceptance scope |
|---|---|---|
|1| Question/decision: PROJECT_SPEC.md; CAMPAIGN_REPORT.md; DECISION_STATUS.md | NARROW; no decision-grade material claim. The regeneration control does not change this verdict. |
|2| Retrieval manifests: retrieval_manifest.json; public_response_inputs.json; public_response_sources.json; per-run manifests | Pinned URLs/revisions/bytes/hashes; relevant raw data remain separate from derived public results. |
|3| Complete stage/cost ledger: WORKFLOW_COSTS.md; campaign_native_resource_accounting.json; source-clock and basis audits | Every workflow stage is measured, historical, projected or explicitly unknown. Final accounting: 79 attempts / 11,357.647 s, below four native wall-hours. |
|4| Tested code/commands: public source build/staging/readback; PUBLIC_RESPONSE_REPRODUCTION.md; offline suite | 135 local tests PASS, 9.362 s; compileall, moment replay and diff check PASS. Automatic 32 bands/serialization/response all PASS. Public Ubuntu CI 46017822969 passes on retry; initial setup failed at an unrelated Microsoft feed HTTP 403. |
|5| Standalone figures/provenance: figures/README.md; PNG/PDF/source hashes | Rank38gap/anisotropic and two-/three-grid figures generated and visually inspected. No invented confidence or physical-error bars. |
|6| Reproduction/sensitivity: archived Nb; V3Si extraction; moment, direction, stencil/grid controls | Reproduction and negative controls preserved. Physical and missing-data boundaries explicit. |
|7| Qualified improvement or justified rejection | Exact indexed lookup: 1920 compiled cases and eight bitwise native exports at 32/48; combined fourth 48 also exact. Rank 38 passes both stationary targets. Held-out 64 reversal retained. No qualified total physical-response improvement. |
|8| Current alternatives | Current primary-source/repository audit; limited search scope recorded. No adoption or researcher demand claimed. |
|9| Negatives/uncertainties | Failed native/build/residual receipts; grid reversal; finite-window/extraction and physical/portability gates | Failures are not relabelled as passing or generalized into global impossibility. |
|10| Final recommendation | CAMPAIGN_REPORT.md | NARROW to the validity study; stop broad material screening. Next gates: portable gap build/inputs, measured complete setup, independent physical qualification. |

## Execution-path review and verification

The review follows public acquisition and source compatibility through build,
input staging, the normal-pressure/hash launch gate, terminal receipt checks,
XML/a2F serialization, native/cache context, response components and registered
comparisons. It also checks the retained gap dependency boundary, signed-weight
identities, extraction conventions and current public claims. This is an agent
review with executable controls, not independent scientific peer review.

Adjacent invariant fixtures cover changed/legacy inputs, wrong parent or grid,
wrong deadlines/defaults, copied identities, energies/weights, missing or duplicate
exports, nonfinite cache data, temperature/gap/context changes and altered
prospective sources. Historical manifests remain immutable; a changed staging
script is not silently adopted into an old execution identity.

Final code checks: `python3.13 -m unittest discover -s research -p 'test_*.py'`
PASS, 135 tests / 9.362 s; maintained-source `compileall` excluding `/raw/` PASS;
`python3.13 research/moment_refinement.py` PASS; `git diff --check` PASS.
Strict final 32 serialization/response and registered comparison commands PASS.
Figure source hash checks and public synchronization are recorded in the ledger.
There is no separate configured typecheck. Maintained Python compilation and
native compiled fixtures/integration are the applicable build checks. CI runs
the offline native fixtures and moment replay on Ubuntu; it does not rerun the
Mac QE integration or validate the material physics.

The acceptable terminal answer is a bounded methods contribution plus a rigorous
explanation of the unproved material-access thesis. No open physical acceptance
gate may be reclassified as completed prediction work.
