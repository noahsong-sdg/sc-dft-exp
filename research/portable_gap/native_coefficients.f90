MODULE native_coefficients
  USE, INTRINSIC :: iso_c_binding, ONLY : c_double, c_int64_t, c_char, c_int
  IMPLICIT NONE
  INTERFACE
    FUNCTION hash_array_checked(values, count, digest) BIND(C) RESULT(status)
      IMPORT c_double, c_int64_t, c_char, c_int
      REAL(c_double), INTENT(IN) :: values(*)
      INTEGER(c_int64_t), INTENT(IN) :: count
      CHARACTER(KIND=c_char), INTENT(OUT) :: digest(64)
      INTEGER(c_int) :: status
    END FUNCTION
  END INTERFACE
CONTAINS
  SUBROUTINE check_compact_coefficients()
    USE sctk_val, ONLY : gg0, omg0, Vc0
    USE, INTRINSIC :: ieee_arithmetic, ONLY : ieee_is_finite
    CHARACTER(KIND=c_char) :: digest(64)
    CHARACTER(64) :: text
    INTEGER :: i
    IF (.NOT. ALL(ieee_is_finite(gg0)) .OR. .NOT. ALL(ieee_is_finite(omg0)) .OR. &
        .NOT. ALL(ieee_is_finite(Vc0))) ERROR STOP 'Nonfinite native compact coefficients'
    IF (hash_array_checked(gg0, SIZE(gg0,KIND=c_int64_t), digest) /= 0) ERROR STOP 'gg0 hashing failed'
    DO i=1,64
      text(i:i)=digest(i)
    END DO
    WRITE(*,'(a,1x,a)') 'NATIVE_COEFFICIENT_HASH gg0', text
    IF (text /= 'ba64fb182bd0a2fbeb2db7f3689aac7708ce1caba2467a806d366fce012d0831') ERROR STOP 'gg0 identity failed'
    IF (hash_array_checked(omg0, SIZE(omg0,KIND=c_int64_t), digest) /= 0) ERROR STOP 'omg0 hashing failed'
    DO i=1,64
      text(i:i)=digest(i)
    END DO
    WRITE(*,'(a,1x,a)') 'NATIVE_COEFFICIENT_HASH omg0', text
    IF (text /= '23e776d13c56d881f367b91db7f9a4c92584945f6d24a19c629723f3920490f5') ERROR STOP 'omg0 identity failed'
    IF (hash_array_checked(Vc0, SIZE(Vc0,KIND=c_int64_t), digest) /= 0) ERROR STOP 'Vc0 hashing failed'
    DO i=1,64
      text(i:i)=digest(i)
    END DO
    WRITE(*,'(a,1x,a)') 'NATIVE_COEFFICIENT_HASH Vc0', text
    IF (text /= '7b304e91a264759dc1e94b9e68d8c2e5c4b3d6094cf553f8619260fce0ecb6fe') ERROR STOP 'Vc0 identity failed'
    FLUSH(6)
  END SUBROUTINE
END MODULE
