# Campaign requirements audit — incomplete

This audits the twelve-hour [specification](../PROJECT_SPEC.md), not the separate
future two-week mandate. Evidence must cover each claim's scope. Passing one
fixture does not close a material-validation requirement. The live
[report](CAMPAIGN_REPORT.md) integrates conclusions; the
[ledger](../RESEARCH_LEDGER.md) owns process state.

## Scientific questions

| Specification question | Owning evidence | Current verdict / missing evidence |
|---|---|---|
| Complete laptop workflow, accuracy and cost | WORKFLOW_COSTS.md; campaign_native_resource_accounting.json; public response pipeline | Several downstream actions measured. Full microscopic cold start, accepted gap and physical response incomplete. Energy and model monetary cost unmeasured. |
| Reusable inputs and invalidation | REUSE_BOUNDARIES.md; GAP_RESPONSE_MAPPING_GATE.md; exact context/hash checks | Fixed-layout reuse documented; momentum state reuse rejected. Cache invalidation regressions pass. No general exact kernel invariance claim. |
| Robust length-scale extraction | response_analysis.py; extraction results/figures; PHYSICAL_INTERPRETATION_GATE.md | Released slope reproduced; peak discrepancy unresolved; fitting sensitivity is not uncertainty. No matched experimental prediction. |
| Small-Q versus scan | LINEAR_RESPONSE_LIMIT.md; SYMMETRY_SCALE_FINDING.md; DIRECTION_AND_ZERO_Q_GATE.md | Analytic limits and selector defect tested. Full production directional small-Q response not qualified. |
| Separate error sources | CAMPAIGN_REPORT.md; ANISOTROPIC_MOMENT_GATE.md; PHYSICAL_INTERPRETATION_GATE.md | Operation-specific averaging bound measured; larger grid/basis/derivative effects remain. Total physical error unbounded. |
| Newly practical scientific decision | CAMPAIGN_REPORT.md | Practical numerical-method diagnosis demonstrated with retained inputs. New reliable material decision remains unproved. |
| Current important gap/demand | CURRENT_LANDSCAPE.md; UPSTREAM_STATUS_AUDIT.md | Existing competitors checked; generic saturation/demand thesis unsupported. No outreach or interviews. |
| Strongest contribution within window | CAMPAIGN_REPORT.md; patches/README.md; public reproduction pipeline | Focused numerical correctness/moment audit is supported. Portable source/input response run passes. Full prediction and final recommendation pending. |

## Required durable deliverables

| Item | Evidence checked | Status |
|---|---|---|
| 1. Clear question/current decision | PROJECT_SPEC.md; DECISION_STATUS.md; CAMPAIGN_REPORT.md | Present, provisional; final continue/narrow/pivot/stop still needed. |
| 2. Retrieval/evidence manifest | retrieval_manifest.json; public_response_inputs.json; public_response_sources.json; source/result manifests | Present; public source and input hashes verified on acquisition. Isolated response run PASS33.24s/187MB; all8exports bitwise match. |
| 3. Complete workflow/cost ledger | WORKFLOW_COSTS.md; resource_accounting.py + regression; historical source-clock manifest | Present with explicit unknowns. Final terminal-attempt accounting must be refreshed. |
| 4. Tested code/runnable commands | research tests; public CI; PUBLIC_RESPONSE_REPRODUCTION.md | Latest local126 tests pass (10.824s), compileall excluding raw, moment-refinement replay and diff check pass. The earlier Mac-only import failure was fixed with a subprocess regression; public CI through59ce422 passes. Exact48/64protocol and composition fixtures pass; their new native experiments remain pending. Public response,897-point bands and separate2769-point serialization/48response integrations pass. |
| 5. Standalone figures/provenance | figures/README.md; PNG/PDF and source hash files | Present. Rank37 validation figure visually inspected; final snapshot must match final results. |
| 6. Reproduction/sensitivity | archived Nb gate; extraction figures; direction/refinement and moment analyses | Present with bounded claims. Peak extraction, derivative and physical gates unresolved. |
| 7. Qualified improvement/held-out validation or no-improvement verdict | thermal/current/RHS fixtures and high-precision controls; second-moment exact identities; candidate full checks | Specific numerical corrections and diagnostics supported; no qualified total material-response improvement. Final scope/validation judgment pending. |
| 8. Current alternatives | CURRENT_LANDSCAPE.md; UPSTREAM_STATUS_AUDIT.md | Present, targeted rather than exhaustive; no empty-field claim. |
| 9. Negative results/uncertainties | CAMPAIGN_REPORT.md; failed full residual receipts; mapping/physical gates; build failures | Present. Do not turn local failures into global impossibility claims. |
| 10. Final recommendation | CAMPAIGN_REPORT.md | Incomplete while decisive bounded experiments run. |

## Final verification still required

Inspect the complete maintained change paths, including source acquisition,
interface/build patch, input staging, terminal guards, native output parsing,
state mapping, signed-weight bounds and public claims. Run the final research
suite and maintained-source compilation check, inspect public CI and repository
synchronization, refresh compute inventory, and verify the documented standalone
native path actually runs or preserve a bounded, explained failure.

An accepted stationary residual requires both unchanged targets. A physical
prediction additionally needs conditioning, discretization, functional and
normalization evidence. If those remain open, the final report must explicitly
reject a reliable-material-access claim and identify the exact decisive missing
experiment. No completion is established by this audit.
