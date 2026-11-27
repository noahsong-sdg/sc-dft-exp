# Known limitations

## Inputs are not yet interaction-equivalent

The scalar and native paths have not been shown to use identical effective
electron–phonon interactions. The public scalar spectrum writer, IsoME parser,
and native q-mode calculation apply different preprocessing and filtering.

In particular:

- SCTK can skip low-frequency q modes using a material-specific minimum
  frequency ratio, while the scalar parser retains positive spectral weight
  down to 0.01 meV.
- V3Si is sensitive to IsoME's extrapolation below the first tabulated spectral
  point. Its public spectrum-writer coupling, public direct q-mode coupling,
  and scalar-parser coupling are approximately 3.4611, 3.3575, and 3.5927.
- The scalar bare-Coulomb arms are sensitivity calculations, not independently
  derived ab-initio screened interactions.

Consequently, current scalar/native differences cannot be attributed solely to
Coulomb or spin-fluctuation terms.

## Scope

The cohort is deliberately selected and small. It cannot establish a universal
rule, an out-of-sample statistical guarantee, or publication novelty by itself.
SCTK is a reference configuration rather than experimental truth.

## Portability

The retained evidence includes machine-local paths, native binaries, and large
public payloads. This public repository reports checked results but is not yet a
one-command reproduction package. A content-addressed portable bundle remains
future work.

