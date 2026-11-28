# A bounded-memory route to the missing full-space defect

This is an algebra/cost proposal, not a material bound or a run admission. The
current full residual and finite Jacobian probes cannot bound the unmeasured
complement. The fixed-operator contraction protocol requires a full induced
norm, including evaluation and rounding error. Its computational feasibility
should be tested before assuming that a dense matrix must fit in RAM.

## Exact finite-dimensional identity

Freeze D0 at the accepted candidate and define a particular inverse candidate
B=I+U W Q^T D0. W is a chosen fixed small matrix, e.g. a recorded approximation
to (I-Q^T D0 U)^-1. The following identity holds for any fixed U,Q,W; it does not
assume exact U=A0 Q or an exactly computed inverse. Let

    P = Q^T D0 A0,
    C = W(P-Q^T).

Then at the base point,

    E0 = I-B(I-A0 D0) = (A0+U C)D0.

A first complete kernel pass can accumulate P, a rank-by-active-state matrix.
A second pass combines streamed A0 tiles with U C tiles and sums absolute row
entries. Every active row/column must be covered. The infinity induced norm is
max_i sum_j |E0_ij|, not the maximum entry or a set of directional actions.

The native block_linear_operator path applies
A01(i,j)=-K1(j,i)*w2(j)/(1+Z1(i)) and
A10(j,i)=-K2(j,i)*w1(i)/(1+Z2(j)), with finite-T linear_weights w and zero
same-side A0 blocks. Keep both orientations; no symmetry/positive metric is
assumed. **U C generally has nonzero same-side blocks.** Those blocks cannot be
omitted merely because the original native operator is off-diagonal.

A radius-ball estimate also needs D(d) variation. Since
B A0=A0+U W P, an independently justified componentwise enclosure
|D_j(d)-D0_j|<=theta_j on the entire ball gives the sufficient row bound

    ||I-B J(d)||_infinity
      <= max_i sum_j (|E0_ij|+|(B A0)_ij|*theta_j).

Bounds for theta and both matrix expressions, finite-precision matrix products,
row sums and kernel evaluation still have to be supplied. An ordinary
floating-point row sum is not an outward certificate. A conservative factored
bound for the variation term could avoid a second dense low-rank contraction,
but may be too loose; no such material bound is accepted.

If a valid q<1 is established at d0, B J(d0) is invertible by the Neumann
argument, hence square finite-dimensional B is invertible as well. This supplies
the nonsingularity needed to turn a fixed point of d-BH(d) into a zero of H.
The ball-mapping eta+q*r<=r and all rounding/branch conditions remain required.

## Exact small nonsymmetric control

An independent Fraction calculation used D=diag(4/5,7/10,3/5,1/2), Q=[e1,e3],
U=A Q, exact W=(I-Q^T D U)^-1, and

    A = [[0,0,1/5,-1/10], [0,0,1/7,1/6],
         [1/4,1/8,0,0], [-1/9,1/10,0,0]].

All16 entries of I-B(I-A D) equal (A+U C)D exactly as rational numbers.
The row norm is195/1952; four same-side entries are nonzero. This validates the
algebra and the same-side warning, not a property of the niobium operator.

## Storage and work, not an unmeasured runtime claim

For134807active states, a dense defect matrix would require145383417992bytes
in binary64, far beyond the3GiB workspace cap. Streaming avoids retaining it.
One rank51-by-active-state coefficient matrix is55001256bytes; extra matrices,
Q/U, native Coulomb storage and work tiles still need simultaneous accounting.
No verified replacement peak-memory result exists yet.

There are9085887960 native off-diagonal entries. Straightforward leading
contraction work for first-pass P and second-pass U C over all active blocks is
2*51*(9085887960+134807^2)=2780399151318 floating operations, plus two kernel
passes, solves, absolute sums and error accounting. This count is dimensional
arithmetic, not measured calls or laptop wall time. The radius-variation route
can add further work. A bounded source-built tile benchmark and independent
small dense nonsymmetric/roundoff controls are necessary before any full pass.

No budget expansion or native run is authorized by this note. First finish and
interpret the already admitted correction sweep. Then assess information gain,
reference-library contraction throughput, memory, kernel/error-bound validity,
stop conditions and pilot budget before choosing whether this route is worth
pursuing. A failed sufficient norm test would be inconclusive about existence
of the physical solution. Functional/current normalization, response grids,
other temperatures and the scientific decision remain separate gates.
