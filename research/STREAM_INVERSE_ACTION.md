# Stream the next frozen-inverse diagnostic

The accepted inverse preparation checks every small matrix entry, retaining all
Q/U columns for that exhaustive replay. The two rank51 bases have a combined
payload16*135880*51=110878080bytes
(105.7415771484375MiB). That exhaustive replay is already accepted and remains
immutable. A later action of the same frozen inverse does not need another
resident copy of those columns.

`stream_inverse_action.py` applies B=I+U M^-1 Q^T D to explicitly supplied
right-hand sides. It streams each Q column for the contractions, solves the
small nonsymmetric system with partial pivoting, and streams U to accumulate
the answers. A second pair of passes independently checks
(I-U Q^T D)answer=rhs using the original diagonal/basis, with the established
1e-30+1e-10*scale algebraic tolerance. It rejects changed small matrices when
they fail that control, singular systems, invalid/nonfinite shapes and arithmetic.
It does not silently change precision or substitute another inverse.

In plain terms, the calculation needs column sums and a short solve, rather
than every basis column in RAM simultaneously. The tradeoff is rereading the
basis. This is a small separate action helper; changing the frozen exhaustive
analyzer would invalidate accepted provenance and is unnecessary. No native
Coulomb allocation or unrelated process is changed.

Tests compare against an independent exact-Fraction full nonsymmetric solve
with multiple right-hand sides, exercise pivoting and stale/singular/nonfinite
inputs, and measure traced Python allocations on a1024state/rank32 fixture.
That fixture's peak allocation is required to stay below three quarters of its
524288byte basis payload, rejecting a full additional basis-payload allocation.
This fixture test is not a measured material RSS improvement.

After complete native correction coverage, prospective right-hand sides are
-Jnative*v and the actual plus-point residual. The outputs would diagnose
B*J*v-v and the action of the base-point frozen inverse on the plus residual.
They would not constitute a new inverse at the perturbed point or bound the
unmeasured complement. Owning full-source/preparation/receipt and input closure
must be bound before any material use. No material action or new native budget
is admitted here; no conditioned-gap or physical-response acceptance follows.

Final gate:258offline tests PASS38.008s, including native fixture builds and
execution;247maintained Python sources compilePASS; moment_refinement exit0;
diffcheckPASS. No separate configured typecheck. No material invocation of this
helper yet. First correction-step production half separately certified; complete
coverage remains necessary before using its saved Jacobian as an input.
