"""Stream a five-float saved gap against freshly prepared response geometry.

Reports compatibility; never transfers a gap or fills a missing field silently.
"""
import argparse
import json
from pathlib import Path
from archived_finite_q_gap import records
from compare_legacy_gap import digest
from preparation_analysis import numbers


def compare(preparation,gap):
    with Path(preparation).open() as source:
        if source.readline().strip()!='# preparation-only-v1; initial gap is NOT self-consistent':
            raise ValueError('Expected fresh preparation schema')
        dimensions=numbers(source.readline(),2,int)
        beta,volume,tpiba=numbers(source.readline(),3)
        momentum=numbers(source.readline(),3);basis=numbers(source.readline(),9)
        if min(dimensions)<=0 or min(beta,volume,tpiba)<=0:
            raise ValueError('Invalid fresh dimensions or scales')
        rows=[dict(states=0,index_mismatches=0,max_xi_absolute_difference=0.,
                   max_weight_absolute_difference=0.,max_shift_absolute_difference=0.) for _ in range(2)]
        for grid,state,archived,indices in records(gap,dimensions):
            fields=source.readline().split()
            if len(fields)!=8:raise ValueError('Missing fresh geometry record')
            fresh=numbers(' '.join(fields[:5]),5)
            owner,k,band=numbers(' '.join(fields[5:]),3,int)
            if owner!=grid+1 or min(k,band)<=0 or fresh[2]<0:
                raise ValueError('Invalid fresh record ownership or assigned weight')
            row=rows[grid];row['states']+=1
            row['index_mismatches']+=indices!=[k,band]
            for key,a,b in (('xi',archived[0],fresh[0]),
                            ('weight',archived[3],fresh[2]),('shift',archived[4],fresh[3])):
                name='max_'+key+'_absolute_difference'
                row[name]=max(row[name],abs(a-b))
        if source.read().strip():raise ValueError('Trailing fresh geometry data')
    return dict(preparation_sha256=digest(preparation),gap_sha256=digest(gap),
                beta=beta,volume=volume,tpiba=tpiba,momentum_fractional=momentum,
                reciprocal_basis_fortran_order=basis,grids=rows,
                scope='Ordered geometry/weight/shift comparison; no gap transfer or provenance conclusion')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('preparation',type=Path);parser.add_argument('gap',type=Path)
    args=parser.parse_args();print(json.dumps(compare(args.preparation,args.gap),indent=2,allow_nan=False))
