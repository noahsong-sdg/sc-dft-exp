"""Streaming checkpoint checks; owning receipts and dependency pins remain required."""
import math
from pathlib import Path
import re
import struct

from fetch_public_response_inputs import digest

HEADER='compact-P-checkpoint-v1; little-endian binary64 Fortran order'


def records(path,count):
    path=Path(path)
    if not 0<path.stat().st_size<=4096:raise ValueError('Invalid P metadata size')
    lines=path.read_text().splitlines()
    if len(lines)!=count:raise ValueError('Stale P metadata records')
    return lines


def integers(line,count):
    fields=line.split()
    if len(fields)!=count or any(re.fullmatch(r'[+-]?[0-9]+',x) is None for x in fields):
        raise ValueError('Invalid P integer fields')
    return list(map(int,fields))


def timings(line,count):
    fields=line.split()
    if len(fields)!=count or any(re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[EeDd][+-]?[0-9]+)?',x) is None for x in fields):
        raise ValueError('Invalid P timing fields')
    values=[float(x.replace('D','E').replace('d','e')) for x in fields]
    if any(not math.isfinite(x) or x<0 for x in values):raise ValueError('Invalid P timings')
    return values


def checkpoint(root,counts,rank,completed,fingerprint,expected_binary_sha256=None):
    root=Path(root)
    if (len(counts)!=2 or min(counts)<=0 or sum(counts)>2147483647 or not 1<=rank<=64
            or not 0<=completed<=counts[0] or completed!=counts[0] and completed%32
            or re.fullmatch('[0-9a-f]{64}',fingerprint) is None):raise ValueError('Invalid P readback context')
    lines=records(root/'compact-p.meta',5)
    if (lines[0]!=HEADER or integers(lines[1],3)!=[*counts,rank]
            or integers(lines[2],1)!=[completed] or lines[3]!=fingerprint):raise ValueError('Different P checkpoint context')
    cpu=timings(lines[4],2);path=root/'compact-p.bin';total=rank*sum(counts)
    if path.stat().st_size!=8*total:raise ValueError('Stale P binary shape')
    # At most 512 KiB of payload; do not materialize rank-by-active matrices.
    with path.open('rb') as stream:
        for at in range(0,total,65536):
            payload=stream.read(8*min(65536,total-at))
            if len(payload)!=8*min(65536,total-at):raise ValueError('Truncated P binary')
            for offset,(value,) in enumerate(struct.iter_unpack('<d',payload)):
                index=at+offset
                if not math.isfinite(value):raise ValueError('Nonfinite P value')
                if completed*rank<=index<counts[0]*rank and value!=0:raise ValueError('Changed unvisited P column')
                if completed==0 and value!=0:raise ValueError('Nonzero initial P checkpoint')
        if stream.read(1):raise ValueError('Trailing P binary')
    if completed==0 and any(cpu):raise ValueError('Nonzero initial P timing')
    sha=digest(path)
    if expected_binary_sha256 is not None and sha!=expected_binary_sha256:raise ValueError('Different accepted P binary')
    return dict(completed_left_rows=completed,cpu_s=cpu,binary_sha256=sha,binary_bytes=8*total,
                all_values_finite=True,unvisited_left_columns_zero=True)


def qualification(root,counts,rank,fingerprint,accepted_partial_sha256):
    """Check replay claim AND exact equality to independently accepted material P."""
    root=Path(root)
    if counts[0]<64:raise ValueError('Qualification needs two full native tiles')
    lines=records(root/'compact-P-qualification.txt',4)
    if (lines[0]!='compact-P-split-qualification-v1; all P bits equal' or lines[1]!=fingerprint
            or integers(lines[2],4)!=[*counts,rank,64]):raise ValueError('Different P qualification context')
    cpu=timings(lines[3],4)
    final=checkpoint(root,counts,rank,64,fingerprint,accepted_partial_sha256)
    split=checkpoint(root/'split',counts,rank,32,fingerprint)
    if final['cpu_s']!=cpu[:2] or any(a>b for a,b in zip(split['cpu_s'],cpu[2:])):
        raise ValueError('Inconsistent P qualification timings')
    return dict(continuous_checkpoint=final,split_checkpoint=split,replay_cpu_s=cpu[2:],
                accepted_partial_P_bitwise_equal=True,complete_P=False,full_space_norm_measured=False)
