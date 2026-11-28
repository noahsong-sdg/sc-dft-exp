"""Compile the exact public Kweight body; test, never assume, reciprocity."""
import json
import math
from pathlib import Path
import subprocess

from fetch_public_response_inputs import digest

POINTS = ((.0001, .0007, .002), (.0007, .003, .002), (.003, .0001, .002),
          (.0003, .004, .001), (.004, .012, .001), (.012, .0003, .001))


def fixture(source, beta):
    if not math.isfinite(beta) or beta <= 0:
        raise ValueError('Finite positive probe beta required')
    lines = Path(source).read_text().splitlines()
    starts = [i for i, s in enumerate(lines) if s.strip().lower() == 'function kweight(beta,x0,y0,z0) result(wk)']
    ends = [i for i, s in enumerate(lines) if s.strip().lower() == 'end function kweight']
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError('Unrecognized public Kweight body')
    body = '\n'.join(lines[starts[0]:ends[0]+1])
    values = ','.join(f'{x:.17e}_dp' for point in POINTS for x in point)
    return f'''! Generated from pinned public SCTK Kweight.
! Copyright (C) 2017 Mitsuaki Kawamura
! Distributed under the GNU General Public License; see the public SCTK License.
module kinds
 use iso_fortran_env,only:dp=>real64
end module
module sctk_val
 integer::scdft_kernel
 logical::zero_kelvin
end module
program orientation_probe
 use kinds
 use sctk_val
 implicit none
 real(dp)::points(3,{len(POINTS)}),x,y,z,a,b
 integer::i,k,t
 points=reshape([{values}],[3,{len(POINTS)}])
 do k=1,2
  scdft_kernel=k
  do t=0,1
   zero_kelvin=t==1
   do i=1,{len(POINTS)}
    x=points(1,i);y=points(2,i);z=points(3,i)
    a=Kweight({beta:.17e}_dp,x,y,z);b=Kweight({beta:.17e}_dp,y,x,z)
    write(*,'(3(i0,1x),5(es26.17e3,1x))')k,t,i,x,y,z,a,b
   end do
  end do
 end do
contains
{body}
end program
'''


def analyze(text):
    rows = []
    for line in text.splitlines():
        fields = line.split()
        if len(fields) != 8:
            raise ValueError('Invalid orientation output row')
        k, t, i = map(int, fields[:3]); x, y, z, forward, reverse = map(float, fields[3:])
        if (k, t, i) != (1+len(rows)//12, (len(rows)//6)%2, 1+len(rows)%6):
            raise ValueError('Incomplete or reordered orientation output')
        if (x, y, z) != POINTS[i-1] or not all(map(math.isfinite, (forward, reverse))) or reverse == 0:
            raise ValueError('Changed/nonfinite orientation control')
        if k == 1 and forward != reverse:
            raise ValueError('Symmetric kernel1 control failed')
        rows.append(dict(kernel=k, zero_kelvin=bool(t), point=i, x=x, y=y, z=z,
                         forward=forward, reverse=reverse, ratio=forward/reverse,
                         relative_asymmetry=abs(forward-reverse)/max(abs(forward), abs(reverse))))
    if len(rows) != 24:
        raise ValueError('Incomplete orientation output')
    if not all(math.isfinite(row['ratio']) and math.isfinite(row['relative_asymmetry']) for row in rows):
        raise ValueError('Nonfinite orientation ratio')
    cycles = []
    for start in range(0, 24, 3):
        group = rows[start:start+3]
        cycles.append(dict(kernel=group[0]['kernel'], zero_kelvin=group[0]['zero_kelvin'],
                           cycle=1+(start//3)%2, ratio_product=math.prod(r['ratio'] for r in group)))
    return dict(rows=rows, cycles=cycles, full_material_reciprocity_verified=False,
                conditioned_gap_error_bounded=False,
                scope='Exact-source pair controls, not exhaustive material tiles or a full-space certificate.')


def run(root):
    root = Path(root).absolute()
    manifest_path = root/'run-manifest.json'; before = manifest_path.read_bytes()
    m = json.loads(before)
    if m['cwd'] != str(root) or Path.cwd() != root:
        raise ValueError('Different orientation owner')
    if any((root/n).exists() for n in ('orientation.x', 'orientation.txt', 'orientation-result.json')):
        raise ValueError('Fresh orientation outputs required')
    def check():
        for item in m['files']:
            p = Path(item['path'])
            if p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
                raise ValueError('Changed orientation input')
    check()
    if (root/'orientation.f90').read_text() != fixture(m['kernel_source'], m['beta']):
        raise ValueError('Generated source differs from public function')
    subprocess.run([m['compiler'], '-O2', '-ffp-contract=off', '-ffree-line-length-none',
                    '-fcheck=all', 'orientation.f90', '-o', 'orientation.x'], cwd=root, check=True)
    output = subprocess.run([str(root/'orientation.x')], cwd=root, check=True, capture_output=True, text=True)
    (root/'orientation.txt').write_text(output.stdout)
    result = analyze(output.stdout); check()
    if manifest_path.read_bytes() != before:
        raise ValueError('Changed orientation manifest')
    result.update(manifest_sha256=digest(manifest_path), inputs_unchanged=True,
                  output_sha256=digest(root/'orientation.txt'), terminal_guard_pass=False)
    (root/'orientation-result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    run(Path.cwd())
