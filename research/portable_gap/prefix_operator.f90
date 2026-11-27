! Native pair arithmetic with a bounded left interval and one call substitution.
! Derived from SCTK sctk_z.f90, Copyright (C) 2017 Mitsuaki Kawamura.
! Distributed under GNU GPL; see the pinned SCTK License.
MODULE prefix_operator
CONTAINS
SUBROUTINE accumulate_Z_block(first,last,reuse)
  USE kinds, ONLY : DP
  USE modes, ONLY : nmodes
  USE el_phon, ONLY : elph_nbnd_min, elph_nbnd_max
  USE sctk_val, ONLY : beta, bindx, dk, gg, lz_coulomb, freq_min, &
       kindx, ngap, omg, xi, Z, lsf, Vc, nci
  USE sctk_kernel_weight, ONLY : Zweight, calc_Zsf
  USE zsf_reuse, ONLY : calc_Zsf_reused
  USE slab_operator, ONLY : ensure_slab
  IMPLICIT NONE
  INTEGER,INTENT(IN) :: first,last
  LOGICAL,INTENT(IN) :: reuse
  INTEGER :: igap,ik,ib,jgap,jk,jb,imode
  REAL(dp) :: x,xp,om,Z0
  IF(first<1.OR.last<first.OR.last>ngap(1)) ERROR STOP 'Invalid registered prefix interval'
  IF(.NOT.ALLOCATED(Z)) ERROR STOP 'Prefix accumulation requires initialized Z'
  DO igap=first,last
     x = xi(igap,1)
     ik = kindx(igap,1)
     CALL ensure_slab(ik,1)
     ib = bindx(igap,1)
     DO jgap = 1, ngap(2)
        xp = xi(jgap,2)
        jk = kindx(jgap,2)
        jb = bindx(jgap,2)
        IF(lsf==2 .OR. lz_coulomb) THEN
           IF(lsf == 2) THEN
              IF(reuse) THEN
                Z0 =   calc_Zsf_reused(ABS(x)+ABS(xp), Vc(nci+1:nci*2,jb,jk,ib,ik))
              ELSE
                Z0 =   calc_Zsf(ABS(x)+ABS(xp), Vc(nci+1:nci*2,jb,jk,ib,ik))
              END IF
           ELSE
              IF(reuse) THEN
                Z0 = - calc_Zsf_reused(ABS(x)+ABS(xp), Vc(1:nci,jb,jk,ib,ik))
              ELSE
                Z0 = - calc_Zsf(ABS(x)+ABS(xp), Vc(1:nci,jb,jk,ib,ik))
              END IF
           END IF
           Z(igap,1) = Z(igap,1) + dk(jgap,2) * Z0
           Z(jgap,2) = Z(jgap,2) + dk(igap,1) * Z0
        END IF
        IF(     elph_nbnd_min <= ib .AND. ib <= elph_nbnd_max &
        & .AND. elph_nbnd_min <= jb .AND. jb <= elph_nbnd_max) THEN
           DO imode = 1, nmodes
              om = omg(imode,jk,ik)
              IF(om < freq_min) CYCLE
              Z(igap,1) = Z(igap,1) - dk(jgap,2) * gg(imode,jb,jk,ib,ik) &
              &                     * Zweight(beta, ABS(x), ABS(xp), om)
              Z(jgap,2) = Z(jgap,2) - dk(igap,1) * gg(imode,jb,jk,ib,ik) &
              &                     * Zweight(beta, ABS(xp), ABS(x), om)
           END DO
        END IF
     END DO
  END DO
END SUBROUTINE
END MODULE
