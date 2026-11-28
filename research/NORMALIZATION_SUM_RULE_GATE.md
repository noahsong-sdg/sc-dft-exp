# Fresh-state normalization diagnostic

`fresh_normalization_sum_rule001_result.json` records measurements, not a
physical-response acceptance or a normalization correction. It binds the fresh
Q0 state, source-built response cache, normal-state XML and owning source hashes.
No native source, input, threshold or weight was changed.

For a complete single-spin band the normalized Brillouin-zone integral is one
state per cell. The XML reports26 bands and13 normal electrons per cell. The
fresh assigned state sums are:

| Quantity | Side1 | Side2 |
|---|---:|---:|
| All-band weight |25.9859800987|25.9859603675|
| Band6 weight |0.9843046085|0.9842732637|
| Band7 weight |1.0016754902|1.0016871039|
| Zero-T normal electrons, with spin2 and half occupation at xi=0 |12.9698753809|12.9698305222|

Every other band has exactly unit weight. The maximum band6 deficit is about
1.573%; the total electron-count deficit is about0.232%. These are different
controls, not interchangeable uncertainty estimates.

## Traced decomposition

The source path is `energy_grid -> calc_dosk -> interpolated cell DOS ->
symm_dosk -> store_d3k`. Before assignment, raw and averaged signed DOS
integrals both equal0.9841920571 for band6 and1.0015601157 for band7 on both
sides. Thus the principal band6 normalization deficit precedes state assignment;
symmetry averaging preserves the signed integral. This localizes the discrepancy
but does not isolate finite energy range from quadrature resolution or the
underlying DOS approximation.

`store_d3k` retains DOS nodes above1e-12 when at least two nodes qualify. For the
tested band6/7 groups, assigned total weights match the averaged positive-DOS
integrals to1e-14. The discarded negative integrals explain their difference
from the signed cache. This is the observed native support rule, not permission
to alter it without a new scientific convergence study.

## Reproduce the two independent sums

From the repository root, the existing strict readers suffice:

```python
import math, sys
sys.path.insert(0, 'research')
from compare_legacy_gap import native_arrays
from cell_moment_cache import read_pair
counts, state = native_arrays('research/raw/fresh-gap-init-001')
for side, count in enumerate(counts[:2]):
    indices = range(side*counts[2], side*counts[2]+count)
    print('assigned', side+1, math.fsum(state['dk'][i] for i in indices))
    print('electrons', 2*math.fsum(state['dk'][i]*(
        1 if state['xi'][i]<0 else .5 if state['xi'][i]==0 else 0)
        for i in indices))
dims, physical, raw, averaged = read_pair('research/raw/public-response-run-001')
nx, first, last, cells, sides = dims
bands = last-first+1
for phase, data in [('raw', raw), ('averaged', averaged)]:
    for side in range(sides):
        for band in range(bands):
            terms = [data['dx0'][ix]*data['dos'][ix+nx*(
                band+bands*(cell+cells*side))]
                for cell in range(cells) for ix in range(nx)]
            print(phase, side+1, first+band, math.fsum(terms),
                  math.fsum(t for t in terms if t<0),
                  math.fsum(t for t in terms if t>0))
```

## Consequence for the response campaign

Do not renormalize by the observed deficit. A scalar state-count error is not
a bound on a gap kernel or response-weighted integral: the latter emphasize
different energy/band support and include signed curvature/velocity terms.
The existing small residuals and grid controls cannot close the registered1%
uncertainty budget by themselves. A relevant energy-grid/range control must
measure the actual observable or bound its weighted missing contributions.
This finding neither proves a1.573% stiffness error nor invalidates the current
fixed-grid convergence experiment. It adds a specific discretization check to
the scientific acceptance path.
