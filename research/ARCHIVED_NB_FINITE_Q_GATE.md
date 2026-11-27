# A stronger saved-gap replay candidate

The earlier negative check concerns pwscf.scgap.old only. The separate current
pwscf.scgap archive now has several matching fingerprints for a documented
finite-Q run. It is not yet accepted for reconstructed response replay.

Verified from bounded public records in the Nb1-151406 directory:

| Record | Observed fingerprint |
| --- | --- |
| Final input | 4 K, q_fractional=(0.0004,0,0), nx=300, nmf=10 |
| Final output | SCTK commit 47c06501da8ffd574c87469ddd6d5a2814171796, QE 7.4.1 |
| Gap-point counts | 159852 and 165242 in both output and saved gap |
| Convergence | iteration 43, residual 6.2838e-16 Ry versus threshold 1e-15 |
| Reported mean gaps | 1.1621 and 1.1607 meV |
| Saved-state means | 1.1621247481 and 1.1606870482 meV, matching printed precision |
| Modification times | gap and final output both 1 February 2026, 18:21:51 GMT |
| Released current | 1.0308e-6 and 1.1274e-6 in reported atomic units |

The complete historical broyden source is byte-identical to our pinned current
file, including the owning supercurrent routine. Its full hash is
1062c2a6656455b223111928fbc37996fce564d6dcf0a3acc945b973a9101598.
This directly links the numerical correction to the routine identified by the
released output. The saved gap itself has no temperature/convergence header.
The association is supported by the fingerprints above, not a self-contained
restart certificate or a mere filename assumption.

nb_current_gap_manifest.json records the bounded 46163371-byte download and
hash. nb_current_gap_provenance.json records URLs, input/output/script hashes,
archive metadata, source identity and output scalars. The raw archive remains
ignored; no redistribution right is inferred. nb_current_gap_scalar_fingerprint.json
records the independent saved-state scalar calculation.

## Missing curvature and decisive next check

The historical writer stores xi, gap, Z, assigned weight, directional shift,
and two integer indices. It omits curvature. The explicit reader rejects the
older four-float and newer six-float schemas rather than guessing columns.
Negative gaps away from the Fermi surface are retained, not clipped.

A preparation-only pilot is staged with the exact temperature, Q, nx and nmf,
using retained microscopic inputs and the same historical revision. It computes
geometry and curvature without allocating interaction kernels or solving a new
gap. The live owner is recorded in the restart ledger. Its constant initial gap
must not replace the saved gap.

After an accepted run, execute:

```sh
python3 research/compare_finite_q_geometry.py research/raw/nb-preparation-archive300-001/response-state.txt research/raw/nb-current-gap-001/pwscf.scgap
```

Require matching dimensions and ordered indices; inspect xi, weight and shift
differences before any transfer. Then reconstruct only the missing curvature
and attempt to reproduce both released currents at their printed precision.
Only after that gate may a frozen-gap corrected-current comparison be described
as a replay of this documented state. It still would not be a corrected
self-consistent solve, a Q=0 stiffness, or an experimentally validated prediction.

This route is prioritized over the fourth-order [111] control because it could
replace imposed-gap diagnostics with an actual converged-state test. That control
was cancelled while waiting, with no native child, and remains unexecuted.
