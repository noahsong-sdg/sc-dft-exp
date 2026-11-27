"""Bounded macOS execution; public copy of the qualified campaign guard.

The process guard is unchanged from historicalSHAf0f6d3399560497ad22e5391ae780ba9ab3d99058ac629dfd239a727390c16f6.
The CLI adds the120s launch gate and puts receipts in the declared fresh cwd.
"""
import ctypes, hashlib, json, os, resource, shutil, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GIB=1024**3
lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib')
class Scale(ctypes.Structure):
    _fields_=[('numer',ctypes.c_uint32),('denom',ctypes.c_uint32)]
scale=Scale();assert lib.mach_timebase_info(ctypes.byref(scale))==0
lib.mach_continuous_time.restype=ctypes.c_uint64
def clock():return lib.mach_continuous_time()*scale.numer/scale.denom/1e9
def pressure():
    return subprocess.check_output(['/usr/sbin/sysctl','-n','kern.memorystatus_vm_pressure_level'],text=True,timeout=3).strip()
def retained():
    return sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink())
def rss(group):
    rows=subprocess.check_output(['/bin/ps','-axo','pgid=,rss='],text=True,timeout=3)
    return sum(int(b)*1024 for a,b in (x.split() for x in rows.splitlines()) if int(a)==group)
def active_group(group):
    rows=subprocess.check_output(['/bin/ps','-axo','pgid=,stat='],text=True,timeout=3)
    return any(int(a)==group and not b.startswith('Z')
               for a,b in (x.split() for x in rows.splitlines()))
def limits():
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_FSIZE,(256*1024**2,)*2)
def run(label,command,cwd,seconds,env=None):
    if not 0<seconds<3300:raise ValueError('Sub-hour native batch required')
    out=ROOT/'results'/label;out.mkdir(parents=True)
    began=clock();p=None;usage=None;peak=0;error=None;code=None
    try:
        if pressure()!='1':raise RuntimeError('Host memory pressure not normal')
        if shutil.disk_usage(ROOT).free<1536*1024**2:raise RuntimeError('Physical disk reserve')
        with (out/'console.log').open('x') as log:
            p=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,
                start_new_session=True,preexec_fn=limits)
            next_memory=began
            next_disk=began
            while True:
                pid,status,observed=os.wait4(p.pid,os.WNOHANG)
                if pid:
                    code=os.waitstatus_to_exitcode(status);p.returncode=code;usage=observed
                    if code:raise RuntimeError('Native command exit '+str(code))
                    break
                now=clock()
                if now-began>=seconds:raise TimeoutError('Native continuous deadline')
                if now>=next_memory:
                    peak=max(peak,rss(p.pid))
                    if peak>3*GIB:raise RuntimeError('Native group RSS3GiB cap')
                    if pressure()!='1':raise RuntimeError('Host memory pressure not normal')
                    next_memory=now+2
                if now>=next_disk:
                    if retained()>3*GIB:raise RuntimeError('Native workspace3GiB cap')
                    if shutil.disk_usage(ROOT).free<1536*1024**2:raise RuntimeError('Physical disk reserve')
                    next_disk=now+10
                if (out/'console.log').stat().st_size>16*1024**2:raise RuntimeError('Log16MiB cap')
                time.sleep(.1)
        if clock()-began>=seconds:raise TimeoutError('Post-return continuous deadline')
        if usage.ru_maxrss>3*GIB:raise RuntimeError('Native peak RSS3GiB cap')
        if pressure()!='1':raise RuntimeError('Final host memory pressure not normal')
        if retained()>3*GIB:raise RuntimeError('Final native workspace3GiB cap')
        if shutil.disk_usage(ROOT).free<1536*1024**2:raise RuntimeError('Final physical disk reserve')
        if (out/'console.log').stat().st_size>16*1024**2:raise RuntimeError('Final log16MiB cap')
    except BaseException as e:error=type(e).__name__+': '+str(e)
    finally:
        if p is not None:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            if p.returncode is None:
                for _ in range(20):
                    pid,status,observed=os.wait4(p.pid,os.WNOHANG)
                    if pid:
                        code=os.waitstatus_to_exitcode(status);p.returncode=code;usage=observed;break
                    time.sleep(.05)
                if p.returncode is None:
                    try:os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    _,status,usage=os.wait4(p.pid,0)
                    code=os.waitstatus_to_exitcode(status);p.returncode=code
            # The leader may have exited while an ignoring descendant survives.
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            until=time.monotonic()+2
            while active_group(p.pid) and time.monotonic()<until:time.sleep(.05)
            if active_group(p.pid):error=(error or '')+'; owned process group remains active'
        if clock()-began>=seconds:error=error or 'TimeoutError: Final continuous deadline'
        row=dict(status='PASS' if error is None else 'FAIL',error=error,command=command,
            cwd=str(cwd),wall_s=clock()-began,exit=code,
            max_individual_descendant_rss_bytes=None if usage is None else usage.ru_maxrss,
            sampled_peak_group_rss_bytes=peak,macos_ru_maxrss_units='bytes',
            rss_sample_interval_s=2,continuous_deadline_s=seconds,
            guard_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        (out/'receipt.json').write_text(json.dumps(row,indent=2)+'\n')
        print(json.dumps(row),flush=True)
    if error:raise RuntimeError(error)
    return row
def wait_normal(root):
    """Require120s normal observations before a new command; bounded20min watch."""
    began=time.monotonic();normal=None
    while time.monotonic()-began<1200:
        level=pressure();now=time.monotonic()
        normal=(now if normal is None else normal) if level=='1' else None
        quiet=0 if normal is None else now-normal
        (root/'campaign_launch_watch.json').write_text(json.dumps(dict(
            pid=os.getpid(),phase='waiting',pressure=level,normal_seconds=quiet),indent=2)+'\n')
        if quiet>=120:return
        time.sleep(15)
    raise RuntimeError('No normal-pressure launch window in bounded20min watch')


def verify_manifest(root, command):
    manifest=json.loads((root/'run-manifest.json').read_text())
    if manifest['cwd']!=str(root) or manifest['command']!=command:
        raise ValueError('Command/cwd differs from staged run manifest')
    for item in manifest['files']:
        path=Path(item['path'])
        if path.stat().st_size!=item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Changed staged input: '+str(path))


def main(arguments=None):
    global ROOT
    label,seconds,cwd,*argv=sys.argv[1:] if arguments is None else arguments
    ROOT=Path(cwd).absolute()
    if (not ROOT.is_dir() or not argv or not 0<float(seconds)<3300
            or Path(label).name != label or label in ('.','..')):
        raise ValueError('Existing fresh run directory, command and sub-hour deadline required')
    verify_manifest(ROOT,argv)
    # Fresh staging is required; never overwrite a prior watcher or receipt.
    with (ROOT/'campaign_launch_watch.json').open('x') as owner:
        owner.write(json.dumps(dict(pid=os.getpid(),phase='initializing'))+'\n')
    try:
        wait_normal(ROOT)
        verify_manifest(ROOT,argv)
        (ROOT/'campaign_launch_watch.json').write_text(json.dumps(dict(pid=os.getpid(),phase='running'))+'\n')
        result=run(label,argv,ROOT,float(seconds),dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    except BaseException:
        (ROOT/'campaign_launch_watch.json').write_text(json.dumps(dict(pid=os.getpid(),phase='failed'))+'\n')
        raise
    (ROOT/'campaign_launch_watch.json').write_text(json.dumps(dict(pid=os.getpid(),phase='completed'))+'\n')
    return result


if __name__=='__main__':
    main()
