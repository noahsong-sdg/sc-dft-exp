# Campaign handoff — 27 November 2026

Start here, then read the [scientific report](research/CAMPAIGN_REPORT.md),
[acceptance audit](research/REQUIREMENTS_AUDIT.md) and [project spec](PROJECT_SPEC.md).
The ledger preserves chronological evidence; old launch states are historical.

## Decision

**NARROW** to a reproducible numerical-validity study and qualified exact
optimization. Commodity hardware supports the measured saved-input diagnostics
and retained-gap stationarity check. Reliable material response and a portable
microscopic cold start remain unproved. No unmet-demand or novelty claim is established.

## Verified results

- Rank 38 passes both unchanged full stationary residuals: maximum 3.172e-11 Ry
  ≤ 1e-10; RMS ratio 7.546e-7 ≤ 1e-5. Full check 680.802 s / 938 MB.
  Conditioning, fresh basis setup and physical response remain open.
- Fourth-order 32³→48³ response spread is ~0.68%, versus ~5.52% for second order.
  The held-out 64³ step is −0.335% to −0.340%: smaller, but reversed. There is
  no continuum error bound. Fourth 64³ native run: 173.621 s / 881 MB.
- Same-band 64³ second/fourth comparison preserves DOS, curvature and energy axes
  bitwise; response differs by ~1.947%. D64/D48≈0.4979, versus the frozen 0.5625
  leading-order prediction. Second 64³ run: 172.033 s / 925 MB.
- Automatic 32³ reconstruction: 97.211 s / 98 MB; owning serialization: 0.803 s /
  85 MB; response: 22.419 s / 195 MB. All 897 points / 26 bands / weights preserved.
  Regeneration shifts response by only ~2.2e-10 relative; this tested provenance
  confound does not explain the original grid trend.
- Exact indexed/fourth 48³ probe matches all eight baseline exports bitwise:
  83.878 s versus 227.041 s, single-pair ratio 2.707×. No full-workflow speedup.

## Resource and execution state

All registered native owners are terminal; no watcher or heavy job remains.
Recheck actual processes before future work. Final guarded accounting: 79 attempts,
11,357.647 s (189.29 min), below the initial 240-minute ceiling. Includes failures;
excludes quiet gates and unguarded analysis. Energy and model billing are unknown.
The goal-system aggregate token checkpoint is recorded separately in WORKFLOW_COSTS.
Hardware: Apple M5, 10 CPU cores, 32 GiB; normal pressure at final snapshot.

135 offline tests pass; maintained Python compilation, moment replay, figure
source hashes and diff checks pass. Public Ubuntu CI 46017822969 passes after an
infrastructure-only retry. The final chat response reports the post-push synchronization check. CI does not rerun the Mac QE experiment or validate physics.

## Future work

The user's reusable [two-week prompt](TWO_WEEK_GOAL_PROMPT.md) is saved and linked;
writing it did not schedule or start another fourteen-day run. The twelve-hour
campaign is ending before its 17:41 UTC ceiling because its bounded controls and
required evidence are complete; unused compute is not a reason to extend it.

Continue only through the [portable-gap gates](research/PORTABLE_GAP_GATE.md):
source-only custom build, compatible rights-cleared microscopic/Z/basis inputs,
complete setup measurement, then a held-out physically qualified response with
an explicit decision and accuracy target. Stop broad screening until those pass.
No outreach, paid compute or subagents were used. Preserve the dirty historical
flux-pinning checkout.

Historical manifests pin their owning code and absolute paths. Never rewrite
those hashes to adopt current code. The 64³ protocols were read back before the
explicit 32³ extension in d3d2dd2; new reproduction requires fresh staging.
Use one heavy job or waiting watcher, 120 continuous normal-pressure seconds,
input hashes rechecked at launch and the unchanged 3 GiB guard. No queued work remains.
