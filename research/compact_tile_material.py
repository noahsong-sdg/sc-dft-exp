"""Admit only selected compact/native material tiles from two accepted parents."""
import json
import math
from pathlib import Path
import shutil

from compact_defect_state import HEADER
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent
COPIED=('gap-seed.meta','gap-seed.bin','map-control.in','native.in','evaluation-context.json')


def accepted(manifest,result,label,rawname):
    mp,rp=map(lambda x:Path(x).absolute(),(manifest,result));m=json.loads(mp.read_text());root=Path(m['cwd'])
    pins=check_pins(m);receipt_path=root/'results'/label/'receipt.json';rawpath=root/rawname
    receipt=json.loads(receipt_path.read_text());raw=json.loads(rawpath.read_text());recorded=json.loads(rp.read_text())
    if (mp.read_bytes()!=(root/'run-manifest.json').read_bytes() or receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None
            or receipt['command']!=m['command'] or receipt['cwd']!=m['cwd']
            or receipt['guard_source_sha256']!=m['guard_source_sha256'] or receipt['continuous_deadline_s']!=m['guard_seconds']
            or not math.isfinite(receipt['wall_s']) or not 0<receipt['wall_s']<m['guard_seconds']
            or any(not 0<=receipt[k]<=m['group_rss_cap_bytes'] for k in ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or recorded.get('terminal_guard_pass') is not True or recorded.get('receipt')!=receipt
            or raw.get('terminal_guard_pass') is not False or raw.get('inputs_unchanged') is not True
            or raw.get('manifest_sha256')!=digest(mp) or recorded.get('readback_sha256')!=digest(rawpath)
            or any(recorded.get(k)!=v for k,v in raw.items() if k!='terminal_guard_pass')
            or json.loads((root/'campaign_launch_watch.json').read_text())['phase']!='completed'):
        raise ValueError('Unaccepted compact material parent')
    for name,item in raw['outputs'].items():
        if identity(root/name)!=item:raise ValueError('Changed compact parent output')
    for path in (mp,rp,root/'run-manifest.json',receipt_path,rawpath,root/'campaign_launch_watch.json',
                 *(root/name for name in raw['outputs'])):
        item=identity(path)
        if item['path'] in pins and pins[item['path']]!=item:raise ValueError('Conflicting compact parent pin')
        pins[item['path']]=item
    return m,recorded,pins


def stage(preparation,preparation_result,build,build_result,destination):
    root=Path(destination).absolute()
    if root.exists():raise ValueError('Fresh compact material directory required')
    prep,pr,pins=accepted(preparation,preparation_result,'prepare','compact-preparation-result.json')
    bm,br,buildpins=accepted(build,build_result,'build','compact-build-result.json')
    for path,item in buildpins.items():
        if path in pins and pins[path]!=item:raise ValueError('Conflicting compact material closure')
        pins[path]=item
    if (br.get('fresh_compile_count')!=18 or br.get('build_plan_matches_console') is not True
            or br.get('cache_checks')!=902 or br.get('cache_all_bitwise_equal') is not True
            or br.get('historical_custom_objects_used') is not False or br.get('material_runtime_qualified') is not False):
        raise ValueError('Unqualified compact native build')
    errors=pr['recipe']['calibration_max_errors'];bounds=pr['recipe']['calibration_bounds']
    if len(errors)!=3 or len(bounds)!=3 or any(not math.isfinite(e) or not math.isfinite(b) or not 0<=e<=b for e,b in zip(errors,bounds)):
        raise ValueError('Unqualified compact chosen inverse')
    parent_path=Path(prep['source_manifest']);require(pins,(parent_path,));parent=json.loads(parent_path.read_text())
    fullpath=Path(parent['full_manifest']);require(pins,(fullpath,));full=json.loads(fullpath.read_text());source=Path(full['cwd'])
    require(pins,(source/name for name in COPIED))
    compact_root=Path(prep['cwd']);meta=(compact_root/'compact-state.meta').read_text().splitlines()
    seed_meta=(source/'gap-seed.meta').read_text().splitlines()
    if len(seed_meta)!=5 or seed_meta[0]!='gap-seed-v1; binary64 Fortran order':raise ValueError('Stale compact native seed')
    counts=list(map(int,seed_meta[1].split()))
    if (len(counts)!=6 or counts[0]<64 or min(counts)<=0 or counts[2]!=max(counts[:2])
            or (source/'gap-seed.bin').stat().st_size!=16*counts[2]
            or float(seed_meta[2])!=pr['beta'] or seed_meta[4]!=pr['operator_sha256']
            or len(meta)!=6 or meta[0]!=HEADER or list(map(int,meta[1].split()))!=[*counts[:3],pr['rank']]
            or float(meta[2])!=pr['beta'] or meta[3]!=pr['operator_sha256'] or meta[4]!=pr['padded_candidate_sha256']
            or meta[5]!=digest(parent_path) or digest(source/'gap-seed.bin')!=meta[4]
            or sum(counts[:2])!=pr['active_states']):raise ValueError('Different compact material base state')
    executable=Path(bm['cwd'])/'full-gap-check.x';require(pins,(executable,))
    for path in (Path(__file__).resolve(),RESEARCH/'macos_native_guard_v2.py',RESEARCH/'compact_tile_readback.py'):
        pins[str(path)]=identity(path)
    root.mkdir(parents=True)
    for name in COPIED:shutil.copy2(source/name,root/name)
    shutil.copy2(executable,root/'compact-native-tiles.x')
    (root/'seed-control.in').write_text(str(root)+'\n'+meta[3]+'\n')
    (root/'compact-tile-control.in').write_text('selected-compact-native-tiles-v1\n'+str(compact_root)+'\n'+str(pr['rank'])+'\n'+'\n'.join(meta[3:])+'\n')
    for name in (*COPIED,'compact-native-tiles.x','seed-control.in','compact-tile-control.in'):
        pins[str(root/name)]=identity(root/name)
    m=dict(cwd=str(root),command=[str(root/'compact-native-tiles.x'),'-in',str(root/'native.in')],files=list(pins.values()),
           preparation_manifest=str(Path(preparation).absolute()),preparation_result=str(Path(preparation_result).absolute()),
           build_manifest=str(Path(build).absolute()),build_result=str(Path(build_result).absolute()),native_source_directory=str(source),
           guard_seconds=90,launch_normal_seconds=120,group_rss_cap_bytes=3221225472,
           guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__,
           acceptance='Rows1:64 partial P, native state/D and independent saved tile controls; no full norm or physical response')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m
