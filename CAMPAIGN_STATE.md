# Active two-week campaign — current restart state

Objective: reliable superconducting response calculations on this laptop, with
public progress in sc-dft-exp. **Not achieved.** Started27November2026 at
16:33:55UTC; campaign ceiling11December2026 at16:33:55UTC. Read
[TWO_WEEK_CAMPAIGN.md](TWO_WEEK_CAMPAIGN.md),
[acceptance gates](research/TWO_WEEK_ACCEPTANCE.md),
[goal prompt](TWO_WEEK_GOAL_PROMPT.md) and [ledger](RESEARCH_LEDGER.md).
The earlier twelve-hour audit and NARROW verdict are historical, not completion.

## Active owner and next action

Reduced004 terminalPASS1.473093417007476s/178372608B; strict1365pins,
source/receipt/geometry and independent binary readback PASS. Rank51 candidate
Fermi means0.15338589025376448/0.15248045857965492meV, ~0.104% belowrank50;
coefficient residual6.288372600415926e-17, not full stationarity.
[Result](research/portable_reduced_gap004_result.json).

Rank51 complete full map: all66867leftrows and1448pins certified; exact source,
seed and qualification005 lineage PASS. Independent normalization maxdiff0,
explicit-sum and Jacobian finite-difference checks PASS.
[Complete result](research/portable_full_map_segment016_result.json).
**Both original stationary-residual targets PASS:** Rinf6.09669437161189e-11Ry
<=1e-10; RMSres/gap1.0312693411116765e-6 <=1e-5. This establishes the registered
finite residual gates for this8.05K candidate; conditioned gap error, physical
response and other temperatures remain unqualified. [Milestone](research/FRESH_STATIONARITY_805K.md).

Separate inverse core/driver and independent output readback now pass fixture
checks: exponential derivative, every small matrix entry, both inverse actions,
native signs, singular diagnostics and stale-source/output boundaries. Basis
columns stream to avoid a second ~106MiB payload copy (allocation, not measured RSS).
[Method](research/LOW_RANK_INVERSE_DIAGNOSTIC.md).
Inverse source build001 terminalPASS1.2207348332740366s; all31pins and exact
three-source/public-library console/plan match. Individual descendant maximum
84475904B;2s group sampling misses the short compiler peak.
[Build result](research/portable_inverse_build001_result.json).
Fresh material runner binds accepted full016 lineage, reduced004 candidate,
source-built executable and immutable parent closures before diagnostics.
Admit material001 diagnostic only:1478pins,240s/quiet120/3GiB, native and
independent Python readback sequential in one owned group.
[Manifest](research/portable_inverse_material001_manifest.json). No correction
application, further native full action or physical response run admitted. Reduced singular values/probe agreement cannot supply a full-space
bound. Preserve all frozen sources/inputs; Brave/otherstudy untouched.

## Latest accepted evidence

- Reduced candidate002:49columns,4Newton iterations, coefficient residual
  4.90059381963448e-17; terminalPASS1.6159827504307032s/171884544B,1155pins.
  Fermi means0.1542994419693468/0.15339041848184634meV (~9.6% shift fromrank48).
  GapSHA9e0a01407aabce7adef104eb21f14bf992955849ac3817ef91c8f21b072f4521.
  [Reduced result](research/portable_reduced_gap002_result.json). Full residual now
  measured and failed both original thresholds; see segment008 result above.
- Occupation preparation001:terminalPASS34.4096539998427s/233996288B,1144pins.
  All inherited Q/U bytes unchanged; new overlap4.754812029020309e-19, norm1.
  Independent exponential image reconstruction error4.2012834183813297e-19Ry.
  [Readback](research/portable_occupation_prepare001_result.json),
  [method](research/SEGMENTED_OCCUPATION_ENRICHMENT.md). No full operator/conditioning bound.
- Previousrank48 complete full map:all66867leftrows,1130pins and ordered chain
  certified, independent normalization maxdiff0, native arithmetic/FD controlsPASS.
  **StationarityFAIL:** Rinf3.6594363917272926e-8Ry >1e-10;
  RMSres/gap0.001451511647600654 >1e-5. No gap/response acceptance.
  [Complete result](research/portable_full_map_segment004_result.json).
- Source-only checkpoint driver built against public QE/SCTK libraries;
  902cache controls bitwisePASS, no historical custom objects. ExecutableSHA
  90c072ebc2c8df205ddc358155b22bdc29756ae091fefebb81f08fa12f58e3d9.
  [Build result](research/portable_full_checkpoint_build001_result.json).
- Fresh64column linear mode:lambda1.0018603316543802, conventional mode4,
  independent residual2.2903598932171266e-10 <=1e-9. No Tc acceptance.

## Frozen contexts and resource ledger

Fresh geometry/Z:research/raw/fresh-gap-context-001.66867/67940active states,
ngapmax67940,nx100,nmf10,nci10,ne50,beta19613.355577892344(8.05K).
OperatorSHA6efcf2d527d3c81ae9620e3280916bb6b58db4809e6683cf0795256ed9fcce62.
FullZSHA4fb37410679421519e6dbae552f800ba197ca4db8c9303ffabf4781cec486426.
Fresh native geometry and full Z source/oracle checks are in the ledger; six
uncached Z samples are controls, not exhaustive equality. Do not import old Z/AQ.

Actual guarded campaign wall20545.044279171005s; ceiling21600s leaves
1054.9557208289953s. A material diagnostic240s would leave
814.9557208289953s reserve; only this bounded diagnostic is admitted. No automatic retry or budget increase.
Historical11357.646588s remain separate. Charge terminal actuals, including
Python preparation, before any next admission. No automatic budget expansion.
One heavy job OR quiet watcher. No paid/cloud compute, outreach or subagents.

Streaming guardv2 reduced verifier allocation by~339MiB; runtime policy unchanged.
Native compact Coulomb storage remains686.6MiB; tiny allocation reuse and bounded
coefficient residency are separate unimplemented proposals, not proven savings.
See [memory accounting](research/NATIVE_MEMORY_ACCOUNTING.md) and
[allocation profile](research/COULOMB_ALLOCATION_PROFILE.md). Do not modify pinned
sources/inputs or relax pressure rules to obtain completion.

## Open scientific requirements and verification

Full stationarity at each temperature; full-space conditioning/gap error;
response functional/units/mass/vertex and matched physical reference; state
mapping, energy/band/response grids/interpolation/derivatives; <=1% numerical
uncertainty on stiffness and ratios;2K/4K in addition to8.05K; justified isotropic
comparison and decision; rights-cleared acquisition and public reproduction.
No novelty/current demand/adoption has been accepted. See acceptance gates.

Conditional gap-to-response derivative and outward ratio helpers exist, but no
material gap radius/stiffness intervals are certified. Analytic parabolic/current
controls do not qualify the Nb functional or fit a physical normalization.

Latest code checks:229tests PASS24.818s including native fixture builds;
224maintained Python sources compilePASS; moment_refinement exit0; diffcheckPASS.
No separate configured typecheck. Public CI46125471800 on8653ee8 PASS; new runner CI pending publication.
Current docs/results do not replace native or scientific qualification.

Chronology remains in RESEARCH_LEDGER.md and immutable public commits. The former
1897line status page is preserved at
[76c853f](https://github.com/noahsong-sdg/sc-dft-exp/blob/76c853fb6ca522be98f69f57300c3cab1dc6eee4/CAMPAIGN_STATE.md).
