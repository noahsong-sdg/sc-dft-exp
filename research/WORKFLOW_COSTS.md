## New measured full nonlinear evaluation

The retained-input Q0 full residual/Jacobian pilot completed in908.645s wall
with881655808-byte peak group RSS (716.608s kernel CPU). The dense interaction
allocation floor at the same66867/67940 counts is67.7GiB; the tiled calculation
does not allocate it. This comparison is an allocation bound versus measured
RSS, not a paired speed benchmark. It includes initialization/readback but not
upstream electronic/phonon/Coulomb generation, a fresh Z calculation, or gap
convergence. See FULL_NONLINEAR_MAP_GATE.md and full_nonlinear_result.json.
The initial arbitrary seed has max residual7.8e-5Ry and is not accepted as a gap.

# Historical V3Si workflow ledger

New local feasibility boundary: [dense interaction memory floor](MEMORY_FLOOR.md).
At inspected state counts, the dense array payload alone exceeds laptop RAM.
This is a source/shape-derived bound, separate from the cluster timing trace.

Generated with `python3 research/workflow_costs.py`. URLs, hashes, all matching
total clocks and reported core layouts are in workflow_cost_manifest.json.
This is an author-machine resource trace, not a Mac forecast or summed bill.

| Stage | Reported wall seconds | Reported cores | Interpretation |
|---|---:|---:|---|
| Ground-state SCF | 15.36 | 336 | One logged run |
| Phonons | Multiple clocks | 336 | Concatenated jobs and intermediate/final summaries; do not sum blindly |
| Dense electron–phonon coupling | Multiple clocks | 336 | Same scope ambiguity |
| Electron–phonon matrices | Multiple clocks | 336 | Same scope ambiguity |
| Dense NSCF | 50.68 | 960 | One logged run |
| Twin-grid electronic calculation | 46.92 | 960 | One logged run |
| Screened interactions | 131280 | 768 | Printed to minute resolution |
| Tc calculation | 716.20 | 1152 | Historical output; not our accepted-result protocol |
| One finite-Q solve | 732.02 | 1152 | 1 K, fractional Q=.0025 |

Missing or unresolved: structure-relaxation allocation, complete phonon job
group accounting, queue/setup costs, peak memory, failed attempts, convergence
controls, retrieval time and machine equivalence. Public outputs have different
dates; do not assume they form one contiguous execution campaign.

For a reused-input scan the expensive interaction-generation step is amortized.
Using just its 131280 s and one 732.02 s action as illustrative anchors,
20 equal-cost response points would cost 145920.4 s total; a 19x speedup of
those response points changes this to 132050.5 s, only 1.105x overall. If inputs
are already available, that same response-only improvement can matter directly.
Actual scan-point times vary; this algebra is not a runtime prediction.

Execution trace: stdin_scdft -> read_elph -> read_Coulomb -> energy_grid ->
ini_delta -> expand_g_v -> make_Z -> make_effint -> broyden_gapeq -> out_delta ->
supercurrent. A preparation-only curvature dump could stop after ini_delta on
the fresh-state branch, but historical saved gap/state alignment must be
reconstructed. Restart does not regenerate the missing curvature. A direct
postprocessing entry point is not established by this trace.

## Current Mac guarded-pilot accounting

[campaign_native_resource_accounting.json](campaign_native_resource_accounting.json)
snapshots terminal native guard receipts, including prelaunch and failed attempts.
Recompute with `python3 research/resource_accounting.py`. After the rank35 full check, moment-cache
export and rank36 reduced pilot, 44 terminal attempts total
5738.039 s: 5470.338 s in 33
guard-PASS attempts and 267.701 s in 11 failures. The full-candidate execution
passed its guard but failed its numerical residual targets. Guard PASS alone is
not scientific acceptance. Waiting, builds,
downloads, Python references and model use are excluded; this is not total
campaign time, CPU time, energy, or monetary cost. Those unmetered quantities
remain unknown. Each row records the original receipt hash and resource metrics.

## Retained basis setup: historical partial accounting

The 31-vector basis is an external thick restart of a 64-vector parent, not a
one-second cold-start input. `basis_setup_cost_audit.json` binds the restart
metadata, transfer receipt, and first four parent-stage logs/controls/receipts.
The controls link consecutive stages; basis metadata grows 16/32/48/64 columns.
Each wrapper reports passed/exit zero. Their printed SCTK wall clocks total
2345.58 s (39.1 minutes). Peak sampled process-group RSS is recorded per stage.

This is a historical source trace, not an independently verified source-platform
or fresh-Mac benchmark. It excludes microscopic preparation, saved-Z generation,
rotation, failed work and later validation. The inspected transfer receipt's
8.08 s concerns copying/preparing helper inputs, not generating the parent basis.
The parent binary is absent at both inspected translated parent locations;
the retained 31-column payload remains available and hash-bound. Full cold-start
reproduction and its total cost are still unproved. No overall speedup follows
from the one-second reduced timings.
