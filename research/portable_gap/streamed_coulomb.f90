! Original SCTK channel transformations; bounded one-q residency and complete identity.
MODULE streamed_coulomb
  USE kinds, ONLY: dp
  USE iso_c_binding, ONLY: c_ptr,c_double,c_int64_t,c_char,c_int
  USE iso_fortran_env, ONLY: int32,int64,iostat_end
  USE,INTRINSIC :: ieee_arithmetic, ONLY: ieee_is_finite
  IMPLICIT NONE
  PRIVATE
  PUBLIC :: read_pairing_files,read_header,finish_record,record_tag
  PUBLIC :: hash_stream_begin,hash_stream_update,hash_stream_finish
  INTERFACE
    FUNCTION hash_stream_begin(handle) BIND(C) RESULT(status)
      IMPORT c_ptr,c_int
      TYPE(c_ptr),INTENT(OUT) :: handle
      INTEGER(c_int) :: status
    END FUNCTION
    FUNCTION hash_stream_update(handle,values,count) BIND(C) RESULT(status)
      IMPORT c_ptr,c_double,c_int64_t,c_int
      TYPE(c_ptr),VALUE :: handle
      REAL(c_double),INTENT(IN) :: values(*)
      INTEGER(c_int64_t),INTENT(IN) :: count
      INTEGER(c_int) :: status
    END FUNCTION
    FUNCTION hash_stream_finish(handle,digest) BIND(C) RESULT(status)
      IMPORT c_ptr,c_char,c_int
      TYPE(c_ptr),VALUE :: handle
      CHARACTER(c_char),INTENT(OUT) :: digest(64)
      INTEGER(c_int) :: status
    END FUNCTION
  END INTERFACE
CONTAINS
  SUBROUTINE record_tag(unit,bytes)
    INTEGER,INTENT(IN) :: unit,bytes
    INTEGER(int32) :: marker
    INTEGER :: ios
    READ(unit,IOSTAT=ios) marker
    IF(ios/=0) ERROR STOP 'Missing native record marker'
    IF(marker/=bytes) ERROR STOP 'Native record size changed'
  END SUBROUTINE
  SUBROUTINE finish_record(unit,bytes)
    INTEGER,INTENT(IN) :: unit,bytes
    CALL record_tag(unit,bytes)
  END SUBROUTINE
  SUBROUTINE read_header(unit,grid,bands,q,coefficients)
    INTEGER,INTENT(IN) :: unit
    INTEGER,INTENT(OUT) :: grid(3),bands,coefficients
    REAL(dp),INTENT(OUT) :: q(3)
    IF(STORAGE_SIZE(0)/=32.OR.STORAGE_SIZE(0.0_dp)/=64) ERROR STOP 'Unsupported native record ABI'
    CALL record_tag(unit,12); READ(unit) grid; CALL finish_record(unit,12)
    CALL record_tag(unit,4); READ(unit) bands; CALL finish_record(unit,4)
    CALL record_tag(unit,24); READ(unit) q; CALL finish_record(unit,24)
    CALL record_tag(unit,4); READ(unit) coefficients; CALL finish_record(unit,4)
  END SUBROUTINE
  SUBROUTINE read_pairing_files(directory,prefix,nb,nk,nq,nc,grid,bg,xq,channels,lz,expected,values,retained)
    CHARACTER(*),INTENT(IN) :: directory,prefix,expected
    INTEGER,INTENT(IN) :: nb,nk,nq,nc,grid(3),channels
    REAL(dp),INTENT(IN) :: bg(3,3),xq(3,nq)
    LOGICAL,INTENT(IN) :: lz
    REAL(dp),ALLOCATABLE,INTENT(OUT) :: values(:,:,:,:,:)
    CHARACTER(64),INTENT(OUT) :: retained
    REAL(dp),ALLOCATABLE :: block(:,:,:,:)
    TYPE(c_ptr) :: full_hash,retained_hash
    CHARACTER(c_char) :: digest(64)
    CHARACTER(64) :: full_text
    CHARACTER(24) :: suffix
    CHARACTER :: extra
    INTEGER :: iq,unit,ios,got_grid(3),got_nb,got_nc,i,record_bytes
    INTEGER(int64) :: elements
    REAL(dp) :: q(3)
    IF(MIN(nb,nk,nq,nc)<1.OR..NOT.ANY(channels==[1,2])) ERROR STOP 'Invalid native coefficient shape'
    IF(LEN_TRIM(expected)/=64) ERROR STOP 'Missing full transformed identity'
    IF(.NOT.ALL(ieee_is_finite(bg)).OR..NOT.ALL(ieee_is_finite(xq))) ERROR STOP 'Nonfinite q context'
    elements=INT(nc,int64)*nb*nb*nk
    IF(elements>HUGE(record_bytes)/8) ERROR STOP 'Native record too large'
    record_bytes=INT(elements*8)
    ALLOCATE(values(nc,nb,nb,nk,nq),block(nc*channels,nb,nb,nk))
    IF(hash_stream_begin(full_hash)/=0) ERROR STOP 'Full SHA start failed'
    IF(hash_stream_begin(retained_hash)/=0) ERROR STOP 'Retained SHA start failed'
    DO iq=1,nq
      WRITE(suffix,'(i0)') iq
      OPEN(NEWUNIT=unit,FILE=TRIM(directory)//TRIM(prefix)//'.vel'//TRIM(suffix), &
        STATUS='old',ACCESS='stream',FORM='unformatted',IOSTAT=ios)
      IF(ios/=0) ERROR STOP 'Missing native coefficient file'
      CALL read_header(unit,got_grid,got_nb,q,got_nc)
      IF(ANY(got_grid/=grid).OR.got_nb/=nb.OR.got_nc/=nc) ERROR STOP 'Stale native coefficient metadata'
      IF(.NOT.ALL(ieee_is_finite(q))) ERROR STOP 'Nonfinite native q metadata'
      q=MATMUL(bg,q)
      IF(ANY(ABS(q-xq(:,iq))>1.0e-5_dp)) ERROR STOP 'Stale native q context'
      CALL record_tag(unit,record_bytes)
      READ(unit,IOSTAT=ios) block(1:nc,:,:,:)
      IF(ios/=0) ERROR STOP 'Truncated Coulomb channel'
      CALL finish_record(unit,record_bytes)
      IF(channels==2) THEN
        CALL record_tag(unit,record_bytes)
        READ(unit,IOSTAT=ios) block(nc+1:2*nc,:,:,:)
        IF(ios/=0) ERROR STOP 'Truncated spin channel'
        CALL finish_record(unit,record_bytes)
      END IF
      READ(unit,IOSTAT=ios) extra
      IF(ios/=iostat_end) ERROR STOP 'Extra native coefficient bytes'
      CLOSE(unit)
      IF(.NOT.ALL(ieee_is_finite(block))) ERROR STOP 'Nonfinite raw coefficient'
      IF(channels==2) THEN
        block(1:nc,:,:,:)=block(1:nc,:,:,:)+block(nc+1:2*nc,:,:,:)
        IF(lz) block(nc+1:2*nc,:,:,:)=block(nc+1:2*nc,:,:,:)*2.0_dp-block(1:nc,:,:,:)
      END IF
      IF(.NOT.ALL(ieee_is_finite(block))) ERROR STOP 'Nonfinite transformed coefficient'
      IF(hash_stream_update(full_hash,block,INT(SIZE(block),c_int64_t))/=0) ERROR STOP 'Full SHA update failed'
      values(:,:,:,:,iq)=block(1:nc,:,:,:)
      IF(hash_stream_update(retained_hash,values(:,:,:,:,iq),elements)/=0) ERROR STOP 'Retained SHA update failed'
    END DO
    IF(hash_stream_finish(full_hash,digest)/=0) ERROR STOP 'Full SHA finish failed'
    DO i=1,64
      full_text(i:i)=digest(i)
    END DO
    IF(full_text/=expected) ERROR STOP 'Full transformed identity failed'
    IF(hash_stream_finish(retained_hash,digest)/=0) ERROR STOP 'Retained SHA finish failed'
    DO i=1,64
      retained(i:i)=digest(i)
    END DO
    WRITE(*,'(a,1x,a)') 'NATIVE_COEFFICIENT_HASH Vc0',full_text
    WRITE(*,'(a,1x,a)') 'NATIVE_RETAINED_HASH Vc0',retained
  END SUBROUTINE
END MODULE
