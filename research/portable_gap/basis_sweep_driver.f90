! Actual-input ordered linear-image restart qualification.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
program basis_sweep_driver
  use kinds,only:dp
  use constants,only:K_BOLTZMANN_RY
  use iso_fortran_env,only:int64
  use environment,only:environment_start,environment_end
  use mp_world,only:nproc
  use input_parameters,only:calculation,restart_mode
  use elph_tetra_mod,only:lshift_q
  use sctk_stdin,only:stdin_control,stdin_scdft
  use sctk_read_file,only:degenerated_band,read_a2Fsave,read_elph
  use sctk_ini_delta,only:energy_grid,ini_delta
  use saved_coulomb,only:read_saved_coulomb,check_saved_coefficients
  use native_state_io,only:verify_initialized_state,read_full_Z
  use sctk_val,only:ngap,ngapmax,nx,nmf,ne,beta,zero_kelvin,initial_delta,Z
  use block_linear_operator,only:linear_weights
  use tiled_operator,only:build_tile
  use slab_operator,only:clear_slab
  use cached_kel,only:reset_kel_cache
  use cached_phonon,only:reset_phonon_cache
  use linear_image_checkpoint,only:write_linear_image_checkpoint,read_linear_image_checkpoint
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical,intent(inout)::needwf
    end subroutine
  end interface
  character(1024)::geometry,completed,trials
  character(64)::context
  character(64)::header
  integer::unit,v,side,counts(4),rate,t0,t1
  integer(int64)::bytes
  real(dp),allocatable::full(:,:),vectors(:,:,:),images(:,:,:),weights(:,:),chi(:,:,:),baseline(:,:,:)
  logical::needwf=.false.
  open(newunit=unit,file='basis-sweep-control.in',status='old')
  read(unit,'(a)')header
  if(header/='fresh-basis-split-control-v1')error stop 'Stale basis split control'
  read(unit,'(a)')geometry
  read(unit,'(a)')completed
  read(unit,'(a)')trials
  read(unit,'(a)')context
  close(unit)
  call environment_start('SCTK')
  if(nproc/=1)error stop 'Serial basis sweep required'
  call stdin_control()
  if(calculation/='scdft'.or.restart_mode/='from_scratch')error stop 'Fresh SCDFT required'
  call read_file_new(needwf);call degenerated_band();call read_a2Fsave()
  lshift_q=.true.;call stdin_scdft()
  if(nx/=100.or.nmf/=10.or.ne/=50.or.initial_delta/='constant'.or..not.zero_kelvin) &
    error stop 'Registered initialization changed'
  call read_elph();call read_saved_coulomb();call check_saved_coefficients()
  call energy_grid();call ini_delta(.true.)
  call verify_initialized_state(trim(geometry))
  if(any(ngap/=[66867,67940]))error stop 'Registered state counts changed'
  beta=1._dp/(8.05_dp*K_BOLTZMANN_RY);zero_kelvin=.false.
  allocate(full(ngapmax,2),vectors(ngapmax,2,16),images(ngapmax,2,16), &
    weights(ngapmax,2),chi(ngapmax,2,16))
  call read_full_Z(trim(completed),1,full);Z=full
  allocate(baseline(ngapmax,2,16))
  inquire(file=trim(trials),size=bytes)
  if(bytes/=2_int64*8*ngapmax*2*16)error stop 'Stale qualified trial payload'
  open(newunit=unit,file=trim(trials),status='old',access='stream',form='unformatted')
  read(unit)vectors
  close(unit)
  if(.not.all(ieee_is_finite(vectors)))error stop 'Nonfinite trial vectors'
  do side=1,2
    if(any(vectors(ngap(side)+1:,side,:)/=0))error stop 'Nonzero trial padding'
  end do
  call linear_weights(weights)
  do v=1,16
    chi(:,:,v)=weights*vectors(:,:,v)
  end do
  counts=[ngap,ngapmax,16];images=0
  call reset_caches();call system_clock(t0,rate)
  call accumulate(1,64)
  call system_clock(t1)
  write(*,*)'BASIS_SPLIT_CONTINUOUS_ROWS_WALL',real(t1-t0,dp)/rate
  baseline=images;images=0
  call reset_caches()
  call accumulate(1,32)
  call write_linear_image_checkpoint('split',context,counts,beta,32,images)
  images=0
  call read_linear_image_checkpoint('split',context,counts,beta,32,images)
  call reset_caches()
  call accumulate(33,64)
  if(any(transfer(images,[0_int64],size(images))/=transfer(baseline,[0_int64],size(images)))) &
    error stop 'Split linear images differ bitwise'
  write(*,'(a)')'BASIS_SWEEP_SPLIT_BITWISE_PASS'
  call write_linear_image_checkpoint('.',context,counts,beta,64,images)
  baseline=0
  call read_linear_image_checkpoint('.',context,counts,beta,64,baseline)
  if(any(transfer(images,[0_int64],size(images))/=transfer(baseline,[0_int64],size(images)))) &
    error stop 'Linear image serialization differs bitwise'
  write(*,'(a)')'BASIS_SWEEP_CHECKPOINT_PASS'
  call environment_end('SCTK')
contains
  subroutine reset_caches()
    call clear_slab();call reset_kel_cache();call reset_phonon_cache()
  end subroutine
  subroutine accumulate(first,last)
    integer,intent(in)::first,last
    integer::next,stopat,column
    real(dp),allocatable::tile(:,:,:)
    do next=first,last,32
      stopat=min(next+31,last)
      allocate(tile(ngap(2),next:stopat,2))
      call build_tile(next,stopat,tile,1)
      do column=1,16
        call dgemv('T',ngap(2),stopat-next+1,1._dp,tile(:,:,1),ngap(2),chi(:,2,column),1, &
          1._dp,images(next:stopat,1,column),1)
        call dgemv('N',ngap(2),stopat-next+1,1._dp,tile(:,:,2),ngap(2),chi(next:stopat,1,column),1, &
          1._dp,images(:,2,column),1)
      end do
      deallocate(tile)
    end do
    if(.not.all(ieee_is_finite(images)))error stop 'Nonfinite linear images'
  end subroutine
end program
