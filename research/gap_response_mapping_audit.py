"""Read-only energy/index grouping audit; no gap transfer or response validation."""
import argparse
import collections
import json
from pathlib import Path

from compare_legacy_gap import digest, native_arrays


def audit(prepare, source):
    prepare, source = Path(prepare), Path(source)
    counts, arrays = native_arrays(prepare)
    nodes = set(arrays['xi0'])
    grids = []
    for side, count in enumerate(counts[:2]):
        groups = collections.defaultdict(list)
        for state in range(count):
            index = side * counts[2] + state
            groups[arrays['kindx'][index], arrays['bindx'][index]].append(index)
        resolved = [rows for rows in groups.values() if len(rows) >= 2]
        single = [rows[0] for rows in groups.values() if len(rows) == 1]
        grids.append(dict(
            side=side+1, states=count, index_groups=len(groups),
            resolved_groups=len(resolved), resolved_states=sum(map(len, resolved)),
            resolved_off_energy_grid=sum(arrays['xi'][i] not in nodes for rows in resolved for i in rows),
            resolved_duplicate_energy_groups=sum(len({arrays['xi'][i] for i in rows}) != len(rows) for rows in resolved),
            single_state_groups=len(single),
            single_states_on_energy_grid=sum(arrays['xi'][i] in nodes for i in single),
            single_state_nonuniform_weights=sum(arrays['dk'][i] != 1/counts[4] for i in single),
            single_state_min_abs_xi=min((abs(arrays['xi'][i]) for i in single), default=None)))
    return dict(counts=counts, grids=grids,
                sha256={str(p): digest(p) for p in (prepare/'native-init.meta', prepare/'native-init.bin', source)},
                scope=__doc__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prepare', type=Path)
    parser.add_argument('owning_source', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.prepare, args.owning_source), indent=2, allow_nan=False))
