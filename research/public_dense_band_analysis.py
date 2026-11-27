"""Verify the declared897-point32cubed fixed-density replay against all bands."""
import argparse
import json
from pathlib import Path

from public_band_pilot_analysis import analyze

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('manifest_path',type=Path)
    args=parser.parse_args()
    result=analyze(args.directory,args.manifest_path,expected_points=897,guard_seconds=600)
    result['scope']=__doc__.strip()+' No fitted offset, density/cutoff/k-grid convergence or physical response qualification.'
    print(json.dumps(result,indent=2,allow_nan=False))
