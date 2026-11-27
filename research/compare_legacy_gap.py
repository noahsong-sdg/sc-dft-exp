"""Compare an explicit four-float legacy gap schema with native initialization.

This checks ordering and geometry; it does not establish gap temperature,
convergence or compatibility with a different momentum.
"""
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import sys


def records(path, counts):
    with Path(path).open() as source:
        header=source.readline().split()
        if header != ['#',*map(str,counts)]:
            raise ValueError('Legacy counts/header differ')
        for grid,count in enumerate(counts):
            for state in range(count):
                line=source.readline()
                while line and not line.strip():
                    line=source.readline()
                fields=line.split()
                if len(fields)!=6:
                    raise ValueError('Expected four floats and two integer indices')
                values=list(map(float,fields[:4]))
                indices=list(map(int,fields[4:]))
                if not all(map(math.isfinite,values)):
                    raise ValueError('Nonfinite legacy state')
                yield grid,state,values,indices
        if source.read().strip():
            raise ValueError('Trailing legacy state data')


def native_arrays(folder):
    if sys.byteorder!='little':
        raise ValueError('Native snapshot is little-endian')
    folder=Path(folder)
    meta=(folder/'native-init.meta').read_text().splitlines()
    if meta[0]!='native-init-v1; arrays are native binary64/int32, Fortran order':
        raise ValueError('Native snapshot schema differs')
    counts=list(map(int,meta[1].split()))
    if len(counts)!=7 or min(counts)<=0 or max(counts[:2])!=counts[2]:
        raise ValueError('Invalid native dimensions')
    maximum,nx=counts[2:4]
    fields=[(name,'d',nx) for name in ('xi0','dx0')]
    fields += [(name,'d',2*maximum) for name in ('xi','delta','dk','dxq','d2xq')]
    fields += [(name,'i',2*maximum) for name in ('kindx','bindx')]
    data={}
    with (folder/'native-init.bin').open('rb') as source:
        for name,kind,size in fields:
            values=array.array(kind)
            if values.itemsize!={'d':8,'i':4}[kind]:
                raise ValueError('Native scalar size differs')
            values.fromfile(source,size)
            if kind=='d' and not all(map(math.isfinite,values)):
                raise ValueError('Nonfinite native state')
            data[name]=values
        if source.read(1):
            raise ValueError('Trailing native snapshot bytes')
    return counts,data


def digest(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as source:
        for chunk in iter(lambda:source.read(1024*1024),b''):
            value.update(chunk)
    return value.hexdigest()


def compare(folder, gap):
    counts,native=native_arrays(folder)
    rows=[dict(states=0,index_mismatches=0,max_xi_absolute_difference=0.,
               max_weight_absolute_difference=0.,max_absolute_gap=0.,
               min_absolute_gap=math.inf) for _ in range(2)]
    for grid,state,values,indices in records(gap,counts[:2]):
        xi,delta,z,weight=values
        offset=grid*counts[2]+state
        row=rows[grid]
        row['states']+=1
        row['index_mismatches']+=indices!=[native['kindx'][offset],native['bindx'][offset]]
        row['max_xi_absolute_difference']=max(row['max_xi_absolute_difference'],abs(xi-native['xi'][offset]))
        row['max_weight_absolute_difference']=max(row['max_weight_absolute_difference'],abs(weight-native['dk'][offset]))
        row['max_absolute_gap']=max(row['max_absolute_gap'],abs(delta))
        row['min_absolute_gap']=min(row['min_absolute_gap'],abs(delta))
    return dict(legacy_sha256=digest(gap),native_metadata_sha256=digest(Path(folder)/'native-init.meta'),
                native_payload_sha256=digest(Path(folder)/'native-init.bin'),grids=rows,
                scope='Geometry/order diagnostics only; no temperature, convergence or finite-Q gap validation')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native_folder',type=Path)
    parser.add_argument('legacy_gap',type=Path)
    args=parser.parse_args()
    print(json.dumps(compare(args.native_folder,args.legacy_gap),indent=2,allow_nan=False))
