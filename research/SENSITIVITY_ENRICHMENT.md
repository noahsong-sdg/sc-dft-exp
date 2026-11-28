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

## Accepted preparation001

TerminalPASS10.18311733333394s, maxindividual97304576B (~92.80MiB), sampled
group97239040B.1857staged/1864accepted closure pins; receipt, exact owner manifest,
watcher, raw readback and output hash checked. [Result](sensitivity_enrichment001_result.json).
Three trial columns3235368B SHA256
f1f90ab4125ee5d907a77768b6dc424191e1762a638e76a69f43e06eedfea3ae.
Public source31bad38 CI46147295398PASS.

Largest-first normalized squared old-Q projections of D*v are
5.231754424102264e-6,9.631075369431758e-7,5.2168829687527895e-6.
Remaining fractions after removing Q and earlier extras are
0.9999973841193666,0.9999994647472692,0.9999929608172785.
Thus derivative weighting does not remove the missing-input-span opportunity.
Maximum trial orthogonality error7.062423971075427e-18; target reconstruction
relative errors3.41e-16–3.90e-16. This qualifies preparation of trial inputs only.
No full A action, new U/P/W, adopted inverse or physical response is available.
Charged campaign21999.40743792042s/25200 leaves3200.592562079579s.
All owners terminal; no new kernel pass admitted.

## Next reviewable execution path

A fresh native variant can apply both original kernel orientations to the three
trial columns while accumulating the three extra rows Qextra^T*D*A during the
same ordered pass. Retain original Q/U/P unchanged and concatenate the new
columns/rows only after independent controls. This avoids another pass solely
for the new P rows. Use A01=-K1^T*w_right/(1+Zleft) and
A10=-K2*w_left/(1+Zright); noninterchangeable orientation controls are mandatory.

Before a material pass, native fixtures must compare both A actions and extra P
to a separately formed dense nonsymmetric operator, cover final short tiles and
reject stale controls/state/outputs. Fresh source-only linkage and a selected
material pilot must pass. A later bounded full pass could retain complete
kernel rows at left1/32/64 (training) and65/33434/66867 (held-out), plus complete
right1/33970/67940 rows. These are fixed now before any new inverse is measured.
New inverse construction and these held-out complete-row defect comparisons
are separate acceptance gates; no tuning to held-out rows. Both old/new row
norms, small solve diagnostics and old native probe controls must be reported.
A passing selected test still requires full-space/outward/response validation.

Forecast only: measured complete51-row P pass506.08s and about1GiB RSS support
investigating one extra-action pass with few-column contractions; actual new
runtime is unknown. Do not launch until its code, tests, pins, budget/stop
conditions and prospective material admission are public. No expansion here.
