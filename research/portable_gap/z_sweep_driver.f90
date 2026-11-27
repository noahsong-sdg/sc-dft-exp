! Exact ordered continuation of genuine finite-temperature Z, not a gap solution.
! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
program z_sweep_driver
  use kinds,only:dp
  use constants,only:K_BOLTZMANN_RY
  use iso_fortran_env,only:int64
  use io_global,only:stdout
  use environment,only:environment_start,environment_end
  use mp_world,only:nproc
  use input_parameters,only:calculation,restart_mode
  use elph_tetra_mod,only:lshift_q
  use sctk_stdin,only:stdin_control,stdin_scdft
  use sctk_read_file,only:degenerated_band,read_a2Fsave,read_elph,read_Coulomb
  use sctk_ini_delta,only:energy_grid,ini_delta
  use native_coefficients,only:check_compact_coefficients
  use native_state_io,only:verify_initialized_state,write_full_Z
  use sctk_val,only:ngap,ngapmax,nx,nmf,ne,beta,zero_kelvin,initial_delta,Z,Vc0,nci,lsf
  use slab_operator,only:clear_slab
  use prefix_operator,only:accumulate_Z_block
  use zsf_reuse,only:initialize_zsf_cache,clear_zsf_cache
  use z_checkpoint,only:write_z_checkpoint,read_z_checkpoint
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical,intent(inout)::needwf
    end subroutine
  end interface
  character(1024)::point,previous
  character(64)::context
  character(32)::mode,header
  integer::unit,first,last,counts(3),next,stopat
  integer(int64)::t0,t1,rate
  real(dp),allocatable::uninterrupted(:,:)
  logical::needwf=.false.
  open(newunit=unit,file='z-sweep-control.in',status='old')
  read(unit,'(a)')header
  if(trim(header)/='fresh-Z-sweep-control-v1')error stop 'Stale Z sweep control'
  read(unit,'(a)')point
  read(unit,'(a)')context
  read(unit,*)first,last
  read(unit,'(a)')previous
  read(unit,'(a)')mode
  close(unit)
  if(mode/='qualify'.and.mode/='sweep')error stop 'Invalid Z sweep mode'
  call environment_start('SCTK')
  if(nproc/=1)error stop 'Serial ordered Z sweep required'
  call stdin_control()
  if(calculation/='scdft'.or.restart_mode/='from_scratch')error stop 'Fresh SCDFT required'
  call read_file_new(needwf)
  call degenerated_band()
  call read_a2Fsave()
  lshift_q=.true.
  call stdin_scdft()
  if(nx/=100.or.nmf/=10.or.ne/=50.or.initial_delta/='constant'.or..not.zero_kelvin) &
    error stop 'Registered initialization changed'
  call read_elph()
  call read_Coulomb()
  call check_compact_coefficients()
  if(lsf/=2.or.size(Vc0,1)/=2*nci)error stop 'Two transformed channels required for Z'
  call energy_grid()
  call ini_delta(.true.)
  call verify_initialized_state(trim(point))
  counts=[ngap,ngapmax]
  if(any(ngap/=[66867,67940]).or.first<1.or.last<first.or.last>ngap(1))error stop 'Invalid Z sweep interval'
  beta=1._dp/(8.05_dp*K_BOLTZMANN_RY)
  zero_kelvin=.false.
  allocate(Z(ngapmax,2))
  Z=0
  if(first==1)then
    if(previous/='-')error stop 'First Z batch cannot consume a predecessor'
  else
    if(previous=='-')error stop 'Missing Z predecessor'
    call read_z_checkpoint(trim(previous),context,counts,beta,first-1,Z)
  end if
  call initialize_zsf_cache(65536)
  call system_clock(t0,rate)
  do next=first,last,1024
    stopat=min(next+1023,last)
    call accumulate_Z_block(next,stopat,.true.)
    write(stdout,*)'Z_SWEEP_PROGRESS ',stopat,ngap(1)
    flush(stdout)
  end do
  call system_clock(t1)
  write(*,*)'Z_SWEEP_ROWS_WALL ',first,last,real(t1-t0,dp)/real(rate,dp)
  if(mode=='qualify')then
    if(first/=1.or.last/=16)error stop 'Registered split qualification is rows1:16'
    allocate(uninterrupted(ngapmax,2));uninterrupted=Z
    Z=0
    call clear_slab();call clear_zsf_cache()
    call accumulate_Z_block(1,8,.true.)
    call write_z_checkpoint('split',context,counts,beta,8,Z)
    Z=0
    call read_z_checkpoint('split',context,counts,beta,8,Z)
    call clear_slab();call clear_zsf_cache()
    call accumulate_Z_block(9,16,.true.)
    if(any(transfer(Z,[0_int64],size(Z))/=transfer(uninterrupted,[0_int64],size(Z)))) &
      error stop 'Split Z traversal differs bitwise'
    write(*,'(a)')'Z_SWEEP_SPLIT_BITWISE_PASS'
  end if
  call write_z_checkpoint('.',context,counts,beta,last,Z)
  if(.not.allocated(uninterrupted))allocate(uninterrupted(ngapmax,2))
  call read_z_checkpoint('.',context,counts,beta,last,uninterrupted)
  if(any(transfer(Z,[0_int64],size(Z))/=transfer(uninterrupted,[0_int64],size(Z)))) &
    error stop 'Z checkpoint serialization differs bitwise'
  if(last==ngap(1))call write_full_Z(1)
  write(*,'(a)')'Z_SWEEP_CHECKPOINT_PASS'
  call environment_end('SCTK')
end program
