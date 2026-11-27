"""Plot fixed-cache candidate response and averaging bounds, not predictions."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def main():
    source = ROOT/'anisotropic_candidate_response_series.json'
    candidates = json.loads(source.read_text())['candidates']
    ranks = sorted(map(int, candidates))
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), constrained_layout=True)
    for side in (0, 1):
        rows = [candidates[str(rank)]['grids'][side] for rank in ranks]
        axes[0].plot(ranks, [r['combined_raw_second']*1e4 for r in rows], 'o-', label=f'Grid {side+1}')
        axes[1].semilogy(ranks, [r['averaging_bound_over_combined_response']*1e6 for r in rows],
                         'o-', label=f'Grid {side+1}')
    axes[0].set(ylabel='Candidate response (10⁻⁴ code units)', title='Basis sensitivity at fixed inputs')
    axes[1].set(ylabel='Averaging bound / response (ppm)', title='Symmetry averaging error assessment')
    for ax in axes:
        ax.set(xlabel='Basis rank', xticks=ranks)
        ax.grid(alpha=.2)
        ax.legend(fontsize=8)
    fig.suptitle('Nb: one moment cache, five unaccepted gap candidates', fontsize=11)
    out = ROOT/'figures'
    for suffix in ('png', 'pdf'):
        fig.savefig(out/f'anisotropic_response.{suffix}', dpi=180)
    plt.close(fig)
    (out/'anisotropic_response_sources.json').write_text(json.dumps(
        {source.name: hashlib.sha256(source.read_bytes()).hexdigest()}, indent=2)+'\n')


if __name__ == '__main__':
    main()
