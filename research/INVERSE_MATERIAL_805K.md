# First fresh inverse diagnostic at8.05K

The source-built compressed inverse passes independent arithmetic readback at
the accepted rank51 niobium candidate. Its predicted correction is small, but
one full native Jacobian probe shows substantial approximation error. This is
sensitivity evidence, not a full-space gap-error or response certificate.

[Prospective1478-pin manifest](portable_inverse_material001_manifest.json),
[terminal result](portable_inverse_material001_result.json),
[method](LOW_RANK_INVERSE_DIAGNOSTIC.md),
[unchanged full-space acceptance protocol](GAP_CONDITIONING_PROTOCOL.md).

## Verified numerical evidence

The original full residual remains6.09669437161189e-11Ry with normalized RMS
1.0312693411116765e-6; both registered residual thresholds pass. No gap was
changed. At this exact candidate, B=(I-U Q^T D)^(-1) gives:

| Diagnostic | Result | Interpretation |
|---|---:|---|
| Maximum correction B Rnative |5.502435566805578e-10Ry|Compressed-model correction only|
| Correction/max gap |2.327317186525163e-5 (0.0023273%)|Not a certified relative gap error|
| One native probe: maxabs(B J v-v)/maxabs(v) |0.48070172169141706|Substantial error in this declared direction; not a full operator norm|
| Small-matrix largest/smallest singular value |4.641985291352913 /0.003016663459772667|Spectrum of51x51 M only|
| Small-matrix singular-value ratio |1538.781290407094|Not the condition number of the full Jacobian|

Signs are Rnative=-H and native Jacobian output=-Jv; the driver applies the
corresponding sign before the inverse action. Independent exponential derivative
readback differs by at most1.1102230246251565e-15. Exhaustive independent sums
for all2601 small-matrix entries differ by at most8.260059303211165e-14.
Independent inverse-action residuals are1.9748937124703536e-23 and
3.019806626980426e-13, within the registered arithmetic bounds. Native small
singular values pass ordering/positivity/summary and Frobenius checks; they were
not independently recomputed with another material SVD implementation.

## Provenance and cost

Terminal guard PASS0/errorNone, exact command/cwd/guardv2/deadline and all1478
immutable inputs verified. The runner recertified complete full016 lineage,
recorded full candidate, reduced004 gap/control/basis and public-library source
build; post-execution input checks passed. Raw readback correctly withheld its
terminal claim; the separate public result adds the terminal receipt. Outputs
and readback hashes are recorded. No native candidate correction was applied.

Guarded wall44.31549504166469s; validation13.832245749887079s,
native0.904173499904573s, exhaustive readback29.40811820793897s.
Recorded individual peak234225664B (~223.38MiB), sampled group228065280B.
This is a different workload from the full residual sweep and does not establish
a memory or speedup improvement against that sweep. Streamed basis input avoids
a second ~106MiB payload allocation; no controlled material RSS comparison was
performed. Quiet-window waiting and guard preflight hashing are outside this
wall charge; whole-workflow latency and energy remain unknown.

Charged campaign wall20589.35977421267s under21600s, remaining
1010.6402257873306s. No further native job, retry or budget increase is admitted.
Brave and the separate Docker study were untouched. Public CI46126020760 passed;
229tests,224Python compilations and moment replay passed before this run.

## What this changes

The small residual and0.0023% compressed correction cannot bypass full-space
conditioning: the tested inverse is visibly imperfect on a known native action.
The48% directional defect neither establishes nor rules out a contraction;
other directions remain unmeasured. It does not show a48% gap error or a48%
physical-response error. Full-space error and physical-response flags remain
false.

Next trace a full native action on this actual correction, its cost and any
stronger full-space bound supported by the kernel structure before spending
another sweep. An action on the correction and a refined nonlinear residual
would test the proposed correction but would still not, alone, bound the
unmeasured complement. Additional probe fitting is not a substitute for that
bound. The full response functional,1% uncertainty budget, public reproduction
and2K/4K cases remain required; the campaign goal is active.
