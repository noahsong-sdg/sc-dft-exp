"""Plot the committed fixed-gap grid/stencil comparison with explicit scope."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent


def main():
    source=ROOT/'grid_stencil_comparison.json';data=json.loads(source.read_text())
    for name,expected in data['sha256'].items():
        path=ROOT/name.removeprefix('research/')
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('Comparison source changed: '+str(path))
    row=data['cases'][0]
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    for order,color in [('second','#32679c'),('fourth','#bb5b23')]:
        axes[0].plot([32,48],[row[f'{order}32']/row['fourth48'],
            row[f'{order}48']/row['fourth48']],'o-',color=color,label=f'{order.title()} order')
    axes[0].set(xlabel='Electronic grid points per axis',xticks=[32,48],
        ylabel='Diagnostic / fourth-order 48³ value',title='2 K fixed-gap diagnostic')
    axes[0].legend()
    for order,color in [('second','#32679c'),('fourth','#bb5b23')]:
        axes[1].plot([r['temperature_kelvin'] for r in data['cases']],
            [100*abs(r[f'{order}_order_grid_fraction']) for r in data['cases']],
            'o-',color=color,label=f'{order.title()} order')
    axes[1].set(xlabel='Temperature (K)',xticks=[2,4,8],
        ylabel='Observed 32³ → 48³ change (%)',title='Two-grid sensitivity')
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle('Fourth-order velocity reduces observed grid spread',fontsize=13)
    fig.text(.5,.02,'Nb imposed 1.5 meV gap; same density and 512 response cells.\n'
        'Two grids do not establish continuum accuracy or physical penetration depth.',
        ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.12,1,.93])
    out=ROOT/'figures'
    for suffix in ('png','pdf'):
        fig.savefig(out/f'grid_stencil.{suffix}',dpi=180)
    plt.close(fig)
    paths=[source,Path(__file__).resolve()]+[ROOT/path.removeprefix('research/') for path in data['sha256']]
    identities={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (out/'grid_stencil_sources.json').write_text(json.dumps(identities,indent=2)+'\n')


if __name__=='__main__':
    main()
