# Zero-energy current product: root cause and narrow candidate

## Problem and evidence

The prepared Nb geometry contains 651 and 688 states exactly at xi=0 on the
two integration grids. Imposing a zero gap makes E=sqrt(xi²+delta²)=0 there.
The complete released current routine, and the earlier thermal-only candidate,
produce nonfinite currents. This prevents a basic normal-state cancellation
check on actual material-derived quadrature.

The current path computes `xi/E*e_d` unconditionally. At finite beta,

```
e_d(E) = [tanh(beta*(E+abs(dxq))/2)
          + tanh(beta*(E-abs(dxq))/2)]/2
```

is odd and differentiable in E, with e_d(0)=0 and e_d(E)=O(E).
Consequently `(xi/E)*e_d(E)=O(xi)` tends to zero as (xi,delta) tends to (0,0).
The source nevertheless evaluates 0/0 before multiplying by the vanishing
factor. In simple terms, the physical limiting product is well defined, but
its arithmetic is performed in an order that creates an undefined intermediate.

## Fix and why this boundary

`zero_energy_correction` transforms only this product: at exactly E=0 set the
product to zero; otherwise evaluate the original product. It stores that
product back into the routine's already-private e_d variable just before
accumulation, after all other uses. No additional shared state, interface,
cutoff, energy threshold, discarded integration states or temperature-dependent
fallback is introduced. Existing OpenMP ownership is preserved.

An exact equality guard enforces the demonstrated domain boundary. An arbitrary
small-energy cutoff would modify finite-energy states; dropping these states
would also discard their other current terms. Neither is necessary. This
argument is for finite beta, not a proof about noncommuting zero-temperature
and zero-energy limits. Q=0 normalization remains outside this finite-Q routine.

`robust_correction` composes this narrow correction with the earlier thermal
candidate. Those changes remain separable so their individual effects can be
investigated. These are research transformations against hash-checked source;
no upstream patch has been sent and no production solver has been changed.

## Verification

`python3 research/zero_energy_probe.py` compiles the complete pinned current:
nine controls at xi=0 and xi=±1e-12, three shifts, and zero gap. Earlier thermal
candidate fails all three exact-zero cases. The combined candidate returns
exactly zero normal current in all nine, both serial O0 and O3/OpenMP four-thread
builds. Results: zero_energy_results.json.

The complete 81-case nonzero-energy boundary grid was rerun with the combined
candidate in serial and O3/OpenMP two/four-thread builds: zero failures at the
existing 1e-7 absolute fixture tolerance, max error 2.1711e-8. This confirms that
the product rewrite preserves the previously tested nonzero-energy path.
Results: zero_energy_nonzero_regression.json. The source transformation also
has changed-source/rewrite regression coverage in test_zero_energy.py.

The complete Nb material diagnostic was rerun. All six normal controls (three
temperatures, two grids) now return zero. All nonzero-gap currents are unchanged
from the thermal-only candidate and retain their agreement with direct
occupations. Released routine nonfinite values remain recorded as null, not
silently accepted. See updated nb_material_current_results.json.

Offline suite: 35 tests pass. This repairs a demonstrated numerical boundary;
it does not establish self-consistent gaps, material convergence, physical unit
normalization, or experimental accuracy.
