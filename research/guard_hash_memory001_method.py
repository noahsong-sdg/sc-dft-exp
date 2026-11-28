import hashlib,json,resource,sys,time
from pathlib import Path
mode=sys.argv[1];m=json.loads(Path(sys.argv[2]).read_text());began=time.monotonic();count=0;size=0
for item in m['files']:
 p=Path(item['path']);assert p.stat().st_size==item['bytes']
 if mode=='whole':value=hashlib.sha256(p.read_bytes()).hexdigest()
 else:
  with p.open('rb') as stream:value=hashlib.file_digest(stream,'sha256').hexdigest()
 assert value==item['sha256'];count+=1;size+=item['bytes']
print(json.dumps(dict(mode=mode,files=count,bytes_verified=size,wall_s=time.monotonic()-began,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,all_digests_match=True)))
