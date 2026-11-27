"""Account for terminal guarded native attempts, including failed/prelaunch ones.

This excludes launch-watch waiting, compilation, downloads, Python analyses and
unmetered model use. Guard PASS is not scientific or physical acceptance.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path


def summarize(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError('Receipt directory is unavailable: ' + str(root))
    rows = []
    for path in sorted(root.rglob('receipt.json')):
        data = path.read_bytes()
        receipt = json.loads(data)
        if 'continuous_deadline_s' not in receipt:
            continue
        wall = receipt['wall_s']
        if receipt['status'] not in ('PASS', 'FAIL') or not math.isfinite(wall) or wall < 0:
            raise ValueError('Invalid terminal guarded receipt: ' + str(path))
        rows.append(dict(path=str(path.relative_to(root)),
                         receipt_sha256=hashlib.sha256(data).hexdigest(),
                         status=receipt['status'], wall_s=wall, error=receipt['error'],
                         exit=receipt['exit'],
                         individual_peak_rss_bytes=receipt['max_individual_descendant_rss_bytes'],
                         sampled_group_peak_rss_bytes=receipt['sampled_peak_group_rss_bytes'],
                         guard_source_sha256=receipt['guard_source_sha256']))
    totals = {status: dict(attempts=sum(row['status'] == status for row in rows),
                           wall_s=math.fsum(row['wall_s'] for row in rows if row['status'] == status))
              for status in ('PASS', 'FAIL')}
    return dict(as_of_utc=datetime.now(timezone.utc).isoformat(), attempts=rows,
                totals=totals, total_guarded_wall_s=math.fsum(row['wall_s'] for row in rows),
                scope=__doc__.strip(),
                cpu_time_energy_model_cost='Not instrumented; no estimates inferred')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, nargs='?', default=Path('research/raw'))
    print(json.dumps(summarize(parser.parse_args().root), indent=2, allow_nan=False))
