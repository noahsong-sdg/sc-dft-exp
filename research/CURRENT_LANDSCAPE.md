# Current opportunity assessment — 26 November 2026

Follow-up: [current upstream duplication check](UPSTREAM_STATUS_AUDIT.md),
27 November, confirms main still matches our pinned revision. No matching issue
or PR was found in the stated limited search; this is not proof of novelty or
demand. The recent installation request is explicitly excluded from the response
success thesis.

## Finding

Do not claim the broad response/penetration-depth pathway is unsaturated. Two
2026 methods directly overlap the proposed target. Current evidence favors a
focused correctness/reproducibility contribution over a generic platform claim.
No researcher interviews were conducted; user demand remains unvalidated.

## Primary-source comparison

| Method | Existing capability | Boundary relevant to us |
|---|---|---|
| Kawamura et al., finite-Q SCDFT | Shared microscopic framework for Tc and length scales | Our audited implementation; needs current and extraction qualification |
| Fuchs et al., extended GL | Gradient expansion retaining full order-parameter dependence, including multiband models | Targets low-temperature regime; benchmarked against real-space BdG in studied models, not interchangeable with full material SCDFT |
| Hiorth et al., DFT superfluid weight | Efficient zero-temperature uniform-pairing stiffness and penetration depth, conventional/geometric parts | Cheaper direct competitor for stiffness; assumptions differ from finite-T anisotropic SCDFT |
| EPW | Anisotropic Eliashberg, sparse frequency sampling and acceleration | Strong competition for generic gap/Tc automation; no absence-of-response claim established |
| IsoME | Automated isotropic Eliashberg Tc/gap workflows | Reusing spectral inputs already serves some commodity-hardware needs |

Primary sources inspected:

- https://doi.org/10.1103/lrhl-j9bt and released code/data.
- https://arxiv.org/html/2609.06014v1 (abstract and introduction).
- https://doi.org/10.1103/2xrg-6fy6 (published abstract; full subscription text not inspected).
- https://docs.epw-code.org/Releases and prior inspected tutorial.
- https://arxiv.org/abs/2503.03559 .

The extended-GL paper explicitly distinguishes conventional-GL finite-momentum
extraction from its new method, warning about extending small-order-parameter
relations to low temperature. This is a theoretical validity concern independent
of the algebraic implementation issues we found. Therefore slope/peak differences
cannot automatically be attributed to code, sampling or experimental error.

Hiorth et al. report validation for Al, Pb, Nb, MgB2 and two ruthenium borides,
including nonlocal/strong-coupling/sample corrections. Their uniform-pairing
zero-temperature assumption matters when comparing predictions. Efficient
penetration-depth screening already has serious work behind it.

## Decision implications

Our verified normal-reference discrepancies are specific, executable and current;
they are a stronger contribution thesis than old support issues or broad access
rhetoric. A useful deliverable is a pinned regression harness and a narrowly
qualified correction, together with an exact statement of missing material
replay data. Its physical impact still requires reconstruction or a new state.

For a larger project, first compare the scientific decision against the cheaper
stiffness method and the extended-GL validity domain. New SCDFT compute is
justified only if material-specific finite-temperature/anisotropic interactions
change the answer beyond existing alternatives. Novelty and demand are not
established by the existence of a new method alone.

This is a targeted source survey, not an exhaustive bibliometric saturation
measurement. No claim that competing authors have overlooked our code finding.
