! Scalar reproduction of upstream normal-reference branches; no QE dependency.
program current_probe
  use iso_fortran_env, only: dp => real64
  implicit none
  real(dp) :: x, d, gap, beta, a, b, e, released, direct, error
  integer :: case_id
  do case_id=1,3
    select case(case_id)
    case(1)
      x=.4_dp; d=.2_dp; gap=0._dp; beta=2._dp
    case(2)
      x=.4_dp; d=.2_dp; gap=1._dp; beta=2._dp
    case(3)
      x=1._dp; d=2._dp; gap=2._dp; beta=100._dp
    end select
    a=tanh(.5_dp*beta*d)
    b=tanh(.5_dp*beta*x)
    e=tanh(.5_dp*beta*sqrt(x*x+gap*gap))
    if (1._dp-a*b < 1.e-10_dp) then
      if (x*x+gap*gap > d*d) then
        released=b*(1._dp+a)/(1._dp+a*b)
      else
        released=0._dp
      end if
    else
      released=e*(1._dp+a)/(1._dp+a*b)*(1._dp-a)/(1._dp-a*b)
    end if
    direct=.5_dp*(tanh(.5_dp*beta*(x+d))+tanh(.5_dp*beta*(x-d)))
    error=abs(released-direct)
    write(*,'(i0,3(1x,es24.16))') case_id,released,direct,error
    if (case_id==1 .and. error>1.e-14_dp) stop 1
    if (case_id==2 .and. error<.1_dp) stop 2
    if (case_id==3 .and. error<.99_dp) stop 3
  end do
end program current_probe
