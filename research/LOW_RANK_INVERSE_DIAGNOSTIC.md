# Low-rank inverse action diagnostic

The fresh8.05K candidate passes the original full residual thresholds. Its gap
error remains unbounded: the native check supplies Rnative=-H and one action
Jnative*v=-J*v, while the reduced Newton solver does not retain inverse-action
diagnostics. Near a sensitive root, a small residual alone is insufficient.

The separate source module low_rank_inverse.f90 implements

    M = I - Q^T D U
    B w = w + U solve(M, Q^T D w)

for multiple right-hand sides, using DGEMM, DGESV and DGESVD. D is supplied by the
caller and must correspond to the candidate's occupation derivative. Singular
values describe M only. The original reduced solver, native probe and all pinned
input chains remain unchanged.

The routine independently applies Jmodel=I-U Q^T D to the returned vectors and
reports maxabs(Jmodel*Bw-w). This checks the compressed inverse algebra and
finite numerical execution, without asserting a full-operator error bound.
Nonfinite inputs/outputs and invalid dimensions fail explicitly; a singular
small solve or failed SVD returns a nonzero LAPACK status. A material caller
must reject that status before using any output. Workspace scales with n*rank
and the number of right-hand sides; no dense full-state Jacobian is formed.

For the existing full output, the proposed two right-hand sides are Rnative and
-Jnative*v. Then B*Rnative is the approximate Newton correction -B*H, and
B*(-Jnative*v)-v is the defect measured on that particular native direction.
Its ratio to ||v|| is a probe diagnostic. It cannot upper-bound the defect on
unmeasured directions. No file-bound material run has yet been admitted.

## Independent controls

The actual Fortran module is compiled and compared with a separately formed,
full dense nonsymmetric Jacobian solve, including the Newton and native-Jacobian
signs. Other controls reject a singular small matrix, changed output shape and
nonfinite input before a solve is accepted. Inputs are checked for preservation.

A separate native counterexample has a well-conditioned small matrix and a
perfect probe, but an arbitrarily sensitive unmeasured full-space direction.
This prevents interpreting probe agreement as evidence of a global condition
bound. Its scientific limitation is structural, not a tolerance to relax.

223 offline tests PASS22.481s, including native fixture builds/execution;
220maintained Python files compilePASS; moment_refinement exit0; diffcheckPASS.
No separate configured typecheck. This tests the core, not an actual material
inverse estimate or response uncertainty.

## File-bound driver controls

low_rank_inverse_driver.f90 now reads an explicit versioned control, retained
basis metadata/payload, initialized geometry, seed metadata/binary and full-map
summary/binary. It requires matching beta/operator/configuration, dimensions,
bitwise seed preservation, orthonormal basis and zero inactive padding. It
recomputes both residual statistics and requires the original passing targets
before using the state for inverse diagnostics. It does not rerun the kernel or
independently certify a fabricated full-map input; the prospective staging and
readback must bind these files to the accepted full-segment016 certificate.

The driver reuses the unchanged occupation_ratio derivative and inverse_actions
core. It computes B*Rnative and B*(-Jnative*v)-v, without overwriting the accepted
candidate. The separate low_rank_inverse.mk builds only these three inspected
sources against the configured BLAS/LAPACK libraries; production targets remain
unchanged. Diagnostic output retains D, correction, probe defect, small matrix
and singular values, with explicit NO full-space bound text.

Actual source-built fixture readback independently checks the exponential
occupation derivative, the returned inverse action, every small-matrix entry,
analytic2x2 singular values and zero padding. Rejection controls cover stale
operator/beta/configuration/geometry, truncated payloads, bitwise candidate
changes (including signed zero), nonfinite state, nonzero padding and trailing
metadata. No diagnostic output is accepted in these stale cases.

225 offline tests PASS25.296s including native builds/execution;221maintained
Python sources compilePASS; moment_refinement exit0; diffcheckPASS. No separate
configured typecheck. These fixtures use their declared test libraries; no
actual public-library material build/run has yet been accepted.

## Independent output readback

low_rank_inverse_analysis.py now checks the declared source context, bitwise
candidate, original full-map summaries and both original residual gates. It
recomputes the derivative using an independent exponential formulation, every
entry of M using math.fsum, and both returned inverse actions using Q/U directly.
It checks singular-value ordering/positivity, native summary consistency and the
Frobenius identity, without claiming an independently solved singular spectrum.
The spectrum remains a native LAPACK diagnostic, not a full Jacobian estimate.

Readback rejects changed derivative/correction/probe/matrix/singular payloads,
truncation, NaN, excessive reported inverse residual, a stale zero-gap source
and changed context. Output and input hashes are reported; an owning terminal
receipt and accepted parent provenance must still be bound separately.

The basis is read one column at a time. This avoids a second full payload copy
(~106MiB for135880x51 Q/U); it is an allocation reduction, not a measured process
RSS claim. All2601 small-matrix entries require353423880 scalar dot-product terms
at the material size. That independent Python work needs a bounded runtime pilot;
it is not hidden inside the previously measured native residual time.

226tests PASS24.392s incl native builds/execution;222maintained Python sources
compilePASS; moment_refinement exit0; diffcheckPASS. No separate typecheck.
Native source targets and accepted candidate/residual thresholds are unchanged.

## Build-only admission

portable_inverse_build001_manifest.json binds31inputs and a checked four-command
make plan: the three inspected sources, three fresh local objects, qualified
public liblapack.a/libblas.a and exact compiler/f951 identity. All inherited
source/configuration/library pins and the prior reduced-build owning receipt,
manifest and executable were revalidated. No historical custom object is linked.
This is a prospective build, not a completed public-library qualification.

Admit only that build,120s/quiet120/3GiB. The current guarded ledger remains
20543.82354433773s, leaving1056.1764556622693s under21600; worst build120 leaves
936.1764556622693s. Fixture build/run/readback1.369s supports the bounded build,
not a material timing guarantee. A later exhaustive material diagnostic may need
240s, leaving696.1764556622693s even after worst build; it is not admitted yet.
Before it runs, bind the accepted full-segment016 closure/result, source-built
executable and independent readback in a fresh root. Preserve H=-Rnative and
J*v=-Jnative*v, exclude padding and never overwrite the accepted candidate.

A full action on a useful correction and its actual nonlinear residual remain
necessary before interpreting a refined candidate. None of these small-matrix
or probe checks supply the missing full-space bound in GAP_CONDITIONING_PROTOCOL.md.
