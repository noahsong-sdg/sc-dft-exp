# Superconducting DFT benchmark progress

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

