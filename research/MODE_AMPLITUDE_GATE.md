# Reusing a qualified conventional mode for the nonlinear equation

The full arbitrary-seed pilot evaluates and differentiates the nonlinear map.
It does not locate the superconducting branch. The retained near-transition
conventional Ritz mode is a better motivated next starting point: its saved
linearized eigenvalue is1.0018603316299344 and both Fermi averages are positive.
The saved-data audit is not a fresh operator check.

## Proposed experiment

Apply the native kernel to eight weight batches in one pass: the zero-gap
linear derivative acting on the saved mode, plus seven nonlinear occupations
at mean Fermi gap amplitudes0.025,0.05,0.1,0.15,0.2,0.3,0.5meV. Amplitudes mean
the arithmetic mean of the two signed, dk-weighted Fermi averages; normalization
is explicit, not a fit to experimental data. Orient the overall mode sign so
both averages are positive. High-energy sign changes remain untouched.

The existing derivative has a finite zero-energy limit. The microscopic K and
saved Z remain fixed at8.05K; occupations change with amplitude. This is exact
batching of the declared diagnostic vectors, not an assertion that a single
mode spans the nonlinear solution. The expensive kernel is built once per tile,
not once per amplitude. We will report actual measured cost, not claim an8x
end-to-end speedup from the batch count.

## Acceptance before interpretation

Check the candidate basis schema, dimensions, temperature, configuration and
declared context, selected metadata, binary shape, finite values, normalization,
zero padding and same-sign nonzero Fermi averages. Retain current fresh native
initialization and saved-Z checks before reading the mode. Pin exact input,
mode, source, executable and retained dependency identities prospectively.

A fresh linear action must reproduce lambda*mode plus the stored residual to
2e-13+2e-12*maxabs(image), with relative eigenpair residual at most1e-9. This
checks this candidate's action, not completeness over all modes or independent
physical correctness of K. Do not reorder eigenpairs to manufacture acceptance.

For each amplitude, retain full residual vectors through the binary mode/image
representation. Readback recomputes projection, infinity norm and RMS from those
vectors, checks exact shape, finite values and padded zeros, and compares them
with the summary. A projected sign change only brackets a root of that scalar
projection; it is not a full nonlinear root. Residual-to-gap or response error
needs separate conditioning and convergence evidence. Do not call any scan
amplitude a solved gap.

## Verification and costs

A boundschecked native build passes. The compiled full amplitude module is
checked against an analytic rectangular rank-one kernel, all seven nonlinear
residuals, a fresh linear action, and stale-context rejection. A strict readback
fixture includes incomplete/stale/nonfinite payload and changed padding cases.
These tests do not replace the native candidate-action check.

Wait for the existing full pilot to terminate and pass readback before launching
this next job. Use a separate raw directory, unchanged3GiB process-group cap,
normal-pressure monitoring and120 continuous normal seconds before launch.
The proposed next pass has a1200s limit, within the original4h pilot budget.
This retains a single heavy native owner. Final launch authorization depends on
the measured full-pass result and remaining campaign time; the existence of this
document or an executable is not a launched or accepted experiment.

Build explicit target `mode-amplitude-probe.x` with the same retained toolchain
variables as FULL_NONLINEAR_MAP_GATE.md. `mode-control.in` contains the absolute
candidate directory and its declared context on separate lines. Run strict
readback with `python3 research/mode_amplitude_analysis.py <run-directory>`.
As with the prior native pilots, retained microscopic inputs and build objects
are external to this checkout; this is not a portable cold-start DFT workflow.

## Native result

Terminal PASS937.563265s, peak937394176bytes; strict full-vector readback PASS.
Kernel/application CPU747.158671s. Fresh linear action differs from the saved
lambda*mode+residual by1.5612511283791264e-17; relative eigenpair residual
3.920375975386137e-11. See mode_amplitude_result.json and receipt in the manifest.

The projected residual changes sign between0.10 and0.15meV. Full infinity
residuals over the scan range from7.01e-9 to2.66e-6Ry; none reaches the
prospective1e-10Ry native stationary-residual target. The smallest residual at
the smallest amplitude is not evidence of a nonzero root: zero gap is always a
root. The scan does not qualify any solved gap. Use0.15meV, the upper projected
bracket endpoint, as the explicitly declared reduced-solver starting amplitude.
