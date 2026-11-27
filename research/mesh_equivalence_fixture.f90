program mesh_equivalence_fixture
  use iso_fortran_env, only: real64
  use mesh_equivalence
  use ieee_arithmetic, only: ieee_value,ieee_quiet_nan
  implicit none
  integer::shape,mask,rev,nsym,colin,stride,mode,grid(3),shift(3),i,cases=0
  character(len=32)::context
  call get_command_argument(1,context)
  if(len_trim(context)>0)call invalid_context(trim(context))
  do shape=1,3
    select case(shape)
    case(1);grid=[2,3,4]
    case(2);grid=[4,4,4]
    case(3);grid=[1,2,3]
    end select
    do mask=0,7
      do i=1,3
        shift(i)=ibits(mask,i-1,1)
      end do
      do rev=0,1
      do nsym=1,2
      do colin=0,2,2
      do stride=1,2
      do mode=0,4
        call check_case(grid,shift,rev==1,nsym,colin,stride,mode)
        cases=cases+1
      end do
      end do
      end do
      end do
      end do
    end do
  end do
  print *,cases,' uniform-mesh cases match brute force'
contains
  subroutine invalid_context(context)
    character(len=*),intent(in)::context
    integer::s(3,3,48),t_rev(48),map(1),ng,ni,i
    real(real64)::xk(3,1),xkg(3,1),eps
    s=0;t_rev=0;xk=0;xkg=0;eps=1.e-5_real64
    do i=1,3
      s(i,i,1)=1
    end do
    select case(context)
    case('ambiguous');eps=0.6_real64
    case('nonfinite');xk(1,1)=ieee_value(0._real64,ieee_quiet_nan)
    case('range');xk(1,1)=2._real64*real(huge(ng),real64)
    case default;error stop 'Unknown fixture context'
    end select
    call uniform_equivalence_map(1,1,[1,1,1],[0,0,0],1,s,t_rev, &
        .false.,0,xk,xkg,eps,map,ng,ni)
    error stop 'Invalid context was accepted'
  end subroutine

  subroutine check_case(grid,shift,reversal,nsym,colin,stride,mode)
    integer,intent(in)::grid(3),shift(3),nsym,colin,stride,mode
    logical,intent(in)::reversal
    integer::n,nks,i1,i2,i3,ik,jk,j,isym,ng,ni,expected_ng,expected_ni
    integer::s(3,3,48),t_rev(48)
    real(real64),allocatable::xk(:,:),xkg(:,:)
    integer,allocatable::actual(:),expected(:)
    real(real64)::rotated(3),plus(3),minus(3),eps=1.e-5_real64
    logical::found
    n=product(grid);nks=n*stride
    if(mode==3)nks=nks+stride
    if(mode==4)nks=nks-stride
    allocate(xk(3,nks),xkg(3,n),actual(n),expected(n));xk=0
    ik=0
    do i1=0,grid(1)-1
    do i2=0,grid(2)-1
    do i3=0,grid(3)-1
      ik=ik+1
      xkg(:,ik)=(real([i1,i2,i3],real64)+0.5_real64*shift)/real(grid,real64)
    end do
    end do
    end do
    j=0
    do jk=1,nks,stride
      j=j+1
      xk(:,jk)=xkg(:,1+modulo(j,n))
    end do
    if(mode==1)xk(1,1)=xk(1,1)+0.999_real64*eps
    if(mode==2)xk(1,1)=xk(1,1)+1.001_real64*eps
    if(mode==3)xk(:,n*stride+1)=xk(:,1)
    s=0;t_rev=0
    do j=1,3
      s(j,j,1)=1
    end do
    s(1,2,2)=-1;s(2,1,2)=1;s(3,3,2)=1;t_rev(2)=1
    call uniform_equivalence_map(nks,nsym,grid,shift,stride,s,t_rev, &
        reversal,colin,xk,xkg,eps,actual,ng,ni)
    ! Independently enumerate every target/input/symmetry as the owning search.
    expected=0;expected_ng=0;expected_ni=0
    do ik=1,n
      found=.false.
      inputs: do jk=1,nks,stride
        do isym=1,nsym
          rotated=matmul(real(s(:,:,isym),real64),xk(:,jk))
          if(t_rev(isym)==1.and.colin<2)rotated=-rotated
          plus=rotated-xkg(:,ik)-nint(rotated-xkg(:,ik))
          minus=rotated+xkg(:,ik)-nint(rotated+xkg(:,ik))
          if(sqrt(plus(1)**2+plus(2)**2+plus(3)**2)<eps.or.(reversal.and. &
              sqrt(minus(1)**2+minus(2)**2+minus(3)**2)<eps))then
            expected(ik)=jk;found=.true.;exit inputs
          end if
        end do
      end do inputs
      if(.not.found)then
        expected_ng=ik;exit
      end if
    end do
    if(expected_ng==0)then
      do jk=1,nks,stride
        if(.not.any(expected==jk))then
          expected_ni=jk;exit
        end if
      end do
    end if
    if(ng/=expected_ng.or.ni/=expected_ni)error stop 'Mapping failure identity differs'
    if(ng==0.and.any(actual/=expected))error stop 'First-match mesh map differs'
    if(ng>0)then
      if(any(actual(:ng-1)/=expected(:ng-1)))error stop 'Pre-failure map differs'
    end if
  end subroutine
end program
