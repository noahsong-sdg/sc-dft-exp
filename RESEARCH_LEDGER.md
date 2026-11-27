# Research restart ledger

## Current state — 2026-11-27 05:41 UTC

Active twelve-hour campaign; specification in PROJECT_SPEC.md. Previous turn
classification: progress (released finite-Q evidence traced). Current milestone:
durable specification and isolated public checkout created. No solver launched.

Next: pin upstream commit, implement bounded public retrieval and extraction;
analyze saved V3Si curves and reproduce author formulas with analytic controls.
Keep raw downloads ignored pending redistribution-rights review. Record hashes.

Native compute spent this campaign: 0 hours. Native pilot gate remains closed
until saved-data analysis identifies a consequential uncertainty. Full scope
remains active; neither demand nor laptop feasibility has been established.

## 2026-11-27 05:44 UTC checkpoint

Specification published in main commit 4eafc82. Retrieved seven public V3Si
curves plus original extraction/plot scripts; bounded fetch prints hashes.
Implemented deterministic analysis and three analytic/input-validation tests.
All three passed. No native compute. Current public processed data plus author
formula produces 184.44 nm at 1 K, versus published 97 nm: reproduction is NOT
established. Resolve provenance, units and protocol before interpreting window
sensitivity. Next: independently execute original formula, inspect xi.dat and
raw outputs, derive conversions and compare source revision/history.

## Conversion correction

The apparent 184.44 versus 97 nm discrepancy was our missing final plotting
factor 0.529177249, not a demonstrated release discrepancy. Corrected result is
approximately 97.60 nm. Archived xi.dat independently reports ll=1844.38 before
the plot's 0.1*0.529177249 conversion. Regression test now checks this external
reference. Window ratios are unaffected. Next: calculate peak-route conversion,
temperature dependence and physically justified small-Q fitting domains.
