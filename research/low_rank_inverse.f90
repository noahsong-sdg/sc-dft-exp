! Compressed inverse diagnostics only; no full-operator condition/error bound.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
module low_rank_inverse
  use iso_fortran_env, only: dp=>real64
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
  private
  public :: inverse_actions
contains
  subroutine inverse_actions(q,u,diagonal,rhs,result,small,singular,model_residual,info)
    real(dp),intent(in) :: q(:,:),u(:,:),diagonal(:),rhs(:,:)
    real(dp),intent(out) :: result(:,:),small(:,:),singular(:),model_residual
    integer,intent(out) :: info
    real(dp),allocatable :: du(:,:),factor(:,:),projected(:,:),svd(:,:),work(:),check(:,:)
    real(dp) :: query(1),unused_left(1,1),unused_right(1,1)
    integer,allocatable :: pivots(:)
    integer :: n,rank,nrhs,j,lwork
    n=size(q,1);rank=size(q,2);nrhs=size(rhs,2)
    if(n<1.or.rank<1.or.rank>n.or.nrhs<1.or.any(shape(u)/=shape(q)).or. &
      size(diagonal)/=n.or.size(rhs,1)/=n.or.any(shape(result)/=shape(rhs)).or. &
      any(shape(small)/=[rank,rank]).or.size(singular)/=rank)error stop 'Invalid inverse dimensions'
    if(.not.all(ieee_is_finite(q)).or..not.all(ieee_is_finite(u)).or. &
      .not.all(ieee_is_finite(diagonal)).or..not.all(ieee_is_finite(rhs))) &
      error stop 'Nonfinite inverse input'
    allocate(du(n,rank),factor(rank,rank),projected(rank,nrhs),svd(rank,rank), &
      pivots(rank),check(n,nrhs))
    result=0;singular=0;model_residual=huge(1._dp)
    do j=1,rank
      du(:,j)=diagonal*u(:,j)
    end do
    call dgemm('T','N',rank,rank,n,-1._dp,q,n,du,n,0._dp,small,rank)
    do j=1,rank
      small(j,j)=small(j,j)+1
    end do
    if(.not.all(ieee_is_finite(small)))error stop 'Nonfinite small inverse matrix'
    svd=small
    call dgesvd('N','N',rank,rank,svd,rank,singular,unused_left,1,unused_right,1,query,-1,info)
    if(info/=0)return
    if(.not.ieee_is_finite(query(1)).or.query(1)<1.or.query(1)>huge(lwork)) &
      error stop 'Invalid inverse SVD workspace'
    lwork=ceiling(query(1));allocate(work(lwork))
    svd=small
    call dgesvd('N','N',rank,rank,svd,rank,singular,unused_left,1,unused_right,1,work,lwork,info)
    if(info/=0)return
    if(.not.all(ieee_is_finite(singular)))error stop 'Nonfinite small singular values'
    do j=1,nrhs
      check(:,j)=diagonal*rhs(:,j)
    end do
    call dgemm('T','N',rank,nrhs,n,1._dp,q,n,check,n,0._dp,projected,rank)
    factor=small
    call dgesv(rank,nrhs,factor,rank,pivots,projected,rank,info)
    if(info/=0)return
    result=rhs
    call dgemm('N','N',n,nrhs,rank,1._dp,u,n,projected,rank,1._dp,result,n)
    ! Independent action of J_model=I-U Q^T D on the returned vectors.
    do j=1,nrhs
      check(:,j)=diagonal*result(:,j)
    end do
    call dgemm('T','N',rank,nrhs,n,1._dp,q,n,check,n,0._dp,projected,rank)
    check=result-rhs
    call dgemm('N','N',n,nrhs,rank,-1._dp,u,n,projected,rank,1._dp,check,n)
    model_residual=maxval(abs(check))
    if(.not.all(ieee_is_finite(result)).or..not.ieee_is_finite(model_residual)) &
      error stop 'Nonfinite inverse output'
  end subroutine
end module
