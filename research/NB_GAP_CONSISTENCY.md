# Archived Nb gap fails the released scalar consistency check

The legacy backup matches fresh Q=0 geometry in all ordered band/k indices.
That establishes geometry compatibility only. A new scalar check prevents
mistaking that result for a qualified superconducting restart.

Using the native `compute_dabs` convention, select abs(xi)<1e-7 Ry and compute
sum(abs(gap)*weight)/sum(weight) separately on each grid. For the legacy backup,
the two means are 2.20807960 and 2.19869789 meV, with average 2.20338875 meV.
There are 701 and 724 selected states. Conversion used 13605.693122994 meV/Ry;
its precision does not explain this discrepancy.

The released [delta0.dat](https://arim.mdx.jp/nextcloud/public.php/dav/files/zqS4RXS8zaD26p5/nso/Nb1-151406/delta0.dat)
lists temperatures 0.5–7 K with mean gaps from 1.4658 down to 0.867415 meV.
The legacy scalar does not match any listed row. Source URL, downloaded content
hash, summary values and calculated means are in nb_gap_scalar_consistency.json.

This does not identify the backup's temperature, kernel or convergence state,
and does not prove the backup itself is incorrect. It does reject assigning it
to the released temperature series merely from geometry matching or its filename.
Possible differences in physical/numerical setup require provenance, not a
rescaling chosen to make the means agree. No physical gap transfer is accepted.

The moment experiment deliberately uses an imposed constant gap and remains a
matched-quadrature diagnostic. A qualified anisotropic response demonstration
still needs compatible, converged gap data with sufficient metadata.
