# Material-derived response fixture: preparation pilot

This pilot reconstructs the missing response arrays from existing Nb microscopic
inputs. It does not restore the V3Si archive or solve a superconducting state.
An imposed initial gap permits only a numerical diagnostic of material-derived
weights and velocities/curvatures. Do not call it a physical response prediction.

## Execution path and bounded scope

The historical native source at SCTK revision
`47c06501da8ffd574c87469ddd6d5a2814171796` has working compiled QE dependencies.
The wrapper calls `stdin_control -> read_file_new(false) -> degenerated_band ->
read_a2Fsave -> stdin_scdft -> read_elph -> energy_grid -> ini_delta(true)`.
The fresh initializer calls `compute_d3k -> compute_dosk -> calc_d_xi_q`, then
interpolates derivatives and assigns response arrays to the integration states.
Inspection of `energy_grid` and this fresh path shows no direct Coulomb-reader
dependency; this omission is a pilot hypothesis until the run succeeds.

The wrapper stops before expand_g_v, make_Z, make_effint, or gap iteration. It
writes an explicitly labeled preparation-only state. It neither patches the
historical libraries nor overwrites their retained fixtures. The custom text
schema has a comment, grid counts, beta/volume/tpiba, momentum, reciprocal matrix
(Fortran column order), then xi/initial-gap/dk/dxq/d2xq and grid/k-index/band-index.
It is deliberately distinct from a production scgap restart file.

The two current outputs are integration-grid estimates: `compute_d3k` assigns
shift=0 for grid 1 and shift=0.5 for grid 2 before `store_d3k`. The current routine
accumulates each grid separately. Their difference is not automatically a
statistical uncertainty or a comparison between independent physical methods.

## Build and launch state

`prepare_response_state.f90` and `.mk` build against the pre-existing native
libraries. Build in a fresh ignored directory, passing `NATIVE_MAKEFILE` and
`RESPONSE_SOURCE` as absolute paths. No full QE rebuild is claimed. Initial
wrapper compiled/linked successfully; the final schema was subsequently rebuilt
successfully in `research/raw/nb-preparation-002`. The linker reports a
pre-existing duplicate BLAS library warning.

The first attempt was staged under `research/raw/nb-preparation-001`, with the
existing native input changed only to temp=1 K and q_fflo=(.001,0,0). A 120-second,
3-GiB process-group guard refused launch because host memory pressure was 2,
not normal (1). Exit was null, no child launched, and native compute consumed by
the pilot was zero. Failure receipt remains in the ignored attempt directory.
Do not overwrite it when retrying. The prior historical initializer's 30.96 s /
0.91 GB observation is only a sizing lead, not a measurement of this wrapper.

All 78 retained library/input files matched the historical recorded SHA256 hashes;
see preparation_input_verification.json. This verifies retained artifacts, not
their physical adequacy. Memory pressure remained at 2 after the rebuild.

Next: recheck memory pressure; stage the final wrapper in the fresh directory;
run one guarded
pilot only when normal. Check all output counts, finite values, nonzero curvature
and provenance before evaluating any currents. Qualification of a self-consistent
material response requires additional matching gap data and convergence evidence.
