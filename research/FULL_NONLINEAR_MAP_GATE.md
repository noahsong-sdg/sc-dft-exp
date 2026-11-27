# Full matrix-free nonlinear map gate

The selected-row experiment passed native compatibility and coefficient checks.
It did not evaluate a full residual. This experiment extends that tested path to
both sides of the Q0 gap equation, at the same saved8.05K Z and imposed seed.
It does not call the old nonlinear thermal-product code or form a dense kernel.

## Execution path and reason for the change

The retained `build_tile` returns two directional kernel components. Component1
maps right weights to left values with a transpose; component2 maps left weights
to right values without a transpose. The old selected diagnostic tested only
left rows. A full residual requires both orientations and accumulation across
all left tiles. Simply repeating the left-row comparison cannot establish this.

`nonlinear_tile_apply.f90` applies both orientations to four weight batches.
`full_nonlinear_probe.f90` supplies the imposed-seed occupation, occupations at
seed±h*v, and the analytic occupation derivative timesv, withh=1e-8Ry. Directionv
has opposite signs on the two sides to avoid a symmetric control masking index
errors. The derivative uses its finite Q0 zero-energy limit. Each kernel tile
is built once; all four actions share it. No physical approximation is added by
batching or tiling. The chosen seed and direction are diagnostic inputs, not
self-consistent solutions or physical observables.

The residual is R=-K*chi/(1+Z)-delta. Its Jacobian action is
Jv=-K*(chi_prime*v)/(1+Z)-v. Compare Jv with the central finite difference of R.
The same full pass thus measures the residual and checks a derivative needed by
subsequent nonlinear solvers. This is preferable to four separate kernel passes.
It is not an independent physical validation: both actions share K and Z.

## Prospective acceptance and resource budget

The fresh initialization must pass the existing declared cross-platform checker;
saved Z retains its exact scalar, finite, shape and normalization checks. The
native source point, input, binaries, source and executable are hash-bound by
`full_nonlinear_manifest.json` and the preceding reuse manifests.

Require finite output, unchanged seed, zero padding, tile explicit-sum errors
within2e-13+2e-12*scale and Jacobian finite-difference error within
1e-8+2e-6*maxabs(Jv). The finite-difference comparison is a numerical derivative
check at one seed/direction; it is not a general solver error bound. Readback
checks persisted dimensions, exact binary size, finite values, padding and both
residual summaries. Terminal guard PASS is additionally required.

Measured8-row tile CPU times0.081–0.109s project roughly680–913s for66867 rows.
This is a forecast, not a full-run measurement. One1200s pilot fits the initial
four-hour native feasibility budget. The3GiB process-group cap and normal host
memory-pressure requirement remain unchanged. Launch requires120 continuous
normal seconds. Abort on the retained guard's resource/deadline conditions.

## Verification and reproduction boundary

The boundschecked full native executable builds. Tests run the actual BLAS
wrapper on distinct rectangular directional matrices, four batches, partial
final tiles, poisoned padding and explicit sums. Another test runs the full map
routine with a synthetic kernel, comparing both sides against explicit sums and
checking its finite-difference gate, zero-energy point and persisted padding.
The strict readback regression includes stale, truncated, nonfinite and changed
padding cases. These isolate application/orientation errors from native physics.

Build with the existing local retained native toolchain (not a clean-checkout
portable build), using explicit target `full-nonlinear-probe.x` in a fresh build
directory. Set `NATIVE_MAKEFILE`, `RESEARCH_SOURCE_DIR`, `MAP_SOURCE`,
`MAP_FLAGS=-DCROSS_PLATFORM_STATE_CHECKS -I<cross-platform-v1/build>`, and
`MAP_EXTRA_OBJECTS=<cross-platform-v1/build/native_state_io_cross_platform.o>`.
The exact build command output is hashed in the manifest. The retained SCTK/QE
objects and large microscopic inputs are not bundled here; manifest hashes alone
do not make an independent cold-start reproduction possible. Do not overstate
this experiment as end-to-end laptop electronic-structure preparation.

Run offline tests with `python3 -m unittest discover -s research -p 'test_*.py'`.
Read a terminal native result using `python3 research/full_nonlinear_analysis.py
<raw-run-directory>`. Native output remains pending until the ledger records its
terminal receipt and verified readback. A full imposed-seed evaluation passing
would justify a nonlinear solve experiment, not establish a converged gap.

Checkpoint verification:59 offline tests PASS(4.478s), compileall PASS and
`git diff --check` PASS. Full native boundschecked build PASS. No separate
project typecheck command applies to these Python/Fortran diagnostics. The
previous unchanged moment refinement replay passed in the preceding checkpoint.
