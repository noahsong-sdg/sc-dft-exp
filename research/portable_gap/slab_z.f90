!
! Copyright (C) 2017 Mitsuaki Kawamura
! This file is distributed under the terms of the
! GNU General Public License. See the file `License'
! in the root directory of the present distribution,
! or http://www.gnu.org/copyleft/gpl.txt .
!
MODULE slab_z
CONTAINS
SUBROUTINE make_Z_slab(width)
  !
  USE kinds, ONLY : DP
  USE iso_fortran_env, ONLY : int64
  USE io_global, ONLY : stdout
  USE mp_world, ONLY : mpime, world_comm
  USE mp, ONLY : mp_sum
  USE modes, ONLY : nmodes
  USE el_phon, ONLY : elph_nbnd_min, elph_nbnd_max
  !
  USE sctk_val, ONLY : beta, bindx, dk, emin, gg, lz_coulomb, freq_min, &
  &                    kindx, ngapmax, ngap, omg, xi, Z, lsf, Vc, nci
  !
  USE sctk_kernel_weight, ONLY : Zweight
  USE zsf_reuse, ONLY : calc_Zsf => calc_Zsf_reused
  !
  USE slab_operator, ONLY : ensure_slab, clear_slab
  IMPLICIT NONE
  INTEGER,INTENT(IN) :: width
  !
  INTEGER :: igap, ik, ib, jgap, jk, jb, imode, ngap1(2), ii
  REAL(dp) :: x, xp, om, zave(2), ave(2), Z0
  !
  IF(width<1) ERROR STOP "Invalid slab width"
  CALL clear_slab()
  CALL start_clock("make_Z")
  !
  IF(.NOT. ALLOCATED(Z)) ALLOCATE(Z(ngapmax,2))
  Z(1:ngapmax,1:2) = 0.0_dp
  !
  CALL divide(world_comm, ngap(1), ngap1(1), ngap1(2))
  !
  !
  DO igap = ngap1(1), ngap1(2)
     !
     x = xi(igap,1)
     ik = kindx(igap,1)
     CALL ensure_slab(ik,width)
     ib = bindx(igap,1)
     !
     DO jgap = 1, ngap(2)
        !
        xp = xi(jgap,2)
        jk = kindx(jgap,2)
        jb = bindx(jgap,2)
        !
        ! Spin-fluctuation renormalization
        !
        IF(lsf==2 .OR. lz_coulomb) THEN
           !
           IF(lsf == 2) THEN
              Z0 =   calc_Zsf(ABS(x)+ABS(xp), Vc(nci+1:nci*2,jb,jk,ib,ik))
           ELSE
              Z0 = - calc_Zsf(ABS(x)+ABS(xp), Vc(1:nci,jb,jk,ib,ik))
           END IF
           !
           Z(igap,1) = Z(igap,1) + dk(jgap,2) * Z0
           Z(jgap,2) = Z(jgap,2) + dk(igap,1) * Z0
           !
        END IF
        !      
        ! Electron-phonon renormalization
        !
        IF(     elph_nbnd_min <= ib .AND. ib <= elph_nbnd_max &
        & .AND. elph_nbnd_min <= jb .AND. jb <= elph_nbnd_max) THEN
           !
           DO imode = 1, nmodes
              !
              om = omg(imode,jk,ik)
              IF(om < freq_min) CYCLE
              !
              Z(igap,1) = Z(igap,1) - dk(jgap,2) * gg(imode,jb,jk,ib,ik) &
              &                     * Zweight(beta, ABS(x), ABS(xp), om)
              Z(jgap,2) = Z(jgap,2) - dk(igap,1) * gg(imode,jb,jk,ib,ik) &
              &                     * Zweight(beta, ABS(xp), ABS(x), om)
              !
           END DO ! imode
           !
        END IF ! (elph_nbnd_min <= jb .AND. jb <= elph_nbnd_max)
        !
     END DO ! jgap
     IF(MOD(igap,256)==0 .OR. igap==ngap1(2)) THEN
       WRITE(stdout,*) 'Z_COMPLETED_LEFT_PAIRS ',igap,ngap(1),INT(igap,int64)*INT(ngap(2),int64)
       FLUSH(stdout)
     END IF
     !
  END DO ! igap
  !
  !
  CALL mp_sum( Z, world_comm )
  !
  DO ii = 1, 2
    zave(ii) = SUM(Z(1:ngapmax,ii) * dk(1:ngapmax,ii), ABS(xi(1:ngapmax,ii)) < emin)
    ave(ii) = SUM(dk(1:ngapmax,ii), ABS(xi(1:ngapmax,ii)) < emin)
  END DO
  !
  zave(1:2) = zave(1:2) / ave(1:2)
  !
  IF(mpime == 0)  WRITE(*,'(7x,"Averaged Z_{FS} : ",2(e12.5,2x))') zave(1:2)
  !
  CALL stop_clock("make_Z")
  !
END SUBROUTINE make_Z_slab
END MODULE
