! Genuine fresh-state two-channel Z partial sums, not full Z or a response.
! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
program z_partial_driver
  use kinds, only: dp
  use constants, only: K_BOLTZMANN_RY
  use iso_fortran_env, only: int64
  use environment, only: environment_start, environment_end
  use mp_world, only: nproc
  use input_parameters, only: calculation,restart_mode
  use elph_tetra_mod, only: lshift_q
  use sctk_stdin, only: stdin_control,stdin_scdft
  use sctk_read_file, only: degenerated_band,read_a2Fsave,read_elph,read_Coulomb
  use sctk_ini_delta, only: energy_grid,ini_delta
  use native_coefficients, only: check_compact_coefficients
  use native_state_io, only: verify_initialized_state
  use sctk_val, only: ngap,ngapmax,nx,nmf,ne,beta,zero_kelvin,initial_delta,Z,Vc0,nci,lsf
  use slab_operator, only: clear_slab
  use prefix_operator, only: accumulate_Z_block
  use zsf_reuse, only: initialize_zsf_cache,clear_zsf_cache
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical,intent(inout)::needwf
    end subroutine
  end interface
  character(1024)::point
  integer::unit,arm,block,firsts(4),lasts(4)
  integer(int64)::t0,t1,rate
  real(dp),allocatable::direct(:,:)
  real(dp)::elapsed,error
  logical::needwf=.false.
  open(newunit=unit,file='z-control.in',status='old')
  read(unit,'(a)')point
  close(unit)
  call environment_start('SCTK')
  if(nproc/=1)error stop 'Serial Z qualification required'
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
  ! Z requires both renormalization and pairing channels, unlike gap-only residency.
  call read_Coulomb()
  call check_compact_coefficients()
  if(lsf/=2.or.size(Vc0,1)/=2*nci)error stop 'Two transformed channels required for Z'
  call energy_grid()
  call ini_delta(.true.)
  call verify_initialized_state(trim(point))
  if(any(ngap/=[66867,67940]))error stop 'Registered partial rows changed'
  beta=1._dp/(8.05_dp*K_BOLTZMANN_RY)
  zero_kelvin=.false.
  firsts=[1,1+ngap(1)/4,1+ngap(1)/2,ngap(1)-63];lasts=firsts+63
  allocate(Z(ngapmax,2),direct(ngapmax,2))
  call initialize_zsf_cache(65536)
  open(newunit=unit,file='z-partial.meta',status='new')
  write(unit,'(a)') 'fresh-Z-partial-v1; direct then cached; not full Z'
  write(unit,*)ngap,ngapmax
  write(unit,'(es26.17e3)')beta
  do arm=1,2
    Z=0
    do block=1,4
      call clear_slab()
      call clear_zsf_cache()
      call system_clock(t0,rate)
      call accumulate_Z_block(firsts(block),lasts(block),arm==2)
      call system_clock(t1)
      elapsed=real(t1-t0,dp)/real(rate,dp)
      write(unit,*)arm,block,firsts(block),lasts(block),elapsed
      write(*,*)'Z_PARTIAL_BLOCK ',arm,block,firsts(block),lasts(block),elapsed
      flush(unit)
    end do
    if(.not.all(ieee_is_finite(Z)))error stop 'Nonfinite partial Z'
    if(arm==1)direct=Z
  end do
  error=maxval(abs(Z-direct))
  if(error/=0._dp)error stop 'Partial cached/direct accumulation differs'
  write(unit,*)error,256_int64*int(ngap(2),int64)
  close(unit)
  open(newunit=unit,file='z-partial.bin',status='new',access='stream',form='unformatted')
  write(unit)direct,Z
  close(unit)
  write(*,'(a)')'Z_PARTIAL_DIRECT_CACHED_PASS'
  call environment_end('SCTK')
end program
