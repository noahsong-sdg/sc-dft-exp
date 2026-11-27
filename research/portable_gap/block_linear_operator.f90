! Exact finite-T, Q=0 derivative of the native gap map F(delta)=R(delta)+delta.
! Pair kernels and DGEMV order are inherited from the qualified tiled_operator.
! Derived from SCTK sctk_gapeq_rhs.f90, Copyright (C) 2017 Mitsuaki Kawamura.
! Distributed under the GNU GPL; see the pinned SCTK License.
MODULE block_linear_operator
  IMPLICIT NONE
CONTAINS
  SUBROUTINE linear_weights(weights)
    USE kinds, ONLY : dp
    USE mp_world, ONLY : nproc
    USE sctk_val, ONLY : ngapmax,ngap,beta,zero_kelvin,xi,dk,dxq,xic,Z
    USE,INTRINSIC :: ieee_arithmetic, ONLY : ieee_is_finite
    IMPLICIT NONE
    REAL(dp),INTENT(OUT) :: weights(ngapmax,2)
    REAL(dp) :: energy
    INTEGER :: side,i
    IF(nproc/=1) ERROR STOP 'Linear block requires the qualified serial path'
    IF(zero_kelvin.OR..NOT.ieee_is_finite(beta).OR.beta<=0.0_dp) &
      ERROR STOP 'Linear block requires finite positive temperature'
    IF(.NOT.ieee_is_finite(xic).OR.xic>=0.0_dp.OR.ANY(dxq/=0.0_dp)) &
      ERROR STOP 'Linear block requires Q=0 and xic<0'
    IF(ANY(ngap<1).OR.ANY(ngap>ngapmax)) ERROR STOP 'Invalid linear block state counts'
    IF(.NOT.ALL(ieee_is_finite(xi)).OR..NOT.ALL(ieee_is_finite(dk)).OR. &
       .NOT.ALL(ieee_is_finite(Z)).OR.ANY(1.0_dp+Z<=0.0_dp)) &
      ERROR STOP 'Invalid linear block state or renormalization'
    weights=0.0_dp
    DO side=1,2
      DO i=1,ngap(side)
        energy=ABS(xi(i,side))
        IF(energy==0.0_dp) THEN
          weights(i,side)=0.25_dp*beta*dk(i,side)
        ELSE
          weights(i,side)=0.5_dp*dk(i,side)*TANH(0.5_dp*beta*energy)/energy
        END IF
      END DO
    END DO
    IF(.NOT.ALL(ieee_is_finite(weights))) ERROR STOP 'Nonfinite linear block weights'
  END SUBROUTINE

  SUBROUTINE apply_linear_block(vectors,images,nvec,tile_width,slab_width)
    USE kinds, ONLY : dp
    USE sctk_val, ONLY : ngapmax,ngap,Z
    USE tiled_operator, ONLY : build_tile
    USE slab_operator, ONLY : clear_slab
    USE,INTRINSIC :: ieee_arithmetic, ONLY : ieee_is_finite
    IMPLICIT NONE
    INTEGER,INTENT(IN) :: nvec,tile_width,slab_width
    REAL(dp),INTENT(IN) :: vectors(ngapmax,2,nvec)
    REAL(dp),INTENT(OUT) :: images(ngapmax,2,nvec)
    REAL(dp),ALLOCATABLE :: block(:,:,:),chi(:,:,:),weights(:,:)
    INTEGER :: first,last,vector,side
    IF(nvec<1.OR.tile_width<1.OR.slab_width<1) ERROR STOP 'Invalid linear block dimensions'
    IF(.NOT.ALL(ieee_is_finite(vectors))) ERROR STOP 'Nonfinite trial block'
    ALLOCATE(weights(ngapmax,2),chi(ngapmax,2,nvec))
    CALL linear_weights(weights)
    DO side=1,2
      IF(ANY(vectors(ngap(side)+1:ngapmax,side,:)/=0.0_dp)) &
        ERROR STOP 'Nonzero trial block padding'
    END DO
    DO vector=1,nvec
      chi(:,:,vector)=weights*vectors(:,:,vector)
    END DO
    images=0.0_dp
    CALL clear_slab()
    DO first=1,ngap(1),tile_width
      last=MIN(first+tile_width-1,ngap(1))
      ALLOCATE(block(ngap(2),first:last,2))
      CALL build_tile(first,last,block,slab_width)
      DO vector=1,nvec
        CALL dgemv('T',ngap(2),last-first+1,1.0_dp,block(:,:,1),ngap(2), &
          chi(1:ngap(2),2,vector),1,1.0_dp,images(first:last,1,vector),1)
        CALL dgemv('N',ngap(2),last-first+1,1.0_dp,block(:,:,2),ngap(2), &
          chi(first:last,1,vector),1,1.0_dp,images(1:ngap(2),2,vector),1)
      END DO
      DEALLOCATE(block)
    END DO
    DO vector=1,nvec
      images(:,:,vector)=-images(:,:,vector)/(1.0_dp+Z)
    END DO
    IF(.NOT.ALL(ieee_is_finite(images))) ERROR STOP 'Nonfinite linear block image'
  END SUBROUTINE
END MODULE
