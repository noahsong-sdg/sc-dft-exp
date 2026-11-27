! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
program z_qualification
  use kinds, only: dp
  use iso_fortran_env, only: int64
  use sctk_val, only: mf,wmf,nmf,nci,emin
  use sctk_kernel_weight, only: calc_Zsf
  use zsf_reuse, only: calc_Zsf_reused,initialize_zsf_cache,get_zsf_cache_stats
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  integer :: context,i,repeat,checks
  integer(int64) :: hits,misses,resets,collisions,bytes
  real(dp) :: x,a,b,v(10)
  nmf=10;nci=10;emin=1.e-7_dp;checks=0
  allocate(mf(10),wmf(10,2))
  do i=1,10
    mf(i)=.2_dp*real(i,dp)
    wmf(i,:)=1._dp/real(i+1,dp)
    v(i)=(-1._dp)**i/real(i+2,dp)
  end do
  ! One slot guarantees repeated collisions; identical calls must still hit.
  call initialize_zsf_cache(1)
  do context=1,6
    select case(context)
    case(2)
      mf=mf*1.1_dp
    case(3)
      wmf(:,2)=wmf(:,2)*.7_dp
    case(4)
      emin=2.e-5_dp
    case(5)
      nci=5
    case(6)
      nmf=7
    end select
    do i=1,100
      x=real(i-1,dp)*1.e-6_dp
      a=calc_Zsf(x,v(:nci))
      do repeat=1,2
        b=calc_Zsf_reused(x,v(:nci))
        if(.not.ieee_is_finite(a).or..not.ieee_is_finite(b))error stop 'Nonfinite Z kernel'
        if(transfer(a,0_int64)/=transfer(b,0_int64))error stop 'Z cache differs bitwise from upstream'
        checks=checks+1
      end do
    end do
  end do
  call get_zsf_cache_stats(hits,misses,resets,collisions,bytes)
  if(hits<600.or.collisions<100.or.resets<3)error stop 'Z cache contexts/collisions not exercised'
  print '(a,i0)', 'Z_QUALIFICATION_PASS checks=',checks
end program
