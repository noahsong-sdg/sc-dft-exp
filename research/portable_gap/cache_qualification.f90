! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
program cache_qualification
  use kinds,only:dp
  use sctk_val,only:mf,wmf,nmf,nci,zero_kelvin,scdft_kernel
  use sctk_kernel_weight,only:Kweight,calc_Kel
  use cached_phonon,only:begin_phonon_context,Kweight_cached,phonon_hits,phonon_slot
  use cached_kel,only:begin_kel_context,calc_Kel_cached,hits,kel_slot
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  real(dp)::b,x,y,z,a,c,v(4)
  integer::i,j,k,t,checks,slots(65536)
  logical::found
  checks=0
  nmf=5;nci=4
  allocate(mf(nmf),wmf(nmf,1))
  mf=[.1_dp,.5_dp,1._dp,2._dp,10._dp];wmf(:,1)=[.1_dp,.2_dp,.3_dp,.2_dp,.2_dp]
  v=[.2_dp,-.1_dp,.03_dp,.004_dp]
  do t=1,3
    if(t==2)mf=mf*1.1_dp
    if(t==3)wmf=wmf*1.2_dp
    call begin_kel_context()
    do i=1,30
      x=real(i,dp)/37
      a=calc_Kel(x,v);c=calc_Kel_cached(x,v)
      call same(a,c)
      c=calc_Kel_cached(x,v);call same(a,c)
    end do
    if(hits<30)error stop 'Kel cache not exercised'
  end do
  ! Search an actual collision, then require first-key recomputation.
  slots=0;found=.false.
  do i=1,65536
    x=real(i,dp)/65537;k=kel_slot(x)
    if(slots(k)/=0)then
      y=real(slots(k),dp)/65537
      a=calc_Kel_cached(y,v);c=calc_Kel_cached(x,v)
      a=calc_Kel_cached(y,v);call same(a,calc_Kel(y,v))
      found=.true.;exit
    end if
    slots(k)=i
  end do
  if(.not.found)error stop 'No Kel collision exercised'
  do k=1,2
    scdft_kernel=k
    do j=0,1
      zero_kelvin=j==1
      do t=1,3
        b=real(t,dp)*1000
        call begin_phonon_context(b)
        do i=1,30
          x=real(i,dp)/10000;y=x*1.7_dp;z=.002_dp
          a=Kweight(b,x,y,z);c=Kweight_cached(b,x,y,z);call same(a,c)
          c=Kweight_cached(b,x,y,z);call same(a,c)
        end do
        if(phonon_hits<30)error stop 'Phonon cache not exercised'
      end do
    end do
  end do
  slots=0;found=.false.;zero_kelvin=.false.;scdft_kernel=1;b=2000
  call begin_phonon_context(b)
  do i=1,65536
    x=real(i,dp)/655370;k=phonon_slot(x,.003_dp,.002_dp)
    if(slots(k)/=0)then
      y=real(slots(k),dp)/655370
      a=Kweight_cached(b,y,.003_dp,.002_dp);c=Kweight_cached(b,x,.003_dp,.002_dp)
      a=Kweight_cached(b,y,.003_dp,.002_dp);call same(a,Kweight(b,y,.003_dp,.002_dp))
      found=.true.;exit
    end if
    slots(k)=i
  end do
  if(.not.found)error stop 'No phonon collision exercised'
  print '(a,i0)', 'CACHE_QUALIFICATION_PASS checks=',checks
contains
  subroutine same(a,b)
    real(dp),intent(in)::a,b
    if(.not.ieee_is_finite(a).or..not.ieee_is_finite(b))error stop 'Nonfinite kernel'
    if(a/=b)error stop 'Cached kernel differs from original'
    checks=checks+1
  end subroutine
end program
