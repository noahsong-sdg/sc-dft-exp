# Derivative-weighted trial-input preparation

The accepted64-row diagnostic exposes three gap-domain directions v. Existing
Q approximates A, while the Jacobian uses A*D. The coherent enrichment inputs
are therefore D*v, not v. This stage prepares only three extra orthonormal inputs;
A actions, an augmented inverse and held-out validation remain separate gates.

Source sensitivity_enrichment.py reads the accepted spectrum closure and compact
Q/D. In largest-singular-value-first order, it applies D, uses twice-reorthogonalized
modified Gram–Schmidt against Q and previous extras, and rejects zero or already
captured inputs rather than inventing substitute directions. It records normalized
Q projection, remaining norm, orthogonality and independently reconstructed target
error. Inputs remain unchanged; trial columns are saved separately. Memory uses
existing Q (~55MB) plus a few vectors, without U, C, full kernels or a dense matrix.
This is a forecast of allocation, not measured RSS or a same-workload speedup.

Exact-arithmetic justification: if D*v belongs to span(Qnew) and Unew=A*Qnew,
then (A-Unew*Qnew^T)*D*v=0. A new inverse could still amplify remaining errors;
training direction annihilation alone is not a full-space or response certificate.
The measured Q^T*v spectrum overlap does not measure Q^T*D*v; this stage resolves
that specific uncertainty before a more expensive kernel pass.

## Prospective admission001

One90s Python preparation owner,120continuous normal-pressure seconds,3GiB group
and workspace cap, no new native kernels or inverse. Root raw/sensitivity-enrichment-001;
manifest sensitivity_enrichment001_manifest.json. At admission21989.224320587087s
charged of25200;3210.7756794129127s remain, worst90 leaves3120.7756794129127s.
Include all numerical preparation/verification inside the charged owner; parent
receipt/hash validation is separate workflow cost. Stop on pressure, deadline,
changed pins, stale outputs or failed mapping/orthogonality/reconstruction.
No automatic retry, new kernel pass or resource expansion. Brave and other study
untouched. Existing candidate/gap/inverse files are preserved.

Fixture tests distinguish D*v from v, verify orthogonality and reconstruction,
and reject zero/exhausted/nonfinite inputs, stale shapes/outputs, changed pins
and wrong owner cwd. No fallback or silent rank reduction is introduced.

Source gate324testsPASS50.966s incl native fixture builds,297Python sources
compilePASS, moment_refinement exit0, diffcheckPASS. Parent closure validation
and staging2.669517290778458s,1857pins; separate read-only workflow cost.
