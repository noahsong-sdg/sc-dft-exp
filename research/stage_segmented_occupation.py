"""Stage one bounded occupation enrichment from published full segmented evidence."""
import argparse
import json
from pathlib import Path
import sys

from fetch_public_response_inputs import digest
from full_map_segments import certify, recorded_result, OUTPUTS

RESEARCH = Path(__file__).resolve().parent


def stage(full_manifest, full_result, reduced_directory, destination):
    protocol, result, reduced, root = map(lambda p: Path(p).absolute(),
                                         (full_manifest, full_result, reduced_directory, destination))
    if root.exists():
        raise ValueError('Fresh occupation preparation directory required')
    checked = certify(protocol)
    recorded_result(result, checked)
    if (not checked['complete_left_row_coverage']
            or json.loads(result.read_text()).get('full_candidate') != checked['full_candidate']):
        raise ValueError('Published complete full-map certification required')
    parent = json.loads(protocol.read_text()); full = Path(parent['cwd'])
    entries = {item['path']: item for item in parent['files']}
    sources = ('prepare_segmented_occupation.py', 'stage_segmented_occupation.py',
               'compare_legacy_gap.py', 'occupation_enrichment.py', 'reduced_nonlinear_analysis.py',
               'full_map_segments.py', 'full_map_segment_analysis.py', 'verify_gap_candidate_v2.py',
               'full_nonlinear_analysis.py', 'fetch_public_response_inputs.py', 'macos_native_guard_v2.py')
    paths = [protocol, result, full/'run-manifest.json', full/'results/moment/receipt.json',
             full/'results/moment/console.log', full/'full-map.bin', full/'full-map.txt',
             *(full/name for name in OUTPUTS), *(RESEARCH/name for name in sources), Path(sys.executable)]
    for name in ('reduced-control.in', 'reduced-gap.bin', 'reduced-result.txt'):
        path = reduced/name
        expected = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
        if entries.get(str(path)) != expected:
            raise ValueError('Reduced candidate is outside certified input closure')
    for path in paths:
        item = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
        if str(path) in entries and entries[str(path)] != item:
            raise ValueError('Cannot rebind immutable predecessor input')
        entries[str(path)] = item
    root.mkdir(parents=True)
    command = [sys.executable, str(RESEARCH/'prepare_segmented_occupation.py'), str(full),
               str(protocol), str(result), str(reduced), str(root/'basis')]
    manifest = dict(cwd=str(root), command=command, files=list(entries.values()), guard_seconds=180,
                    guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),
                    full_manifest=str(protocol), full_result=str(result), reduced_directory=str(reduced),
                    operator_context_sha256=parent['operator_context_sha256'],
                    acceptance='Complete certified images; unchanged input closure; finite orthogonal occupation enrichment; no gap acceptance',
                    scope=__doc__)
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('full_manifest', 'full_result', 'reduced_directory', 'destination'):
        parser.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())), indent=2, allow_nan=False))
