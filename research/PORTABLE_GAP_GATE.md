# Boundary of the retained-input rank38 stationarity result

## Verified capability

The rank38candidate passes both fixed-Q0 stationary-residual targets under a
full native action:3.172e-11Ry maximum,7.546e-7RMSratio;680.802s/938MB.
The tiled path avoids the67.7GiB dense interaction allocation at66867/67940
states. This establishes feasibility of the measured action and this residual
check on32GiB hardware. It does not measure a new-material microscopic cold start.

## Raw dependencies checked

`nonlinear_map_probe.f90` initializes geometry against retained native state,
reads saved screened-interaction coefficients and fullZ, then evaluates the
nonlinear occupation/kernel map at8.05K. `nonlinear_map_probe.mk` links
`RETAINED_OBJECTS` from a historical native build. The inspected verify build
log confirms custom slab/tiled, cached interaction, native-pair, state-IO and
hashing objects plus QE/SCTK/BLAS libraries. Their identities are retained in
nonlinear_map_build_manifest.json and the full-check manifests; the public
response-only build is a different dependency chain. No retained source or
object was changed for this audit.

The31-vector parent is a thick restart of a historical64-vector basis. Its
four inspected setup stages report2345.58s; hardware provenance is not a fresh
Mac measurement. The original64-column payload is absent. Saved geometry andZ
metadata are checked against input parameters and exact context; copying them
is not regenerating them. Compatibility of the response-only31public files
with a fresh full-gap preparation has not been demonstrated.

## Meaning of the remaining barrier

This is an evidence/packaging and validation gap, not a measured hardware
impossibility. The retained exact action already fits memory. Conversely, that
fit does not imply that all upstream inputs are cheap, that their preparation
is portable, or that the response functional is physically adequate. No claim
of a one-second public SCDFT solution follows from the reduced Newton stage.

## Reviewable continuation if justified

Do not hide this dependency migration in a response or verification patch.
A deeper continuation should have three separately verifiable slices:

1. Reconstruct the custom native dependency build from pinned public QE/SCTK
   source and inspectable licensed source/patches, with no retained objects or
   modules. Verify initialization and selected kernel/Z entries against the
   recorded contexts. Include download/build/storage costs and failures.
2. Recreate a usable initial basis and savedZ from documented microscopic input
   sources, or explicitly distribute a rights-cleared reusable input release.
   An unavailable parent payload cannot be replaced by a claimed setup time.
   Measure fresh setup, reduced solve and independent full residual together.
3. Test a held-out state in a justified physical domain, bound relevant
   conditioning/discretization, and resolve the current functional/normalization
   before making a physical response claim. Specify the decision/tolerance first.

The current campaign should finish the bounded grid control and publish the
measured numerical-validity result. Launching a broad materials workflow before
these slices are qualified would not answer the original accessibility thesis.
