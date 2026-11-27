# Current campaign state — 2026-11-27 14:38 UTC

Read this first; then PROJECT_SPEC.md, the scientific report and the relevant
prospective manifest. The ledger is chronological history. Recheck processes
and receipts: a stored state file alone never proves that a job is live.

## Mandate and limits

Active twelve-hour campaign ends 2026-11-27 17:41 UTC. The two-week prompt is a
separate reusable mandate, not a scheduled extension. Public repository is
noahsong-sdg/sc-dft-exp; primary checkout /Users/noahs/Developer/sc-dft-exp.
Preserve the dirty flux-pinning checkout. No outreach, paid compute or subagents.
One heavy native job or waiting watcher at a time; 120 continuous normal-pressure
seconds and all input hashes rechecked before launch; 3 GiB process-group cap.
Initial native ceiling: 4 wall-hours. Latest terminal accounting: 11237.213 s across
76 attempts (187.29 min); no native run currently active. Energy/model money unmeasured.

## Verified scientific state

- Rank 38 retained-input Q0 candidate meets both unchanged full stationary residuals:
  maximum 3.172e-11 Ry ≤ 1e-10; RMS ratio 7.546e-7 ≤ 1e-5. Full check: 680.802 s / 938 MB.
  Conditioning, fresh basis setup and physical response remain unverified.
- Fourth-order 32→48 diagnostic spread: ~0.68%, versus ~5.52% for second order. No
  continuum bound. Combined indexed/fourth-order 48-grid probe matches all eight baseline
  exports bitwise: 83.878 s versus 227.041 s, single-pair ratio 2.707×.
- 64-grid bands pass in 826.542 s: 6273 points / 26 bands; 897 shared points, maximum difference 4.152e-7 Ry ≤ 1e-6.
  Owning serialization passes in 1.473 s; all coordinates, energies and weights are preserved.
- 132 local offline tests pass in 11.568 s; compilation, moment replay and diff checks pass.
  Public CI for c4f0944 passes. Newer data/document-only commits need final CI check.

## Held-out third-grid result and next controls

64 response is terminal PASS: 173.621 s / 881 MB. The registered comparison
contracts in absolute step at all three temperatures, but reverses direction:
32→48 is +0.677–0.680%; 48→64 is −0.335–0.340%. Both conditional h²/h⁴
continuation predictions miss this reversal. No continuum error bound follows.
See `research/third_grid_comparison_result.json` and `research/figures/third_grid.png`.

Second64control is terminal PASS172.033s/925MB. Same-band DOS/curvature/energy
axes are bitwise equal; F4/F2−1≈1.947% at allT. Absolute stencil difference
D64/D48≈.4979 versus the frozen .5625 prediction (−11.5% discrepancy).
This is a controlled stencil effect, not a continuum-error estimate.

Automatic32bands PASS97.211s/98MB; owning serialization PASS0.803s/85MB.
All897coordinates/26bands/weights preserved; shared897energies max4.152e-7Ry.
All prior native owners are terminal. The sole next root is
`research/raw/public-fourth-regenerated32-001`, responseguard120s after120normal
seconds. It uses the exact-qualified combined fourth-order probe and frozen
`regenerated32_analysis.py`.135offline testsPASS9.362s; compileall/momentreplay/
diffcheckPASS. After strict readback and comparison, close the full requirement
and public-evidence audit; do not add further variants without a new scientific gate.

## Remaining completion work

Finish bounded controls, inspect figures and public artifacts, refresh full cost
accounting, run final checks, and audit PROJECT_SPEC.md deliverables 1–10 against
current evidence. Give a supported continue/narrow/pivot/stop recommendation.
Do not equate residual acceptance, conservation or an exact speedup with reliable
material prediction. [The portable-gap gate](research/PORTABLE_GAP_GATE.md) records the inspected gap dependency
boundary; no broad demand/unsaturated-platform claim is established.
