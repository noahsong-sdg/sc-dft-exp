# Saved-state replay feasibility

Inspected 27 November 2026 UTC. Public V3Si directory lists one pwscf.scgap.
WebDAV metadata reports 48,591,571 bytes, modified 3 February 2026. A bounded
range read of the header and first records shows counts 171578 and 170616,
then five floating values and two integer indices per state. Example:

    -4.68774234432135 -2.64197278292306e-5 .036517307749784 .008 0 1 1

Historical source 47c06501da8ffd574c87469ddd6d5a2814171796 writes xi, delta,
Z, dk, dxq, kindx, bindx in exactly this five-float format. It omits d2xq,
although the same revision's supercurrent routine uses that array. Current
4bc883e5 writes six floats, adding d2xq. These are incompatible record schemas;
do not read legacy indices as curvature or supply zero curvature.

Consequently the archived scgap alone cannot replay the complete current.
It also lacks an intrinsic temperature/momentum provenance header. The first
sample's dxq is zero, but this alone does not identify the complete state's Q.
No full 49 MB download was needed to establish the format limitation.

Potential routes remain: reconstruct curvature from matching microscopic files
and the historical preparation path, or create a new fixed-state dump from a
qualified native run. Both need compatibility validation. This is a data
limitation, not a reason to declare the entire project blocked.

Current machine inspection found an unrelated virtual-machine process using
over 600% CPU. Do not interfere with it. Avoid launching a heavy native pilot
until resource availability is rechecked. Lightweight analytic and compiled
fixture work can continue.

The parser in state_format.py explicitly rejects the demonstrated legacy schema
and has a stale-format regression test. It validates individual records only;
it is not a certified full-file reader or replay implementation.
