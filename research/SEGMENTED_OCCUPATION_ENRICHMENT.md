# Measured occupation enrichment after segmented full evaluation

The full fresh candidate fails stationarity: maximum residual3.6594363917272926e-8Ry
and RMS residual/gap0.001451511647600654. Its48column reduced equation omits
occupation components outside Q. The complete native image F(d)=d+R is now
available with passing arithmetic, state, source and ordered checkpoint controls.
It can supply one new direction and action without a second kernel evaluation:

    h = f(d)-Q Q^T f(d)
    A0 h = F(d)-U Q^T f(d),  U=A0 Q.

The existing occupation_enrichment.enrich applies identical orthogonalization
subtractions to h and its image, then normalizes both by the same norm. This
identity does not turn uncertain inherited actions into exact ones; full native
candidate validation and conditioning remain required. A measured failure of
stationarity is valid enrichment evidence; failed execution, arithmetic or input
provenance is not.

The frozen prepare_occupation_enrichment path calls the old globally unique
executable-basename verifier and accepts no segmented provenance. New version
prepare_segmented_occupation preserves all occupation/enrichment/padding math,
but first requires full_map_segments.certify complete coverage, exact owning root,
the published predecessor/output record and identical full-candidate readback.
Basis, geometry and reduced control/gap/summary must be hash-pinned in the same
certified full input inventory. The separate stage_segmented_occupation recipe
pins every input plus complete outputs, accepted result, interpreter and Python
source closure before creating a fresh execution directory. No output basis is
created by staging; preparation creates it only after source and numerical gates.

This versioned boundary is chosen to preserve frozen manifests and avoid changing
historical acceptance, deleting ancestor pins or patching shared module globals.
The new tests control the boundary with explicit certificates; existing native
segment tests independently execute the complete chain reader. Exact2I fixture
images check the owning enrichment arithmetic, including accepting a failed
stationarity candidate. Partial/failed chains, stale public candidate, wrong root,
unpinned control and changed persisted basis are rejected before output.

Final checks:218tests PASS31.130s including native fixture builds;216maintained
Python sources compile PASS; moment_refinement exit0; git diff --check PASS.
No separate configured typecheck. No native kernel/reduced solver changes.

Prospective admission: only portable-occupation-prepare-001,180s/3GiB after120
continuous normal-pressure seconds, one heavy owner.1144inputs pinned. Terminal
native ledger18182.12777283633s under21600; worst next180 leaves3237.872227163669s.
The previous full residual now makes targeted preparation scientifically useful;
expected tens of seconds to roughly two minutes for hashing and orthogonalization
is a forecast, not a bound. No automatic retry, reduced solve or full evaluation
is admitted by this preparation. Brave and the other study remain untouched.

## Actual preparation and independent readback

Preparation001 terminalPASS34.4096539998427s, peak233996288B. All1144input
pins/public-consumed manifest/receipt/source/deadline checks pass. Added direction
norm0.9999999999999999, old overlap4.754812029020309e-19; every inherited Q/U
column is byte-identical. Streaming independent expm1 occupation reconstruction
agrees with the complete measured image to4.2012834183813297e-19Ry, below
4.539416123276439e-17 algebraic-control bound. This is neither a full operator
error bound nor a new candidate residual. See occupation_prepare_readback001.py
and portable_occupation_prepare001_result.json. Relative occupation defect
0.0013436350567505534 supports the omitted-direction hypothesis but does not
prove that one direction is enough. Source/report/basis hashes are recorded.

Final gate218tests PASS25.993s incl native builds;217maintained Python sources
compile PASS; moment_refinement exit0; diffcheckPASS. PublicCI46115314125 on
7d94584 PASS. No separate configured typecheck.

Admit exactly portable-reduced-gap-002, unchanged source-built solver and fresh
49column basis; same fresh geometry/Z/operator,64column accepted linear mode,
0.15meV starting amplitude,60s/quiet120/3GiB.1155prospective pins. Actual guarded
ledger18216.537426836174s leaves3383.462573163826s under21600; worst next60 leaves
3323.462573163826s. No automatic retry/newfull evaluation admitted.

## Explicit-manifest reader and second actual preparation

The first independent reader intentionally names dataset001 and is now frozen
in descendant input inventories. Dataset002 demonstrates the need for another
input manifest. New occupation_prepare_readback.py takes that path explicitly,
retaining the streaming inherited-column comparison, exponential occupation,
normalization/orthogonality, source/receipt and complete-chain checks. It also
checks finite nonnegative bounded RSS and report rank/beta/context against the
full evaluation. Numerical thresholds and original001 reader remain unchanged.
This small versioned change avoids per-dataset numerical copies and mutable
shared globals; it adds no native solver abstraction or fallback.

Two tests cover distinct declared datasets and reject adopted output hashes for
changed inherited columns, nonunit direction, incorrect action and stale context,
as well as incomplete certificates, nonfinite RSS and a changed acceptance flag.
Full suite220tests PASS22.258s including native builds;219maintained Python sources
compile PASS; moment_refinement exit0; diffcheckPASS; no separate typecheck.
Replay on the actual001 manifest matches all prior scientific/receipt/hash fields
exactly (scope text and separate ledger accounting excluded).

Actual preparation002 terminalPASS25.520065541379154s, peak228605952B. All1249pins
and original state/source/result binding pass. Every inherited Q/U byte is
preserved; new direction norm1, old overlap8.300874945971308e-19. Independent
exponential image reconstruction error4.573977915173222e-19Ry is below the
4.956606846793945e-17 algebraic-control bound. Rank49->50 basisSHA
8ef54048eccd584bf5eec919224e47c8fe83fb959d88b725ae40429c26bdd1a7.
This does not accept another gap, inverse bound or physical response.

Admit only reduced-gap003 with unchanged solver/mode/geometry/operator and
0.15meV initial amplitude,50columns,60s/quiet120/3GiB;1260prospective pins.
Guarded ledger19060.74679766953s leaves2539.2532023304702s under21600; worst
next60 leaves2479.2532023304702s. No automatic retry or full-pass admission.
