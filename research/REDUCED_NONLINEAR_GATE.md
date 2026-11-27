# Reusing a linear operator basis for a nonlinear candidate

Repeated15-minute kernel passes could dominate a nonlinear solve. A retained
31-vector orthonormal basis Q and its images U=A0*Q exist at the exact8.05K
operator context used by the current pilot. This motivates an approximate
solve whose candidate is subsequently checked by the full native operator.
No additional microscopic approximation is accepted merely because it is cheap.

## Exact identity and declared approximation

At finite temperature, Q=0 and xic<0, write the gap map as
F(delta)=-(1+Z)^(-1)*K*chi(delta). Its zero-gap derivative is A0. Define
f(delta)=chi(delta)/chi_prime(0), with the dk-independent continuous extension
where dk=0. Then F(delta)=A0*f(delta) exactly for the fixed K,Z,beta setup.
For xi!=0, f=(delta/E)*tanh(beta*E/2)/(tanh(beta*abs(xi)/2)/abs(xi)).
For xi=0, f=2*tanh(beta*delta/2)/beta. Its derivative at xi=delta=0 is1.
Signed integration weights do not require a positive-definite metric here.

The new approximation is A0≈U*Q^T. Seek delta=U*c and solve
G(c)=Q^T*f(U*c)-c=0, with Jacobian Q^T*diag(f_prime)*U-I. The core uses
LAPACK Newton steps and a residual-decreasing line search. It stops on the
coefficient residual, not a claim about the full SCDFT residual. Nonfinite,
singular, non-decreasing and iteration-limit cases are explicit failures.

This reuses the recorded linear actions rather than constructing a new kernel
on every Newton iteration. The approximation omits f(delta)'s components
outside Q, and could fail even when the reduced residual is tiny. Source
identity, nonlinear convergence and physical accuracy are separate checks.
A native residual of the resulting full-length delta is the decisive next test.

Do not assume the native kernel is symmetric to invent a left eigenvector:
the inspected kernel2 zero-temperature expression treats x and y differently.
The general nonsymmetric model and its full residual require no such shortcut.
No novelty or general error bound is claimed for this reduced-basis experiment.

## Owning execution path and qualification

`reduced_nonlinear_core.f90` implements the ratio, derivative and reduced solve.
`reduced_nonlinear_driver.f90` reads hash-bound retained basis/state/mode files,
checks exact schema/dimensions/temperature/context/configuration, payload size,
finite values, orthonormality and padding, and seeds from the conventional mode.
It reports the mode's projection error into the retained representation.
It rejects zero or sign-changing candidates on the tested positive-weight Fermi
support; the minimum mean amplitude threshold is0.001meV for this experiment.
That is a candidate-selection boundary, not a universal normal-state criterion.

The output includes the full gap vector in Ry, Fermi means/minimum in meV and
the executable's Ry/eV conversion constant. Strict readback recomputes these
from the vector and matching initialized xi/dk. It explicitly marks full native
residual verification false. A small reduced residual alone does not qualify a
gap, response, or decision-grade prediction.

Compiled tests solve an exactly represented nonsymmetric problem and compare
with an independent exponential-occupation residual. They check the zero-energy
derivative and a normal-state root. A file-bound fixture repeats the full driver,
then rejects stale context/truncated basis and nonfinite/truncated output.
These test the actual owning routines, not only a copy of their formula.

## Resource and next-action gate

The proposed basis has135880 rows and31 columns, about67MB for Q and U. This is
an input-size measurement, not a measured solver peak. Use a120s/3GiB guarded
pilot only after the current amplitude owner terminates and its mode action
passes. Choose the starting amplitude from that measured scan and record it
before launch. Preserve one heavy native job at a time and the normal-pressure
launch/stop requirements. No reduced material job has been launched yet.

A successful reduced solve would justify one source-bound full native gap-map
validation at its candidate vector. Require finite full residuals, exact geometry
and saved-Z compatibility, fresh operator checks, and a separately stated
residual/conditioning criterion before any convergence or response claim.
If the omitted subspace dominates, record the failure and evaluate whether
residual enrichment or a full iterative solve is worth its measured cost.

Build explicit target `reduced-nonlinear-solve.x` with the retained native
Makefile and `RESEARCH_SOURCE_DIR`. Core fixtures require BLAS and LAPACK; CI
installs both development libraries. As before, retained large microscopic
inputs and native build objects remain external to this public checkout.

Checkpoint:64 offline tests PASS(7.227s), compileall and diff checks PASS;
retained-input reduced executable boundschecked build PASS. Native material
run remains unlaunched. Earlier mode/full manifests pin source snapshots before
this makefile extension:23d529a for mode amplitudes,90f922f for the full pilot.
Historical hashes should be checked against those revisions and immutable raw
artifacts, not silently replaced with later source hashes.
