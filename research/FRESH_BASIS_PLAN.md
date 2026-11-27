# Fresh compatible gap basis

The execution path is fresh geometry -> verified finite-temperature Z -> linear
weights -> tiled microscopic pair operator -> block images -> Rayleigh–Ritz
checkpoint -> reduced nonlinear candidate -> independent full residual. The
historical basis and its images are not a compatible fresh calculation.

Two byte-preserved source modules are now public, with hashes and origin recorded
in portable_gap/basis_source_provenance.json. They are not yet compiled or run in
this context. basis_compile.mk provides the source-only compile target using the
already public operator build. No historical custom object is linked.

block_linear_operator forms the exact finite-temperature Q0 zero-gap derivative,
including the finite xi=0 limit beta*dk/4, applies both tile orientations, and
normalizes by the current 1+Z. It requires serial execution, finite positive beta,
xic<0, zero dxq, valid counts and zero padding. An independent uncached native
row/column oracle must qualify the new actual-input application before its
images are accepted.

tc_subspace generates deterministic fresh energy/band/state trial functions and
orthonormalizes them twice. Its checkpoint combines trial vectors and their
current images, validates the Gram matrix, and solves the nonsymmetric projected
problem. Residuals select a candidate and new projected directions. These are
algorithmic candidates, not a converged gap or an error bound. A positive
conventional Fermi branch must be checked independently of residual size.

First qualify source compilation and an actual-input bounded linear application
with uncached row/column controls. Measure that application on this Mac before
forecasting the full initial16-vector image sweep. Bind the eventual basis to
fresh geometry, physical temperature, full Z, pair coefficients, source/library
identities and the exact trial payload. Reject changed contexts and stale basis
images. A continued basis must preserve its original certified identities.

Only then run bounded full image applications and enrichment as needed. Preserve
the unchanged full nonlinear residual criteria (maximum1e-10Ry and normalized
RMS1e-5); quantify conditioning and gap-to-response error separately. The 8.05K
anchor does not qualify other temperatures. No basis stage is completion of the
response goal.
