! Genuine native-state verification and bounded diagnostic output, no restart substitute.
MODULE native_state_io
  USE kinds, ONLY : dp
  USE iso_fortran_env, ONLY : int64
  USE sctk_val, ONLY : ngap, ngapmax, nx, nqbz, emin, Zemin, beta, zero_kelvin, &
       xi0, dx0, xi, delta, dk, dxq, d2xq, kindx, bindx, Z
  USE wvfct, ONLY : nbnd
  USE klist, ONLY : nks
  USE ener, ONLY : ef
  USE, INTRINSIC :: ieee_arithmetic, ONLY : ieee_is_finite
  IMPLICIT NONE
CONTAINS
  SUBROUTINE verify_initialized_state(directory)
    CHARACTER(*), INTENT(IN) :: directory
    INTEGER :: unit, counts(7), expected(7), bytes, side, ios
    INTEGER(int64) :: actual_bytes
    REAL(dp) :: scalars(7), current(7), denominator(2)
    REAL(dp), ALLOCATABLE :: vector(:), matrix(:,:)
    INTEGER, ALLOCATABLE :: indices(:,:)
    LOGICAL :: zero
    CHARACTER(256) :: header, trailing
    IF (ANY(ngap <= 0) .OR. ngapmax /= MAXVAL(ngap)) ERROR STOP 'Invalid native dimensions'
    DO side=1,2
      IF (.NOT. ALL(ieee_is_finite(xi(:ngap(side),side))) .OR. &
          .NOT. ALL(ieee_is_finite(dk(:ngap(side),side)))) ERROR STOP 'Nonfinite native state'
      IF (ANY(kindx(:ngap(side),side)<1) .OR. ANY(kindx(:ngap(side),side)>nqbz) .OR. &
          ANY(bindx(:ngap(side),side)<1) .OR. ANY(bindx(:ngap(side),side)>nbnd)) &
           ERROR STOP 'Invalid native indices'
    END DO
    CALL fermi_averages(denominator)
    expected=[ngap,ngapmax,nx,nqbz,nbnd,nks]
    current=[ef,emin,Zemin,beta,denominator,MAXVAL(ABS(delta))]
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/native-init.meta',STATUS='old')
    READ(unit,'(a)') header
    IF (TRIM(header)/='native-init-v1; arrays are native binary64/int32, Fortran order') &
         ERROR STOP 'Unsupported native state schema'
    READ(unit,*) counts
    READ(unit,*) scalars
    READ(unit,*) zero
    READ(unit,'(a)',IOSTAT=ios) trailing
    CLOSE(unit)
    IF (ios>=0) ERROR STOP 'Trailing native state metadata'
    IF (ANY(counts/=expected)) ERROR STOP 'Native initialization counts differ from reference'
    IF (.NOT. bits1(scalars,current) .OR. (zero.NEQV.zero_kelvin)) &
         ERROR STOP 'Native initialization scalars differ from reference'
    INQUIRE(IOLENGTH=bytes) xi0,dx0,xi,delta,dk,dxq,d2xq,kindx,bindx
    INQUIRE(FILE=TRIM(directory)//'/native-init.bin',SIZE=actual_bytes)
    IF (actual_bytes/=INT(bytes,int64)) ERROR STOP 'Stale native state binary shape'
    ALLOCATE(vector(SIZE(xi0)),matrix(ngapmax,2),indices(ngapmax,2))
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/native-init.bin',STATUS='old', &
         ACCESS='stream',FORM='unformatted')
    READ(unit) vector
    IF (.NOT. bits1(vector,xi0)) ERROR STOP 'Native xi0 differs from reference'
    READ(unit) vector
    IF (.NOT. bits1(vector,dx0)) ERROR STOP 'Native dx0 differs from reference'
    READ(unit) matrix
    IF (.NOT. bits2(matrix,xi)) ERROR STOP 'Native xi differs from reference'
    READ(unit) matrix
    IF (.NOT. bits2(matrix,delta)) ERROR STOP 'Native delta differs from reference'
    READ(unit) matrix
    IF (.NOT. bits2(matrix,dk)) ERROR STOP 'Native dk differs from reference'
    READ(unit) matrix
    IF (.NOT. bits2(matrix,dxq)) ERROR STOP 'Native dxq differs from reference'
    READ(unit) matrix
    IF (.NOT. bits2(matrix,d2xq)) ERROR STOP 'Native d2xq differs from reference'
    READ(unit) indices
    IF (ANY(indices/=kindx)) ERROR STOP 'Native k indices differ from reference'
    READ(unit) indices
    IF (ANY(indices/=bindx)) ERROR STOP 'Native band indices differ from reference'
    CLOSE(unit)
  END SUBROUTINE

  SUBROUTINE fermi_averages(denominator,average)
    REAL(dp), INTENT(OUT) :: denominator(2)
    REAL(dp), INTENT(OUT), OPTIONAL :: average(2)
    INTEGER :: side
    IF (.NOT. ieee_is_finite(emin) .OR. emin<=0.0_dp .OR. &
        .NOT. ieee_is_finite(Zemin) .OR. Zemin<=0.0_dp) ERROR STOP 'Invalid native grid scales'
    DO side=1,2
      denominator(side)=SUM(dk(:,side),ABS(xi(:,side))<emin)
      IF (.NOT. ieee_is_finite(denominator(side)) .OR. denominator(side)<=0.0_dp) &
           ERROR STOP 'Invalid native Fermi normalization'
      IF (PRESENT(average)) average(side)=SUM(Z(:,side)*dk(:,side),ABS(xi(:,side))<emin)/denominator(side)
    END DO
  END SUBROUTINE

  SUBROUTINE freeze_samples(indices,counts)
    INTEGER, INTENT(OUT) :: indices(3,2),counts(2)
    INTEGER :: side, i, candidate(3), cursor, unit
    indices=0; counts=0
    OPEN(NEWUNIT=unit,FILE='z-samples.meta',STATUS='new')
    WRITE(unit,'(a)') 'first, last, first positive-dk ABS(xi)<native emin; deduplicated in that order'
    DO side=1,2
      cursor=0
      DO i=1,ngap(side)
        IF (dk(i,side)>0.0_dp.AND.ABS(xi(i,side))<emin) THEN
          cursor=i
          EXIT
        END IF
      END DO
      IF (cursor==0) ERROR STOP 'No positive-weight Fermi state'
      candidate=[1,ngap(side),cursor]
      DO i=1,3
        IF (ANY(indices(:counts(side),side)==candidate(i))) CYCLE
        counts(side)=counts(side)+1
        indices(counts(side),side)=candidate(i)
        WRITE(unit,'(5i12,2es26.17e3)') side,counts(side),candidate(i), &
             kindx(candidate(i),side),bindx(candidate(i),side),xi(candidate(i),side),dk(candidate(i),side)
      END DO
    END DO
    CLOSE(unit)
  END SUBROUTINE

  SUBROUTINE write_full_Z(temperature)
    INTEGER, INTENT(IN) :: temperature
    INTEGER :: unit, side
    REAL(dp) :: denominator(2),average(2)
    IF (.NOT. ALL(ieee_is_finite(Z)).OR.ANY(1.0_dp+Z<=0.0_dp)) ERROR STOP 'Invalid full Z'
    DO side=1,2
      IF (ANY(Z(ngap(side)+1:ngapmax,side)/=0.0_dp)) ERROR STOP 'Nonzero Z padding'
    END DO
    CALL fermi_averages(denominator,average)
    OPEN(NEWUNIT=unit,FILE='full-z.meta',STATUS='new')
    WRITE(unit,'(a)') 'native-Z-v1; binary64 Fortran order'
    WRITE(unit,*) ngap,ngapmax,nx,temperature
    WRITE(unit,'(8es26.17e3)') beta,emin,Zemin,ef,denominator,average
    WRITE(unit,*) zero_kelvin
    CLOSE(unit)
    OPEN(NEWUNIT=unit,FILE='full-z.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
    WRITE(unit) Z
    CLOSE(unit)
    WRITE(*,'(a,4es26.17e3)') 'CHECKED_FULL_Z_FS ',denominator,average
  END SUBROUTINE

  SUBROUTINE read_full_Z(directory,temperature,full)
    CHARACTER(*), INTENT(IN) :: directory
    INTEGER, INTENT(IN) :: temperature
    REAL(dp), INTENT(OUT) :: full(ngapmax,2)
    INTEGER :: unit, counts(5),side,ios
    INTEGER(int64) :: bytes
    REAL(dp) :: scalars(8),expected(4),denominator(2),average(2)
    LOGICAL :: zero
    CHARACTER(256) :: header,trailing
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/full-z.meta',STATUS='old')
    READ(unit,'(a)') header
    IF (TRIM(header)/='native-Z-v1; binary64 Fortran order') ERROR STOP 'Unsupported Z schema'
    READ(unit,*) counts
    READ(unit,*) scalars
    READ(unit,*) zero
    READ(unit,'(a)',IOSTAT=ios) trailing
    CLOSE(unit)
    IF (ios>=0) ERROR STOP 'Trailing full Z metadata'
    expected=[beta,emin,Zemin,ef]
    IF (ANY(counts/=[ngap,ngapmax,nx,temperature]).OR..NOT.bits1(scalars(:4),expected).OR. &
        (zero.NEQV.zero_kelvin)) ERROR STOP 'Full Z metadata mismatch'
    INQUIRE(FILE=TRIM(directory)//'/full-z.bin',SIZE=bytes)
    IF (bytes/=8_int64*SIZE(full,kind=int64)) ERROR STOP 'Stale full Z binary shape'
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/full-z.bin',STATUS='old',ACCESS='stream',FORM='unformatted')
    READ(unit) full
    CLOSE(unit)
    IF (.NOT.ALL(ieee_is_finite(full)).OR.ANY(1.0_dp+full<=0.0_dp)) ERROR STOP 'Invalid reference full Z'
    CALL fermi_averages(denominator)
    DO side=1,2
      IF (ANY(full(ngap(side)+1:ngapmax,side)/=0.0_dp)) ERROR STOP 'Reference Z padding'
      average(side)=SUM(full(:,side)*dk(:,side),ABS(xi(:,side))<emin)/denominator(side)
    END DO
    IF (.NOT.bits1(scalars(5:8),[denominator,average])) ERROR STOP 'Reference Fermi averages mismatch'
  END SUBROUTINE

  LOGICAL FUNCTION bits1(a,b)
    REAL(dp), INTENT(IN) :: a(:),b(:)
    bits1=SIZE(a)==SIZE(b)
    IF (bits1) bits1=ALL(TRANSFER(a,[0_int64],SIZE(a))==TRANSFER(b,[0_int64],SIZE(b)))
  END FUNCTION
  LOGICAL FUNCTION bits2(a,b)
    REAL(dp), INTENT(IN) :: a(:,:),b(:,:)
    bits2=ALL(SHAPE(a)==SHAPE(b))
    IF (bits2) bits2=ALL(TRANSFER(a,[0_int64],SIZE(a))==TRANSFER(b,[0_int64],SIZE(b)))
  END FUNCTION
END MODULE
