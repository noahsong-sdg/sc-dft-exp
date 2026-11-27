# A recoverable saved Nb gap: geometry alignment, not physical qualification

The author's `Nb1-151406/pwscf.scgap.old` was downloaded with a 20 MiB bound
(15,772,438 bytes). It remains ignored; URL, retrieval time and SHA256 are in
nb_legacy_gap_manifest.json. The server reports modification on 30 January 2025;
that timestamp is not a calculation temperature, convergence receipt or source
revision. It predates the finite-Q output used elsewhere in this campaign.

Its explicit schema is four floats (xi, gap, Z, weight) and two integer indices.
It contains neither Doppler shift nor curvature. Do not use the newer six-float
restart parser for it. `compare_legacy_gap.py` validates this old schema directly
and compares geometry/order with the retained native zero-momentum initializer.
It does not import it as a certified production restart.

Both grids have identical counts (66,867 and 67,940), with zero band/k-index
mismatches across all 134,807 states. Maximum absolute xi differences are
4.2721381987576024e-13 and 1.9149171137655685e-10 Ry; maximum absolute weight
differences are 1.3893610383269167e-13 and 1.234844136123979e-13. Exact hashes and
metrics are in nb_legacy_alignment.json. This is close numerical alignment, not
byte-exact equivalence or proof that interaction settings agree.

The saved gap is nonzero, but its temperature, interaction model, convergence and
generation history remain unverified. The later delta0.dat temperature table
does not establish those properties for this older backup. It is suitable as a
candidate fixed-gap diagnostic input, subject to explicit labeling. Predictive
finite-temperature response or nonlinear finite-Q claims need further evidence.

The native Q=0 initializer already serializes d2xq, but it vanishes there. The
live preparation pilot is still needed for nonzero-Q geometry. New-Q weights and
state counts may differ; do not copy gap rows solely because the Q=0 counts match.
For linear response, a Q=0-gap reuse route is worth deriving and convergence
testing, rather than assuming that an entire nonlinear scan needs no new solve.

Reproduce the comparison after retrieving the manifest URL into the ignored raw
path and verifying its SHA256:

```
python3 research/compare_legacy_gap.py /path/to/native-initializer-folder research/raw/nb-legacy-gap.old
python3 -m unittest discover -s research -v
```

The native folder must contain the exact documented native-init.meta/bin schema.
Its payload hash here differs from the historical Linux fixture; both are named
explicitly in the result, rather than retrospectively passing the old byte-exact
cross-platform gate. The raw legacy file is not redistributed by this repository.
