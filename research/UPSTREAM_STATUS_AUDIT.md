# Current upstream duplication check

Checked 27 November 2026, approximately 06:19 UTC, through the connected GitHub
read/search tools. No messages or pull requests were sent.

The [main commit](https://github.com/mitsuaki1987/sctk/commits/main/) still resolves
to `4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33`, dated 9 October 2026. This is the
revision already hash-checked by the current and RHS fixtures. Its latest change
concerns static Coulomb input handling, not the thermal branches audited here.

Repository-scoped issue searches for `supercurrent`, `tanh`, `"finite momentum"`,
and `"penetration"` returned no results. A `supercurrent is:pr` search also
returned none. A repository-wide PR search returned two entries: build-system
PR 28 and production Pb-example PR 14. Neither describes these thermal factors.
Search is not proof of exhaustive absence: comments, other terms, forks,
unpublished work and unindexed records remain outside this check.

The issue search updated since 1 January 2026 returned
[issue 32](https://github.com/mitsuaki1987/sctk/issues/32), requesting CMake
installation support. That is current evidence about installation, not demand
for a finite-Q correction or laptop response platform. It is not a load-bearing
reason to pursue this study. Older support issues are likewise not used as
current demand evidence.

Conclusion: the inspected current upstream source still contains the demonstrated
expressions, and this limited search found no matching public report or fix.
This keeps the focused correction investigation viable; it does not establish
priority, novelty, material impact, external demand or broad lack of competition.
