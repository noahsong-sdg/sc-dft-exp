# Superconducting response on a laptop: living scientific report

Checkpoint: 2026-11-27. This report is provisional while the campaign runs.
The [restart ledger](../RESEARCH_LEDGER.md) owns live process state. The
[requirements audit](REQUIREMENTS_AUDIT.md) records incomplete acceptance gates.

## Answer currently supported

Reusable microscopic inputs make several useful response **diagnostics** practical
on this Mac. They do not yet make a reliable, self-consistent material response
prediction demonstrably accessible. The distinction is the principal result so
far: memory feasibility, a converged reduced equation, matched quadrature, and
experimental accuracy are separate gates, and the experiments expose failures
at more than one gate.

The strongest contribution is a reproducible accuracy audit: retain second
velocity moments, test the native symmetry averaging at an unchanged anisotropic
gap candidate, and bound that operation's observable effect even with signed
quadrature weights. This can tell another method developer whether compression
or averaging is smaller than other numerical sensitivities before spending on
new microscopic inputs or a material scan. It is a scientific reliability tool;
its value is not an established new-material discovery capability.

## Measured evidence and what it proves

| Evidence | Result | Valid conclusion | Not established |
|---|---|---|---|
| Fixed-gap matched-energy response | Squared means retain only40–45% of the fine-grid second-moment sum in tested coarse cells | Mean-velocity closure can lose a large numerical contribution | Physical penetration-depth error of that magnitude |
| Native moment export | 37.28s/194MB; constant controls and native averaging replay agree | One small cache supports repeated candidate diagnostics | Complete current functional or self-consistency |
| Rank35 anisotropic audit | ~20ppm computed averaging bound; actual changes−0.169/+0.900ppm | This averaging operation is small for this candidate | Formal interval certification or total response error |
| Same candidate, two grids | 2.738% response spread | Larger unresolved numerical sensitivity remains | Statistical uncertainty or a convergence certificate |
| Complete native nonlinear evaluation | 908.65s/882MB; tile/Jacobian controls pass | The tested action fits memory without the67.7GiB dense payload | End-to-end solve speedup or new-material feasibility |
| Rank36 reduced/full pair | Reduced0.893s; full580.35s/938MB; RMS passes, max residual fails | Compression approaches the registered stationary targets | Accepted gap, conditioned error, physical response |
| Frozen converged archived Nb replay | Released currents reproduced; correction changes2.5–2.8ppm | Synthetic thermal findings need material weighting | Large demonstrated material impact |
| Public response reproduction | Fresh build261.64s; native33.24s/187MB; all8exports bitwise match retained run;31inputs unchanged | Diagnostic is reproducible from public sources/inputs on this Mac | Full SCDFT cold start or physical prediction |

Detailed sources: [moments](VELOCITY_MOMENT_METHOD.md),
[anisotropic audit](ANISOTROPIC_MOMENT_GATE.md),
[full map](FULL_NONLINEAR_MAP_GATE.md),
[rank36 full receipt](verify_fourth_occupation_gap_result.json),
[archived replay](ARCHIVED_NB_FINITE_Q_GATE.md), and
[public reproduction](PUBLIC_RESPONSE_REPRODUCTION.md).

## Why the numerical changes are warranted

The first-moment closure squares an averaged directional velocity. Squaring and
averaging do not commute; inversion-related velocities may cancel before they
are squared. The second moment preserves the matched discrete sum instead.
Signed tetrahedron weights require direct identities and absolute triangle
bounds, rather than an assumed nonnegative variance theorem. The export is
opt-in and changes no native solver arithmetic.

The anisotropic extension does not silently force a candidate gap to respect
symmetry. It replays the actual native averaging operator, verifies state/support
mapping, and computes coefficient-range bounds at that same candidate. The
separate native single-state branch remains unchanged. This directly tests the
operation under suspicion while avoiding an unqualified interpolation or a
looser scalar-symmetry acceptance threshold.

Separate thermal and zero-energy findings have complete-routine fixtures,
high-precision scalar controls, and narrowly scoped source patches. Their frozen
converged-material effect is small in the tested Nb state. They remain useful
correctness findings, but do not carry a large-impact material claim. See the
[patch explanations and validation](patches/README.md).

## Where reuse is valid and where it fails

Primitive fixed-band derivatives can be reused algebraically within the stated
finite-difference approximation. Final assigned response states cannot simply
be reused across momentum: energy shifts precede DOS interpolation and can alter
weights, selected states, and ordering. Directional response and Q0 gap geometry
also differ under the inspected selector. The full48 tiny-Q control diagnoses
that selector; it is not a physical small-Q prediction.

A fixed-layout moment cache can be reused across candidate gaps only after exact
mapping and context checks. A reduced interaction basis additionally depends on
its kernel, saved renormalization, temperature convention and enrichment history.
A small coefficient residual does not certify the full native residual. Neither
residual alone bounds solution error near a critical eigenvalue. These boundaries
are explicit in [reuse](REUSE_BOUNDARIES.md) and [mapping](GAP_RESPONSE_MAPPING_GATE.md).

## Cost and opportunity cost

[Workflow costs](WORKFLOW_COSTS.md) separate historical cluster clocks, current
Mac actions, retained-basis setup and unknown upstream work. No calibrated Mac
cold-start forecast exists for microscopic electronic/phonon/Coulomb preparation.
The historical64-vector parent printed39.1minutes across four stages; it is not
a freshly reproduced Mac basis setup. A subsecond reduced solve therefore does
not imply a subsecond accessible workflow.

The sensible remaining investment is a bounded isolated reproduction and a
small number of discriminating validation experiments, not a material screen.
Repeated full checks must buy evidence against unchanged targets. Token usage,
energy and complete monetary cost are not measured here. Compute ceilings are
limits, not a reason to consume them.

## Comparison and scientific significance

The [current-method comparison](CURRENT_LANDSCAPE.md) identifies direct stiffness,
extended-GL, Eliashberg and finite-Q SCDFT approaches. A broad claim that cheap
response is an empty field is unsupported. No interviews or outreach establish
unmet user demand. This audit instead addresses a concrete numerical question
inside an existing microscopic workflow and provides inspectable evidence that
another researcher can use without accepting our impact narrative.

A consequential positive material result would require an explicit decision,
converged compatible gap, directional mapping, derivative/integration controls,
consistent current functional and normalization, plus independent validation
suited to that decision. [Physical interpretation](PHYSICAL_INTERPRETATION_GATE.md)
explains why matching experiment by inserting a fitted mass factor is inadequate.
The present data neither prove that broad goal impossible nor satisfy it.

## Remaining decisive experiments

The pinned public-source build and isolated31-input run now pass. Geometry,
raw/averaged cache and controls match all eight retained exports bit for bit;
original inputs are unchanged. This establishes practical reproducibility of
the diagnostic. The full prediction remains unqualified. The next bounded
fixed-density band replay tests an upstream reuse substage and measures its cost;
it does not refine the32³ derivative grid merely by changing XML bands.

Test rank37 cheaply after the build terminates. Consider another full check only
if the candidate stays numerically stable and the expected information justifies
its measured cost. If stationary targets pass, address conditioning rather than
promoting residual convergence directly to physical accuracy.

The final recommendation must distinguish a supported methods contribution
from the still-open material-access thesis, and explain what new calculation,
decision or exclusion has actually become practical. No final verdict or goal
completion is claimed at this checkpoint.
