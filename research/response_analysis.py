"""Bounded retrieval and deterministic sensitivity analysis of released curves."""
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

BASE = "https://arim.mdx.jp/nextcloud/public.php/dav/files/zqS4RXS8zaD26p5/nso/"
TEMPERATURES = (1, 3, 5, 7, 10, 12, 15)


def fetch(root):
    root.mkdir(parents=True, exist_ok=True)
    names = ["xi.sh", "fflo_j.sh"] + [
        "Si2V6-186003/fflo_%s.0.dat" % t for t in TEMPERATURES
    ] + ["Si2V6-186003/fflo.gp"]
    manifest = []
    for name in names:
        url = BASE + name
        with urlopen(url, timeout=45) as response:
            data = response.read(1_000_001)
        if len(data) > 1_000_000 or b"<html" in data.lower():
            raise ValueError("Unexpected size/content: " + url)
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        manifest.append(dict(url=url, path=name, bytes=len(data),
                             sha256=hashlib.sha256(data).hexdigest()))
    return dict(retrieved_utc=datetime.now(timezone.utc).isoformat(), files=manifest)


def parse_curve(text):
    rows = [tuple(map(float, line.split())) for line in text.splitlines() if line.strip()]
    if len(rows) < 5 or any(len(row) != 4 for row in rows):
        raise ValueError("Expected at least five four-column samples")
    if any(not all(math.isfinite(x) for x in row) for row in rows):
        raise ValueError("Nonfinite processed curve")
    if rows[0][0] != 0 or any(b[0] <= a[0] for a, b in zip(rows, rows[1:])):
        raise ValueError("Expected zero endpoint and increasing momentum")
    return rows


def slope(rows):
    """Origin-constrained least squares; a diagnostic, not a certified Q limit."""
    return sum(q*j for q, _, _, j in rows) / sum(q*q for q, _, _, _ in rows)


def analyze(rows):
    first = rows[1][3] / rows[1][0]
    if first <= 0:
        raise ValueError("Nonpositive initial stiffness proxy")
    # Reproduce xi.sh and its plot's conversion to nm, retaining its constants.
    author_lambda = (math.sqrt(0.529177249 / (1.3383525114e-3 * 0.5 * first))
                     * 0.1 * 0.529177249)
    windows = []
    for count in (1, 2, 3, 4):
        estimate = slope(rows[1:count+1])
        windows.append(dict(points=count, qmax_angstrom_inverse=rows[count][0],
                            slope_ratio=estimate/first,
                            lambda_ratio=math.sqrt(first/estimate) if estimate > 0 else None))
    peak = max(rows, key=lambda row: row[3])
    return dict(samples=len(rows), author_single_point_lambda_nm=author_lambda,
                windows=windows, peak_q_angstrom_inverse=peak[0],
                peak_current_reported_au=peak[3],
                gap_at_peak_over_zero=peak[1]/rows[0][1],
                negative_current_samples=sum(row[3] < 0 for row in rows))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("fetch", "analyze"))
    parser.add_argument("--root", type=Path, default=Path("research/raw"))
    args = parser.parse_args()
    if args.command == "fetch":
        result = fetch(args.root)
    else:
        result = {str(t): analyze(parse_curve((args.root / "Si2V6-186003" /
                  ("fflo_%s.0.dat" % t)).read_text())) for t in TEMPERATURES}
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
