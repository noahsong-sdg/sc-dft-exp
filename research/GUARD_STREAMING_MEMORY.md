# Bounded-memory input verification

The original guard verifies each declared input using `Path.read_bytes()` before
hashing. This allocates a buffer the size of the entire file; allocator residency
can outlive that individual hash. In simple terms, checking a large input first
loads the whole file into RAM even though SHA256 can read it in small pieces.

A fresh-process comparison over the same complete 1,031-file, 3,958,035,445-byte
manifest found whole-file verification peaked at378,241,024 bytes (360.72MiB),
while streaming peaked at20,889,600 bytes (19.92MiB). Every size and digest matched.
The actual versioned guard's verifier peaked at22,609,920 bytes (21.56MiB), a
339.16MiB lower peak than the whole-file comparison. These measurements cover
verification, not whole-host memory pressure or total native-run memory. Timing
is cache/order dependent and is not a speedup claim.

`macos_native_guard_v2.py` uses `hashlib.file_digest` on a binary stream after the
same size check. This standard-library operation bounds the hashing buffer and
preserves the exact SHA256 check. It is chosen over reducing verification,
changing limits, adding a dependency, or manually maintaining another digest
implementation. It does not change the native process, physics, pressure gate,
3GiB limits, deadlines, process observation timeout, or fail-closed behavior.

The original guard remains byte-identical at SHA256
`2740874650a93797646622838dc00ccb1226538a45feb32dc5c301c2d9f0127b`.
A separately versioned file is necessary because existing prospective scientific
manifests pin the original source path and hash. Editing it in place would
invalidate those retained provenance chains. New admissions must explicitly pin
and select v2; existing staged commands are not silently changed.

The preceding full-gap check failed because a process-memory `ps` query exceeded
3seconds. This optimization does **not** establish why that happened or guarantee
it cannot recur. The query timeout and termination policy remain unchanged. No
retry is implied by the memory improvement.

## Reproduction and checks

With the locally acquired pinned input tree, run separate fresh processes:

```sh
python3.13 research/guard_hash_memory001_method.py whole research/portable_full_gap001_manifest.json
python3.13 research/guard_hash_memory001_method.py stream research/portable_full_gap001_manifest.json
```

The method records macOS `ru_maxrss` in bytes and checks every digest. The result
JSON also records a fresh actual-v2 verifier invocation and source identities.
The large underlying input tree remains subject to the project's acquisition
and redistribution limitations; these measurements do not close public setup.

Regression coverage rejects same-size changed bytes, truncated and missing
inputs, and forbids whole-input `read_bytes` allocation. Existing guard tests
exercise launch ownership, stale command/input rejection, normal-pressure reset,
real child success/failure and deadline termination against v2. An AST comparison
requires every other runtime definition to match the frozen original.

Final checks: `python3.13 -m unittest discover -s research -p 'test_*.py' -v`
passed190tests in42.742s;197maintained Python files compiled using `compile`;
`python3.13 research/moment_refinement.py` exited0. Native fixture compilation is
included in the tests. There is no separately configured typecheck.
