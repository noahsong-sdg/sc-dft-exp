"""Move calc_dosk ratio work into its existing nonzero-support branches.

This changes no weight expression or branch condition. The native baseline must
still be qualified: an output-preservation hypothesis is not a speedup result.
"""

RATIOS='''           DO ii = 1, 4
              a(ii,1:4) = (xi0(ix) - e(1:4)) / (e(ii) - e(1:4))
           END DO
           !
'''
BRANCHES=(
    '           IF(e(1) < xi0(ix) .AND. xi0(ix) <= e(2)) THEN\n',
    '           ELSE IF(e(2) < xi0(ix) .AND. xi0(ix) <= e(3)) THEN\n',
    '           ELSE IF(e(3) < xi0(ix) .AND. xi0(ix) < e(4)) THEN\n')


def patch(source):
    start='SUBROUTINE calc_dosk(dosd)';end='END SUBROUTINE calc_dosk'
    if source.count(start)!=1 or source.count(end)!=1:
        raise ValueError('Changed owning calc_dosk boundary')
    before,body=source.split(start);body,after=body.split(end)
    if body.count(RATIOS)!=1 or any(body.count(branch)!=1 for branch in BRANCHES):
        raise ValueError('Changed tetrahedron ratio or support branches')
    body=body.replace(RATIOS,'')
    for branch in BRANCHES:
        body=body.replace(branch,branch+RATIOS)
    return before+start+body+end+after
