# Fresh8.05K stationary-residual checkpoint

The51column reduced candidate now passes both originally registered full native
residual tests. This is the first such fresh source-only candidate in this
campaign. It does not close the reliable-response objective.

## Numerical evidence

| Occupation basis rank | Maximum residual / Ry | RMS residual / RMS gap | Both targets |
|---|---:|---:|---|
| 48 | 3.6594364e-08 | 0.0014515116 | FAIL |
| 49 | 2.5192548e-09 | 4.6868829e-05 | FAIL |
| 50 | 3.1509825e-10 | 6.950913e-06 | FAIL |
| 51 | 6.0966944e-11 | 1.0312693e-06 | PASS |

Thresholds remain maximum<=1e-10Ry AND RMSratio<=1e-5. These are finite numerical
residual criteria, not an exact-root assertion or conditioned gap-error bound.
The unchanged verifier independently recomputes summaries from the full binary.
[Complete certification](portable_full_map_segment016_result.json) binds all1448
inputs and the ordered four-production-segment chain to qualification005.

All66867leftrows and67940rightstates are included in both kernel orientations.
The candidate is bitwise preserved; active geometry, gap, dk, Z and four occupation
fields bind every restart to the same state. Independent reconstruction from
unnormalized checkpoint images matches the final normalized output exactly.
Explicit-sum error5.124915249121731e-15 and analytic-Jacobian central-difference
mismatch3.420923988528557e-9 pass their original controls. Padding is excluded
from residual statistics and independently checked.

Candidate gapSHA303b379af5a563e82e1a9c54bec0b36fada9ff94cd4622d7e1a83d6df296f3d7;
fullmapSHA4738cd9dee699dcfff928565bece797ceeb613d25fa432570b6a1fe045d72711.
Fermi means0.15338589025376448/0.15248045857965492meV are reported candidate
quantities, not a new Tc, experimental match or physical-response result.
OperatorSHA6efcf2d527d3c81ae9620e3280916bb6b58db4809e6683cf0795256ed9fcce62,
beta19613.355577892344, fresh geometry/Z context unchanged.

## Laptop cost and limits

This candidate's four production segments total688.877348750364s guarded wall;
qualification36.779333082959056s is separate. Production peak<=922992640B
(~880.2MiB); qualification peak932052992B (~888.9MiB). Quiet waiting, input hashing,
analysis, source preparation and earlier attempts are not included in that
production total. Cumulative campaign guarded wall20543.82354433773s includes
charged earlier work and leaves1056.1764556622693s under the21600s pilot ceiling.
These are not whole-workflow latency, energy consumption or a controlled speedup.

No pressure policy was relaxed. The streaming-hash guard reduces verifier memory;
the native compact Coulomb table still sets most of the native allocation floor.
Brave and the other study were untouched. No next heavy job is admitted.

## Remaining scientific step

A small residual can coexist with a poorly determined gap. The full Jacobian
inverse/error transport remains missing; a51dimensional Newton solve or one
finite-difference direction cannot establish full-space conditioning. Trace the
available Q/U inverse candidate and full residual before choosing a bounded
conditioning/correction experiment; preserve the signs H=d-F=-Rnative.
See [conditioning protocol](GAP_CONDITIONING_PROTOCOL.md).

The response functional/current normalization/mass/vertex, relevant grid and
interpolation errors, <=1% uncertainty on stiffness and normalized ratios,
2K/4K compatible contexts, isotropic comparison, matched physical reference,
rights-cleared acquisition and public reproduction remain necessary. This
milestone accepts none of those by implication.
