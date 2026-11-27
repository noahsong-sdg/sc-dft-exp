"""Plot the registered third-grid comparison without implying physical accuracy."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent


def main():
    source=ROOT/'third_grid_comparison_result.json';data=json.loads(source.read_text())
    paths=[source,Path(__file__).resolve()]
    for name,expected in data['sha256'].items():
        path=Path(name)
        if not path.is_absolute():
            path=ROOT.parent/path
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError('Third-grid comparison source changed: '+str(path))
        paths.append(path)
    row=data['cases'][0]
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    axes[0].plot([32,48,64],[row[f'fourth{n}']/row['fourth48'] for n in (32,48,64)],
                 'o-',color='#32679c',label='Fourth-order velocity')
    axes[0].set(xlabel='Electronic grid points per axis',xticks=[32,48,64],
        ylabel='Diagnostic / 48³ value',title='2 K fixed-gap diagnostic')
    axes[0].legend()
    for key,label,color in [('previous_grid_fraction','32³ → 48³','#32679c'),
                            ('held_out_grid_fraction','48³ → 64³','#bb5b23')]:
        axes[1].plot([r['temperature_kelvin'] for r in data['cases']],
            [100*abs(r[key]) for r in data['cases']],'o-',color=color,label=label)
    axes[1].set(xlabel='Temperature (K)',xticks=[2,4,8],
        ylabel='Absolute step / preceding-grid value (%)',title='Observed grid sensitivity')
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle('Nb fixed-gap diagnostic: held-out 64³ electronic-grid control',fontsize=12)
    fig.text(.5,.02,'Imposed 1.5 meV gap; same density and 512 response cells.\n'
        'Grid sensitivity is not a continuum-error bound or physical penetration depth.',
        ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.12,1,.93])
    out=ROOT/'figures'
    for suffix in ('png','pdf'):
        fig.savefig(out/f'third_grid.{suffix}',dpi=180)
    plt.close(fig)
    (out/'third_grid_sources.json').write_text(json.dumps(
        {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')


if __name__=='__main__':
    main()
