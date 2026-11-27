# Dense effective-interaction memory floor

The pinned `make_effint` allocates two binary64 arrays of shape
`(ngap(2), local_columns_of_ngap(1))`. Source:
https://github.com/mitsuaki1987/sctk/blob/47c06501da8ffd574c87469ddd6d5a2814171796/src/sctk_gapeq_rhs.f90

For one process, its payload alone is `16 * ngap(1) * ngap(2)` bytes. MPI splits
columns across ranks but does not reduce the combined payload for ranks resident
on one laptop. OpenMP does not distribute this allocation. This excludes all
other arrays, runtime overhead, OS use and construction temporaries.

| Inspected state counts | Dense effint bytes | GiB | Fraction of 32 GiB RAM |
|---|---:|---:|---:|
| Nb matched legacy: 66867 × 67940 | 72,687,103,680 | 67.695 | 2.115× |
| Nb larger archive: 159852 × 165242 | 422,628,226,944 | 393.603 | 12.300× |
| V3Si archive: 171578 × 170616 | 468,383,232,768 | 436.216 | 13.632× |

Counts come from inspected saved-state headers; the first also matches the
retained native initializer. These are arithmetic allocation requirements for
those cardinalities, not measured peaks or guaranteed counts for another Q/grid.
The calculation is independently reproducible as `2 * n1 * n2 * 8 / 1024**3`.

Thus an unmodified dense nonlinear solve at these sizes cannot reside entirely
in this 32 GiB laptop's RAM. Faster matrix construction alone cannot remove that
barrier. Exact matrix-free/streamed application, validated compression, or a
scientifically justified smaller discretization is required for a new solve.
Their time and error costs remain to be measured; do not infer infeasibility of
all SCDFT from the dense allocation, or assume previous linearized-Tc engineering
automatically qualifies a nonlinear response implementation.

This is why preparation/postprocessing can be plausible while a cold-start
nonlinear workflow remains unqualified. A compatible saved converged gap might
avoid that allocation for a carefully justified response question, but missing
provenance and new-Q state remapping remain separate scientific gates.
