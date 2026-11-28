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
Material001 terminalPASS44.31549504166469s, all1478pins/source-lineage and
independent full matrix/both-action readback PASS; individual peak234225664B.
Compressed correction/maxgap2.327317186525163e-5 (0.0023273%), but one native
probe inverse defect0.48070172169141706; no full-space error acceptance.
[Result](research/portable_inverse_material001_result.json),
[interpretation/cost](research/INVERSE_MATERIAL_805K.md).
Declared-direction native boundary now fixture-qualified: original direction
matches frozen output bitwise, arbitrary direction matches independent dense
nonsymmetric J action, restart equality and changed-state rejection PASS.
[Method](research/DECLARED_DIRECTION_PROBE.md). Frozen production sources unchanged.
Source build001 terminalPASS4.413896750193089s;556pins, exact20fresh compiles,
2links/17distinct archives and902cache controls PASS; peakindividual133152768B.
[Build result](research/portable_full_direction_build001_result.json).
Explicit step native/checkpoint and independent plus/minus-image normalization
now fixture-qualified at actual correction scale5.502435566805578e-10Ry; dense
nonlinear sums, restart equality and stale step/schema rejection PASS.
[Method](research/DECLARED_STEP_CORRECTION.md). Same four-batch/kernel order;
frozen sources untouched. New summary reader binds exact step and streams arrays.
Source-step-build001 terminalPASS4.790972708724439s, all566pins, exact20fresh
compiles/2links/17archives and902cache controls PASS; peakindividual133414912B.
[Build result](research/portable_full_step_build001_result.json).
Declared-step preparation, evaluation and checkpoint readers are now certified.
Preparation001 terminalPASS46.14212279161438s/238190592B;1486pins and exhaustive
inverse replay PASS; exact candidate, unit direction and actual correction scale.
[Preparation](research/correction_direction_prepare001_result.json).
Qualifier001 terminalPASS36.70167237473652s/931561472B;1533pins and actual native
continuous64 vs32+32 bitwise equality PASS. Both production halves terminalPASS:
311.66590004134923s/913653760B and310.0547899999656s/922468352B. Complete66867rows,
1577pins, recursive source/state/preparation/qualification closure certified.
[Final result](research/portable_full_step_segment002_result.json),
[interpretation](research/CORRECTION_ACTION_805K.md).

**Actual plus correction improves full residual:** Rinf1.5375314641797623e-11Ry,
RMSres/gap2.843395985000644e-7, both original targets PASS; improvement factors
3.96525/3.62689. Negative step Rinf1.1214212172330003e-10Ry fails original max.
Original base gap/residual preserved bitwise; d0+h*v equals d0+c bitwise.
Plus gapSHAc5ad7e2a2d1e18debacd22e4162db2256193b344e29e90cf84e70967d43cc507.
No seed overwritten, full-space error or physical-response acceptance.

Streamed inverse-action001 terminalPASS23.520716750063002s, peak105431040B
(~100.55MiB); all1589pins and three independent equation controls PASS.
[Result](research/correction_inverse_action001_result.json). Original native
correction reproduced within2.481541837659083e-24Ry. Useful-direction inverse
defect0.6410778371097358; frozen B times plus residual/original correction
0.6410456591853905. Neither is a gap/response error bound or global contraction.
This reuses saved native images without a kernel sweep or resident basis copy;
no controlled before/after memory comparison. Saved-action secant001 terminalPASS21.248003708198667s/92323840B (~88.05MiB),
all1597pins. Training defect improves to1.11e-16 by construction, but separate
probe worsens0.4807017→15.2333336; plus residual action also worsens. **Reject
this rank-one update for the unweighted infinity-contraction route.** No seed or
inverse adopted. Independent70digit Decimal replay checks every action entry.
[Result](research/secant_inverse_action001_result.json),
[interpretation](research/SECANT_INVERSE_DIAGNOSTIC.md). All owners terminal;
no next run/retry/budgetincrease. BLAS tile feasibility001 terminalPASS3.7081837s,
peak66568192B (~63.48MiB),44pins, both80entry signed/54sample rational controls.
Reference rates3.29–7.17GFLOP/s versus Accelerate285.91–352.60; contraction-only
forecast490.89–545.04s versus8.42–9.69s. **No fullnorm/solver speedup claim.**
[Result](research/tile_blas_feasibility001_result.json),
[method/evidence](research/TILE_BLAS_FEASIBILITY.md). Committed synthetic binaries
and summaries permit offline arithmetic replay. Current native producer has
32-row blocks. New separate streamed defect core passes exact dense I-BJ controls
on actual32-row strided/native-bound layouts, including partial tiles and both
same-side blocks. [Core](research/STREAMED_DEFECT_CORE.md). Next source-bind the
compact/padded adapter and native tile producer, then qualify selected actual
tiles before a full pass. No material norm/timing or outward certificate yet.
Kernel/IO/radius/rounding work remains open.
Compact state writer/native reader now pass six regression tests: unequal-band
padding, bitwise readback, independent dense inverse action and stale/context/
shape boundaries. Basis columns stream; fixed stored W is checked on both sides.
[Bridge](research/COMPACT_DEFECT_STATE.md). Material preparation001 terminalPASS24.014388291630894s/102563840B
(~97.81MiB),1598pins. All102Q/U columns independently bitwise checked after
compaction; three saved actions calibrate within1.11023e-15/3.61892e-25/
5.16988e-25 absolute. Stored W two-sided errors2.33952e-14/4.49790e-14.
[Result](research/compact_defect_prepare001_result.json). No material native
reader/kernel run or full norm yet. All owners terminal; next source-bind native
producer to this compact state and qualify selected actual tiles.
The exact [streamed identity](research/STREAMED_FULL_DEFECT_ROUTE.md) includes
same-side blocks and avoids a145GB dense matrix;2.78Tflops is not runtime evidence.
[Method and interpretation](research/CORRECTION_INVERSE_DIAGNOSTIC.md).
Full correction postread14.195769s/75923456B remains separate from native wall.
Kernel2 source orientation controls showed14.2146% pair asymmetry; positive dk
alone supplies no accepted symmetric metric. Finite probe agreement cannot
bound the unmeasured complement. Brave/otherstudy untouched.

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

Actual guarded campaign wall21376.431543087903s; ceiling21600s leaves
223.56845691209674s. No next run, automatic retry/fullnorm/kernel pass or budget
increase admitted.
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

Latest code checks:278tests PASS42.086s including native fixture builds;
258maintained Python sources compilePASS; moment_refinement exit0; diffcheckPASS.
No separate configured typecheck. Public latest helper/resultCI46131518726 on7e37f98 PASS; prospective final-halfCI46131592238 on1d335c8 PASS. Earlier CI46125471800 on8653ee8 PASS; runner CI46126020760 on4e0fecf PASS; material-result CI46126382268 on2ac1a50 PASS; orientation helper CI46126757526 onf10730c PASS; result CI46126994654 on3997c72 PASS; direction helper CI46127521198 onad67046 PASS; result CI46127763049 on6a12d8c PASS; step helperCI46128222986 on1084b00 PASS; readerCI46128690566 ond839ced PASS; preparation helperCI46129155495 on79344e4 PASS.
Latest streamed helper CI46132810239 onf7fdd9d PASS; prospective manifest
CI46132854664 one59e821 PASS. Previous resultCI46133492457 one6aeff2 PASS;
secant helperCI46133944602 on285e13e and prospectiveCI46133984159 ona95c65d PASS;
secant resultCI46134385800 on7f27443 PASS. Tile sourceCI46135078932 on1c44258 and
prospectiveCI46135120773 onb210279 PASS; tile evidenceCI46135532189 onf60eb52 PASS.
Current docs/results do not replace scientific qualification.

Chronology remains in RESEARCH_LEDGER.md and immutable public commits. The former
1897line status page is preserved at
[76c853f](https://github.com/noahsong-sdg/sc-dft-exp/blob/76c853fb6ca522be98f69f57300c3cab1dc6eee4/CAMPAIGN_STATE.md).
