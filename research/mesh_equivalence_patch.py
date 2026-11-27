"""Replace only the owning uniform-mesh lookup and reverse-coverage search."""
import hashlib

SOURCE_SHA256='f2b5dde5691d510b613b3e3acef8bb837c549f03082ff7249429469d23d17812'


def patch(source):
    if hashlib.sha256(source.encode()).hexdigest()!=SOURCE_SHA256:
        raise ValueError('Changed pinned QE tetra source')
    start='  SUBROUTINE opt_tetra_init(';end='END SUBROUTINE opt_tetra_init'
    if source.count(start)!=1 or source.count(end)!=1:
        raise ValueError('Changed opt_tetra_init boundary')
    before,body=source.split(start);body,after=body.split(end)
    use='  USE noncollin_module,   ONLY : colin_mag\n'
    declaration='             equiv(nk1*nk2*nk3) ! index equivalent k in irr-BZ'
    first='  DO ik = 1, nk1 * nk2 * nk3\n     DO jk = 1, nks, kstep\n'
    last='  !\n  !  bring irreducible k-points back to cartesian axis\n'
    if any(body.count(x)!=1 for x in (use,declaration,first,last)):
        raise ValueError('Changed mesh mapping source boundaries')
    left,search=body.split(first);search,right=search.split(last)
    required=('              equiv(ik) = jk','              GOTO 15',
              "'cannot locate  k point'","'cannot remap grid on k-point list'",'20   CONTINUE')
    if any(search.count(x)!=1 for x in required):
        raise ValueError('Changed owning mesh matching or coverage semantics')
    replacement='''  CALL uniform_equivalence_map(nks,nsym,(/nk1,nk2,nk3/),(/k1,k2,k3/), &
       kstep,s,t_rev,time_reversal,colin_mag,xk(:,1:nks),xkg,eps,equiv,missing_grid,missing_input)
  IF(missing_grid/=0) CALL errore('opt_tetra_init','cannot locate  k point',missing_grid)
  IF(missing_input/=0) CALL errore('opt_tetra_init','cannot remap grid on k-point list',missing_input)
'''
    body=left+replacement+last+right
    body=body.replace(use,use+'  USE mesh_equivalence, ONLY : uniform_equivalence_map\n')
    body=body.replace(declaration,'             equiv(nk1*nk2*nk3), missing_grid, missing_input')
    return before+start+body+end+after
