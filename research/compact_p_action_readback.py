"""Bind a complete material P to the independently saved full native linear image."""
import json
import math
from pathlib import Path

from compact_p_actions import compare
from compact_p_segment import analyze as segment_analyze
from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary,seed_context
from full_step_segments import certify
from inverse_material_run import check_pins,identity,require
from step_checkpoint_analysis import declared
from stream_inverse_action import column


def analyze(manifest,result):
    mp,rp=map(lambda x:Path(x).absolute(),(manifest,result));m=json.loads(mp.read_text());recorded=json.loads(rp.read_text())
    checked=segment_analyze(mp)
    if (any(recorded.get(k)!=v for k,v in checked.items()) or set(recorded)-set(checked)-{'postread_wall_s','postread_maxrss_bytes'}
            or any(not math.isfinite(recorded[k]) or recorded[k]<=0 for k in ('postread_wall_s','postread_maxrss_bytes') if k in recorded)
            or checked.get('complete_P') is not True):raise ValueError('Unaccepted complete P action parent')
    pins=check_pins(m);root=Path(m['cwd']);qual=json.loads(Path(m['predecessor_manifest']).read_text())
    selected=json.loads(Path(qual['selected_manifest']).read_text());prep=json.loads(Path(selected['preparation_manifest']).read_text())
    compact=Path(prep['cwd']);inverse=json.loads(Path(prep['source_manifest']).read_text())
    fm,fr=Path(inverse['full_manifest']),Path(inverse['full_result']);require(pins,(fm,fr))
    full=certify(fm);saved=json.loads(fr.read_text())
    if any(saved.get(k)!=v for k,v in full.items()) or full.get('full_native_residual_verified') is not True:
        raise ValueError('Unaccepted native linear-image parent')
    source=Path(json.loads(fm.read_text())['cwd'])
    if source!=Path(selected['native_source_directory']):raise ValueError('Different saved native source')
    dims,beta,operator,fields=seed_context(source)
    if [*dims[:3],m['counts'][3]]!=m['counts']:raise ValueError('Different native P action geometry')
    binding=declared(source,dims[:3],beta,operator,fields);left,right,maximum=dims[:3];n=left+right;padded=2*maximum
    paths=(mp,rp,root/'compact-p.bin',compact/'compact-q.bin',compact/'compact-state.bin',fm,fr,
           source/'linear-image-checkpoint.bin',source/'direction-state.meta',source/'direction-state.bin',source/'full-map-step.in',
           source/'gap-seed.meta',source/'gap-seed.bin',source/'evaluation-context.json',Path(__file__).resolve(),
           Path(__file__).with_name('compact_p_actions.py'))
    require(pins,(path for path in paths if path not in (mp,rp,root/'compact-p.bin',Path(__file__).resolve(),Path(__file__).with_name('compact_p_actions.py'))))
    before={str(path):identity(path) for path in paths}
    images=binary(source/'linear-image-checkpoint.bin',4*padded)
    image=images[3*padded:];direction=binding['direction'];z=fields[3]
    # The original native image is before output normalization: ADv=-image/(1+Z).
    indexes=(*range(left),*range(maximum,maximum+right))
    v=[direction[i] for i in indexes];adv=[-image[i]/(1+z[i]) for i in indexes]
    with (compact/'compact-state.bin').open('rb') as stream:
        stream.seek(8*4*n);d=column(stream,n)
    controlled=compare(compact/'compact-q.bin',root/'compact-p.bin',d,v,adv,m['counts'][3])
    check_pins(m)
    if any(identity(Path(path))!=item for path,item in before.items()):raise ValueError('Changed P action readback input')
    return dict(accepted_complete_P_manifest_sha256=digest(mp),accepted_complete_P_result_sha256=digest(rp),
                complete_P=True,independent_full_P_action_controls_passed=True,inputs_unchanged=True,bindings=before,
                saved_native_image_identity='ADv=-raw fourth image/(1+Z); original declared correction direction',**controlled)
