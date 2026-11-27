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

## Launch decision after the amplitude result

The native amplitude pass and strict reader passed. Its fresh conventional mode
action matches saved data to1.56e-17, and the scalar projection changes sign
between0.10/0.15meV. Select0.15meV before the reduced run. All prospective input
hashes were revalidated; the makefile snapshot is explicitly bound to273e607
since later commits append other targets. Pin reduced-control.in in the manifest.
A single120s/3GiB job is now queued behind120 quiet normal-pressure seconds.
This is a launch decision, not a material reduced-root result.

## Material reduced solve result

Terminal PASS1.071587s wall,113115136-byte individual peak RSS; group sampling
missed the short-lived peak (2s interval), so report the individual high-water
mark. Five Newton iterations reach coefficient residual2.0911549401814167e-17.
Strict readback PASS. Fermi averages0.1663104329/0.1653257249meV and minimum
positive-weight Fermi gap0.1271840629meV. The representation's saved-mode
projection error is7.098444363887353e-6, so a tiny coefficient residual cannot
be interpreted as a full-space residual. No speedup versus a full solve is
claimed: these are different acceptance levels and exclude basis preparation.

See reduced_nonlinear_result.json and the terminal manifest receipt. The full
native seed-verification job is now separately queued with prospective hashes
and stationary-residual targets in verify_reduced_gap_manifest.json.

## First enrichment and critical-mode audit

The rank-31 candidate failed both full native residual targets; see
GAP_SEED_VERIFY_GATE.md. A source-bound occupation-defect direction produces a
rank-32 basis. Its guarded reduced solve passes in 1.013797 s with
116375552-byte individual peak RSS, five Newton iterations and coefficient
residual 2.26338e-15. Strict readback passes. Fermi averages are
0.1230505613/0.1223244445 meV, about 26% below the first candidate, despite both
having tiny reduced residuals. No full residual has been computed at this new
candidate. See enriched_reduced_result.json and its terminal receipt.

The critical-mode representation audit separates two quantities. Rank 31 has
mode projection defect norm 0.00161901 and mode-action defect norm 0.000362514;
rank 32 has projection defect 0.00108424 and action defect 0.00146301. Thus the
occupation enrichment does not by itself reproduce the independently measured
linear mode. These are representation diagnostics, not full-space error bounds
or evidence that the inherited actions are inconsistent.

`critical_mode_projection_audit.py AMPLITUDE_DIRECTORY BASIS_DIRECTORY...`
reproduces these numbers from strict amplitude readback and same-beta/context
bases. A fixture distinguishes projection from action error and rejects stale
context. See critical_mode_projection_audit.json for source identities. The
amplitude run already measured the mode and its complete native image, allowing
the same tested algebra to append that missing mode component without another
kernel pass. Preparing that additional direction before full validation is the
next experiment, rather than spending a full pass on rank 32 first.

Neither reduced runtime includes preparing the original 31-vector basis or
upstream microscopic inputs. Their complete historical preparation cost remains
unresolved; no end-to-end acceleration follows from these timings.

## Measured critical-mode direction prepared

`prepare_critical_mode_enrichment.py` binds the basis to its manifest and the
completed amplitude run to its exact runtime inputs, terminal receipt and
published output hashes. Both bases must share beta, operator context and
configuration. It appends the omitted mode component and measured linear image
using matching orthogonalization subtractions. A file fixture verifies a known
nonsymmetric image and rejects a failed/stale receipt before creating output.

Rank 32 -> 33 preparation passes in 17.41 s / 183631872-byte peak RSS. The new
mode projection defect norm is 1.1421e-14, action defect norm 1.3708e-14 and
maximum action error 1.2880e-16. This verifies reproduction of the measured mode,
not all inherited actions or a nonlinear root. See critical_mode_enrichment_result.json.
The prospective critical_reduced_manifest.json pins one unchanged-executable
reduced pilot with the same 0.15 meV branch seed and 120 s / 3 GiB guard after
120 quiet normal seconds. All 71 local regressions pass (6.317 s), including
native fixtures; Python compilation and diff checks pass. Fortran source and
the previously qualified native executable have not changed.

## Rank33 reduced result and full-check decision

Terminal guard PASS: 0.905815 s wall, 119635968-byte individual peak RSS.
Strict readback passes: five Newton iterations, coefficient residual
3.42608e-17, positive Fermi means 0.1396677569/0.1388429262 meV and minimum
positive-weight Fermi gap 0.10681595 meV. The driver's mode-projection error
falls to 1.00316e-12. See critical_reduced_result.json, including the receipt.
These remain reduced-model results; the full residual is unknown.

One new full native check is justified by this improved representation and the
previous measured 785.63 s / 904 MB pass. verify_critical_gap_manifest.json pins
the candidate, reused native executable and controls before launch. The full
reader must enforce the same infinity/RMS targets, exact seed preservation,
tile and derivative controls, and terminal guard. Keep 120 quiet normal seconds,
1200 s / 3 GiB and one heavy owner. No threshold is relaxed.

## Rank34 reduced candidate

The second measured occupation direction gives a rank34 candidate in0.810367s
with122880000-byte individual peak RSS. Four Newton iterations reach coefficient
residual8.1532e-17; strict readback passes. Fermi means0.1541226193/0.1532134005
meV increase10.35% from rank33, while the measured-mode representation remains
accurate to1.0032e-12 in the driver diagnostic. Full native residual is unknown.
See second_occupation_reduced_result.json with receipt and manifest hash. This
continued amplitude sensitivity prohibits treating reduced convergence as
physical or full-space convergence. No additional full pass has launched.

## Rank35 reduced candidate and next full check

Terminal guard PASS0.703092s/126173184-byte individual peak RSS. Four Newton
iterations reach coefficient residual1.99493e-17. Strict readback passes; Fermi
means0.1533366410/0.1524306759meV decrease0.510/0.511% from rank34, compared
with the preceding10.35% shift. The driver's mode-projection error remains
1.00316e-12. See third_occupation_reduced_result.json with receipt/manifest.

The rank34 full residual had contracted19-fold in RMS ratio. Together with
this smaller candidate change and the measured524.86s/934MB native cost, that
justifies one next full check. verify_third_occupation_gap_manifest.json pins
the unchanged executable, new exact seed and original1e-10Ry/1e-5 targets.
Owner2285 is waiting behind120 quiet normal-pressure seconds, then1200s/3GiB;
no other production owner is active. No full residual or conditioning claim
is made for rank35 before terminal readback.

## Latest: rank35 full failure and rank36 reduced follow-up

The rank35 full check is terminal:587.598s/934281216B; native controls pass,
but Rinf1.04879e-9Ry and RMSratio1.67659e-5 fail both original targets.
`verify_third_occupation_gap_result.json` preserves exact seed and receipt hashes.
The next measured occupation defect has relative norm2.67829e-5; preparing
rank36 takes14.92s/184532992B. Its reduced solve takes0.893453s/129417216B,
four Newton iterations, coefficient residual4.51028e-17. Mean gaps
0.1534081823/0.1525029520meV change~0.047% fromrank35. Full rank36 residual
is unknown; verify_fourth_occupation_gap_manifest.json registers the next check.
No threshold or conditioning requirement has been relaxed. Earlier launch and
unknown-result statements above describe historical checkpoints.


## Standalone public-source recipe

The reduced driver/core can now be built in a fresh directory with
`make -f /absolute/research/portable_gap/reduced_nonlinear.mk QE_ROOT=/configured/public/qe`.
The recipe compiles both custom sources and links the configured BLAS/LAPACK;
it needs the existing public QE kinds/constants modules. The file-bound solver
fixture exercises this recipe and retains stale-data/context rejection. Actual
public-configuration build and material runtime remain pending. The nonlinear
seed threshold remains1e-9; building the driver does not qualify a seed or gap.
