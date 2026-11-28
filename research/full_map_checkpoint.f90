! Fixed-seed nonlinear images: ordered partial sums and exact state binding.
! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
module full_map_checkpoint
  use iso_fortran_env,only:real64,int64
  use linear_image_checkpoint,only:write_linear_image_checkpoint,read_linear_image_checkpoint
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  private
  public::write_full_map_checkpoint,read_full_map_checkpoint
contains
  subroutine validate_state(counts,state,step,error,cpu)
    integer,intent(in)::counts(4)
    real(real64),intent(in)::state(:,:,:),step,error,cpu
    if(counts(4)/=4.or.any(shape(state)/=[counts(3),2,8]))error stop 'Invalid full-map checkpoint state shape'
    if(.not.all(ieee_is_finite(state)).or..not.all(ieee_is_finite([step,error,cpu]))) &
      error stop 'Nonfinite full-map checkpoint state'
    if(step/=1.e-8_real64.or.min(error,cpu)<0)error stop 'Invalid full-map checkpoint diagnostics'
  end subroutine

  subroutine write_full_map_checkpoint(directory,context,counts,beta,step,completed,values,state,error,cpu)
    character(*),intent(in)::directory,context
    integer,intent(in)::counts(4),completed
    real(real64),intent(in)::beta,step,values(:,:,:),state(:,:,:),error,cpu
    integer::unit
    call validate_state(counts,state,step,error,cpu)
    call write_linear_image_checkpoint(directory,context,counts,beta,completed,values)
    open(newunit=unit,file=trim(directory)//'/full-map-checkpoint.meta',status='new')
    write(unit,'(a)')'ordered-full-map-checkpoint-v1; exact active state binding'
    write(unit,'(3(es26.17e3,1x))')step,error,cpu
    close(unit)
    open(newunit=unit,file=trim(directory)//'/full-map-checkpoint-state.bin', &
      status='new',access='stream',form='unformatted')
    write(unit)state
    close(unit)
  end subroutine

  subroutine read_full_map_checkpoint(directory,context,counts,beta,step,completed,values,state,error,cpu)
    character(*),intent(in)::directory,context
    integer,intent(in)::counts(4),completed
    real(real64),intent(in)::beta,step,state(:,:,:)
    real(real64),intent(out)::values(:,:,:),error,cpu
    character(256)::header,trailing
    integer::unit,ios,k
    integer(int64)::bytes
    real(real64)::saved_step
    real(real64),allocatable::saved(:,:)
    call read_linear_image_checkpoint(directory,context,counts,beta,completed,values)
    open(newunit=unit,file=trim(directory)//'/full-map-checkpoint.meta',status='old')
    read(unit,'(a)')header
    if(header/='ordered-full-map-checkpoint-v1; exact active state binding')error stop 'Stale full-map checkpoint schema'
    read(unit,*)saved_step,error,cpu
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0)error stop 'Trailing full-map checkpoint metadata'
    call validate_state(counts,state,step,error,cpu)
    if(transfer(saved_step,0_int64)/=transfer(step,0_int64))error stop 'Stale full-map checkpoint step'
    inquire(file=trim(directory)//'/full-map-checkpoint-state.bin',size=bytes)
    if(bytes/=8_int64*size(state,kind=int64))error stop 'Stale full-map checkpoint state size'
    allocate(saved(counts(3),2))
    open(newunit=unit,file=trim(directory)//'/full-map-checkpoint-state.bin', &
      status='old',access='stream',form='unformatted')
    do k=1,8
      read(unit)saved
      if(any(transfer(saved,[0_int64],size(saved))/=transfer(state(:,:,k),[0_int64],size(saved)))) &
        error stop 'Changed full-map checkpoint active state'
    end do
    close(unit)
  end subroutine
end module
