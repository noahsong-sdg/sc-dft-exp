"""Fresh native response build from pinned archives, without retained objects.

Requires Python>=3.12, gfortran, GNU cpp-16, clang, cmake and make on macOS.
Installs nothing. Its destination must not exist; source archives may be cached.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from urllib.request import urlopen

from current_moment_geometry import URL, extract

RESEARCH = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(65536), b''):
            h.update(block)
    return h.hexdigest()


def archive_file(name, item, cache):
    path = cache/(name+'.tar.gz')
    if not path.exists():
        partial = path.with_suffix('.partial')
        with urlopen(item['url'], timeout=30) as response, partial.open('xb') as output:
            count = 0
            while block := response.read(min(65536, item['bytes']-count+1)):
                count += len(block)
                if count > item['bytes']:
                    raise ValueError('Source archive exceeds pinned size')
                output.write(block)
        if partial.stat().st_size != item['bytes'] or digest(partial) != item['sha256']:
            raise ValueError('Downloaded source archive differs')
        partial.rename(path)
    if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
        raise ValueError('Existing source archive differs; preserved')
    return path


def unpack(archive, target):
    if target.exists():
        target.rmdir()  # Only an empty gitlink placeholder may be replaced.
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as temporary:
        with tarfile.open(archive) as source:
            roots = {Path(m.name).parts[0] for m in source.getmembers()}
            if len(roots) != 1:
                raise ValueError('Expected one source archive root')
            source.extractall(temporary, filter='data')
        (Path(temporary)/roots.pop()).rename(target)


def patch_build_rules(qe, pins):
    """Offline archive acquisition replaces git hooks; numerical code unchanged."""
    changes = []
    path = qe/'install/install_utils'
    original = path.read_text()
    start = original.index('define update_submodule\n')
    end = original.index('\nendef', start)+len('\nendef')
    candidate = original[:start]+('define update_submodule\n'
        '  @test -s $(TOPDIR)/$(1)/$(2)/SC_DFT_SOURCE_PIN\nendef')+original[end:]
    changes.append((path, original, candidate))
    path = qe/'SCTK/src/Makefile'; original = path.read_text()
    start = original.index('hash:\n'); end = original.index('\nsctk.x :', start)
    candidate = original[:start]+'hash:\n\t@test -s sctk_write_hash.f90\n'+original[end:]
    changes.append((path, original, candidate))
    template = (qe/'SCTK/src/sctk_write_hash').read_text()
    (qe/'SCTK/src/sctk_write_hash.f90').write_text(template.replace('HASH', pins['sctk']['commit']))
    for path, original, candidate in changes:
        path.write_text(candidate)
    return ''.join(''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
        fromfile=str(path.relative_to(qe)), tofile=str(path.relative_to(qe))))
        for path, before, after in changes)


def build(destination, archive_directory=None):
    if sys.version_info < (3, 12):
        raise RuntimeError('Fresh build requires Python>=3.12 for safe archive extraction')
    root = Path(destination).absolute()
    tools = {name: shutil.which(name) for name in ('gfortran', 'cpp-16', 'clang', 'cmake', 'make')}
    if not all(tools.values()):
        raise RuntimeError('Required installed tools missing: '+str(tools))
    root.mkdir(parents=True)  # Never adopt an existing configured/build tree.
    cache = Path(archive_directory).absolute() if archive_directory else root/'downloads'
    cache.mkdir(parents=True, exist_ok=True)
    pins = json.loads((RESEARCH/'public_response_sources.json').read_text())['sources']
    targets = dict(qe=root/'qe', sctk=root/'qe/SCTK', fox=root/'qe/external/fox',
                   mbd=root/'qe/external/mbd', devxlib=root/'qe/external/devxlib', lapack=root/'lapack')
    started = time.monotonic()
    for name, item in pins.items():
        unpack(archive_file(name, item, cache), targets[name])
        (targets[name]/'SC_DFT_SOURCE_PIN').write_text(json.dumps(item, sort_keys=True)+'\n')
    qe = targets['qe']
    (root/'archive-build-adjustments.patch').write_text(patch_build_rules(qe, pins))
    commands = []

    def run(command, cwd, timeout):
        begin = time.monotonic()
        log = root/f'build-step-{len(commands)+1}.log'
        with log.open('x') as output:
            subprocess.run(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT, check=True, timeout=timeout)
        commands.append(dict(command=list(map(str, command)), cwd=str(cwd),
                             wall_s=time.monotonic()-begin, log_sha256=digest(log)))
        (root/'build-progress.json').write_text(json.dumps(commands, indent=2)+'\n')

    lapack = root/'lapack-build'
    run([tools['cmake'], '-S', str(targets['lapack']), '-B', str(lapack),
         '-DCMAKE_POLICY_VERSION_MINIMUM=3.5', '-DCMAKE_Fortran_COMPILER='+tools['gfortran'],
         '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_Fortran_FLAGS_RELEASE=-O2 -ffp-contract=off -frecursive',
         '-DBUILD_TESTING=OFF', '-DBUILD_SHARED_LIBS=OFF', '-DLAPACKE=OFF', '-DCBLAS=OFF'], root, 120)
    run([tools['cmake'], '--build', str(lapack), '--parallel', '2'], root, 900)
    blas, lap = lapack/'lib/libblas.a', lapack/'lib/liblapack.a'
    run(['./configure', '--disable-parallel', '--disable-openmp',
         'F90='+tools['gfortran'], 'F77='+tools['gfortran'], 'FC='+tools['gfortran'], 'CC='+tools['clang'],
         'FFLAGS=-O2 -ffp-contract=off -fallow-argument-mismatch',
         'F90FLAGS=-O2 -ffp-contract=off -fallow-argument-mismatch -cpp',
         'BLAS_LIBS='+str(blas), 'LAPACK_LIBS='+str(lap)+' '+str(blas)], qe, 120)
    make_inc = qe/'make.inc'
    text, count = re.subn(r'^CPP\s*=.*$', 'CPP = '+tools['cpp-16'], make_inc.read_text(), flags=re.M)
    if count != 1:
        raise ValueError('Configured preprocessor assignment changed')
    make_inc.write_text(text)
    run([tools['make'], '-j2', 'pw', 'ph', 'pp'], qe, 1800)
    run([tools['make'], '-C', 'SCTK/src', '-j2', 'libs-sctk', 'TLDEPS='], qe, 900)
    probe = root/'probe'; probe.mkdir()
    with urlopen(URL, timeout=45) as response:
        geometry_source = response.read(300001)
    (probe/'current_geometry.f90').write_text(extract(geometry_source, unshifted=True))
    run([tools['make'], '-f', str(RESEARCH/'public_response_probe.mk'), 'QE_ROOT='+str(qe),
         'velocity-moment-probe.x'], probe, 120)
    exe = probe/'velocity-moment-probe.x'
    result = dict(wall_s=time.monotonic()-started, tools=tools, commands=commands,
                  executable=str(exe), executable_sha256=digest(exe),
                  source_manifest_sha256=digest(RESEARCH/'public_response_sources.json'),
                  scope='Fresh archive build; numerical/material qualification requires separate execution')
    (root/'build-result.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--archive-directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.destination, args.archive_directory), indent=2))
