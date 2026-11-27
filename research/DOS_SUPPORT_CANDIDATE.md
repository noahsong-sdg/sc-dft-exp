# Deferred DOS-support arithmetic candidate

This is a candidate, not a qualified optimization or the next launch. The active
scientific priority is the32/48 derivative-stencil comparison. Future agents must
read the current ledger before using any staged build manifest.

The owning path is velocity_moment_probe -> calc_dosk in the pinned SCTK module.
It constructs a4x4 ratio array for every energy node before checking its three
nonzero tetrahedron-support cases. Nodes outside all three cases get zero
weights. Moving only the ratio computation into those existing branches avoids
unused divisions while preserving every branch condition and weight expression.
In plain terms, it avoids computing quantities that the zero-weight branch never
uses. No support cutoff, quadrature approximation or new fallback is introduced.

`dos_support_optimization.py` checks the exact owning routine boundaries, one
ratio loop and all three support branches before generating the candidate.
`build_dos_support_response.py` compiles the generated full module separately and
relinks against unchanged source-built libraries. It preserves the parent tree
and original second-order geometry. Generated GPL source stays under ignored raw
build storage. Parent executable identity, source, libraries, modules and make
inputs are recorded and rechecked. The build is not a fresh cold start.

Compiled synthetic ratio/branch fixtures match bit for bit at endpoints, near
repeated energies and repeated-energy cases. They do not exercise the complete
SCTK weight routine. The source transformation rejects stale or already modified
boundaries. No native candidate build or material run has occurred.

Why deferred: a one-second sample near the first response deadline found
calc_dosk; a similar late sample during the retry found opt_tetra_init instead.
Neither interval measures total phase times. The ratio relocation may leave the
dominant startup cost untouched. Obtain actual phase timings before spending a
native baseline here. This is preferable to claiming a speedup from source
inspection or a single short profile.

If subsequently justified, link under the180s/3GiB guard with120normal-pressure
seconds, no concurrent heavy owner. Require the original32cubed eight exports
bitwise before a distinct48candidate. Compare complete accepted-result time,
setup and memory. Preserve baseline failures and unchanged scientific gates.
IEEE exception flags outside support may differ because unused divisions are
removed; no claim about preserving those flags is made. Interior degeneracy
formulas and their behavior are unchanged. No speedup or physical-accuracy claim
is established by this candidate.
