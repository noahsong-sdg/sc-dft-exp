"""Plot committed candidate diagnostics; no native solver or inferred results."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
REDUCED = ['reduced_nonlinear_result.json', 'enriched_reduced_result.json',
           'critical_reduced_result.json', 'second_occupation_reduced_result.json',
           'third_occupation_reduced_result.json']
FULL = {31: 'verify_reduced_gap_result.json',
        33: 'verify_critical_gap_result.json',
        34: 'verify_second_occupation_gap_result.json',
        35: 'verify_third_occupation_gap_result.json'}


def main():
    sources = REDUCED + list(FULL.values())
    rows = [json.loads((ROOT / name).read_text()) for name in REDUCED]
    ranks = [row['dimensions'][-1] for row in rows]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), constrained_layout=True)
    axes[0].semilogy(ranks, [r['coefficient_residual'] for r in rows], 'o-')
    axes[0].axhline(1e-13, color='gray', linestyle='--', label='Reduced target')
    axes[0].set(ylabel='Coefficient residual (Ry)', title='Reduced convergence')
    axes[0].legend(fontsize=8)
    for side in range(2):
        axes[1].plot(ranks, [r['fermi_averages_mev'][side] for r in rows],
                     'o-', label=f'Grid {side + 1}')
    axes[1].set(ylabel='Candidate mean gap (meV)', title='Basis sensitivity')
    axes[1].legend(fontsize=8)
    full = [(rank, json.loads((ROOT / name).read_text())) for rank, name in FULL.items()]
    for key, label in [('residual_infinity_ry', 'Maximum residual / target'),
                       ('rms_residual_over_gap', 'RMS ratio / target')]:
        axes[2].semilogy([rank for rank, _ in full],
                         [row[key] / row['thresholds'][key] for _, row in full],
                         'o-', label=label)
    axes[2].axhline(1, color='gray', linestyle='--')
    axes[2].set(ylabel='Acceptance ratio (≤1 required)', title='Full native validation')
    axes[2].legend(fontsize=8)
    for ax in axes:
        ax.set(xlabel='Basis rank', xticks=ranks)
        ax.grid(alpha=.2)
    fig.suptitle('Nb fixed-input candidate study: ranks31/33/34/35 full-validated; none accepted', fontsize=11)
    out = ROOT / 'figures'
    for suffix in ['png', 'pdf']:
        fig.savefig(out / f'gap_validation.{suffix}', dpi=180)
    plt.close(fig)
    provenance = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                  for name in sources}
    (out / 'gap_validation_sources.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
