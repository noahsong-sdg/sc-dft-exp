# Public-input reproduction of the response diagnostic

## Current qualification status

The31-file input acquisition has been freshly tested:12,855,871bytes downloaded
from the original public release in74.642s, with exact per-file size/SHA256
matches. See public_response_input_download_result.json. All six source archives also freshly downloaded and hash-verified. The first
build stopped after16.464s at a nested LAPACK/CMake policy compatibility error;
see public_response_build_attempt001_result.json. Native execution using only
these files and a successful fresh-source build are still pending. Do not call this
a proven cold start until those checks pass. It does not generate a gap or Z.

The author [data page](https://mkawamura.ynu.ac.jp/data/) links the coherence-
length/penetration-depth benchmark release. This workflow retrieves selected
Nb1-151406 files from that release; it does not rehost the microscopic inputs.
The preserved full historical manifest listed58assets/1,452,686,099bytes.
The response-only candidate subset omits26Coulomb `.vel` files and `matdyn0`.
Source trace: the driver calls `read_file_new(needwf=false)`, `read_a2Fsave`,
`stdin_scdft`, `read_elph`, and the geometry routines, never `read_Coulomb`.
Actual isolated execution remains the decisive check on this subset.

`read_elph -> q_points` generates the working `matdyn0`. Its difference from
the downloaded file is not a missing input transformation in this path. Preserve
both original hashes in provenance; do not claim that one was downloaded as the
other or apply an unexplained round-to-zero preprocessing patch.

## Commands, independent of the historical checkout

Requirements: Python>=3.12, installed gfortran/GNU cpp-16, clang, cmake and make.
No package installation or global configuration is performed. Run from repo root:

```sh
python3 research/fetch_public_response_inputs.py research/raw/public-inputs
python3 research/build_public_response.py research/raw/public-build
python3 research/stage_public_response.py research/raw/public-build research/raw/public-inputs research/raw/public-run
(cd research/raw/public-run && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 SCTK_MOMENT_GRID=8 ./velocity-moment-probe.x -in native.in)
python3 research/moment_analysis.py research/raw/public-run/velocity-moments.txt
```

Each destination must be new, except input acquisition can verify/resume exact
existing files. Stale files are preserved and rejected. The build downloads
pinned QE/SCTK, FoX, MBD, devxlib and reference LAPACK3.11 archives, hashes them,
extracts fresh source and compiles without using retained objects or modules.
An optional `--archive-directory` supplies a hash-checked source-archive cache;
a run using it must report that reuse rather than call it fresh downloading.
`public_response_sources.json` pins every archive; current geometry extraction
has its separate exact source pin in current_moment_geometry.py.

The build emits its executed commands, logs/hashes, build-rule patch and final
executable identity. Only the offline submodule/hash recipes and configured GNU
preprocessor selection change. The current-geometry extraction is deliberately
an unshifted-band, fully shifted-grid compatibility diagnostic; it is not a
complete build of current SCTK. Toolchain and numerical qualification remain
separate from successful compilation.

Execute the exact command and environment in `public-run/run-manifest.json`,
from that file's `cwd`. The campaign additionally applies its120-second
normal-pressure launch gate,120-second native deadline and3GiB process-group
RSS guard. Expected native time is37seconds based on the retained-library
exporter, not a promise about the untested fresh build. Outputs include:

- `velocity-moments.txt`: constant-gap controls and fine-quadrature comparison;
- `response-assignment.{txt,bin}`: native state assignment;
- `response-symmetry.txt`: actual native cell rotations;
- `cell-moments-{raw,averaged}.{txt,bin}`: reusable moments before/after averaging.

The supplied input intentionally uses q1e-12 and the known absolute-selector
behavior to reproduce the full48-operation averaging diagnostic. It is not a
production small-Q prescription. A separate relative-selector fix has material
geometry controls; do not silently conflate the two experiments.

## What this can and cannot reproduce

If qualified, this gives independent public-input preparation of geometry and
moment-cache controls, without Coulomb matrices, savedZ, a nonlinear basis or an
HPC calculation on the user's machine. It does not demonstrate upstream
microscopic generation on a laptop, solve a self-consistent gap, reproduce the
private retained basis, qualify physical normalization, or provide a converged
material response. Replaying anisotropic candidates requires their own exact
state/context and numerical qualification. These are separate gates, not extra
claims inferred from a small input download or successful build.

## Preserved build failure and root-cause fix

Attempt001 downloads and verifies all source archives, then fails in LAPACK's
nested timing-compiler probe under CMake4.4.5. The top-level `-D` policy cache
entry belongs to the outer build tree; it does not initialize that nested
project. In plain terms, the parent setting was not passed to the child.

The fix adds process-local `CMAKE_POLICY_VERSION_MINIMUM=3.5` to command
execution. CMake documents that [this environment variable initializes new
build trees](https://cmake.org/cmake/help/latest/envvar/CMAKE_POLICY_VERSION_MINIMUM.html),
including nested projects. It preserves the intended policy choice throughout
the command tree without changing third-party Fortran or requiring an older
CMake installation. It is smaller and more direct than patching each vendor
CMakeLists file. No machine environment or installed package is modified.

A real nested-project regression reproduces the CMake4 failure without that
environment and compiles successfully with it. A new build root and a separate
prospective retry manifest preserve attempt001. The retry reuses only the
source archives freshly downloaded by001, after rechecking every hash; it
reuses no configured tree, object or module. Retry compilation and material
qualification are still pending. Failure time remains part of the cost record.
