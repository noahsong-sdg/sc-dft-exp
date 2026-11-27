# Benchmark status

Snapshot date: 2026-11-25 (America/Los_Angeles).

## Verified results

### Scalar IsoME panel

All 36 registered cells reached terminal status. Thirty cells produced a
transition-temperature bracket. Six aluminium cells were censored because the
next requested temperature was below the qualified 2 K domain.

Across 378 independently reconstructed accepted temperature points:

- the maximum worker–reader eigenvalue difference was `2.709e-14`;
- the maximum eigenpair residual was `1.987e-14` against `1e-10`;
- the largest normalized native derivative error was `9.969e-9` against
  `1e-8`;
- the widest accepted temperature bracket was `0.03125 K` against the
  registered `0.04 K` bound;
- the 7000 and 9000 meV cutoffs gave identical endpoints at the registered
  resolution for every bracketed cell.

The columns in the data file are the registered **bare** Coulomb parameter
`mu`. IsoME converts it to

`mu_star = mu / (1 + mu * ln(10000 meV / cutoff))`.

### Native SCTK study

The full native benchmark is incomplete. One of 14 registered model sets has a
completed transition bracket.

Nb model D has independently accepted points at 4 K and 20 K. These establish
only a coarse 4–20 K sign bracket. They do not complete the refined search or
its numerical controls.

At the current 12 K point, 22 stages are committed and both starts remain
active. No endpoint is accepted:

| Start | Full residual | Fixed limit |
|---|---:|---:|
| First | 2.8900851250702076e-8 | 1e-10 |
| Independent | 5.080759868978398e-6 | 1e-10 |

No native process was active when this snapshot was prepared. The next
scientific action is a new first-start continuation after fresh resource and
state admission.

## Remaining work

- Refine the Nb-D transition bracket and complete its numerical controls.
- Execute and qualify Nb B/C physical searches; the software path is tested,
  but no B/C endpoint is accepted.
- Complete the aluminium native convergence path without weakening the 2 K
  scalar-domain boundary.
- Qualify payloads, capacity, and finite execution contracts for Ta, SOC-Pb,
  beta-Sn, and V3Si native runs.
- Produce a portable evidence bundle that replaces machine-local paths with
  content-addressed public artifacts.

## Claims not supported yet

The current results do not establish:

- experimental predictive accuracy;
- that IsoME is more or less accurate than SCTK;
- identical effective electron–phonon interactions across the two paths;
- a completed six-material paired comparison;
- general warm-start or runtime acceleration.

