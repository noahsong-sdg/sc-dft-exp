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
32-row blocks. The separate streamed defect core passes exact dense I-BJ controls
on native strided layouts, partial tiles and both same-side blocks.
[Core](research/STREAMED_DEFECT_CORE.md). Compact preparation001 terminalPASS
24.014388291630894s/102563840B;1598pins, all102Q/U columns independently
bitwise checked after padding removal and three saved B actions calibrated.
[Preparation](research/compact_defect_prepare001_result.json).
**Normalization invariant:** stored D differentiates the normalized occupation
ratio; A0 carries finite-T linear weights dk*tanh(beta*abs(xi)/2)/(2*abs(xi)),
with the xi=0 limit. Fixture D comes from the frozen inverse producer. The first
new probe convention was corrected before material use; prepared D/W unchanged.
Compact native build001 terminalPASS3.6612219577655196s/133087232B;576pins,
18fresh compiles/35outputs/902cache controls and explicit SDK-first link verified.
[Build](research/compact_tile_build001_result.json).
Selected material001 terminalPASS29.737132583279163s/1033355264B (~985.48MiB),
1666pins. Native state and D agree (max4.44e-16);30native and21independent
saved-kernel controls PASS (max1.11e-16). All P/kernel values finite and unvisited
left P columns zero. [Result](research/compact_tile_material001_result.json),
[method](research/COMPACT_MATERIAL_TILES.md). Kernel CPU0.227426/0.219171s
versus contraction0.017620/0.013659s are selected sections, not full-run speedup.
Postread6.107946s/54394880B remains separate. Public CI46139920906PASS.
New ordered-P checkpoint/pass source now passes synthetic continuous/restart
bitwise controls, final short tiles and independent full-P dense arithmetic.
[Checkpoint](research/COMPACT_P_CHECKPOINT.md).297testsPASS45.185s. Metadata
binds exact coverage/dimensions/context, binary shape and untouched columns;
new pass supports a cache-reset32+32qualification and declared predecessor.
P dependency fingerprint is now implemented: binds Q/state/grid/beta/operator/
candidate/executable/SDK/platform; excludes U/W and relocation. Parent receipt/pin
validation is still required separately. Ordered-P build001 staged with577pins,
19fresh compiles in checked dry plan;60s,120quiet seconds,3GiB caps.
[Build admission](research/compact_p_build001_manifest.json).301testsPASS44.966s.
Ordered-P build001 now terminalPASS3.6561458753421903s/133152768B;
577pins,19fresh compiles/37outputs/902cache controls and exact plan verified.
[Build result](research/compact_p_build001_result.json). Actual P dependency
context43be64148f45cab2975254ad80a543945a60423745b226bdbf77a09b8cf79cca
is [registered](research/compact_p_context001.json), with accepted parent/file
identities; material flags remain false. Source CI46141075791PASS.
Streaming checkpoint readback now checks metadata, finite payload/unvisited zeros,
replay timing consistency and equality to an externally accepted partial-P SHA256
in512KiB payload blocks. No complete P arrays allocated by this reader; actual RSS
unmeasured. Three new persisted-state/corruption regressions PASS.
Final304testsPASS47.727s,277Python compilationsPASS; native fixtures/builds PASS.
Public build/context580a7c7 CI46141345023PASS.
Owning material qualifier now validates parent closures/receipts, recomputes context
and stages continuous64 versus checkpoint32+32 with selected material001 P identity.
[Admission001](research/compact_p_material001_manifest.json):1735pins,90s cap,
120quiet seconds,3GiB caps; no full pass/budget expansion.306testsPASS43.509s;
279Python compilationsPASS; native fixtures and moment refinement PASS. No complete material P, full norm,
outward certificate, conditioned gap error or physical response accepted.
Material restart qualifier001 now terminalPASS30.05208083288744s; all1735pins and
6,875,157partial-P entries match accepted selected material001 bitwise.
Native peak1076133888B (~1026.28MiB); readback14.913044875022024s/55492608B
separate from native cost. [Result](research/compact_p_material001_result.json).
Complete P segment001 now terminalPASS506.08344662515447s/1053638656B
(~1004.83MiB). All1756pins,66progress records, final19-row tile, finite checkpoint
and preserved64-row left prefix PASS. [Result](research/compact_p_segment001_result.json).
Full P SHA1bdfce3d4adff9e8d24010565684b014479c315542e0e07dbe98854569517bd3;
cumulative kernel/contraction CPU447.471099/29.651572s include prior64rows.
Postread33.47346162516624s/59834368B (~57.06MiB), separate from native cost;
ran concurrently with final unit verification. All native owners terminal.
Independent saved-image action control now PASS all51rank components:
P(Dv)=Q^T D(ADv), using independently saved original native image.
Maxdiff1.6431300764452317e-14, maxerror/bound7.641409651929256e-7.
[Action result](research/compact_p_actions001_result.json). Readback47.81856029108167s/
118603776B (~113.11MiB), separate workflow cost. Exact Fraction/stale-state tests
and final312testsPASS45.022s,285Python compilations/native fixtures/moment PASS.
[Method](research/COMPLETE_P_ACTION_CONTROL.md).
[Scientific-value budget decision](research/COMPLETE_P_ADMISSION.md): local ceiling
seven hours under original authorized4→16h pilot expansion. The selected defect
diagnostic below now rejects continuing this stored unweighted-contraction route.
Retained K1 comparison now gives AD-only row sums6.30851/1.42047/3.63946
versus chosen-B272.463/205.759/123.741: current B worsens this metric; identity B
also fails. [Reproduction recipe](research/STREAMED_DEFECT_SECOND_PASS.md).
Retained64-row spectrum now independently checked: leading direction contains
99.9534% squared Frobenius energy and has only1.30433e-6 squared projection into
current Q span. Three directions contain99.99842%; none adopted. This supports
prospective input-basis enrichment, not a qualified repair. Guard6.431358041707426s,
peak281575424B (~268.53MiB), all1839pins/output/receipt and1856closure pins checked.
[Diagnostic](research/RETAINED_ROW_SPECTRUM.md), [result](research/defect_row_spectrum001_result.json).
Derivative-weighted enrichment preparation001 now terminalPASS10.18311733333394s,
peak97304576B (~92.80MiB),1857staged/1864accepted closure pins checked. D*v old-Q
projection squared fractions5.23e-6/9.63e-7/5.22e-6; three extras orthonormal and
reconstruct mapped targets within3.90e-16. No A actions/new inverse adopted.
[Preparation and fixed holdouts](research/SENSITIVITY_ENRICHMENT.md),
[result](research/sensitivity_enrichment001_result.json).
Joint A*extras/extra-P variant now fixture-qualified against independent dense
nonsymmetric full/partial/final-short-tile controls. Fresh source build001
terminalPASS3.7499855835922062s/133201920B (~127.03MiB),571staged/614closure
pins/19fresh compiles/37outputs/exact plan/902cache checks PASS. No material kernels.
[Method](research/ENRICHMENT_ACTION_PASS.md), [build](research/enrichment_action_build001_result.json).
Selected joint-action material001 now terminalPASS33.78485658345744s/994099200B
(~948.05MiB),1921staged/1933closure pins and six output hashes checked. All18saved
row A-action and9bilinear P controls PASS, maxerror7.11e-17, maxerror/bound7.06e-5.
Exactly64rows and finite/unvisited-zero; complete_A_and_P=false. No new inverse.
[Selected result](research/enrichment_action_material001_result.json).
Complete joint-action001 now terminalPASS507.8289217497222s, individual peak
1014677504B (~967.67MiB), sampled group1022738432B.1942staged/1954closure pins,
all66867rows/66progress records and six output identities checked.27saved-row
A-action/9bilinear controls PASS; maxerror2.52e-16, maxerror/bound1.46e-4.
Complete_A_and_P=true; no augmented inverse, full norm or physical response accepted.
[Complete result](research/enrichment_action_complete001_result.json),
[method](research/FULL_ENRICHMENT_ADMISSION.md).
54-column inverse diagnostic001 now terminalPASS30.27037683315575s/328024064B
(~312.83MiB),1958staged/1974closure pins and all independent M/W/C/row checks PASS.
But every tested complete row still11.67–25.69 versus old123.74–272.46. Candidate
REJECTED for unweighted contraction; no full sweep or adopted inverse.
[Result](research/enriched_inverse001_result.json), [fixed gate/table](research/ENRICHED_INVERSE_PROTOCOL.md).
Read-only E*v postread shows all27 selected-direction components<=3.88e-15;
repair captured its three directions but remaining errors matter. Original
training spectrum resolves9directions under its preexisting threshold, only3used.
Next assess six omitted training-derived directions before spending new kernels;
any future candidate needs fresh held-out rows and prospective admission.
New second-pass native driver and independent coefficient/row readback now pass
compiled full/partial denseI-BJ controls, both same-side blocks, final short tiles,
stale predecessor and finite corruption regressions. New owning selected gate
checks exact full P/saved-action parents and fresh build; only64/64rows permitted.
[Method](research/STREAMED_DEFECT_SECOND_PASS.md).318testsPASS49.875s,
291Python compiles/native fixtures/moment PASS. Source build001 staged577pins,
60s,120quiet seconds,3GiB caps. Build001 now terminalPASS3.7740026665851474s,
maxindividual134643712B (~128.41MiB);577pins/19fresh compiles/37outputs/902cache
controls PASS. [Build result](research/compact_defect_build001_result.json).
Source/admission8e19886 CI46144804164PASS; no native kernels in build.
Selected material001 now staged1824pins,90s,120quiet seconds,3GiB caps,
64left/64same-right columns only. [Admission](research/compact_defect_material001_manifest.json).
Material001 now terminalPASS29.39738891646266s/1143193600B (~1090.23MiB).
All1824pins,306C controls and six independent row checks PASS.
Complete left rows1/32/64 sum272.463383/205.758588/123.741233; selected maximum
304.375753. This stored B does not support unweighted infinity contraction;
no full second sweep will be launched on current B. Other inverses/metrics and
physical solution remain undecided. No outward certificate or full norm claimed.
[Result](research/compact_defect_material001_result.json). Postread38.610814957879484s/
62373888B (~59.48MiB) separate from native cost. All owners terminal.
No full norm, outward/radius bound, conditioned gap error or physical response accepted.
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

Actual guarded campaign wall22575.04157867035s; revised local ceiling25200s
leaves2624.958421329651s. Complete P segment001 is terminalPASS; no native
owner running. No automatic retry/fullnorm pass or further budget
increase admitted. [Decision and termination plan](research/COMPLETE_P_ADMISSION.md).
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

Latest code checks:331tests PASS53.854s including native fixture builds;
309maintained Python sources compilePASS; moment_refinement exit0; diffcheckPASS.
Spectrum source/admission5444ebf CI46146669175PASS.
Enrichment source/admission31bad38 CI46147295398PASS.
Joint action source/admissionc888baf CI46148038612PASS.
Selected material source/admissionc080ec4 CI46148570348PASS.
Full action source/admissionba807d7 CI46149069233PASS.
Enriched diagnostic source/admissionb93c140 CI46150551746PASS.
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
