"""Hash P dependencies; caller must separately certify parent receipts and pins."""
import hashlib
import json
import math
from pathlib import Path
import platform

from inverse_material_run import identity


def fingerprint(counts,grid,beta,operator,candidate,q,state,executable,blas):
    if (len(counts)!=4 or min(counts)<=0 or counts[2]!=max(counts[:2]) or counts[3]>64
            or len(grid)!=3 or min(grid)<=0 or not math.isfinite(beta) or beta<=0
            or any(len(x)!=64 or any(c not in '0123456789abcdef' for c in x) for x in (operator,candidate))):
        raise ValueError('Invalid P dependency context')
    n=sum(counts[:2]);rank=counts[3]
    if Path(q).stat().st_size!=8*n*rank or Path(state).stat().st_size!=40*n:raise ValueError('Stale P dependency shape')
    files={}
    for name,path in (('Q',q),('state_gap_xi_dk_Z_D',state),('native_executable',executable),('blas_sdk',blas)):
        item=identity(path)
        if item['bytes']<=0:raise ValueError('Empty P dependency')
        files[name]={k:v for k,v in item.items() if k!='path'}
    description=dict(schema='compact-P-dependencies-v1',counts=list(counts),native_grid=list(grid),beta_binary64_hex=beta.hex(),
                     operator_sha256=operator,padded_candidate_sha256=candidate,files=files,platform=platform.platform(),
                     normalization='A0 carries dk*tanh(beta*abs(xi)/2)/(2*abs(xi)); D is normalized occupation derivative; xi=0 limit',
                     native_tile_width=32)
    encoded=json.dumps(description,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(encoded).hexdigest(),description
