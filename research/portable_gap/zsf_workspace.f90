! Derived calc_Zsf basis: Copyright (C) 2017 Mitsuaki Kawamura.
! GNU General Public License; see pinned SCTK License / http://www.gnu.org/copyleft/gpl.txt.
! Source: SCTK 47c06501da8ffd574c87469ddd6d5a2814171796, sctk_kernel_weight.f90.
! Exact basis reuse with private serial scratch; live arithmetic is retained.
MODULE zsf_reuse
  USE kinds, ONLY : dp
  USE iso_fortran_env, ONLY : int64
  USE sctk_val, ONLY : mf,nmf,nci,wmf,emin
  IMPLICIT NONE
  PRIVATE
  PUBLIC :: calc_Zsf_reused,initialize_zsf_cache,clear_zsf_cache,get_zsf_cache_stats
  PUBLIC :: get_zsf_workspace_bytes
  INTEGER,PARAMETER :: real_bytes=STORAGE_SIZE(0.0_dp)/8,key_bytes=STORAGE_SIZE(0_int64)/8
  INTEGER,PARAMETER :: valid_bytes=STORAGE_SIZE(.FALSE.)/8
  REAL(dp),ALLOCATABLE,SAVE :: tables(:,:,:)
  INTEGER(int64),ALLOCATABLE,SAVE :: keys(:),context_mf(:)
  LOGICAL,ALLOCATABLE,SAVE :: valid(:)
  REAL(dp),ALLOCATABLE,SAVE :: Vc1(:),mf1(:),cheb(:,:)
  INTEGER,SAVE :: slots=65536,context_nmf=0,context_nci=0
  INTEGER(int64),SAVE :: hits=0,misses=0,context_resets=0,collisions=0,storage_bytes=0
  INTEGER(int64),SAVE :: workspace_bytes=0
CONTAINS
  SUBROUTINE allocate_storage()
    INTEGER(int64) :: bytes,per_entry,cap,scratch_bytes
    INTEGER :: i
    cap=64_int64*1024*1024
    IF(nmf<1.OR.nci<1.OR.slots<1) ERROR STOP 'Zsf cache dimension boundary'
    IF(real_bytes/=8.OR.key_bytes/=8) ERROR STOP 'Zsf cache requires binary64/int64'
    IF(INT(nmf,int64)>cap/key_bytes) ERROR STOP 'Zsf cache nmf boundary'
    IF(INT(nci,int64)>cap/(INT(real_bytes,int64)*nmf)) ERROR STOP 'Zsf cache nci boundary'
    per_entry=INT(real_bytes,int64)*nmf*nci+key_bytes+valid_bytes
    IF(INT(slots,int64)>(cap-INT(key_bytes,int64)*nmf)/per_entry) ERROR STOP 'Zsf cache storage boundary'
    bytes=INT(slots,int64)*per_entry+INT(key_bytes,int64)*nmf
    ! The unchanged cache bound makes these products safe and implies <=96MiB.
    scratch_bytes=INT(real_bytes,int64)*nmf*(INT(nci,int64)+2_int64)
    IF(scratch_bytes>96_int64*1024*1024) ERROR STOP 'Zsf workspace storage boundary'
    IF(ALLOCATED(tables)) DEALLOCATE(tables,keys,valid,context_mf,Vc1,mf1,cheb)
    ALLOCATE(tables(nmf,nci,slots),keys(slots),valid(slots),context_mf(nmf))
    ALLOCATE(Vc1(nmf),mf1(nmf),cheb(nmf,nci))
    valid=.FALSE.
    context_nmf=nmf; context_nci=nci
    DO i=1,nmf
      context_mf(i)=TRANSFER(mf(i),context_mf(i))
    END DO
    storage_bytes=bytes
    workspace_bytes=scratch_bytes
  END SUBROUTINE

  FUNCTION get_zsf_workspace_bytes() RESULT(bytes)
    INTEGER(int64) :: bytes
    bytes=workspace_bytes
  END FUNCTION

  SUBROUTINE initialize_zsf_cache(requested_slots)
    INTEGER,INTENT(IN),OPTIONAL :: requested_slots
    slots=65536
    IF(PRESENT(requested_slots)) slots=requested_slots
    CALL allocate_storage()
    hits=0; misses=0; context_resets=0; collisions=0
  END SUBROUTINE

  SUBROUTINE clear_zsf_cache()
    IF(ALLOCATED(valid)) valid=.FALSE.
  END SUBROUTINE

  SUBROUTINE get_zsf_cache_stats(nhit,nmiss,ncontext,ncollision,nbytes)
    INTEGER(int64),INTENT(OUT) :: nhit,nmiss,ncontext,ncollision,nbytes
    nhit=hits; nmiss=misses; ncontext=context_resets; ncollision=collisions; nbytes=storage_bytes
  END SUBROUTINE

  FUNCTION calc_Zsf_reused(x,Vc0) RESULT(Zsf)
    USE constants, ONLY : pi
    REAL(dp),INTENT(IN) :: x,Vc0(nci)
    REAL(dp) :: Zsf,x0,e0
    INTEGER :: ici,slot,i
    INTEGER(int64) :: bits
    LOGICAL :: changed
    IF(.NOT.ALLOCATED(tables)) CALL initialize_zsf_cache()
    IF(context_nmf/=nmf.OR.context_nci/=nci) THEN
      CALL allocate_storage()
      context_resets=context_resets+1
    ELSE
      changed=.FALSE.
      DO i=1,nmf
        bits=TRANSFER(mf(i),bits)
        IF(bits/=context_mf(i)) changed=.TRUE.
      END DO
      IF(changed) THEN
        CALL clear_zsf_cache()
        DO i=1,nmf
          context_mf(i)=TRANSFER(mf(i),context_mf(i))
        END DO
        context_resets=context_resets+1
      END IF
    END IF
    ! Keep the native conditional, including NaN/signed-zero comparison semantics.
    IF(x < emin) THEN
       e0 = emin
    ELSE
       e0 = x
    END IF
    bits=TRANSFER(e0,bits)
    slot=1+INT(MODULO(IEOR(bits,SHIFTR(bits,32)),INT(slots,int64)))
    IF(valid(slot)) THEN
      IF(keys(slot)==bits) THEN
        hits=hits+1
      ELSE
        collisions=collisions+1
        valid(slot)=.FALSE.
      END IF
    END IF
    IF(.NOT.valid(slot)) THEN
      misses=misses+1
      ! Verbatim native basis construction; no approximation or contraction change.
      mf1(1:nmf) = e0 * mf(1:nmf)
      x0 = COS(pi / REAL(2 * nci, dp))
      mf1(1:nmf) = x0 * (mf1(1:nmf) - 1.0_dp) / (mf1(1:nmf) + 1.0_dp)
      mf1(1:nmf) = ACOS(mf1(1:nmf))
      DO ici = 1, nci
         cheb(1:nmf,ici) = COS(REAL(ici-1,dp) * mf1(1:nmf))
      END DO
      tables(:,:,slot)=cheb
      keys(slot)=bits
      valid(slot)=.TRUE.
    END IF
    Vc1(1:nmf) = MATMUL(tables(1:nmf,1:nci,slot), Vc0(1:nci))
    Zsf = DOT_PRODUCT(wmf(1:nmf,2), Vc1(1:nmf)) / e0
  END FUNCTION
END MODULE
