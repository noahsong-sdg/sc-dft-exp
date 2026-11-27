"""Summarize fixed-band, fixed-energy response-cell refinement."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FILES=('nb_velocity_moment_results.json','nb_velocity_moment_grid16_results.json',
       'nb_velocity_moment_grid32_results.json')


def summary():
    datasets=[json.loads((ROOT/name).read_text()) for name in FILES]
    base=datasets[0];rows=[]
    for name,data,n in zip(FILES,datasets,(8,16,32)):
        if (data['dimensions'][:4]!=base['dimensions'][:4] or
            data['dimensions'][4]!=n**3 or data['qnorm']!=base['qnorm'] or
            data['volume']!=base['volume']):
            raise ValueError('Refinement changes more than the response-cell grid')
        for case in data['cases']:
            reference=case['fine_grid_reference']
            if reference<=0:raise ValueError('Expected positive diagnostic reference')
            rows.append(dict(grid=n,temperature_kelvin=case['temperature_kelvin'],
                             mean_squared_ratios=[x/reference for x in case['mean_squared_active']],
                             second_active_ratios=[x/reference for x in case['second_moment_active']],
                             second_all_ratios=[x/reference for x in case['second_moment_all']],
                             source=name,raw_diagnostic_sha256=data['sha256']))
    return dict(conditions=dict(fine_k_grid=[32,32,32],energy_bins=base['dimensions'][0],
                               imposed_gap_mev=1.5,qnorm=base['qnorm']),cases=rows,
                scope='Response-cell refinement only; same band/energy approximation and imposed gap')


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=[r for r in result['cases'] if r['temperature_kelvin']==2]
    fig,ax=plt.subplots(figsize=(7.5,4.8),layout='constrained')
    for grid,marker in ((0,'o'),(1,'s')):
        label='unshifted' if grid==0 else 'half-shifted'
        ax.plot([r['grid'] for r in rows],[r['mean_squared_ratios'][grid] for r in rows],
                marker=marker,color=('#31688e' if grid==0 else '#35b779'),label='Mean squared, '+label)
        ax.plot([r['grid'] for r in rows],[r['second_active_ratios'][grid] for r in rows],
                marker=marker,fillstyle='none',linestyle=':',color=('#31688e' if grid==0 else '#35b779'),
                label='Second moment, positive support, '+label)
    ax.axhline(1,color='#202020',linestyle='--',label='Signed second moment / fine reference')
    ax.set(xlabel='Response-cell grid per direction',ylabel='Diagnostic stiffness / direct fine-grid value',
           xticks=[8,16,32],ylim=(.3,1.12),title='Velocity closure and support truncation are separate effects')
    ax.grid(alpha=.2);ax.legend(fontsize=8,loc='lower right')
    fig.supxlabel('Nb retained bands; fine grid 32³; 100 energy bins; imposed gap 1.5 meV; T = 2 K',fontsize=8)
    folder=ROOT/'figures';folder.mkdir(exist_ok=True)
    for suffix in ('png','pdf'):fig.savefig(folder/f'moment-refinement.{suffix}',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--plot',action='store_true')
    args=parser.parse_args();result=summary()
    if args.plot:plot(result)
    print(json.dumps(result,indent=2,allow_nan=False))
