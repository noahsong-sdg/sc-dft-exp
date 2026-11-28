# Source bridge from native kernels to compact partial P

The compact-state artifacts and defect algebra were separately tested. Their
remaining execution boundary is the loaded native material state and the original
32-row kernel producer. Feeding mismatched Z, input weights or derivative into
otherwise correct contractions would change the finite operator. Feeding padded
right-band indices into an active array would silently contract the wrong states.

`compact_native_tile_probe.f90` supplies the existing driver's run_full_map entry
point as a separate source variant. It reads a versioned compact control with
root, rank and operator/candidate/parent hashes, requires the seed operator to
match, and uses the strict compact reader. Every active gap, xi, dk and Z entry
must equal the freshly loaded native entry. A separate native derivative evaluation
must agree with stored D within1e-30+1e-12relative scale. This tolerance is an
arithmetic compatibility diagnostic, not a derivative uncertainty allowance.

Only after these checks does it reset native caches, build rows1:32 and33:64
using the unchanged build_tile and call the actual streamed accumulate_p. Native
blocks retain their nonunit lower bounds. Direct sums control three rank positions,
left endpoints and right endpoints/midpoint, including accumulated right-side
contributions after the second tile. Every raw kernel block, partial P, state check
and separate kernel/contraction CPU interval is written for independent readback.
This probe deliberately leaves P incomplete. It cannot call make_c or report any
full-space norm. U and W are read/context-checked, then released before kernels;
Q is released after constructing DQ. These reduce simultaneous payloads, but actual
material RSS remains unmeasured for this variant.

The new compact_tile_link.mk source variant preserves the original initialized
native driver, caches, slabs and kernel producer. It replaces only the probe and
adds the two compact modules. DEFECT_BLAS precedes CORELIBS so a prospective
explicit SDK library can resolve dgemm before the static reference archive. The
actual material link still needs its own source-bound build and receipt; the
fixture's generic BLAS link is no evidence of an Accelerate material speedup.
Frozen source/build manifests and earlier material outputs are unchanged.

The regression fixture compiles the actual new probe, reader and defect core
against synthetic native modules:65left/67right, rank3, two32-row tiles, unequal
Z and weights, signed asymmetric kernels and nonuniform D. A Fraction oracle uses
the exact represented Q/D/weights/Z/kernel values and checks **every** partial P
entry; the unvisited65thleft column remains zero. Thirty direct controls must have
the expected records. Legacy controls, extra rank fields, long identity lines,
trailing records, changed seed operator/candidate/parent, geometry, loaded gap or
D fail before a kernel file exists. This exercises the real adapter path, while
synthetic native modules do not establish actual material initialization or cost.

This is a source/fixture checkpoint, not a material admission. Next source-build
the new link, bind accepted compact preparation001 and original native initialization,
then run only these selected tiles under a fresh guard. Independently replay saved
kernel products before considering a full P pass. Current guarded material ledger
21376.431543087903s/21600 leaves223.56845691209674s; no budget expansion here.
Full response, conditioning, outward rounding/radius and other-temperature gates
remain open. No changes to Brave or the other study.

Final verification on this source checkpoint:

- `/opt/homebrew/opt/python@3.13/bin/python3.13 -m unittest discover -s research -p 'test_compact_native_tile_probe.py' -v`:1PASS; synthetic native fixture compiles/executes, all396partial P entries and10rejection cases checked.
- `/opt/homebrew/opt/python@3.13/bin/python3.13 -m unittest discover -s research -p 'test_*.py'`:285PASS45.301s, including compiled native fixtures.
- Python `compile` over263maintained research/*.py files:PASS.
- `/opt/homebrew/opt/python@3.13/bin/python3.13 research/moment_refinement.py`:exit0.
- `git diff --check`:PASS. No separate configured typecheck.

The actual probe compiles and links in the fixture; the material make target is
prospective, not claimed built. Two non-test source files total175lines.
