! Copyright (C) 2017 Mitsuaki Kawamura
! GPL-2.0-or-later; see ../../licenses/GPL-2.0.txt.
! Unmodified owning routine extracted from pinned SCTK 4bc883e.
SUBROUTINE symm_dosk(dos, dxq_dos,d2xq_dos)
  !
  USE kinds, ONLY : DP
  USE symm_base, ONLY : nsym, s
  USE disp,  ONLY : nq1, nq2, nq3
  USE el_phon, ONLY : elph_nbnd_min, elph_nbnd_max
  USE io_global, ONLY : stdout
  USE sctk_val, ONLY : nqbz, nx, q_fflo
  USE elph_tetra_mod, ONLY : lshift_q
  !
  IMPLICIT NONE
  !
  REAL(dp),INTENT(inout) :: dos(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2), &
  &                     dxq_dos(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2), &
  &                    d2xq_dos(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2)
  !
  INTEGER :: ik, ik2, isym, ikv2(3), nksym(nqbz), ii
  REAL(dp) :: dostmp(nx,elph_nbnd_min:elph_nbnd_max,nqbz), kv1(3), kv2(3), q_fflo2(3), qnorm, &
  &       dxq_dostmp(nx,elph_nbnd_min:elph_nbnd_max,nqbz), d2xq_dostmp(nx,elph_nbnd_min:elph_nbnd_max,nqbz)
  LOGICAL :: lq_sym(nsym)
  !
  ! Only symmetries conserving q_fflo is used.
  !
  lq_sym(1:nsym) = .FALSE.
  DO isym = 1, nsym
     q_fflo2(1:3) = MATMUL(REAL(s(1:3,1:3,isym), dp), q_fflo(1:3))
     q_fflo2(1:3) = q_fflo2(1:3) - q_fflo(1:3)
     qnorm = DOT_PRODUCT(q_fflo2, q_fflo2)
     IF(qnorm < 1.0e-15_dp) lq_sym(isym) = .TRUE.
  END DO
  WRITE(stdout,'(7x,"Number of symmetries conserving q_FFLO : ",i5)') COUNT(lq_sym(1:nsym)) 
  !
  DO ii = 1, 2
    !
    nksym(1:nqbz) = 0
    dostmp(     1:nx,elph_nbnd_min:elph_nbnd_max,1:nqbz) = 0.0_dp
    dxq_dostmp( 1:nx,elph_nbnd_min:elph_nbnd_max,1:nqbz) = 0.0_dp
    d2xq_dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,1:nqbz) = 0.0_dp
    !
    DO ik = 1, nqbz
      !
      ikv2(1) = (ik - 1) / (nq2*nq3)
      ikv2(2) = (ik - 1 - ikv2(1)*nq2*nq3) / nq3
      ikv2(3) =  ik - 1 - ikv2(1)*nq2*nq3 - ikv2(2)*nq3
      kv1(1:3) = (REAL(ikv2(1:3), dp) + 0.5_dp*REAL((ii-1)*lshift_q(1:3), DP)) / REAL((/nq1,nq2,nq3/), dp)
      !
      DO isym = 1, nsym
        !
        IF(.NOT. lq_sym(isym)) CYCLE
        !
        kv2(1:3) = MATMUL(REAL(s(1:3,1:3,isym), dp), kv1(1:3)) * REAL((/nq1,nq2,nq3/), dp)
        kv2(1:3) = kv2(1:3) - 0.5_dp * REAL((ii-1)*lshift_q(1:3),dp)
        ikv2(1:3) = NINT(kv2(1:3))
        !
        IF(ANY(ABS(kv2(1:3) - REAL(ikv2(1:3), dp)) > 1e-8_dp)) CYCLE
        !
        ikv2(1:3) = MODULO(ikv2(1:3), (/nq1,nq2,nq3/))
        ik2 = 1 + ikv2(3) + ikv2(2)*nq3 + ikv2(1)*nq2*nq3
        !
        nksym(ik2) = nksym(ik2) + 1
        !
        dostmp(    1:nx,elph_nbnd_min:elph_nbnd_max,ik2) &
        & = dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,ik2) &
        & + dos(   1:nx,elph_nbnd_min:elph_nbnd_max,ik,ii)
        !
        dxq_dostmp(    1:nx,elph_nbnd_min:elph_nbnd_max,ik2) &
        & = dxq_dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,ik2) &
        & + dxq_dos(   1:nx,elph_nbnd_min:elph_nbnd_max,ik,ii)
        !
        d2xq_dostmp(    1:nx,elph_nbnd_min:elph_nbnd_max,ik2) &
        & = d2xq_dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,ik2) &
        & + d2xq_dos(   1:nx,elph_nbnd_min:elph_nbnd_max,ik,ii)
        !
      END DO
      !
    END DO
    !
    DO ik = 1, nqbz
      dos(       1:nx,elph_nbnd_min:elph_nbnd_max,ik,ii) &
      & = dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,ik) / REAL(nksym(ik), dp)
      !
      dxq_dos(       1:nx,elph_nbnd_min:elph_nbnd_max,ik,ii) &
      & = dxq_dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,ik) / REAL(nksym(ik), dp)
      !
      d2xq_dos(       1:nx,elph_nbnd_min:elph_nbnd_max,ik,ii) &
      & = d2xq_dostmp(1:nx,elph_nbnd_min:elph_nbnd_max,ik) / REAL(nksym(ik), dp)
    END DO
    !
  END DO ! ii
  !
END SUBROUTINE symm_dosk
