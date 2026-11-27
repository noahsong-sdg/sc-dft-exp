"""Retrieve bounded V3Si stage logs and report all matching total clocks."""
import hashlib
import json
import re
from urllib.request import urlopen

BASE = "https://arim.mdx.jp/nextcloud/public.php/dav/files/zqS4RXS8zaD26p5/nso/Si2V6-186003/"
STAGES = ("scf", "ph", "elph", "epmat", "nscf", "twin", "kel", "tc",
          "fflo_1.0_0.0025")


def duration(text):
    units = dict(d=86400, h=3600, m=60, s=1)
    tokens = re.findall(r"([\d.]+)\s*([dhms])", text)
    if not tokens:
        raise ValueError("Unrecognized clock: " + text)
    return sum(float(value)*units[unit] for value, unit in tokens)


def main():
    rows = []
    for stage in STAGES:
        url = BASE + stage + ".out"
        with urlopen(url, timeout=45) as response:
            data = response.read(5_000_001)
        if len(data) > 5_000_000 or b"<html" in data.lower():
            raise ValueError("Unexpected log: " + url)
        text = data.decode()
        totals = re.findall(r"^\s*(PWSCF|PHONON|SCTK)\s*:\s*(.*?) CPU\s*(.*?) WALL", text, re.M)
        rows.append(dict(stage=stage, url=url, sha256=hashlib.sha256(data).hexdigest(),
                         bytes=len(data), cores=re.findall(r"running on\s+(\d+) processor cores",text),
                         totals=[dict(program=p,cpu_printed=c,wall_printed=w,
                                      wall_seconds=duration(w)) for p,c,w in totals]))
    print(json.dumps(dict(scope="Historical author-machine logs; not laptop forecast; all totals retained",
                         stages=rows),indent=2))


if __name__ == "__main__":
    main()
