!
! Copyright (C) 2017 Mitsuaki Kawamura
! This file is distributed under the terms of the
! GNU General Public License. See the file `License'
! in the root directory of the present distribution,
! or http://www.gnu.org/copyleft/gpl.txt .
!
MODULE tiled_operator
CONTAINS
SUBROUTINE build_tile(first,last,block,slab_width)
  !
  USE kinds, ONLY : DP
  USE mp_world, ONLY : world_comm
  USE modes, ONLY : nmodes
  USE el_phon, ONLY : elph_nbnd_min, elph_nbnd_max
  !
  USE sctk_val, ONLY : beta, zero_kelvin, bindx, gg, kindx, ngap, &
  &                    omg, Vc, xi, nci, freq_min
  !
  USE sctk_kernel_weight, ONLY : Kweight
  USE cached_phonon, ONLY : Kweight_cached, begin_phonon_context
  USE cached_kel, ONLY : calc_Kel_cached, begin_kel_context
  USE slab_operator, ONLY : ensure_slab
  !
  IMPLICIT NONE
  INTEGER,INTENT(IN) :: first,last,slab_width
  REAL(dp),INTENT(OUT) :: block(ngap(2),first:last,2)
  !
  INTEGER :: igap, ik, ib, jgap, jk, jb, imode, ngap1(2)
  REAL(dp) :: x, xp, om, Kph(2), Kel
  !
  CALL start_clock("build_tile")
  !
  IF(first<1 .OR. last>ngap(1) .OR. last<first) ERROR STOP 'Invalid tile range'
  ngap1=[first,last]
  CALL begin_kel_context()
  CALL begin_phonon_context(beta)

  !
  !
  DO igap = ngap1(1), ngap1(2)
     !
     x = xi(igap,1)
     ik = kindx(igap,1)
     CALL ensure_slab(ik,slab_width)
     ib = bindx(igap,1)
     !
     DO jgap = 1, ngap(2)
        !
        xp = xi(jgap,2)
        jk = kindx(jgap,2)
        jb = bindx(jgap,2)
        !
        ! Electron-phonon
        !
        Kph(1:2) = 0.0_dp
        !
        IF(ALL((/elph_nbnd_min <= ib, ib <= elph_nbnd_max, &
        &        elph_nbnd_min <= jb, jb <= elph_nbnd_max/))) THEN
           !
           DO imode = 1, nmodes
              !
              om = omg(imode,jk,ik)
              IF(om < freq_min) CYCLE
              !
              IF(zero_kelvin) THEN
              Kph(1) = Kph(1) + gg(imode,jb,jk,ib,ik) * Kweight(beta, ABS(x), ABS(xp), om)
              Kph(2) = Kph(2) + gg(imode,jb,jk,ib,ik) * Kweight(beta, ABS(xp), ABS(x), om)
              ELSE
              Kph(1) = Kph(1) + gg(imode,jb,jk,ib,ik) * Kweight_cached(beta, ABS(x), ABS(xp), om)
              Kph(2) = Kph(2) + gg(imode,jb,jk,ib,ik) * Kweight_cached(beta, ABS(xp), ABS(x), om)
              END IF
              !       
           END DO ! imode
           !
        END IF
        !
        ! Coulomb (+ spin-fluctuation)
        !
        Kel = calc_Kel_cached(ABS(x)+ABS(xp),Vc(1:nci,jb,jk,ib,ik))
        !
        block(jgap,igap,1:2) = Kph(1:2) + Kel
        !
     END DO ! jgap
     !
  END DO ! igap
  !
  CALL stop_clock("build_tile")
  !
END SUBROUTINE build_tile
SUBROUTINE gapeq_rhs_tiled(delta,res,tile_width,slab_width)
  !
  USE kinds, ONLY : DP
  USE io_global, ONLY : stdout
  USE mp_world, ONLY : world_comm
  USE mp, ONLY : mp_sum
  USE constants, ONLY : RYTOEV
  USE slab_operator, ONLY : clear_slab
  !
  USE sctk_val, ONLY : beta, zero_kelvin, dk, &
  &                    ngapmax, ngap, xi, xic, Z, dxq
  !
  IMPLICIT NONE
  !
  REAL(dp),INTENT(in)  :: delta(ngapmax,2)
  REAL(dp),INTENT(OUT) :: res(ngapmax,2)
  !
  INTEGER,INTENT(IN) :: tile_width,slab_width
  INTEGER :: igap, ngap1(2), nh(2), ii, first,last
  REAL(dp),ALLOCATABLE :: block(:,:,:)
  REAL(dp) :: chi(ngapmax,2), dosh(2), Kh, dlth(2), xmax(2), tanhd, tanhe
  !
  IF(tile_width<1.OR.slab_width<1) ERROR STOP "Invalid tile/slab width"
  CALL clear_slab()
  CALL start_clock("gapeq_rhs")
  !
  CALL divide(world_comm, ngap(1), ngap1(1), ngap1(2))
  !
  res(1:ngapmax,1:2) = 0.0_dp
  chi(1:ngapmax,1:2) = 0.0_dp
  !
  IF(zero_kelvin) THEN
    !
    DO ii = 1, 2
      !
      DO igap = 1, ngap(ii)
        IF(xi(igap,ii)**2 + delta(igap,ii)**2 > dxq(igap,ii)**2) THEN
          chi(igap,ii) = 1.0_dp
        ELSE
          chi(igap,ii) = 0.0_dp
        END IF
      END DO ! igap
      !
    END DO ! ii
    !
  ELSE
    !
    DO ii = 1, 2
      !
      DO igap = 1, ngap(ii)
        !
        tanhe = TANH(0.5_dp * beta * SQRT(xi(igap,ii)**2 + delta(igap,ii)**2))
        tanhd = TANH(0.5_dp * beta * ABS(dxq(igap,ii)))
        !
        IF(1.0_dp - tanhd * tanhe < 1.0e-10_dp) THEN
          IF(xi(igap,ii)**2 + delta(igap,ii)**2 > dxq(igap,ii)**2) THEN
            chi(igap,ii) = tanhe * (1.0_dp + tanhd) / (1.0_dp + tanhd * tanhe)
          ELSE
            chi(igap,ii) = 0.0_dp
          END IF
        ELSE
          chi(igap,ii) = tanhe * (1.0_dp + tanhd) / (1.0_dp + tanhd * tanhe) &
          &                    * (1.0_dp - tanhd) / (1.0_dp - tanhd * tanhe)
        END IF
        !
      END DO ! igap
      !
    END DO ! ii
    !
  END IF
  !
  DO ii = 1, 2
    chi(1:ngap(ii),ii) = 0.5_dp * dk(1:ngap(ii),ii) * delta(1:ngap(ii),ii) * chi(1:ngap(ii),ii) &
    &                  / SQRT(xi(1:ngap(ii),ii)**2 + delta(1:ngap(ii),ii)**2)
  END DO
  !
  IF(xic > 0) THEN
    !
    DO ii = 1, 2
      nh(ii) = count(xi(1:ngap(ii),ii) > xic)
      dlth(ii) = SUM(delta(1:ngap(ii),ii) / xi(1:ngap(ii),ii), xi(1:ngap(ii),ii) > xic) &
      &        / SUM(1.0_dp / xi(1:ngap(ii),ii)**2,         xi(1:ngap(ii),ii) > xic)
      !
      xmax(ii) = MAXVAL(xi(1:ngap(ii),ii))
      dosh(ii) = SUM(dk(1:ngap(ii),ii), xi(1:ngap(ii),ii) > xic) / (xmax(ii) - xic)
      !
      WRITE(stdout,'(9x,"Extrapol ",i1," : ",e12.5)') ii, dlth(ii) / xic * RYTOEV * 1.0e3_dp
    END DO
    !
  END IF
  DO first=ngap1(1),ngap1(2),tile_width
    last=MIN(first+tile_width-1,ngap1(2))
    ALLOCATE(block(ngap(2),first:last,2))
    CALL build_tile(first,last,block,slab_width)
    CALL dgemv("T",ngap(2),last-first+1,1.0_dp,block(:,:,1),ngap(2), &
      chi(1:ngap(2),2),1,1.0_dp,res(first:last,1),1)
    CALL dgemv("N",ngap(2),last-first+1,1.0_dp,block(:,:,2),ngap(2), &
      chi(first:last,1),1,1.0_dp,res(1:ngap(2),2),1)
    IF(xic>0) THEN
      DO igap=1,ngap(2)
        Kh=SUM(block(igap,first:last,2),xi(first:last,1)>xic)/REAL(nh(1),dp)
        res(igap,2)=res(igap,2)+0.5_dp*dosh(1)*Kh*dlth(1)/xmax(1)
      END DO
      DO igap=first,last
        Kh=SUM(block(1:ngap(2),igap,1),xi(1:ngap(2),2)>xic)/REAL(nh(2),dp)
        res(igap,1)=res(igap,1)+0.5_dp*dosh(2)*Kh*dlth(2)/xmax(2)
      END DO
    END IF
    DEALLOCATE(block)
  END DO
  CALL mp_sum( res, world_comm )
  !
  res(1:ngapmax,1:2) = - res(1:ngapmax,1:2) / (1.0_dp + Z(1:ngapmax,1:2)) - delta(1:ngapmax,1:2)
  !
  CALL stop_clock("gapeq_rhs")
  !
END SUBROUTINE gapeq_rhs_tiled
END MODULE
