program compact_p_checkpoint_fixture
  use streamed_defect_core,only:accumulate_p
  use compact_p_checkpoint
  use iso_fortran_env,only:dp=>real64
  use ieee_arithmetic,only:ieee_value,ieee_quiet_nan
  implicit none
  integer,parameter::left=35,right=39,n=74,r=3
  real(dp)::w(n),z(n),qd(n,r),p(r,n),baseline(r,n),cpu(2)
  real(dp),allocatable::block(:,:,:)
  integer::i,k,first,last,next,file,completed
  character(32)::mode
  character(64)::identity
  call get_command_argument(1,mode)
  identity=repeat('a',64);completed=32
  do i=1,n
    w(i)=.5_dp+real(mod(i,5),dp)/16;z(i)=real(mod(i,7),dp)/16
    do k=1,r
      qd(i,k)=real(mod(i,9),dp)/8*real(mod(7*i+3*k,17)-8,dp)/64
    end do
  end do
  if(mode=='read'.or.mode=='identity'.or.mode=='coverage')then
    if(mode=='identity')identity=repeat('b',64)
    if(mode=='coverage')completed=35
    call read_p_checkpoint('.', [left,right],r,completed,identity,p,cpu)
  else
    p=0;next=1
    call tile(1,32);call accumulate_p(left,1,block,w,z,qd,p,next);deallocate(block)
    cpu=[.25_dp,.125_dp]
    if(mode=='write-unvisited')p(1,33)=1
    if(mode=='write-nonfinite')p(1,1)=ieee_value(1._dp,ieee_quiet_nan)
    if(mode=='write-split')completed=31
    if(mode=='write-negative-time')cpu(1)=-1
    call write_p_checkpoint('.',[left,right],r,completed,identity,p,cpu)
    if(mode=='normal')then
      baseline=p
      call tile(33,35);call accumulate_p(left,33,block,w,z,qd,baseline,next);deallocate(block)
      open(newunit=file,file='continuous.bin',status='new',access='stream',form='unformatted')
      write(file)baseline
      close(file)
      p=0;cpu=0
      call read_p_checkpoint('.',[left,right],r,32,identity,p,cpu)
      if(any(cpu/=[.25_dp,.125_dp]))error stop 'Checkpoint CPU changed'
      next=33
      call tile(33,35);call accumulate_p(left,33,block,w,z,qd,p,next);deallocate(block)
      if(any(p/=baseline).or.next/=left+1)error stop 'Checkpoint ordered restart changed P'
      call write_p_checkpoint('complete',[left,right],r,left,identity,p,cpu)
      p=0
      call read_p_checkpoint('complete',[left,right],r,left,identity,p,cpu)
    end if
  end if
  open(newunit=file,file='echo.bin',status='new',access='stream',form='unformatted')
  write(file)p
  close(file)
contains
  subroutine tile(first,last)
    integer,intent(in)::first,last
    integer::i,j
    allocate(block(right,first:last,2))
    do j=first,last
      do i=1,right
        block(i,j,1)=real(mod(13*i+7*j,23)-11,dp)/32
        block(i,j,2)=real(mod(17*i+5*j,29)-14,dp)/32
      end do
    end do
  end subroutine
end program
