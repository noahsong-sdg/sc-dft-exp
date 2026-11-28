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

## Next bounded material step

Add a separate driver and strict file-bound tests before launch. Bind Q/U,
geometry, beta, operator, full candidate, Rnative, direction and Jnative to the
accepted full-segment016 manifest/result. Recompute the occupation derivative;
exclude padding from reported norms. Save the small matrix/singular values,
correction and probe defect with independent readback. Source-build against the
already-qualified public BLAS/LAPACK closure; never reuse historical custom
objects or change the accepted residual candidate in place.

Check the full action on a useful correction and the actual nonlinear residual
before interpreting a refined candidate. Neither this module nor those probes
supply the missing full-space contraction/inverse bound in
GAP_CONDITIONING_PROTOCOL.md. The1056.1764556622693s remaining guarded budget and
normal-pressure/one-owner/3GiB policy remain in force; no next job is admitted.
