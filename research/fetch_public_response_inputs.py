"""Acquire hash-pinned public Nb response inputs without a historical checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

PREFIX = 'https://arim.mdx.jp/nextcloud/public.php/dav/files/zqS4RXS8zaD26p5/nso/Nb1-151406/'


def validate(name, item):
    relative = Path(name)
    if (not name or relative.is_absolute() or '..' in relative.parts or str(relative) != name
            or item['url'] != PREFIX+name or type(item['bytes']) is not int or item['bytes'] <= 0
            or not re.fullmatch('[0-9a-f]{64}', item['sha256'])):
        raise ValueError('Invalid public input identity or path')
    return relative


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def fetch_one(root, name, item, deadline):
    relative = validate(name, item)
    path = root/relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Symlink in public input destination')
    if path.exists():
        if not path.is_file() or path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Existing public input differs; preserved')
        return dict(name=name, status='verified_existing', bytes=item['bytes'], sha256=item['sha256'])
    remaining = deadline-time.monotonic()
    if remaining <= 0:
        raise TimeoutError('Public input acquisition deadline')
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name+'.partial')
    request = Request(item['url'], headers={'Accept-Encoding': 'identity', 'User-Agent': 'sc-dft-exp/1'})
    count = 0
    h = hashlib.sha256()
    with urlopen(request, timeout=min(30., remaining)) as response:
        if (response.status != 200 or response.geturl() != item['url']
                or response.headers.get('Content-Encoding', 'identity') != 'identity'):
            raise ValueError('Unexpected public input HTTP response')
        with partial.open('xb') as output:
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError('Public input acquisition deadline')
                block = response.read(min(65536, item['bytes']-count+1))
                if not block:
                    break
                count += len(block)
                if count > item['bytes']:
                    raise ValueError('Public input exceeds declared size')
                output.write(block)
                h.update(block)
    if count != item['bytes'] or h.hexdigest() != item['sha256']:
        raise ValueError('Public input size or SHA256 differs')
    partial.rename(path)
    return dict(name=name, status='downloaded', bytes=count, sha256=h.hexdigest())


def fetch(manifest_path, destination):
    manifest_path, root = map(Path, (manifest_path, destination))
    manifest = json.loads(manifest_path.read_text())
    files = manifest['files']
    if not files or sum(item['bytes'] for item in files.values()) != manifest['total_bytes']:
        raise ValueError('Public input manifest total differs')
    for name, item in files.items():
        validate(name, item)
    root.mkdir(parents=True, exist_ok=True)
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError('Symlink in public input destination')
    started = time.monotonic()
    rows = [fetch_one(root, name, item, started+300) for name, item in files.items()]
    return dict(files=rows, wall_s=time.monotonic()-started,
                manifest_sha256=digest(manifest_path), total_bytes=manifest['total_bytes'],
                bytes_downloaded=sum(row['bytes'] for row in rows if row['status'] == 'downloaded'),
                destination=str(root.absolute()),
                scope='Hash-verified acquisition only; native response and cold-start build qualification separate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--manifest', type=Path, default=Path(__file__).with_name('public_response_inputs.json'))
    args = parser.parse_args()
    print(json.dumps(fetch(args.manifest, args.destination), indent=2, allow_nan=False))
