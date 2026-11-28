! Bounded contraction throughput and saved signed controls; no material kernel.
program tile_blas_probe
  use iso_fortran_env, only: dp=>real64, int64
  use ieee_arithmetic, only: ieee_is_finite
  implicit none
  integer :: c,rank,repeats,count,meta,controls,samples
  integer :: ms(3)=[256,512,1024],ns(3)=[384,768,1024]
  character(32) :: prefix,mode
  call get_command_argument(1,prefix)
  call get_command_argument(2,mode)
  if(trim(prefix)/='reference'.and.trim(prefix)/='accelerate')error stop 'Unsupported output prefix'
  if(trim(mode)=='fixture')then
    ms(1)=9;ns(1)=11;rank=3;repeats=128;count=1
  else if(trim(mode)=='benchmark')then
    rank=51;repeats=32;count=3
  else
    error stop 'Explicit fixture or benchmark mode required'
  end if
  open(newunit=meta,file=trim(prefix)//'-summary.txt',status='new')
  open(newunit=controls,file=trim(prefix)//'-controls.bin',status='new',access='stream',form='unformatted')
  open(newunit=samples,file=trim(prefix)//'-samples.bin',status='new',access='stream',form='unformatted')
  write(meta,'(a)')'tile-blas-probe-v1 '//trim(mode)
  call control('P',controls)
  call control('U',controls)
  do c=1,count
    call measure('P',c,ms(c),ns(c),rank,repeats,meta,samples)
    call measure('U',c,ms(c),ns(c),rank,repeats,meta,samples)
  end do
  close(meta);close(controls);close(samples)
contains
  subroutine fill(a,which)
    real(dp),intent(out)::a(:,:)
    integer,intent(in)::which
    integer::i,j
    do j=1,size(a,2)
      do i=1,size(a,1)
        if(which==1)then
          a(i,j)=real(mod(17*i+13*j,31)-15,dp)/16+real((-1)**(i+j)*(i+j),dp)*2._dp**(-40)
        else
          a(i,j)=real(mod(11*i+7*j,29)-14,dp)/16+real((-1)**(i+j)*(i+2*j),dp)*2._dp**(-43)
        end if
      end do
    end do
  end subroutine
  subroutine control(kind,unit)
    character,intent(in)::kind
    integer,intent(in)::unit
    real(dp)::a(7,9),bp(7,5),bu(9,5),cp(9,5),cu(7,5)
    call fill(a,1)
    if(kind=='P')then
      call fill(bp,2)
      call dgemm('T','N',9,5,7,1._dp,a,7,bp,7,0._dp,cp,9)
      if(.not.all(ieee_is_finite(cp)))error stop 'Nonfinite P control'
      write(unit)a,bp,cp
    else
      call fill(bu,2)
      call dgemm('N','N',7,5,9,1._dp,a,7,bu,9,0._dp,cu,7)
      if(.not.all(ieee_is_finite(cu)))error stop 'Nonfinite U control'
      write(unit)a,bu,cu
    end if
  end subroutine
  subroutine measure(kind,case_id,m,n,r,repetitions,meta,samples)
    character,intent(in)::kind
    integer,intent(in)::case_id,m,n,r,repetitions,meta,samples
    real(dp),allocatable::a(:,:),b(:,:),out(:,:)
    integer::i,j,k,rows(3),cols(3)
    integer(int64)::first,last,rate
    real(dp)::cpu_first,cpu_last
    allocate(a(m,r));call fill(a,1)
    if(kind=='P')then
      allocate(b(m,n),out(r,n))
    else
      allocate(b(r,n),out(m,n))
    end if
    call fill(b,2)
    ! Warm the selected library outside timed repetitions, with identical inputs.
    call product(kind,a,b,out)
    call system_clock(first,rate);call cpu_time(cpu_first)
    do k=1,repetitions
      call product(kind,a,b,out)
    end do
    call cpu_time(cpu_last);call system_clock(last)
    if(rate<=0.or.last<=first)then
      write(*,*)'Invalid clock: ',rate,first,last
      error stop 'Invalid tile clock'
    end if
    if(.not.all(ieee_is_finite(out)))error stop 'Nonfinite timed product'
    write(meta,*)kind,case_id,m,n,r,repetitions,real(last-first,dp)/real(rate,dp),cpu_last-cpu_first
    rows=[1,(size(out,1)+1)/2,size(out,1)];cols=[1,(n+1)/2,n]
    do j=1,3
      do i=1,3
        write(samples)out(rows(i),cols(j))
      end do
    end do
  end subroutine
  subroutine product(kind,a,b,out)
    character,intent(in)::kind
    real(dp),intent(in)::a(:,:),b(:,:)
    real(dp),intent(out)::out(:,:)
    integer::m,n,r
    m=size(a,1);r=size(a,2);n=size(b,2)
    if(kind=='P')then
      call dgemm('T','N',r,n,m,1._dp,a,m,b,m,0._dp,out,r)
    else
      call dgemm('N','N',m,n,r,1._dp,a,m,b,r,0._dp,out,m)
    end if
  end subroutine
end program
