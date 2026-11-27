! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
module linear_image_checkpoint
  use iso_fortran_env, only: real64,int64
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  private
  public::write_linear_image_checkpoint,read_linear_image_checkpoint
contains
  subroutine validate(context,counts,beta,completed,values)
    character(*),intent(in)::context
    integer,intent(in)::counts(4),completed
    real(real64),intent(in)::beta,values(:,:,:)
    if(len_trim(context)/=64.or.verify(trim(context),'0123456789abcdef')/=0) &
      error stop 'Invalid linear image checkpoint context identity'
    if(minval(counts)<1.or.counts(4)>64.or.counts(3)/=maxval(counts(:2)))error stop 'Invalid linear image checkpoint dimensions'
    if(any(shape(values)/=[counts(3),2,counts(4)]))error stop 'Invalid linear image checkpoint array shape'
    if(completed<1.or.completed>counts(1))error stop 'Invalid linear image checkpoint completed rows'
    if(.not.ieee_is_finite(beta).or.beta<=0.or..not.all(ieee_is_finite(values))) &
      error stop 'Nonfinite linear image checkpoint data'
    if(any(values(completed+1:,1,:)/=0).or.any(values(counts(2)+1:,2,:)/=0)) &
      error stop 'Nonzero uncomputed linear image checkpoint rows'
  end subroutine

  subroutine write_linear_image_checkpoint(directory,context,counts,beta,completed,values)
    character(*),intent(in)::directory,context
    integer,intent(in)::counts(4),completed
    real(real64),intent(in)::beta,values(:,:,:)
    integer::unit
    call validate(context,counts,beta,completed,values)
    open(newunit=unit,file=trim(directory)//'/linear-image-checkpoint.meta',status='new')
    write(unit,'(a)')'ordered-linear-image-checkpoint-v1; unnormalized partial sums'
    write(unit,'(a)')trim(context)
    write(unit,*)counts,completed
    write(unit,'(es26.17e3)')beta
    close(unit)
    open(newunit=unit,file=trim(directory)//'/linear-image-checkpoint.bin',status='new',access='stream',form='unformatted')
    write(unit)values
    close(unit)
  end subroutine

  subroutine read_linear_image_checkpoint(directory,context,counts,beta,completed,values)
    character(*),intent(in)::directory,context
    integer,intent(in)::counts(4),completed
    real(real64),intent(in)::beta
    real(real64),intent(out)::values(:,:,:)
    character(256)::header,saved_context,trailing
    integer::unit,ios,saved_counts(4),saved_completed
    integer(int64)::bytes
    real(real64)::saved_beta
    open(newunit=unit,file=trim(directory)//'/linear-image-checkpoint.meta',status='old')
    read(unit,'(a)')header
    if(trim(header)/='ordered-linear-image-checkpoint-v1; unnormalized partial sums')error stop 'Stale linear image checkpoint schema'
    read(unit,'(a)')saved_context
    read(unit,*)saved_counts,saved_completed
    read(unit,*)saved_beta
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0)error stop 'Trailing linear image checkpoint metadata'
    if(trim(saved_context)/=context.or.any(saved_counts/=counts).or.saved_completed/=completed) &
      error stop 'Stale linear image checkpoint context or row range'
    if(transfer(saved_beta,0_int64)/=transfer(beta,0_int64))error stop 'Stale linear image checkpoint temperature'
    inquire(file=trim(directory)//'/linear-image-checkpoint.bin',size=bytes)
    if(bytes/=8_int64*size(values,kind=int64))error stop 'Stale linear image checkpoint binary shape'
    open(newunit=unit,file=trim(directory)//'/linear-image-checkpoint.bin',status='old',access='stream',form='unformatted')
    read(unit)values
    close(unit)
    call validate(context,counts,beta,completed,values)
  end subroutine
end module
