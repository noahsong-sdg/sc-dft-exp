# Finite-temperature RHS product boundary

The complete pinned gapeq_rhs routine first computes an occupation factor
F(E,s)=[tanh(beta(E+s)/2)+tanh(beta(E-s)/2)]/2, then forms
chi=(dk/2) delta F(E,s)/E, with E=sqrt(xi²+delta²).

At any fixed finite temperature and shift, F is smooth and odd in E, so
F(E,s)=O(E). Thus delta F/E tends to zero as xi and delta tend to zero.
The literal implementation instead evaluates 0/0 at the exact origin. In
plain terms, a zero normal-state contribution becomes NaN before matrix
multiplication, which then contaminates other residuals.

The candidate checks exactly xi=delta=0 at finite temperature and sets the
product to zero before division. Other states use the original arithmetic.
The loop is outside the completed thermal OpenMP region; its existing igap
index is valid there. No shared parallel scratch is introduced. The exact
domain check avoids an arbitrary small-energy threshold and leaves near-zero
states unchanged. Zero-temperature behavior is explicitly preserved because
its joint limits need separate treatment; this is not a universal zero-T fix.

`rhs_zero_energy_probe.py` compiles the complete owning routine with real
retained BLAS, synthetic nontrivial interactions, unequal grid sizes, and serial
MPI stubs. Nine normal-state cases combine xi=-1e-12/0/+1e-12 with shifts
0/0.2/0.4, beta=2 and zero gap. Each produces five active residuals.

The thermal-only candidate gives 15 nonfinite residuals at xi=0. The product
candidate gives all 45 residuals exactly zero in both O0 serial and O3 OpenMP
with four threads. The five earlier nonzero-gap controls retain zero error
against their independent assembled residual reference. This verifies the
finite-T boundary and those adjacent controls, not an entire gap solve.

Command (passed):

```sh
python3 research/rhs_zero_energy_probe.py --blas /Users/noahs/Developer/flux-pinning/native-macos-v1/lapack-build-v2/lib/libblas.a
```

Source and BLAS hashes, counts and results are in rhs_zero_energy_results.json.
The updated review patch includes this correction; isolated dry-run, actual
application, and both resulting full-file hashes pass. The high-energy xic>0
branch, kernel accuracy, zero-T limits and material predictions remain outside
these tests. The fixture uses xic=-1. All 38 existing offline tests also pass;
this complete-routine regression additionally requires the pinned network
source and a compatible BLAS library.
