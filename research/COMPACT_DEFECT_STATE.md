# Compact state for the streamed defect calculation

The native source pads both bands to the larger band count. Directly consuming
that layout in the active-state core would shift right-band indices and include
inactive entries. The adapter removes only inactive padding, requiring zero
padding in Q, U, gap and D. Finite inactive xi/dk/Z values are ignored. The actual
geometry has66867left+67940right=134807active states, versus135880padded.
This is an index correction and modest payload reduction, not a measured host
memory improvement. Q and U are written one column at a time; no second complete
basis is resident in the Python preparation.

The fixed binary64 W is constructed by solving each column of the saved small
nonsymmetric M against a unit vector. Both MW-I and WM-I must pass a1e-10
arithmetic diagnostic. The streamed identity accepts this stored W directly;
it does not assume an exact inverse. Preparation then calibrates B=I+UWQ^TD
against all three accepted saved native actions, without another kernel sweep.
The original base state is retained; the rejected secant update is not used.

Five files define the native state: six-line versioned metadata; column-major
Q and U; five columns gap/xi/dk/Z/D; and column-major W. Metadata binds dimensions,
rank, temperature, operator hash, padded gap hash and parent manifest hash.
The reader checks context and exact byte counts before allocation, bounds metadata
at4096bytes to prevent silently truncated identity lines, rejects trailing records,
and rejects nonfinite data or1+Z<=0. Little-endian binary64 is explicit.

Synthetic regression tests compile the actual native reader and echo every bit;
an independent Fraction dense B action checks the stored inverse convention.
Unequal band sizes, distinct columns, nonzero harmless inactive fields, stale
schemas, shifted dimensions, extra fields, long context lines, truncated binaries,
nonfinite values and invalid normalization are covered. Source receipt and closure
mutations must fail before expensive context validation. This is the smallest
bridge between existing padded artifacts and the new compact core; changing frozen
producers or retaining padded indices would add avoidable compatibility work.

Required final checks: full unittest discovery, Python compilation, native reader
syntax/fixture compilation, moment_refinement.py and git diff --check. Native tests
provide the required build check; no separate typecheck is configured. The material
preparation is a separate90s admission under the existing120s normal-pressure
launch window and3GiB guard. This document alone admits no new kernel pass.

No full-space norm, outward enclosure, conditioned gap-error bound or physical
response is established by state preparation. Native producer integration and
selected material tiles are the next gates; the full campaign remains open.
