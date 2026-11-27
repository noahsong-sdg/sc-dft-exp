! Nonlinear solve for A ~= U Q^T; full native validation is required.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
module reduced_nonlinear_core
  use iso_fortran_env, only: dp=>real64
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
  private
  public :: solve_reduced, occupation_ratio
contains
  subroutine occupation_ratio(x,delta,beta,value,derivative)
    real(dp),intent(in) :: x(:),delta(:),beta
    real(dp),intent(out) :: value(:),derivative(:)
    real(dp) :: energy,denominator,t,tail
    integer :: i
    do i=1,size(x)
      energy=hypot(x(i),delta(i))
      if(energy==0)then
        value(i)=0;derivative(i)=1
      else
        denominator=beta/2
        if(x(i)/=0)denominator=tanh(beta*abs(x(i))/2)/abs(x(i))
        t=tanh(beta*energy/2)
        tail=exp(-beta*energy)
        value(i)=delta(i)/energy*t/denominator
        derivative(i)=((x(i)/energy)**2*t/energy &
          +beta/2*(delta(i)/energy)**2*4*tail/(1+tail)**2)/denominator
      end if
    end do
  end subroutine

  subroutine solve_reduced(q,u,x,beta,coeff,delta,iterations,residual,info)
    real(dp),intent(in) :: q(:,:),u(:,:),x(:),beta
    real(dp),intent(inout) :: coeff(:)
    real(dp),intent(out) :: delta(:),residual
    integer,intent(out) :: iterations,info
    real(dp),allocatable :: value(:),derivative(:),du(:,:),g(:),jac(:,:),step(:),trial(:),trial_g(:)
    integer,allocatable :: pivots(:)
    real(dp) :: alpha,trial_norm
    integer :: n,rank,j,search,lapack_info
    n=size(q,1);rank=size(q,2)
    if(n<1.or.rank<1.or.any(shape(u)/=shape(q)).or.size(x)/=n.or.size(delta)/=n.or.size(coeff)/=rank) &
      error stop 'Invalid reduced nonlinear dimensions'
    if(.not.ieee_is_finite(beta).or.beta<=0.or..not.all(ieee_is_finite(q)).or. &
      .not.all(ieee_is_finite(u)).or..not.all(ieee_is_finite(x)).or. &
      .not.all(ieee_is_finite(coeff)))error stop 'Invalid reduced nonlinear inputs'
    allocate(value(n),derivative(n),du(n,rank),g(rank),jac(rank,rank),step(rank), &
      trial(rank),trial_g(rank),pivots(rank))
    info=1
    do iterations=1,40
      call evaluate(coeff,g)
      residual=maxval(abs(g))
      if(.not.ieee_is_finite(residual))then
        info=2;return
      end if
      if(residual<=1.e-13_dp)then
        info=0;return
      end if
      do j=1,rank
        du(:,j)=derivative*u(:,j)
      end do
      call dgemm('T','N',rank,rank,n,1._dp,q,n,du,n,0._dp,jac,rank)
      do j=1,rank
        jac(j,j)=jac(j,j)-1
      end do
      step=-g
      call dgesv(rank,1,jac,rank,pivots,step,rank,lapack_info)
      if(lapack_info/=0.or..not.all(ieee_is_finite(step)))then
        info=3;return
      end if
      alpha=1
      do search=0,16
        trial=coeff+alpha*step
        call evaluate(trial,trial_g)
        trial_norm=maxval(abs(trial_g))
        if(ieee_is_finite(trial_norm).and.trial_norm<(1-1.e-4_dp*alpha)*residual)exit
        alpha=alpha/2
      end do
      if(search>16)then
        info=4;return
      end if
      coeff=trial
    end do
    call evaluate(coeff,g)
    residual=maxval(abs(g))
  contains
    subroutine evaluate(c,out)
      real(dp),intent(in) :: c(:)
      real(dp),intent(out) :: out(:)
      call dgemv('N',n,rank,1._dp,u,n,c,1,0._dp,delta,1)
      call occupation_ratio(x,delta,beta,value,derivative)
      call dgemv('T',n,rank,1._dp,q,n,value,1,0._dp,out,1)
      out=out-c
    end subroutine
  end subroutine
end module
