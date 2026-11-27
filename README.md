# Superconducting DFT benchmark progress

**Active research: start with [PROJECT_SPEC.md](PROJECT_SPEC.md) and
[RESEARCH_LEDGER.md](RESEARCH_LEDGER.md).** Future agents should read
[AGENTS.md](AGENTS.md). The benchmark snapshot below predates this campaign.

The reusable [two-week mandate](TWO_WEEK_GOAL_PROMPT.md) is also saved here;
writing it does not schedule continuous background execution.

## Active campaign evidence

The present scientific lead is an accuracy audit of response quadrature,
supported by a retained-input matrix-free gap workflow. A reliable physical
response prediction and a portable cold-start workflow remain unproved.

| Experiment | Verified result | Limitation |
|---|---|---|
| Fixed-gap response moments | Second moments preserve the matched fine-grid sum; squared means retain only 40–45% on the tested coarse cells | Constant gap; shared band/quadrature approximations |
| Full nonlinear map and derivative action | 908.65 s, 882 MB peak RSS on the Mac | Arbitrary seed, not a solved gap; upstream inputs reused |
| Reduced nonlinear candidate | 1.07 s, 113 MB peak RSS, five Newton iterations | Failed subsequent full-space residual targets |
| Frozen converged Nb replay | Released currents reproduced; thermal correction changes them by 2.5–2.8 ppm | Not corrected self-consistency or a Q=0 prediction |

The reduced candidate's mean Fermi gaps are 0.1663/0.1653 meV at 8.05 K.
Its full native check completed in 785.63 s / 904 MB peak RSS, but its maximum
residual of 8.96e-8 Ry and residual/gap RMS ratio of 0.00236 fail the declared
targets. One source-bound occupation enrichment gives a second reduced
candidate in 1.01 s, but changes its mean gaps by about 26%; it is also
unverified in full space. Adding the measured critical mode produces a rank33
candidate in 0.906 s, with mean gaps 0.13967/0.13884 meV. Its full-space
validation is running; no stationary residual has yet been accepted.
No speedup against an equivalently
qualified full solve is claimed. The [gap-to-response mapping audit](research/GAP_RESPONSE_MAPPING_GATE.md)
identifies the energy-resolved and single-state branches that a subsequent
anisotropic response test must preserve.

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

