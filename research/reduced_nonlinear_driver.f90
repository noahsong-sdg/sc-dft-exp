! Retained-basis nonlinear candidate; never a full SCDFT acceptance.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
program reduced_nonlinear_driver
  use kinds, only: dp
  use constants, only: RYTOEV
  use reduced_nonlinear_core, only: solve_reduced
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
  character(1024) :: basis_dir,prepare,mode_dir
  character(256) :: header,context,expected_context,trailing,mode_context
  integer :: unit,ios,n,rank,counts(7),config(6),mode_config(6),mode_n,mode_rank
  integer :: bytes,actual,i,g,iterations,info,index,columns
  real(dp) :: beta,expected_beta,amplitude,mode_beta,lambda,reported,residual,orth,average(2),scale,mode_error,fermi_min
  real(dp),allocatable :: q(:,:),u(:,:),x(:),dk(:),discard(:),v(:),vr(:),c(:),delta(:),gram(:,:),projection(:)
  open(newunit=unit,file='reduced-control.in',status='old')
  read(unit,'(a)')basis_dir
  read(unit,'(a)')prepare
  read(unit,'(a)')mode_dir
  read(unit,'(a)')expected_context
  read(unit,*)expected_beta,amplitude
  read(unit,'(a)',iostat=ios)trailing
  close(unit)
  if(ios>=0.or.expected_beta<=0.or.amplitude<=0.or.len_trim(expected_context)/=64.or. &
    .not.ieee_is_finite(expected_beta).or..not.ieee_is_finite(amplitude))error stop 'Invalid reduced control'
  open(newunit=unit,file=trim(basis_dir)//'/basis.meta',status='old')
  read(unit,'(a)')header
  read(unit,*)n,rank
  read(unit,*)beta
  read(unit,'(a)')context
  read(unit,*)config
  read(unit,'(a)',iostat=ios)trailing
  close(unit)
  if(ios>=0.or.header/='tc-basis-v1'.or.rank<1.or.rank>64.or.n<2.or.mod(n,2)/=0.or. &
    beta/=expected_beta.or.context/=expected_context)error stop 'Stale reduced basis context'
  allocate(q(n,rank),u(n,rank),x(n),dk(n),discard(n),v(n),vr(n),c(rank),delta(n),gram(rank,rank),projection(n))
  inquire(iolength=bytes)q,u
  inquire(file=trim(basis_dir)//'/basis.bin',size=actual)
  if(actual/=bytes)error stop 'Stale reduced basis payload'
  open(newunit=unit,file=trim(basis_dir)//'/basis.bin',status='old',access='stream',form='unformatted')
  read(unit)q,u
  close(unit)
  if(.not.all(ieee_is_finite(q)).or..not.all(ieee_is_finite(u)))error stop 'Nonfinite reduced basis'
  call dgemm('T','N',rank,rank,n,1._dp,q,n,q,n,0._dp,gram,rank)
  do i=1,rank
    gram(i,i)=gram(i,i)-1
  end do
  orth=maxval(abs(gram))
  if(orth>1.e-10_dp)error stop 'Reduced basis orthogonality failed'
  open(newunit=unit,file=trim(mode_dir)//'/basis.meta',status='old')
  read(unit,'(a)')header
  read(unit,*)mode_n,mode_rank
  read(unit,*)mode_beta
  read(unit,'(a)')mode_context
  read(unit,*)mode_config
  read(unit,'(a)',iostat=ios)trailing
  close(unit)
  if(ios>=0.or.header/='tc-basis-v1'.or.mode_n/=n.or.mode_beta/=beta.or. &
    mode_context/=context.or.any(mode_config/=config))error stop 'Stale reduced candidate context'
  open(newunit=unit,file=trim(mode_dir)//'/selected.meta',status='old')
  read(unit,*)index,columns
  read(unit,*)lambda,reported
  read(unit,'(a)',iostat=ios)trailing
  close(unit)
  if(ios>=0.or.columns/=mode_rank.or.index<1.or.index>columns.or.lambda<=1.or.reported>1.e-9_dp.or. &
    reported<0.or..not.ieee_is_finite(lambda).or..not.ieee_is_finite(reported))error stop 'Invalid reduced seed mode'
  inquire(iolength=bytes)v,vr
  inquire(file=trim(mode_dir)//'/selected.bin',size=actual)
  if(actual/=bytes)error stop 'Stale reduced seed shape'
  open(newunit=unit,file=trim(mode_dir)//'/selected.bin',status='old',access='stream',form='unformatted')
  read(unit)v,vr
  close(unit)
  if(.not.all(ieee_is_finite(v)).or..not.all(ieee_is_finite(vr)).or.abs(sum(v*v)-1)>1.e-10_dp) &
    error stop 'Invalid reduced seed vector'
  open(newunit=unit,file=trim(prepare)//'/native-init.meta',status='old')
  read(unit,'(a)')header
  read(unit,*)counts
  close(unit)
  if(header/='native-init-v1; arrays are native binary64/int32, Fortran order'.or. &
    minval(counts)<1.or.counts(3)/=maxval(counts(1:2)).or.n/=2*counts(3).or. &
    config(1)/=counts(4).or.any(config(5:6)/=counts(1:2)))error stop 'Stale reduced geometry'
  inquire(file=trim(prepare)//'/native-init.bin',size=actual)
  if(actual/=16*counts(4)+96*counts(3))error stop 'Stale reduced geometry payload'
  open(newunit=unit,file=trim(prepare)//'/native-init.bin',status='old',access='stream',form='unformatted')
  read(unit,pos=16*counts(4)+1)x,discard,dk
  close(unit)
  if(.not.all(ieee_is_finite(x)).or..not.all(ieee_is_finite(dk)))error stop 'Nonfinite reduced geometry'
  do g=1,2
    i=(g-1)*counts(3)
    if(any(q(i+counts(g)+1:g*counts(3),:)/=0).or.any(u(i+counts(g)+1:g*counts(3),:)/=0).or. &
      any(v(i+counts(g)+1:g*counts(3))/=0).or.any(dk(i+counts(g)+1:g*counts(3))/=0)) &
      error stop 'Nonzero reduced padding'
  end do
  ! Fermi mask uses the native emin from initialization metadata, not an arbitrary window.
  call fermi_average(v,average)
  if(average(1)*average(2)<=0)error stop 'No conventional reduced seed'
  if(average(1)<0)v=-v
  scale=amplitude/(1000*RYTOEV)/(abs(sum(average))/2)
  call dgemv('T',n,rank,1._dp,q,n,v,1,0._dp,c,1)
  call dgemv('N',n,rank,1._dp,u,n,c,1,0._dp,projection,1)
  mode_error=maxval(abs(projection-lambda*v))
  c=c*scale/lambda
  call solve_reduced(q,u,x,beta,c,delta,iterations,residual,info)
  if(info/=0)error stop 'Reduced Newton solve failed'
  call fermi_average(delta,average,fermi_min)
  average=average*1000*RYTOEV
  if(minval(average)<=.001_dp.or.fermi_min<=0)error stop 'No accepted positive nonzero reduced candidate'
  open(newunit=unit,file='reduced-result.txt',status='new')
  write(unit,'(a)') '# reduced-nonlinear-v1; candidate; FULL native residual required'
  write(unit,*)counts(1:4),rank
  write(unit,*)beta,amplitude,iterations,residual,orth,mode_error,RYTOEV
  write(unit,*)average,maxval(abs(delta)),fermi_min*1000*RYTOEV
  close(unit)
  open(newunit=unit,file='reduced-gap.bin',status='new',access='stream',form='unformatted')
  write(unit)delta
  close(unit)
contains
  subroutine fermi_average(vector,averages,minimum)
    real(dp),intent(in) :: vector(:)
    real(dp),intent(out) :: averages(2)
    real(dp),intent(out),optional :: minimum
    real(dp) :: scalars(7),denominator
    integer :: side,offset
    open(newunit=unit,file=trim(prepare)//'/native-init.meta',status='old')
    read(unit,'(a)')header
    read(unit,'(a)')trailing
    read(unit,*)scalars
    close(unit)
    if(.not.all(ieee_is_finite(scalars)).or.scalars(2)<=0)error stop 'Invalid reduced Fermi scale'
    if(present(minimum))minimum=huge(1._dp)
    do side=1,2
      offset=(side-1)*counts(3)
      denominator=sum(dk(offset+1:offset+counts(side)),abs(x(offset+1:offset+counts(side)))<scalars(2))
      if(denominator<=0)error stop 'Invalid reduced Fermi denominator'
      if(present(minimum))minimum=min(minimum,minval(vector(offset+1:offset+counts(side)), &
        mask=dk(offset+1:offset+counts(side))>0.and.abs(x(offset+1:offset+counts(side)))<scalars(2)))
      averages(side)=sum(vector(offset+1:offset+counts(side))*dk(offset+1:offset+counts(side)), &
        abs(x(offset+1:offset+counts(side)))<scalars(2))/denominator
    end do
  end subroutine
end program
