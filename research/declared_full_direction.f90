! Explicit full-map direction bound to the exact candidate, not a new gap.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
module declared_full_direction
  use kinds,only:dp
  use iso_fortran_env,only:int64
  use sctk_val,only:ngap,ngapmax,beta,delta
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
contains
  subroutine load_declared_direction(direction)
    real(dp),intent(out)::direction(ngapmax,2)
    real(dp),allocatable::candidate(:,:)
    real(dp)::saved_beta
    integer::unit,ios,counts(3),side
    integer(int64)::bytes
    character(1024)::header,context,expected,directory,line
    open(newunit=unit,file='seed-control.in',status='old')
    read(unit,'(a)')directory
    read(unit,'(a)')expected
    read(unit,'(a)',iostat=ios)line
    close(unit)
    if(ios>=0.or.len_trim(directory)==0.or.len_trim(expected)/=64.or. &
      verify(trim(expected),'0123456789abcdef')/=0)error stop 'Invalid direction seed control'
    open(newunit=unit,file='direction-state.meta',status='old')
    read(unit,'(a)')header
    read(unit,*)counts
    read(unit,*)saved_beta
    read(unit,'(a)')context
    read(unit,'(a)',iostat=ios)line
    close(unit)
    if(ios>=0.or.header/='declared-full-map-direction-v1'.or.any(counts/=[ngap,ngapmax]).or. &
      .not.ieee_is_finite(saved_beta).or.saved_beta/=beta.or.context/=expected) &
      error stop 'Stale declared direction context'
    inquire(file='direction-state.bin',size=bytes)
    if(bytes/=32_int64*ngapmax)error stop 'Stale declared direction payload size'
    allocate(candidate(ngapmax,2))
    open(newunit=unit,file='direction-state.bin',status='old',access='stream',form='unformatted')
    read(unit)candidate,direction
    close(unit)
    if(.not.all(ieee_is_finite(candidate)).or..not.all(ieee_is_finite(direction))) &
      error stop 'Nonfinite declared direction state'
    if(any(transfer(candidate,[0_int64],size(candidate))/=transfer(delta,[0_int64],size(delta)))) &
      error stop 'Declared direction candidate differs bitwise'
    if(maxval(abs(direction))/=1._dp)error stop 'Declared direction requires unit infinity norm'
    do side=1,2
      if(any(direction(ngap(side)+1:,side)/=0).or.any(candidate(ngap(side)+1:,side)/=0)) &
        error stop 'Nonzero declared direction padding'
    end do
  end subroutine
end module
