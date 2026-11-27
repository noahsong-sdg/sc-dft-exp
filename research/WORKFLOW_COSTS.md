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
Recompute with `python3 research/resource_accounting.py`. Final terminal snapshot: 79 guarded attempts, 11,357.647 s (189.29 min).
Guard passes: 63 / 10,302.409 s; failures: 16 / 1,055.237 s. All registered
native owners are terminal. Guard acceptance is not scientific acceptance;
rank 38 separately passes stationary residuals, and the grid controls are
numerical diagnostics. The original 240-minute native ceiling was not expanded.

This includes guarded build/download work and failed attempts. It excludes
launch-watch waiting, unguarded compilation/acquisition/analysis, and model use.
CPU, energy and monetary cost are not inferred. It is not the total campaign
wall time or an end-to-end new-material cost. Source input/basis setup costs
remain separate below. Refresh the JSON before using this as a live budget.

## Public saved-input substages now measured

| Substage | Wall | Peak individual RSS | Scope |
|---|---:|---:|---|
|31public microscopic input downloads|74.642s|Not instrumented|12,855,871bytes; no Coulomb files|
|Fresh serial source build004|261.643s|466MB|No retained objects/modules/libraries|
|Exact public response diagnostic|33.235s|187MB|All8exports bitwise match; physical gates open|
|Eight-point fixed-density bands|1.695s|92MB|All208energies within9.61e-9Ry|
|Complete897-point fixed-density bands|98.947s|96MB|All23322energies within4.152e-7Ry; no offset fit|

These are individually measured, composable saved-input substages. The smaller
band pilot is calibration, not additional production required by every user.
Archive acquisition, all compatibility failures, quiet windows and unguarded
analysis must remain visible when describing campaign cost. They do not measure
new-density convergence, phonon/Coulomb generation, savedZ preparation, fresh
basis setup or a converged physical response. The separate retained rank38problem
meets stationary-residual targets; that is not a complete cold-start solve. No end-to-end cold-start forecast follows.


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


## Third-grid preparation and composed exact optimization

Fixed-density64XMLbands:826.542049s/116391936B,6273irreducible points,26bands,
897shared references max4.151732e-7Ry under unchanged1e-6target. Separate native
serialization is required; no new-density convergence or derivative bound follows.
Combined indexed/fourth48response:83.878123s, all eight exports bitwise equal
to the227.040529s original fourth48baseline. Observed single-pair ratio2.70679x;
relink2.545802s is separate. These timings do not include cold microscopic input
generation or establish a statistical speedup. Refresh JSON for full attempt costs.

Fourth64response:173.621s/881MB, serializer1.473s. Registered comparison
contracts the absolute step but reverses its sign at all temperatures. This
provides a negative control on monotone extrapolation, not a physical prediction.


## Final same-grid control and model-cost boundary

Automatic 32 bands: 97.211 s / 98 MB; owning serialization: 0.803 s / 85 MB;
fourth-order response: 22.419 s / 195 MB. Relative regeneration shift: 2.19–2.20e-10;
it does not explain the grid trend. These are saved-density costs, not a new
microscopic cold start.

At a 14:37 UTC checkpoint, the goal system reported 3,120,349 aggregate tokens.
That counter is not an API invoice, a per-model breakdown or the final token
count; monetary model cost remains unknown. It is recorded to make the substantial
agent overhead visible. No measured scientific-value-per-dollar claim follows.
Future work should optimize information per token as well as native runtime;
sunk effort is not a reason to expand the project.
