!
! Copyright (C) 2017 Mitsuaki Kawamura
! This file is distributed under the terms of the
! GNU General Public License. See the file `License'
! in the root directory of the present distribution,
! or http://www.gnu.org/copyleft/gpl.txt .
!
MODULE native_rotation
CONTAINS
SUBROUTINE expand_g_v()
  !
  USE kinds, ONLY : DP
  USE io_global, ONLY : stdout
  USE mp_world, ONLY : mpime, nproc, world_comm
  USE mp, ONLY : mp_bcast, mp_max
  USE symm_base, ONLY : nsym
  USE modes, ONLY : nmodes
  USE disp,  ONLY : nqs
  USE el_phon, ONLY : elph_nbnd_min, elph_nbnd_max
  USE sctk_val, ONLY : fbee, gg, gg0, lbee, nqbz, omg, omg0, Vc, Vc0, &
  &                    ngap, kindx, lsf, nci
  !
  USE sctk_cnt_dsp, ONLY : cnt_and_dsp
  !
  IMPLICIT NONE
  !
  INTEGER :: iq, ik, jk, ik2, ii, cnt, dsp, cntmax, ipe, fstk, lstk
  INTEGER,ALLOCATABLE :: qindx(:), nqsym(:,:), iks(:,:,:,:)
  REAL(dp),ALLOCATABLE :: gg1(:,:,:,:,:), Vc1(:,:,:,:,:), omg1(:,:)
  !
  CALL start_clock("expand_g_v")
  !
  CALL divide(world_comm, ngap(1),ik,jk)
  fstk = MINVAL(kindx(ik:jk,1))
  lstk = MAXVAL(kindx(ik:jk,1))
  !
  ALLOCATE(nqsym(nqs, fstk:lstk), iks(2, nsym*2, nqs, fstk:lstk))
  !
  WRITE(stdout,'(9x,"Total RAM for Vc per process : ",e10.2," GB")') &
  &     REAL(nci*lsf,dp)*REAL(lbee-fbee+1,dp)**2*REAL(nqbz,dp)*REAL(lstk-fstk+1,dp)*8.0e-9_dp
  WRITE(stdout,'(9x,"Total RAM for gg per process : ",e10.2," GB")') &
  &     REAL(nmodes,dp)*REAL(elph_nbnd_max-elph_nbnd_min+1,dp)**2 &
  &     *REAL(nqbz,dp)*REAL(lstk-fstk+1,dp)*8.0e-9_dp
  ALLOCATE(Vc(nci*lsf,fbee:lbee,nqbz,fbee:lbee,fstk:lstk), &
  &        gg(nmodes,elph_nbnd_min:elph_nbnd_max,nqbz,elph_nbnd_min:elph_nbnd_max,fstk:lstk), &
  &        omg(nmodes,nqbz,fstk:lstk))
  !
  CALL cnt_and_dsp(nqs,cnt,dsp)
  !
  cntmax = cnt
  CALL mp_max(cntmax, world_comm)
  !
  WRITE(stdout,'(9x,"Total RAM for Vc (temporary) per process : ",e10.2," GB")') &
  &     REAL(nci*lsf,dp)*REAL(lbee-fbee+1,dp)**2*REAL(nqbz,dp)*REAL(cntmax,dp)*8.0e-9_dp
  WRITE(stdout,'(9x,"Total RAM for gg (temporary) per process : ",e10.2," GB")') &
  &     REAL(nmodes,dp)*REAL(elph_nbnd_max-elph_nbnd_min+1,dp)**2 &
  &     *REAL(nqbz,dp)*REAL(cntmax,dp)*8.0e-9_dp
  ALLOCATE(gg1(nmodes,elph_nbnd_min:elph_nbnd_max,elph_nbnd_min:elph_nbnd_max,nqbz,cntmax), &
  &        Vc1(nci*lsf,fbee:lbee,fbee:lbee,nqbz,cntmax), &
  &        omg1(nmodes,cntmax), qindx(cntmax))
  !
  ! #####  Symmetrize  #####
  !
  CALL k_kplusq_sym(fstk,lstk,nqsym,iks)
  !
  ! #####  Communicate  #####
  !
  Vc(1:nci*lsf,fbee:lbee,1:nqbz,fbee:lbee,fstk:lstk) = 0.0_dp
  gg( 1:nmodes,elph_nbnd_min:elph_nbnd_max,1:nqbz,elph_nbnd_min:elph_nbnd_max,fstk:lstk) = 0.0_dp
  omg(1:nmodes,          1:nqbz,          fstk:lstk) = 0.0_dp
  DO ipe = 0, nproc - 1
     !
     Vc1(1:nci*lsf,fbee:lbee,fbee:lbee,1:nqbz,1:cntmax) = 0.0_dp
     gg1( 1:nmodes,elph_nbnd_min:elph_nbnd_max,elph_nbnd_min:elph_nbnd_max,1:nqbz,1:cntmax) = 0.0_dp
     omg1(1:nmodes,                         1:cntmax) = 0.0_dp
     qindx(1:cntmax) = 1
     !
     IF(ipe == mpime) THEN
        !
        Vc1(1:nci*lsf,fbee:lbee,fbee:lbee,1:nqbz,1:cnt) = Vc0(1:nci*lsf,fbee:lbee,fbee:lbee,1:nqbz,1:cnt)
        gg1(     1:nmodes,elph_nbnd_min:elph_nbnd_max,elph_nbnd_min:elph_nbnd_max,1:nqbz,1:cnt) &
        & = gg0( 1:nmodes,elph_nbnd_min:elph_nbnd_max,elph_nbnd_min:elph_nbnd_max,1:nqbz,1:cnt)
        omg1(1:nmodes,                         1:cnt) = omg0(1:nmodes,                         1:cnt)
        !        
        DO iq = 1, cnt
           qindx(iq) = dsp + iq
        END DO
        !
     END IF
     !
     CALL mp_bcast(Vc1,   ipe, world_comm )
     CALL mp_bcast(gg1,   ipe, world_comm )
     CALL mp_bcast(omg1,  ipe, world_comm )
     CALL mp_bcast(qindx, ipe, world_comm )
     !
     !$OMP PARALLEL DEFAULT(NONE) &
     !$OMP & SHARED(nqsym,iks,fstk,lstk,cntmax,qindx,lsf,nmodes,nci, &
     !$OMP &        elph_nbnd_min, elph_nbnd_max, Vc1,Vc,omg1,omg,gg1,gg,fbee,lbee) &
     !$OMP & PRIVATE(ik,jk,iq,ik2,ii)
     !
     !$OMP DO
     DO ik = fstk, lstk
        DO iq = 1, cntmax
           !
           DO ii = 1, nqsym(qindx(iq),ik)
              !
              jk  = iks(1, ii, qindx(iq), ik)
              ik2 = iks(2, ii, qindx(iq), ik)
              !
              Vc(1:nci*lsf,fbee:lbee,jk,fbee:lbee,ik) = Vc(1:nci*lsf,fbee:lbee,jk,fbee:lbee,ik) &
              &                   + Vc1(1:nci*lsf,fbee:lbee,fbee:lbee,ik2,iq)
              !
              gg(    1:nmodes,elph_nbnd_min:elph_nbnd_max,jk,elph_nbnd_min:elph_nbnd_max,ik) &
              & = gg(1:nmodes,elph_nbnd_min:elph_nbnd_max,jk,elph_nbnd_min:elph_nbnd_max,ik) &
              &        + gg1(1:nmodes,elph_nbnd_min:elph_nbnd_max,elph_nbnd_min:elph_nbnd_max,ik2,iq)
              !
              omg(1:nmodes,jk,ik) = omg(1:nmodes,jk,ik) &
              &        + omg1(1:nmodes,iq)
              !
           END DO ! ii
           !
        END DO ! ik2
     END DO ! iq
     !$OMP END DO
     !$OMP END PARALLEL
     !
  END DO ! ipe
  !
  !$OMP PARALLEL DEFAULT(NONE) &
  !$OMP & SHARED(fstk,lstk,lsf,nmodes,nqs,nqbz,Vc,gg,omg,iks,nsym, &
  !$OMP &        elph_nbnd_min,elph_nbnd_max,fbee,lbee,nci) &
  !$OMP & PRIVATE(ik,jk)
  !
  !$OMP DO
  DO ik = fstk, lstk
     DO jk = 1, nqbz
        Vc(1:nci*lsf,fbee:lbee,jk,fbee:lbee,ik) = Vc(1:nci*lsf,fbee:lbee,jk,fbee:lbee,ik) &
        &                         / REAL(count(iks(1,1:nsym*2,1:nqs,ik) == jk), dp)
        gg(    1:nmodes,elph_nbnd_min:elph_nbnd_max,jk,elph_nbnd_min:elph_nbnd_max,ik) &
        & = gg(1:nmodes,elph_nbnd_min:elph_nbnd_max,jk,elph_nbnd_min:elph_nbnd_max,ik) &
        &                                   / REAL(count(iks(1,1:nsym*2,1:nqs,ik) == jk), dp)
        omg(1:nmodes,jk,ik) = omg(1:nmodes,jk,ik) &
        &       / REAL(count(iks(1,1:nsym*2,1:nqs,ik) == jk), dp)
     END DO ! jk
  END DO ! ik
  !$OMP END DO
  !$OMP END PARALLEL
  !
  DEALLOCATE(gg0, Vc0, omg0, gg1, Vc1, omg1, nqsym, iks)
  !
  CALL stop_clock("expand_g_v")
  !
END SUBROUTINE expand_g_v
SUBROUTINE k_kplusq_sym(fstk,lstk,nqsym,iks)
  !
  USE kinds, ONLY : DP
  USE symm_base, ONLY : nsym, s, time_reversal
  USE cell_base, ONLY : at
  USE disp,  ONLY : nq1, nq2, nq3, nqs, x_q
  USE sctk_val, ONLY : nqbz
  !
  IMPLICIT NONE
  !
  INTEGER,INTENT(IN) :: fstk, lstk
  INTEGER,INTENT(OUT) :: nqsym(nqs,fstk:lstk)
  INTEGER,INTENT(OUT) :: iks(2,nsym*2,nqs,fstk:lstk)
  !
  INTEGER :: iq, ik, isym, ikv1(3), ik2, jk2, tsign(2), ntsign, itsign
  REAL(dp) :: kv0(3), kv1(3), rqv(3)
  !
  tsign(1:2) = (/1, -1/)
  if(time_reversal) THEN
     ntsign = 2
  ELSE
     ntsign = 1
  END IF
  !
  nqsym(           1:nqs,fstk:lstk) = 0
  iks(1:2,1:nsym*2,1:nqs,fstk:lstk) = 0
  !
  DO iq = 1, nqs
     !
     rqv(1:3) = MATMUL(x_q(1:3,iq), at(1:3,1:3))
     !
     DO ik = 1, nqbz
        !
        ikv1(1) = (ik - 1) / (nq2*nq3)
        ikv1(2) = (ik - 1 - ikv1(1)*nq2*nq3) / nq3
        ikv1(3) =  ik - 1 - ikv1(1)*nq2*nq3 - ikv1(2)*nq3
        kv0(1:3) = REAL(ikv1(1:3), dp) / REAL((/nq1,nq2,nq3/), dp)
        !
        DO isym = 1, nsym
           !
           DO itsign = 1, ntsign
              !
              kv1(1:3) = MATMUL(REAL(s(1:3,1:3,isym)*tsign(itsign), dp), kv0(1:3)) &
              &        * REAL((/nq1,nq2,nq3/), dp)
              ikv1(1:3) = NINT(kv1(1:3))
              !
              IF(ANY(ABS(kv1(1:3) - REAL(ikv1(1:3), dp)) > 1e-5_dp)) CYCLE
              !
              ikv1(1:3) = MODULO(ikv1(1:3), (/nq1,nq2,nq3/))
              ik2 = 1 + ikv1(3) + ikv1(2)*nq3 + ikv1(1)*nq2*nq3
              !
              IF(ik2 < fstk .OR. lstk < ik2) CYCLE
              !
              kv1(1:3) = MATMUL(REAL(s(1:3,1:3,isym)*tsign(itsign), dp), kv0(1:3) + rqv(1:3))
              kv1(1:3) = kv1(1:3) * REAL((/nq1,nq2,nq3/), dp) - 0.5_dp
              ikv1(1:3) = NINT(kv1(1:3))
              !
              IF(ANY(ABS(kv1(1:3) - REAL(ikv1(1:3), dp)) > 1e-5_dp)) CYCLE
              !
              ikv1(1:3) = MODULO(ikv1(1:3), (/nq1,nq2,nq3/))
              jk2 = 1 + ikv1(3) + ikv1(2)*nq3 + ikv1(1)*nq2*nq3
              !
              nqsym(iq,ik2) = nqsym(iq,ik2) + 1
              iks(1:2,nqsym(iq,ik2),iq,ik2) = (/jk2, ik/)
              !
           END DO ! itsign
           !
        END DO ! isym = 1, nsym
        !
     END DO ! ik
     !
  END DO ! isym
  !
END SUBROUTINE k_kplusq_sym
END MODULE
