! File-bound inverse diagnostics at an accepted full residual candidate.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
program low_rank_inverse_driver
  use iso_fortran_env, only: dp=>real64,int64
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  use reduced_nonlinear_core, only: occupation_ratio
  use low_rank_inverse, only: inverse_actions
  implicit none
  character(1024) :: basis,geometry,full,seed_geometry
  character(256) :: header,context,expected_context,trailing
  integer :: unit,ios,n,rank,counts(7),config(6),expected_config(6),seed_dims(6),dims(4)
  integer :: i,g,offset,actual,info,side
  real(dp) :: beta,expected_beta,seed_beta,controls(6),scalars(7),stats(3),orth,error
  real(dp) :: residual_inf,gap_inf,direction_inf,ratio,correction_inf,probe_ratio
  real(dp),allocatable :: q(:,:),u(:,:),x(:),gap(:),seed(:),residual(:),direction(:),native_jv(:)
  real(dp),allocatable :: value(:),diagonal(:),rhs(:,:),answer(:,:),small(:,:),singular(:),gram(:,:)
  open(newunit=unit,file='inverse-control.in',status='old')
  read(unit,'(a)')header
  if(header/='low-rank-inverse-control-v1')error stop 'Invalid inverse control schema'
  read(unit,'(a)')basis
  read(unit,'(a)')geometry
  read(unit,'(a)')full
  read(unit,'(a)')expected_context
  read(unit,*)expected_beta
  read(unit,*)expected_config
  call finish(unit)
  if(len_trim(expected_context)/=64.or.verify(trim(expected_context),'0123456789abcdef')/=0.or. &
    .not.ieee_is_finite(expected_beta).or.expected_beta<=0)error stop 'Invalid inverse control identity'
  open(newunit=unit,file=trim(basis)//'/basis.meta',status='old')
  read(unit,'(a)')header
  read(unit,*)n,rank
  read(unit,*)beta
  read(unit,'(a)')context
  read(unit,*)config
  call finish(unit)
  if(header/='tc-basis-v1'.or.n<2.or.mod(n,2)/=0.or.rank<1.or.rank>64.or.rank>n.or. &
    beta/=expected_beta.or.context/=expected_context.or.any(config/=expected_config)) &
    error stop 'Stale inverse basis context'
  open(newunit=unit,file=trim(geometry)//'/native-init.meta',status='old')
  read(unit,'(a)')header
  read(unit,*)counts
  read(unit,*)scalars
  read(unit,'(a)')trailing
  call finish(unit)
  if(header/='native-init-v1; arrays are native binary64/int32, Fortran order'.or. &
    minval(counts)<1.or.counts(3)/=maxval(counts(1:2)).or.n/=2*counts(3).or. &
    config(1)/=counts(4).or.config(4)/=2.or.any(config(5:6)/=counts(1:2)).or. &
    .not.all(ieee_is_finite(scalars)))error stop 'Stale inverse geometry'
  open(newunit=unit,file=trim(full)//'/gap-seed.meta',status='old')
  read(unit,'(a)')header
  read(unit,*)seed_dims
  read(unit,*)seed_beta
  read(unit,'(a)')seed_geometry
  read(unit,'(a)')context
  call finish(unit)
  if(header/='gap-seed-v1; binary64 Fortran order'.or.minval(seed_dims)<1.or. &
    any(seed_dims(1:4)/=counts(1:4)).or.seed_dims(5)/=config(2).or.seed_beta/=beta.or. &
    seed_geometry/=geometry.or.context/=expected_context)error stop 'Stale inverse full-map context'
  allocate(q(n,rank),u(n,rank),x(n),gap(n),seed(n),residual(n),direction(n),native_jv(n), &
    value(n),diagonal(n),rhs(n,2),answer(n,2),small(rank,rank),singular(rank),gram(rank,rank))
  call size_check(trim(basis)//'/basis.bin',16*n*rank)
  open(newunit=unit,file=trim(basis)//'/basis.bin',status='old',access='stream',form='unformatted')
  read(unit)q,u
  close(unit)
  call size_check(trim(geometry)//'/native-init.bin',16*counts(4)+96*counts(3))
  open(newunit=unit,file=trim(geometry)//'/native-init.bin',status='old',access='stream',form='unformatted')
  read(unit,pos=16*counts(4)+1)x
  close(unit)
  call size_check(trim(full)//'/full-map.bin',32*n)
  open(newunit=unit,file=trim(full)//'/full-map.bin',status='old',access='stream',form='unformatted')
  read(unit)gap,residual,direction,native_jv
  close(unit)
  call size_check(trim(full)//'/gap-seed.bin',8*n)
  open(newunit=unit,file=trim(full)//'/gap-seed.bin',status='old',access='stream',form='unformatted')
  read(unit)seed
  close(unit)
  if(any(transfer(gap,[0_int64],n)/=transfer(seed,[0_int64],n)))error stop 'Different inverse candidate'
  if(.not.all(ieee_is_finite(q)).or..not.all(ieee_is_finite(u)).or..not.all(ieee_is_finite(x)).or. &
    .not.all(ieee_is_finite(gap)).or..not.all(ieee_is_finite(residual)).or. &
    .not.all(ieee_is_finite(direction)).or..not.all(ieee_is_finite(native_jv)))error stop 'Nonfinite inverse state'
  call dgemm('T','N',rank,rank,n,1._dp,q,n,q,n,0._dp,gram,rank)
  do i=1,rank
    gram(i,i)=gram(i,i)-1
  end do
  orth=maxval(abs(gram))
  if(orth>1.e-10_dp)error stop 'Inverse basis orthogonality failed'
  open(newunit=unit,file=trim(full)//'/full-map.txt',status='old')
  read(unit,'(a)')header
  read(unit,*)dims
  read(unit,*)controls
  if(header/='# full-nonlinear-map-v1; imposed seed; NOT a converged gap'.or. &
    any(dims/=[counts(1:3),4]).or.controls(1)/=beta.or..not.all(ieee_is_finite(controls)).or. &
    minval(controls(2:6))<0.or.controls(2)==0.or.controls(5)>controls(6)) &
    error stop 'Stale inverse full-map summary'
  ratio=0
  do g=1,2
    offset=(g-1)*counts(3)
    read(unit,*)side,stats
    if(side/=g.or..not.all(ieee_is_finite(stats)))error stop 'Invalid inverse full-map side'
    block
      real(dp) :: measured(3),rms_gap
      i=offset+counts(g)
      measured=[maxval(abs(residual(offset+1:i))),sqrt(sum(residual(offset+1:i)**2)/counts(g)), &
        maxval(abs(native_jv(offset+1:i)))]
      rms_gap=sqrt(sum(gap(offset+1:i)**2)/counts(g))
      if(rms_gap<=0.or.any(abs(measured-stats)>1.e-18_dp+2.e-13_dp*abs(measured))) &
        error stop 'Inverse full-map binary/summary mismatch'
      ratio=max(ratio,measured(2)/rms_gap)
      if(any(q(i+1:g*counts(3),:)/=0).or.any(u(i+1:g*counts(3),:)/=0).or. &
        any(gap(i+1:g*counts(3))/=0).or.any(residual(i+1:g*counts(3))/=0).or. &
        any(direction(i+1:g*counts(3))/=0).or.any(native_jv(i+1:g*counts(3))/=0)) &
        error stop 'Nonzero inverse padding'
    end block
  end do
  call finish(unit)
  residual_inf=maxval(abs(residual));gap_inf=maxval(abs(gap));direction_inf=maxval(abs(direction))
  if(residual_inf>1.e-10_dp.or.ratio>1.e-5_dp.or.direction_inf<=0)error stop 'Inverse source residual gate failed'
  call occupation_ratio(x,gap,beta,value,diagonal)
  do g=1,2
    diagonal((g-1)*counts(3)+counts(g)+1:g*counts(3))=0
  end do
  rhs(:,1)=residual;rhs(:,2)=-native_jv
  call inverse_actions(q,u,diagonal,rhs,answer,small,singular,error,info)
  if(info/=0.or.minval(singular)<=0)error stop 'Inverse diagnostic solve failed'
  answer(:,2)=answer(:,2)-direction
  correction_inf=maxval(abs(answer(:,1)));probe_ratio=maxval(abs(answer(:,2)))/direction_inf
  if(.not.all(ieee_is_finite(answer)).or..not.ieee_is_finite(probe_ratio).or. &
    .not.ieee_is_finite(correction_inf/gap_inf))error stop 'Nonfinite inverse diagnostic'
  open(newunit=unit,file='inverse-result.txt',status='new')
  write(unit,'(a)') '# low-rank-inverse-v1; DIAGNOSTIC; NO full-space bound'
  write(unit,*)n,rank,counts(1:3)
  write(unit,*)beta,orth,error,maxval(singular),minval(singular)
  write(unit,*)residual_inf,correction_inf,correction_inf/gap_inf,probe_ratio
  close(unit)
  open(newunit=unit,file='inverse-result.bin',status='new',access='stream',form='unformatted')
  write(unit)diagonal,answer,small,singular
  close(unit)
contains
  subroutine finish(source)
    integer,intent(in) :: source
    read(source,'(a)',iostat=ios)trailing
    close(source)
    if(ios>=0)error stop 'Trailing inverse metadata'
  end subroutine
  subroutine size_check(path,expected)
    character(*),intent(in) :: path
    integer,intent(in) :: expected
    inquire(file=path,size=actual,iostat=ios)
    if(ios/=0.or.actual/=expected)error stop 'Stale inverse payload size'
  end subroutine
end program
