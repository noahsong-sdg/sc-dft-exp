MODULE saved_coulomb
  USE kinds, ONLY: dp
  USE iso_c_binding, ONLY: c_char,c_int64_t
  USE streamed_coulomb, ONLY: read_pairing_files,read_header
  USE native_coefficients, ONLY: hash_array_checked
  IMPLICIT NONE
CONTAINS
  SUBROUTINE read_saved_coulomb()
    USE wvfct, ONLY: nbnd
    USE disp, ONLY: nq1,nq2,nq3,x_q,nqs
    USE cell_base, ONLY: bg
    USE mp_world, ONLY: nproc
    USE io_files, ONLY: prefix,tmp_dir
    USE sctk_val, ONLY: nqbz,Vc0,lsf,nci,lz_coulomb
    INTEGER :: unit,grid(3),bands
    REAL(dp) :: q(3)
    CHARACTER(64) :: retained
    IF(nproc/=1.OR.ALLOCATED(Vc0)) ERROR STOP 'Saved Coulomb requires fresh serial residency'
    OPEN(NEWUNIT=unit,FILE=TRIM(tmp_dir)//TRIM(prefix)//'.vel1', &
      STATUS='old',ACCESS='stream',FORM='unformatted')
    CALL read_header(unit,grid,bands,q,nci)
    CLOSE(unit)
    ! These are the pinned original interaction dimensions, independent of nx/nmf.
    IF(nbnd/=26.OR.nqbz/=512.OR.nqs/=26.OR.nci/=10) ERROR STOP 'Registered Coulomb dimensions changed'
    CALL read_pairing_files(TRIM(tmp_dir),TRIM(prefix),nbnd,nqbz,nqs,nci,[nq1,nq2,nq3], &
      bg,x_q,lsf,lz_coulomb,'7b304e91a264759dc1e94b9e68d8c2e5c4b3d6094cf553f8619260fce0ecb6fe',Vc0,retained)
  END SUBROUTINE
  SUBROUTINE check_saved_coefficients()
    USE sctk_val, ONLY: gg0,omg0,Vc0,nci
    USE,INTRINSIC :: ieee_arithmetic, ONLY: ieee_is_finite
    IF(.NOT.ALL(ieee_is_finite(gg0)).OR..NOT.ALL(ieee_is_finite(omg0)).OR. &
      .NOT.ALL(ieee_is_finite(Vc0))) ERROR STOP 'Nonfinite native compact coefficients'
    IF(SIZE(Vc0,1)/=nci) ERROR STOP 'Pairing residency changed'
    CALL check_hash(gg0,SIZE(gg0,KIND=c_int64_t),'gg0', &
      'ba64fb182bd0a2fbeb2db7f3689aac7708ce1caba2467a806d366fce012d0831')
    CALL check_hash(omg0,SIZE(omg0,KIND=c_int64_t),'omg0', &
      '23e776d13c56d881f367b91db7f9a4c92584945f6d24a19c629723f3920490f5')
  END SUBROUTINE
  SUBROUTINE check_hash(values,count,label,expected)
    INTEGER(c_int64_t),INTENT(IN) :: count
    REAL(dp),INTENT(IN) :: values(*)
    CHARACTER(*),INTENT(IN) :: label,expected
    CHARACTER(c_char) :: digest(64)
    CHARACTER(64) :: text
    INTEGER :: i
    IF(hash_array_checked(values,count,digest)/=0) ERROR STOP 'Native coefficient hashing failed'
    DO i=1,64
      text(i:i)=digest(i)
    END DO
    IF(text/=expected) ERROR STOP 'Native coefficient identity failed'
    WRITE(*,'(a,1x,a,1x,a)') 'NATIVE_COEFFICIENT_HASH',label,text
  END SUBROUTINE
  SUBROUTINE release_kernel_data()
    USE sctk_val, ONLY: Vc0,gg0,omg0
    USE slab_operator, ONLY: clear_slab
    CALL clear_slab()
    IF(ALLOCATED(Vc0)) DEALLOCATE(Vc0)
    IF(ALLOCATED(gg0)) DEALLOCATE(gg0)
    IF(ALLOCATED(omg0)) DEALLOCATE(omg0)
  END SUBROUTINE
END MODULE
