# Superconducting DFT benchmark progress

**Active research: start with [PROJECT_SPEC.md](PROJECT_SPEC.md) and
[RESEARCH_LEDGER.md](RESEARCH_LEDGER.md).** Future agents should read
[AGENTS.md](AGENTS.md). The benchmark snapshot below predates this campaign.

The reusable [two-week mandate](TWO_WEEK_GOAL_PROMPT.md) is also saved here;
writing it does not schedule continuous background execution.

## Active campaign evidence

Read the [living scientific report](research/CAMPAIGN_REPORT.md) for the integrated
answer, supporting evidence, reuse boundaries, and remaining acceptance gates.

The present scientific lead is an accuracy audit of response quadrature,
supported by a retained-input matrix-free gap workflow. A reliable physical
response prediction and a portable cold-start workflow remain unproved.

| Experiment | Verified result | Limitation |
|---|---|---|
| Fixed-gap response moments | Second moments preserve the matched fine-grid sum; squared means retain only 40–45% on the tested coarse cells | Constant gap; shared band/quadrature approximations |
| Full nonlinear map and derivative action | 908.65 s, 882 MB peak RSS on the Mac | Arbitrary seed, not a solved gap; upstream inputs reused |
| Reduced nonlinear enrichment | Rank38: reduced1.115s; full680.80s/938MB; both registered stationary-residual targets pass | Fixed retained inputs; conditioned gap error and physical response remain unverified |
| Frozen converged Nb replay | Released currents reproduced; thermal correction changes them by 2.5–2.8 ppm | Not corrected self-consistency or a Q=0 prediction |
| Public saved-density32→48 electronic-grid control |48 response completed233.59s/401MB; conserved fixed-gap diagnostic increases about5.52% | Fourth order reduces this observed spread to about0.68%; continuum/physical accuracy unresolved |

Measured occupation and critical-mode enrichment now reaches both unchanged full
stationary-residual targets at rank38: maximum3.172e-11Ry≤1e-10 and RMS
residual/gap7.546e-7≤1e-5. The separate full check preserves the exact seed and
passes tile/Jacobian controls in680.80s/938MB. See the
[prospective-manifest-bound result](research/verify_sixth_occupation_gap_result.json).
This certifies residuals for the retained fixed-input problem, not conditioned
gap error, discretization or physical response. Parent basis setup remains
partly historical. No speedup against an equivalently qualified full solve is claimed.

A new [anisotropic moment audit](research/ANISOTROPIC_MOMENT_GATE.md) reuses one
37.28 s /194 MB native cache across five candidates. For rank35, the computed
symmetry-averaging bound is about20 ppm of the candidate response. The two grid
estimates still differ2.738%, and rank34→35 changes the response about1.01%.
These unresolved sensitivities exceed that averaging effect. The analysis keeps
the separate native single-state branch and changes no gap values.

Directional response and Q0 initialization have different layouts. The cache
uses a deliberate full-symmetry diagnostic to match Q0 geometry; it is not a
qualified physical small-Q prescription. A relative symmetry-selector fix
passes separate material geometry controls, with full solver qualification still
open. See the [mapping audit](research/GAP_RESPONSE_MAPPING_GATE.md) and
[standalone figures](research/figures/README.md). Physical normalization,
discretization convergence, conditioned gap error and public cold-start inputs
remain open gates.

The [public-input reproduction path](research/PUBLIC_RESPONSE_REPRODUCTION.md)
now passes from12.9MB of author-hosted Nb inputs: fresh source compilation
261.64s, native diagnostic33.24s/187MB. All eight exported files match the
retained run bit for bit and the31source inputs remain unchanged. This proves
diagnostic reproducibility; it is not a full SCDFT cold start or physical response prediction.
The complete original32cubed dense-band input also reproduces from saved charge
in98.95s/96MB: all23322eigenvalues agree within4.152e-7Ry, without a fitted offset.
A consistent larger-capacity build preserves all8response exports bit for bit.
An [indexed mesh lookup](research/INDEXED_MESH_GATE.md) also preserves all8exports
bit for bit at32and48, with observed native time ratios1.31x/2.73x in single pairs;
these exclude setup and do not establish a full-workflow speedup.
For numerical accuracy,
the [48cubed band-grid study](research/BAND_DERIVATIVE_REFINEMENT_GATE.md) now
produces verified derived band data and a response diagnostic. Its roughly5.52%
change from32cubed shows why conservation alone is insufficient for accuracy.
A fourth-order velocity control reduces the observed spread to about0.68%,
supporting the preregistered stencil hypothesis; this is not a continuum error bound.
The original missing-serialization protocol and240s response timeout are preserved;
separate successful protocols do not erase those failures. No physical prediction follows.


Portable regression checks run in [public CI](https://github.com/noahsong-sdg/sc-dft-exp/actions/workflows/research-checks.yml).
The [first verified run](https://github.com/noahsong-sdg/sc-dft-exp/actions/runs/45956886205)
passed 38 tests and replayed committed refinement data on Ubuntu. This does not
rerun the retained-input native QE experiment or certify physical accuracy.

Current campaign: [scientific decision checkpoint](research/DECISION_STATUS.md),
[analytic linear-response reuse route](research/LINEAR_RESPONSE_LIMIT.md),
[first material-geometry diagnostic](research/NB_MATERIAL_DIAGNOSTIC.md),
[velocity-moment method test](research/VELOCITY_MOMENT_METHOD.md),
[response-cell refinement](research/MOMENT_REFINEMENT_RESULT.md),
[direction and zero-Q gate](research/DIRECTION_AND_ZERO_Q_GATE.md),
[scalar normalization control](research/RESPONSE_NORMALIZATION.md),
[small-Q symmetry validity test](research/SYMMETRY_SCALE_FINDING.md),
[converged saved-gap replay](research/ARCHIVED_NB_FINITE_Q_GATE.md),
[complete gap-RHS finding](research/RHS_THERMAL_FINDING.md),
[finite-temperature RHS zero-energy boundary](research/RHS_ZERO_ENERGY_FINDING.md),
[thermal-factor finding](research/CURRENT_IDENTITY_FINDING.md),
[held-out boundary tests](research/THERMAL_BOUNDARY_RESULT.md),
[reviewable pinned-source correction](research/patches/README.md),
[nonlinear equilibrium-gap reuse gate](research/NONLINEAR_REUSE_GATE.md),
[full nonlinear map qualification](research/FULL_NONLINEAR_MAP_GATE.md),
[informed nonlinear amplitude gate](research/MODE_AMPLITUDE_GATE.md),
[reused-basis nonlinear candidate gate](research/REDUCED_NONLINEAR_GATE.md),
[full explicit-candidate validation gate](research/GAP_SEED_VERIFY_GATE.md),
[workflow costs](research/WORKFLOW_COSTS.md), and
[response figures](research/figures/README.md). The thermal correction is checked on
synthetic fixtures, imposed-gap Nb geometry, and a documented converged frozen
Nb gap. Its current effect in that real state is only 2.5–2.8 ppm; corrected
self-consistent material impact remains unresolved. The [zero-energy correction](research/ZERO_ENERGY_FINDING.md)
also passes normal-state controls that exposed an additional singularity.

Public progress record for a preregistered comparison between an isotropic
Migdal–Eliashberg solver (IsoME) and the superconducting DFT implementation in
the Superconducting Toolkit (SCTK).

## Current result

The benchmark is **in progress**. It does not yet support a solver ranking or a
claim of predictive accuracy.

- The six-material scalar IsoME panel is complete: 30 transition-temperature
  brackets and six aluminium cases censored at the qualified 2 K floor.
- One of 14 registered native SCTK model sets has a completed transition
  bracket.
- Nb model D has accepted endpoints at 4 K and 20 K, giving a coarse 4–20 K
  bracket. Refinement and numerical controls remain incomplete.
- The current 12 K Nb-D point has 22 committed stages but no accepted endpoint.
  Its two residuals are `2.8900851250702076e-8` and
  `5.080759868978398e-6`, above the fixed `1e-10` limit.
- No native solver is running at this snapshot.

See [STATUS.md](STATUS.md) for the evidence boundary and
[data/isome_scalar_panel.csv](data/isome_scalar_panel.csv) for the completed
scalar brackets.

## What this repository contains

- a concise, public status snapshot;
- the preregistered scientific design and acceptance rules;
- independently checked scalar-panel results;
- a hash manifest for the retained source evidence;
- known comparability limitations and the next scientific gates.

Large native inputs, machine-specific receipts, build environments, and
intermediate solver states are not included. Their hashes and readbacks remain
part of the retained private evidence set while a portable release bundle is
prepared.

## Interpretation boundary

SCTK is treated as a numerical reference configuration, not ground truth.
Numerical validation, agreement between specified models, and experimental
predictive accuracy are separate claim levels. The current evidence establishes
some numerical results within registered models; it does not establish that the
two solvers use identical effective interactions.

## License

The documentation and tabular results in this repository are released under
[CC BY 4.0](LICENSE).

