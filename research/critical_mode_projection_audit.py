"""Audit representation of a freshly measured mode; no gap error certificate."""
import argparse
import array
import json
import math
from pathlib import Path

from compare_legacy_gap import digest
from mode_amplitude_analysis import analyze
from occupation_enrichment import combine, dot


def audit(directory, bases):
    root = Path(directory)
    checked = analyze(root)
    control = (root/'mode-control.in').read_text().splitlines()
    if len(control) != 2 or len(control[1]) != 64:
        raise ValueError('Invalid measured-mode context')
    n = 2*checked['dimensions'][2]
    with (root/'mode-amplitudes.bin').open('rb') as source:
        mode = array.array('d'); mode.fromfile(source, n)
        action = array.array('d'); action.fromfile(source, n)
    rows = []
    for folder in map(Path, bases):
        meta = (folder/'basis.meta').read_text().splitlines()
        if (len(meta) != 5 or meta[0] != 'tc-basis-v1'
                or float(meta[2]) != checked['beta'] or meta[3] != control[1]):
            raise ValueError('Incompatible mode-projection basis')
        size, rank = map(int, meta[1].split())
        if size != n or not 1 <= rank <= 64 or (folder/'basis.bin').stat().st_size != 16*n*rank:
            raise ValueError('Stale mode-projection basis shape')
        columns = []
        with (folder/'basis.bin').open('rb') as source:
            for _ in range(2*rank):
                column = array.array('d'); column.fromfile(source, n)
                if not all(map(math.isfinite, column)):
                    raise ValueError('Nonfinite mode-projection basis')
                columns.append(column)
        q, u = columns[:rank], columns[rank:]
        p = [dot(c, mode) for c in q]
        defect = [a-b for a, b in zip(mode, combine(q, p))]
        image_defect = [a-b for a, b in zip(action, combine(u, p))]
        norm = math.sqrt(dot(defect, defect))
        image_norm = math.sqrt(dot(image_defect, image_defect))
        rows.append(dict(basis=str(folder), rank=rank,
                         mode_projection_defect_norm=norm, mode_action_defect_norm=image_norm,
                         defect_action_over_defect_norm=image_norm/norm if norm else None,
                         max_absolute_action_defect=max(map(abs, image_defect)),
                         basis_sha256=digest(folder/'basis.bin'), metadata_sha256=digest(folder/'basis.meta')))
    return dict(rows=rows, fresh_mode_readback=checked, scope=__doc__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('bases', type=Path, nargs='+')
    args = parser.parse_args()
    print(json.dumps(audit(args.directory, args.bases), indent=2, allow_nan=False))
