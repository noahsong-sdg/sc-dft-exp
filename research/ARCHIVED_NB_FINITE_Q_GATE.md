# A stronger saved-gap replay candidate

The earlier negative check concerns pwscf.scgap.old only. The separate current
pwscf.scgap archive now has several matching fingerprints for a documented
finite-Q run. The geometry and released-current replay gates now pass for this frozen state.

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

The preparation-only nx300 pilot completed in 77.132 s, with peak process-group
RSS 322,535,424 bytes. No interaction kernel or new nonlinear gap was solved.
All 325,094 ordered indices match. Maximum differences are 4.89e-15 Ry in xi,
3.13e-16 in weight and 8.55e-15 Ry in shift. The reconstruction transfers only
curvature; the preparation's imposed gap never substitutes for the archive gap.
See [geometry comparison](nb_current_gap_geometry_comparison.json).

## Completed frozen-gap current replay

[archived_current_probe.py](archived_current_probe.py) checks geometry before
transfer, compiles the complete pinned current routine, and compares released,
corrected serial and corrected optimized OpenMP results with separately evaluated
shifted occupations. [Results](nb_archived_current_replay_results.json):

| Response grid | Released replay | Corrected replay | Relative correction |
| --- | --- | --- | --- |
| Unshifted | 1.0308029915044e-6 | 1.0308058532866e-6 | +2.776 ppm |
| Half-shifted | 1.1273879883785e-6 | 1.1273907841280e-6 | +2.480 ppm |

Both released currents match the documented output at its printed precision.
Corrected currents agree with direct occupations to below 3e-20 absolute across
the tested builds. Setting the archived gap to zero exposes NaNs in the released
routine; the corrected routine returns exact zero. The two grids contain 651
and 688 exact xi=0 states. This checks the finite-temperature product boundary,
not a new normal-state material calculation.

The replay, including streaming validation, reference evaluation and three
compilations, took 9.536 s; Python peak RSS was 25,624,576 bytes and maximum child
RSS including the compiler was 44,253,184 bytes. These are separate stage peaks,
not summed simultaneous memory or timings of a full microscopic workflow.

Reproduce after retrieving the hash-identified inputs and preparing geometry:

```sh
python3 research/archived_current_probe.py research/raw/nb-preparation-archive300-001/response-state.txt research/raw/nb-current-gap-001/pwscf.scgap
```

The thermal correction is tiny in this documented real state. Earlier imposed-gap
5–11% discrepancies do not establish comparable material impact. Neither grid is
a convergence certificate. The replay demonstrates inexpensive reuse of a
converged finite-Q state and a real boundary failure, but is not a corrected
self-consistent solve, a Q=0 stiffness, or experimental validation. It does not
establish an end-to-end commodity-hardware solution.

Next priority is a provenance-qualified Q=0 gap or a controlled alternative, and
qualification of derivative and moment representations. The fourth-order [111]
control remains unexecuted; its waiting owner was deliberately cancelled before
any native child launched. There are no live campaign native owners at this
checkpoint.

## Bounded search for equilibrium saved gaps

Depth-one public listings of old_fflo/ (3 responses including directory) and
old_fflo2/ (122 responses including directory) contain output logs and, in old_fflo2, nine .dat summaries, but no
gap-named files. See [listing audit](nb_old_directory_audit.json).
This closes these two candidate directories as sources of saved equilibrium
gaps; it does not prove no compatible gap exists elsewhere. Existing Q=0 logs
provide scalar gaps, which cannot silently substitute for state-resolved gaps.
