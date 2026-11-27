# Qualifying an anisotropic gap for response

The current full native validation concerns a Q=0 gap at 8.05 K. The existing
moment diagnostic imposes the same constant 1.5 meV gap everywhere at 2/4/8 K.
Replacing that scalar by a vector without matching the native state assignment
would introduce an uncontrolled approximation. No response calculation with the
new candidate has yet been accepted.

## Owning path and observed layout

The retained `sctk_ini_delta.f90` path is `ini_delta -> ... -> store_d3k`.
`store_d3k` resolves a band/cell over positive-DOS energy nodes when at least two
nodes exceed its 1e-12 threshold. Otherwise it creates one interpolated band
state with weight 1/nqbz. Both records carry k-cell and band indices; only the
first class is indexed by the energy quadrature. This is why vector position
alone cannot safely connect the two representations.

`gap_response_mapping_audit.json` records a read-only exact grouping audit of
the same retained Q=0 initialization used in the candidate experiment:

| Class | Side 1 | Side 2 |
|---|---:|---:|
| Resolved band/cell groups | 1024 | 1024 |
| Resolved states | 54579 | 55652 |
| Single-state groups | 12288 | 12288 |

Every resolved state's energy is exactly an xi0 node, with no duplicate energy
within a band/cell group. Every single state is off that grid and has exactly
weight 1/512. Its smallest absolute energy is 0.02747/0.03619 Ry. Large energy
does not by itself justify discarding its response contribution.

Reproduce with `python3 research/gap_response_mapping_audit.py PREPARE SOURCE`,
using the paths and SHA256 identities in the JSON. This groups the actual native
snapshot; it does not certify that an arbitrary source file generated it.

## Required next experiment

After full gap qualification, keep its native 8-cubed cells and exact Q=0 bands
for the first anisotropic response test. Map resolved states using side, cell,
band and exact energy index; require native ordering, energy and weight agreement.
Retain the original single-state branch separately. Reconstruct the native
first-moment and curvature path before evaluating second moments on the same
support and gap. Require a constant-gap replay and the existing native controls.

The constant-gap fine-grid equality does not extend automatically to an
anisotropic gap: a fine-grid gap interpolation changes the question. A cellwise
second moment can audit the within-cell closure at a fixed gap representation,
but cannot establish fine-grid anisotropic convergence. Changing response cells
requires an explicit gap-transfer/refinement study, rather than silently reusing
the old vector. Physical normalization and response vertices remain the separate
gates in PHYSICAL_INTERPRETATION_GATE.md.
