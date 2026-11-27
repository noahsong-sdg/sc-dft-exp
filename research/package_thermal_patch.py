"""Package tested transformations against exact upstream files; no installation."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

import full_current_probe as current
import full_rhs_probe as rhs
import rhs_thermal_probe


def package(destination):
    destination.mkdir(parents=True, exist_ok=False)
    changes=[]
    manifest={'revision':current.REVISION, 'files':[],
              'scope':'Review candidate: current thermal/product correction and RHS thermal correction; not a full solver qualification'}
    for name,url,expected,transform in (
        ('sctk_broyden.f90',current.URL,current.SHA256,current.robust_correction),
        ('sctk_gapeq_rhs.f90',rhs_thermal_probe.URL,rhs_thermal_probe.SHA256,rhs.corrected)):
        with urlopen(url,timeout=45) as response:
            data=response.read(1_000_001)
        if hashlib.sha256(data).hexdigest()!=expected:
            raise ValueError('Pinned upstream file differs: '+name)
        original=data.decode()
        candidate=transform(original)
        if candidate==original:
            raise ValueError('Expected correction absent: '+name)
        for tree,text in (('original',original),('candidate',candidate)):
            path=destination/tree/'src'/name
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
        changes.extend(difflib.unified_diff(original.splitlines(True),candidate.splitlines(True),
                                           fromfile='a/src/'+name,tofile='b/src/'+name))
        manifest['files'].append(dict(path='src/'+name,url=url,original_sha256=expected,
            candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest()))
    patch=''.join(changes)
    (destination/'thermal-candidate.patch').write_text(patch)
    manifest['patch_sha256']=hashlib.sha256(patch.encode()).hexdigest()
    (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination',type=Path)
    print(json.dumps(package(parser.parse_args().destination),indent=2))
