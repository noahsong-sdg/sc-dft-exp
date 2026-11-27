! Explicit nonlinear candidate input, after fresh initialization/Z checks.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
module gap_seed_io
  use kinds, only: dp
  use sctk_val, only: ngap,ngapmax,nx,nmf,ne,beta,xi,dk,emin
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
contains
  subroutine load_gap_seed(point,gap)
    character(*),intent(in) :: point
    real(dp),intent(out) :: gap(ngapmax,2)
    character(1024) :: directory,saved_point
    character(256) :: header,context,expected_context,trailing
    integer :: unit,ios,counts(6),bytes,actual,g
    real(dp) :: saved_beta
    open(newunit=unit,file='seed-control.in',status='old')
    read(unit,'(a)')directory
    read(unit,'(a)')expected_context
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0.or.len_trim(expected_context)/=64.or.verify(trim(expected_context),'0123456789abcdef')/=0) &
      error stop 'Invalid declared gap context'
    open(newunit=unit,file=trim(directory)//'/gap-seed.meta',status='old')
    read(unit,'(a)')header
    read(unit,*)counts
    read(unit,*)saved_beta
    read(unit,'(a)')saved_point
    read(unit,'(a)')context
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0.or.header/='gap-seed-v1; binary64 Fortran order'.or. &
      any(counts/=[ngap,ngapmax,nx,nmf,ne]).or.saved_beta/=beta.or. &
      saved_point/=point.or.context/=expected_context)error stop 'Stale gap seed context'
    inquire(iolength=bytes)gap
    inquire(file=trim(directory)//'/gap-seed.bin',size=actual)
    if(actual/=bytes)error stop 'Stale gap seed payload shape'
    open(newunit=unit,file=trim(directory)//'/gap-seed.bin',status='old',access='stream',form='unformatted')
    read(unit)gap
    close(unit)
    if(.not.all(ieee_is_finite(gap)))error stop 'Nonfinite gap seed'
    do g=1,2
      if(any(gap(ngap(g)+1:,g)/=0))error stop 'Nonzero gap seed padding'
      if(count(dk(1:ngap(g),g)>0.and.abs(xi(1:ngap(g),g))<emin)==0) &
        error stop 'No positive-weight Fermi support'
      if(minval(gap(1:ngap(g),g),mask=dk(1:ngap(g),g)>0.and.abs(xi(1:ngap(g),g))<emin)<=0) &
        error stop 'Gap seed is outside declared positive conventional branch'
    end do
  end subroutine
end module
