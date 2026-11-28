! Adversarial synthetic layout fixture, not a niobium driver.
program streamed_defect_fixture
  use streamed_defect_core
  use iso_fortran_env,only:dp=>real64
  use ieee_arithmetic,only:ieee_value,ieee_quiet_nan
  implicit none
  integer,parameter::left=35,right=39,n=left+right,r=3
  real(dp)::w(n),z(n),d(n),q(n,r),u(n,r),qd(n,r),p(r,n),small(r,r),c(r,n),rows(n)
  real(dp),allocatable::block(:,:,:)
  integer::i,j,k,first,last,width,nextp,nextl,nextr,unit,step
  character(32)::mode
  call get_command_argument(1,mode)
  do i=1,n
    w(i)=.5_dp+real(mod(i,5),dp)/16
    z(i)=real(mod(i,7),dp)/16
    d(i)=real(mod(i,9),dp)/8
    do k=1,r
      q(i,k)=real(mod(7*i+3*k,17)-8,dp)/64
      u(i,k)=real(mod(11*i+5*k,19)-9,dp)/128
      qd(i,k)=d(i)*q(i,k)
    end do
  end do
  do j=1,r
    do i=1,r
      small(i,j)=real(i-j,dp)/64
      if(i==j)small(i,j)=1+real(i,dp)/32
    end do
  end do
  p=0;rows=0;nextp=1;nextl=1;nextr=1;step=32
  if(trim(mode)=='stale')p=1
  if(trim(mode)=='normalization')z(1)=-1
  if(trim(mode)=='wide')step=33
  if(trim(mode)=='incomplete')call make_c(p,q,small,c,nextp,left)
  do first=1,left,step
    last=min(first+step-1,left);call tile(first,last)
    if(trim(mode)=='nonfinite')block(1,first,1)=ieee_value(1._dp,ieee_quiet_nan)
    if(trim(mode)=='skip')then
      call accumulate_p(left,first+1,block,w,z,qd,p,nextp)
    else if(trim(mode)=='shape')then
      call accumulate_p(left,first,block,w,z,qd,p(:r-1,:),nextp)
    else
      call accumulate_p(left,first,block,w,z,qd,p,nextp)
    end if
    if(trim(mode)=='duplicate')call accumulate_p(left,first,block,w,z,qd,p,nextp)
    deallocate(block)
  end do
  call make_c(p,q,small,c,nextp,left)
  if(trim(mode)=='rows-stale')rows(1)=1
  do first=1,left,32
    last=min(first+31,left);call tile(first,last)
    call defect_left(left,first,block,w,z,u,c,d,rows,nextl)
    if(trim(mode)=='rows-duplicate')call defect_left(left,first,block,w,z,u,c,d,rows,nextl)
    deallocate(block)
  end do
  if(trim(mode)/='omit')then
    do first=1,right,32
      width=min(32,right-first+1)
      call defect_same_right(left,first,width,u,c,d,rows,nextr)
      if(trim(mode)=='right-duplicate')call defect_same_right(left,first,width,u,c,d,rows,nextr)
    end do
  end if
  if(nextp/=left+1.or.nextl/=left+1.or.nextr/=right+1)error stop 'Incomplete defect coverage'
  open(newunit=unit,file='defect-fixture.bin',status='new',access='stream',form='unformatted')
  write(unit)p,c,rows
  close(unit)
  write(*,*)'DIAGNOSTIC ONLY',left,right,r,nextp,nextl,nextr,maxval(rows)
contains
  subroutine tile(first,last)
    integer,intent(in)::first,last
    integer::i,j
    ! Retain the native producer's nonunit second lower bound.
    allocate(block(right,first:last,2))
    do j=first,last
      do i=1,right
        block(i,j,1)=real(mod(13*i+7*j,23)-11,dp)/32
        block(i,j,2)=real(mod(17*i+5*j,29)-14,dp)/32
      end do
    end do
  end subroutine
end program
