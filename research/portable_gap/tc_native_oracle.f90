! Copyright (C) 2017 Mitsuaki Kawamura (native kernel expressions).
! Distributed under GNU GPL; see the released SCTK License.
! Selected full-row/column oracle: no energy or phonon weight caches.
MODULE tc_native_oracle
  USE kinds, ONLY: dp
  USE sctk_val, ONLY: ngapmax,ngap,beta,zero_kelvin,xic,dxq,xi,dk,Z, &
    kindx,bindx,omg,gg,Vc,nci,freq_min,emin
  USE modes, ONLY: nmodes
  USE el_phon, ONLY: elph_nbnd_min,elph_nbnd_max
  USE sctk_kernel_weight, ONLY: Kweight,calc_Kel
  USE slab_operator, ONLY: ensure_slab,clear_slab
  USE mp_world, ONLY: nproc
  USE,INTRINSIC :: ieee_arithmetic, ONLY: ieee_is_finite
  IMPLICIT NONE
CONTAINS
  SUBROUTINE check_native_linear(vector,saved,directory)
    REAL(dp),INTENT(IN) :: vector(ngapmax,2),saved(ngapmax,2)
    CHARACTER(*),INTENT(IN) :: directory
    REAL(dp),ALLOCATABLE :: left_columns(:,:),right_rows(:,:),chi(:,:)
    REAL(dp) :: native(3,2),samples(3,2),pair(2),energy,bound,difference
    INTEGER :: indices(3,2),counts(2),candidates(3),fermi,side,i,j,k,unit
    LOGICAL :: matched
    IF(nproc/=1.OR.zero_kelvin.OR.xic>=0.OR.ANY(dxq/=0)) ERROR STOP 'Oracle requires serial finite-T Q0'
    IF(.NOT.ieee_is_finite(beta).OR.beta<=0.OR.ANY(ngap<1).OR.ANY(ngap>ngapmax)) &
      ERROR STOP 'Invalid native oracle domain'
    IF(.NOT.ieee_is_finite(xic).OR..NOT.ieee_is_finite(emin).OR.emin<=0) &
      ERROR STOP 'Invalid native oracle energy window'
    IF(.NOT.ALL(ieee_is_finite(vector)).OR..NOT.ALL(ieee_is_finite(saved)).OR. &
      .NOT.ALL(ieee_is_finite(Z)).OR.ANY(1.0_dp+Z<=0)) ERROR STOP 'Invalid native oracle state'
    ALLOCATE(left_columns(ngap(2),3),right_rows(3,ngap(1)),chi(ngapmax,2))
    chi=0; indices=0; counts=0
    DO side=1,2
      fermi=0
      DO i=1,ngap(side)
        IF(dk(i,side)>0.AND.ABS(xi(i,side))<emin) THEN
          fermi=i; EXIT
        END IF
      END DO
      IF(fermi==0) ERROR STOP 'No native oracle Fermi support'
      candidates=[1,ngap(side),fermi]
      DO k=1,3
        IF(ANY(indices(:counts(side),side)==candidates(k))) CYCLE
        counts(side)=counts(side)+1; indices(counts(side),side)=candidates(k)
      END DO
      DO i=1,ngap(side)
        energy=ABS(xi(i,side))
        IF(.NOT.ieee_is_finite(energy).OR..NOT.ieee_is_finite(dk(i,side))) &
          ERROR STOP 'Invalid native oracle integration grid'
        IF(energy==0.0_dp) THEN
          chi(i,side)=beta*dk(i,side)*vector(i,side)/4.0_dp
        ELSE
          chi(i,side)=0.5_dp*dk(i,side)*vector(i,side)*TANH(0.5_dp*beta*energy)/energy
        END IF
      END DO
    END DO
    CALL clear_slab()
    DO k=1,counts(1)
      i=indices(k,1)
      CALL ensure_slab(kindx(i,1),1)
      DO j=1,ngap(2)
        CALL native_pair(i,j,pair)
        left_columns(j,k)=pair(1)
      END DO
    END DO
    DO i=1,ngap(1)
      CALL ensure_slab(kindx(i,1),1)
      DO k=1,counts(2)
        j=indices(k,2)
        CALL native_pair(i,j,pair)
        right_rows(k,i)=pair(2)
      END DO
    END DO
    native=0.0_dp
    CALL dgemv('T',ngap(2),counts(1),1.0_dp,left_columns,ngap(2),chi(:,2),1,0.0_dp,native(:,1),1)
    CALL dgemv('N',counts(2),ngap(1),1.0_dp,right_rows,3,chi(:,1),1,0.0_dp,native(:,2),1)
    DO side=1,2
      DO k=1,counts(side)
        i=indices(k,side)
        native(k,side)=-native(k,side)/(1.0_dp+Z(i,side))
        samples(k,side)=saved(i,side)
      END DO
    END DO
    IF(.NOT.ALL(ieee_is_finite(native))) ERROR STOP 'Nonfinite native oracle map'
    bound=2.0e-13_dp+2.0e-12_dp*MAXVAL(ABS(native)); matched=.TRUE.
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/native-linear.meta',STATUS='new')
    WRITE(unit,'(a)') 'native-linear-v1; side index native saved abs-difference frozen-bound'
    DO side=1,2
      DO k=1,counts(side)
        difference=ABS(native(k,side)-samples(k,side))
        WRITE(unit,'(2i10,4es26.17e3)') side,indices(k,side),native(k,side),samples(k,side),difference,bound
        IF(difference>bound) matched=.FALSE.
      END DO
    END DO
    CLOSE(unit)
    IF(.NOT.matched) ERROR STOP 'Native uncached linear oracle mismatch'
  END SUBROUTINE

  SUBROUTINE native_pair(i,j,pair)
    INTEGER,INTENT(IN) :: i,j
    REAL(dp),INTENT(OUT) :: pair(2)
    INTEGER :: ik,jk,ib,jb,mode
    REAL(dp) :: x,xp,frequency,kel
    x=xi(i,1); xp=xi(j,2)
    ik=kindx(i,1); jk=kindx(j,2); ib=bindx(i,1); jb=bindx(j,2)
    pair=0.0_dp
    IF(ALL([elph_nbnd_min<=ib,ib<=elph_nbnd_max,elph_nbnd_min<=jb,jb<=elph_nbnd_max])) THEN
      DO mode=1,nmodes
        frequency=omg(mode,jk,ik)
        IF(frequency<freq_min) CYCLE
        pair(1)=pair(1)+gg(mode,jb,jk,ib,ik)*Kweight(beta,ABS(x),ABS(xp),frequency)
        pair(2)=pair(2)+gg(mode,jb,jk,ib,ik)*Kweight(beta,ABS(xp),ABS(x),frequency)
      END DO
    END IF
    kel=calc_Kel(ABS(x)+ABS(xp),Vc(1:nci,jb,jk,ib,ik))
    pair=pair+kel
  END SUBROUTINE
END MODULE
