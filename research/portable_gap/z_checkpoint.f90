! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
module z_checkpoint
  use iso_fortran_env, only: real64,int64
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  private
  public::write_z_checkpoint,read_z_checkpoint
contains
  subroutine validate(context,counts,beta,completed,values)
    character(*),intent(in)::context
    integer,intent(in)::counts(3),completed
    real(real64),intent(in)::beta,values(:,:)
    if(len_trim(context)/=64.or.verify(trim(context),'0123456789abcdef')/=0) &
      error stop 'Invalid Z checkpoint context identity'
    if(minval(counts)<1.or.counts(3)/=maxval(counts(:2)))error stop 'Invalid Z checkpoint dimensions'
    if(any(shape(values)/=[counts(3),2]))error stop 'Invalid Z checkpoint array shape'
    if(completed<1.or.completed>counts(1))error stop 'Invalid Z checkpoint completed rows'
    if(.not.ieee_is_finite(beta).or.beta<=0.or..not.all(ieee_is_finite(values))) &
      error stop 'Nonfinite Z checkpoint data'
    if(any(values(completed+1:,1)/=0).or.any(values(counts(2)+1:,2)/=0)) &
      error stop 'Nonzero uncomputed Z checkpoint rows'
  end subroutine

  subroutine write_z_checkpoint(directory,context,counts,beta,completed,values)
    character(*),intent(in)::directory,context
    integer,intent(in)::counts(3),completed
    real(real64),intent(in)::beta,values(:,:)
    integer::unit
    call validate(context,counts,beta,completed,values)
    open(newunit=unit,file=trim(directory)//'/z-checkpoint.meta',status='new')
    write(unit,'(a)')'ordered-Z-checkpoint-v1; partial sums, not full Z'
    write(unit,'(a)')trim(context)
    write(unit,*)counts,completed
    write(unit,'(es26.17e3)')beta
    close(unit)
    open(newunit=unit,file=trim(directory)//'/z-checkpoint.bin',status='new',access='stream',form='unformatted')
    write(unit)values
    close(unit)
  end subroutine

  subroutine read_z_checkpoint(directory,context,counts,beta,completed,values)
    character(*),intent(in)::directory,context
    integer,intent(in)::counts(3),completed
    real(real64),intent(in)::beta
    real(real64),intent(out)::values(:,:)
    character(256)::header,saved_context,trailing
    integer::unit,ios,saved_counts(3),saved_completed
    integer(int64)::bytes
    real(real64)::saved_beta
    open(newunit=unit,file=trim(directory)//'/z-checkpoint.meta',status='old')
    read(unit,'(a)')header
    if(trim(header)/='ordered-Z-checkpoint-v1; partial sums, not full Z')error stop 'Stale Z checkpoint schema'
    read(unit,'(a)')saved_context
    read(unit,*)saved_counts,saved_completed
    read(unit,*)saved_beta
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0)error stop 'Trailing Z checkpoint metadata'
    if(trim(saved_context)/=context.or.any(saved_counts/=counts).or.saved_completed/=completed) &
      error stop 'Stale Z checkpoint context or row range'
    if(transfer(saved_beta,0_int64)/=transfer(beta,0_int64))error stop 'Stale Z checkpoint temperature'
    inquire(file=trim(directory)//'/z-checkpoint.bin',size=bytes)
    if(bytes/=8_int64*size(values,kind=int64))error stop 'Stale Z checkpoint binary shape'
    open(newunit=unit,file=trim(directory)//'/z-checkpoint.bin',status='old',access='stream',form='unformatted')
    read(unit)values
    close(unit)
    call validate(context,counts,beta,completed,values)
  end subroutine
end module
