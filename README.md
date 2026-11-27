# Superconducting DFT benchmark progress

**Active research: start with [PROJECT_SPEC.md](PROJECT_SPEC.md) and
[RESEARCH_LEDGER.md](RESEARCH_LEDGER.md).** Future agents should read
[AGENTS.md](AGENTS.md). The benchmark snapshot below predates this campaign.

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

