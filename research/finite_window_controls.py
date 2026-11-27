"""Deterministic extraction sensitivities; no confidence interval or Q-limit proof."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from response_analysis import TEMPERATURES, parse_curve, slope


def odd_cubic(rows):
    """Fit j=a*q+b*q^3 with scaled q, retaining physical slope units."""
    scale=max(row[0] for row in rows)
    x=[row[0]/scale for row in rows]
    y=[row[3] for row in rows]
    s2=math.fsum(t*t for t in x);s4=math.fsum(t**4 for t in x)
    s6=math.fsum(t**6 for t in x)
    r1=math.fsum(t*j for t,j in zip(x,y));r3=math.fsum(t**3*j for t,j in zip(x,y))
    determinant=s2*s6-s4*s4
    if determinant<=0:
        raise ValueError('Odd cubic fit requires distinct nonzero momenta')
    a=(r1*s6-r3*s4)/determinant
    b=(r3*s2-r1*s4)/determinant
    residual=math.sqrt(math.fsum((j-a*t-b*t**3)**2 for t,j in zip(x,y))/len(x))
    return dict(slope=a/scale,cubic_coefficient=b/scale**3,rms_current_residual=residual,
        points=len(rows),qmax_angstrom_inverse=scale,
        assumption='Odd current through cubic order; parity is imposed, not tested')


def interpolated_peak(rows):
    index=max(range(len(rows)),key=lambda i:rows[i][3])
    if index in (0,len(rows)-1):
        return dict(qualified=False,reason='Sample maximum has no two-sided bracket')
    triple=rows[index-1:index+2]
    origin=triple[1][0];scale=triple[2][0]-triple[0][0]
    x=[(row[0]-origin)/scale for row in triple];y=[row[3] for row in triple]
    left=(y[1]-y[0])/(x[1]-x[0]);right=(y[2]-y[1])/(x[2]-x[1])
    a=(right-left)/(x[2]-x[0]);b=left-a*(x[0]+x[1])
    if a>=0:
        return dict(qualified=False,reason='Local parabola is not concave')
    vertex=-b/(2*a)
    if not x[0]<=vertex<=x[2]:
        return dict(qualified=False,reason='Local vertex lies outside sampled bracket')
    c=y[1]-a*x[1]**2-b*x[1]
    return dict(qualified=True,q_angstrom_inverse=origin+scale*vertex,
        current_reported_au=a*vertex**2+b*vertex+c,
        bracket_angstrom_inverse=[triple[0][0],triple[2][0]],
        scope='Three-point interpolation only; not a measured depairing current')


def analyze(rows):
    first=rows[1][3]/rows[1][0]
    if first<=0:
        raise ValueError('Nonpositive reference stiffness proxy')
    early=rows[1:5]
    leave=[]
    for index,row in enumerate(early):
        estimate=slope(early[:index]+early[index+1:])
        leave.append(dict(removed_q_angstrom_inverse=row[0],slope_ratio_to_first=estimate/first,
            lambda_ratio_to_first=math.sqrt(first/estimate) if estimate>0 else None))
    fits=[]
    for count in (3,4):
        fit=odd_cubic(rows[1:count+1]);estimate=fit['slope']
        fit.update(slope_ratio_to_first=estimate/first,
            lambda_ratio_to_first=math.sqrt(first/estimate) if estimate>0 else None)
        fits.append(fit)
    peak=max(row[3] for row in rows)
    negative=[dict(q_angstrom_inverse=row[0],current_reported_au=row[3]) for row in rows if row[3]<0]
    return dict(leave_one_out_first_four=leave,odd_cubic_fits=fits,
        local_peak_interpolation=interpolated_peak(rows),
        tail=dict(last_q_angstrom_inverse=rows[-1][0],last_current_over_sampled_peak=rows[-1][3]/peak,
            negative_current_samples=negative),
        empirical_parity_test_available=False,separate_current_estimates_available=False,
        data_limit='Released curves contain nonnegative Q only and mean of two current estimates',
        scope=__doc__.strip())


def run(root,manifest_path):
    root=Path(root);manifest_path=Path(manifest_path)
    manifest=json.loads(manifest_path.read_text())
    catalog={item['path']:item for item in manifest['files']}
    script=root/'fflo_j.sh';payload=script.read_bytes();item=catalog['fflo_j.sh']
    script_hash=hashlib.sha256(payload).hexdigest()
    if len(payload)!=item['bytes'] or script_hash!=item['sha256']:
        raise ValueError('Changed released processing script')
    sources={};results={}
    for temperature in TEMPERATURES:
        name=f'Si2V6-186003/fflo_{temperature}.0.dat';path=root/name
        payload=path.read_bytes();identity=hashlib.sha256(payload).hexdigest();item=catalog[name]
        if len(payload)!=item['bytes'] or identity!=item['sha256']:
            raise ValueError('Changed released curve: '+name)
        sources[name]=identity;results[str(temperature)]=analyze(parse_curve(payload.decode()))
    return dict(temperatures_k=results,curve_sha256=sources,processing_script_sha256=script_hash,
        retrieval_manifest_sha256=hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scope=__doc__.strip())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path('research/raw'))
    parser.add_argument('--manifest-path',type=Path,default=Path('research/retrieval_manifest.json'))
    print(json.dumps(run(**vars(parser.parse_args())),indent=2,allow_nan=False))
