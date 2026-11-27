! Selected-row nonlinear map diagnostic, not an iterative gap solver.
! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
! Uses retained GPL SCTK-derived tiled and uncached native-pair routines.
program nonlinear_map_probe
#ifdef MODE_AMPLITUDE
  use mode_amplitude_probe, only: run_mode_amplitudes
#endif
  use kinds, only: dp
  use environment, only: environment_start, environment_end
  use input_parameters, only: calculation, restart_mode
  use elph_tetra_mod, only: lshift_q
  use constants, only: K_BOLTZMANN_RY, RYTOEV
  use sctk_stdin, only: stdin_control, stdin_scdft
  use sctk_read_file, only: degenerated_band, read_a2Fsave, read_elph
  use sctk_ini_delta, only: energy_grid, ini_delta
  use saved_coulomb, only: read_saved_coulomb, check_saved_coefficients
#ifdef CROSS_PLATFORM_STATE_CHECKS
  use native_state_io_cross_platform, only: verify_initialized_state, read_full_Z
#else
  use native_state_io, only: verify_initialized_state, read_full_Z
#endif
#ifdef FULL_MAP
  use full_nonlinear_probe, only: run_full_map
#endif
  use tiled_operator, only: build_tile
  use slab_operator, only: ensure_slab, clear_slab
  use tc_native_oracle, only: native_pair
  use mp_world, only: nproc
  use sctk_val, only: ngapmax, ngap, nx, nmf, ne, beta, zero_kelvin, Z, delta, &
    xi, dk, dxq, xic, kindx, initial_delta
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical, intent(inout) :: needwf
    end subroutine
  end interface
  character(1024) :: point
  real(dp), allocatable :: full(:,:), chi(:,:), block(:,:,:), image(:)
  real(dp) :: energy, pair(2), direct, error, coefficient_error, bound, start, elapsed
  real(dp) :: weight_reference, weight_error, eoverT
  integer :: unit, trial, first, last, i, j, g, k, sample(4), fermi(2), starts(3), zeros
  logical :: needwf=.false.

  open(newunit=unit,file='map-control.in',status='old')
  read(unit,'(a)')point
  close(unit)
  call environment_start('SCTK')
  if(nproc/=1) error stop 'Selected map requires qualified serial MPI path'
  call stdin_control()
  if(calculation/='scdft'.or.restart_mode/='from_scratch') error stop 'Fresh SCDFT input required'
  call read_file_new(needwf)
  call degenerated_band()
  call read_a2Fsave()
  lshift_q=.true.
  call stdin_scdft()
  if(nx/=100.or.nmf/=10.or.ne/=50.or.initial_delta/='constant') error stop 'Registered grid changed'
  if(.not.zero_kelvin.or.xic>=0) error stop 'Expected original zero-T initialization and xic<0'
  call read_elph()
  call read_saved_coulomb()
  call check_saved_coefficients()
  call energy_grid()
  call ini_delta(.true.)
  call verify_initialized_state(trim(point))
  if(any(dxq/=0)) error stop 'Map control requires Q=0'
  beta=1/(8.05_dp*K_BOLTZMANN_RY)
  zero_kelvin=.false.
  allocate(full(ngapmax,2),chi(ngapmax,2))
  call read_full_Z(trim(point),1,full)
  Z=full
  deallocate(full)
#ifdef MODE_AMPLITUDE
  call run_mode_amplitudes()
#else
  ! Deliberately imposed, energy-dependent seed. This is not a solved gap.
  delta=0
  chi=0
  zeros=0;fermi=0;weight_error=0
  do g=1,2
    do i=1,ngap(g)
      if(fermi(g)==0.and.xi(i,g)==0.and.dk(i,g)>0)fermi(g)=i
      delta(i,g)=0.2_dp/(1000*RYTOEV)/sqrt(1+(xi(i,g)/0.01_dp)**2)
      if(xi(i,g)==0)delta(i,g)=0
      energy=sqrt(xi(i,g)**2+delta(i,g)**2)
      if(energy==0)then
        chi(i,g)=0
        zeros=zeros+1
      else
        chi(i,g)=0.5_dp*dk(i,g)*delta(i,g)*tanh(0.5_dp*beta*energy)/energy
      end if
      ! Separate exponential occupation form, stable for positive energy.
      eoverT=beta*energy
      weight_reference=0
      if(energy/=0)weight_reference=0.5_dp*dk(i,g)*delta(i,g)/energy &
        *(1-exp(-eoverT))/(1+exp(-eoverT))
      weight_error=max(weight_error,abs(weight_reference-chi(i,g)))
    end do
  end do
  if(any(fermi==0).or.zeros==0)error stop 'Missing actual zero-energy boundary control'
  if(.not.all(ieee_is_finite(chi)))error stop 'Nonfinite nonlinear weights'
  if(weight_error>1.e-14_dp)error stop 'Independent nonlinear occupation mismatch'
#ifdef FULL_MAP
  call run_full_map(chi)
#else
  starts=[1,max(1,ngap(1)/2),ngap(1)-7]
  sample=[1,ngap(2)/2,ngap(2),fermi(2)]
  open(newunit=unit,file='selected-map.txt',status='new')
  write(unit,'(a)') '# selected-nonlinear-map-v1; imposed seed; NOT a converged gap'
  write(unit,*)ngap,ngapmax,nx,nmf,ne
  write(unit,*)beta,zeros,weight_error
  call clear_slab()
  do trial=1,3
    first=starts(trial);last=min(first+7,ngap(1))
    allocate(block(ngap(2),first:last,2),image(first:last))
    call cpu_time(start)
    call build_tile(first,last,block,1)
    call cpu_time(elapsed)
    elapsed=elapsed-start
    image=0
    call dgemv('T',ngap(2),last-first+1,1._dp,block(:,:,1),ngap(2),chi(:,2),1,0._dp,image,1)
    error=0;coefficient_error=0
    do i=first,last
      direct=sum(block(:,i,1)*chi(1:ngap(2),2))
      error=max(error,abs(image(i)-direct))
      call ensure_slab(kindx(i,1),1)
      do k=1,4
        j=sample(k)
        call native_pair(i,j,pair)
        coefficient_error=max(coefficient_error,maxval(abs(block(j,i,:)-pair)))
        bound=2.e-13_dp+2.e-12_dp*maxval(abs(pair))
        if(any(abs(block(j,i,:)-pair)>bound))error stop 'Uncached pair mismatch'
      end do
    end do
    bound=2.e-13_dp+2.e-12_dp*maxval(abs(image))
    if(error>bound)error stop 'Explicit sum versus BLAS mismatch'
    image=-image/(1+Z(first:last,1))-delta(first:last,1)
    if(.not.all(ieee_is_finite(image)))error stop 'Nonfinite selected residual'
    write(unit,*)first,last,elapsed,error,coefficient_error,maxval(abs(image))
    deallocate(block,image)
  end do
  close(unit)
#endif
#endif
  call environment_end('SCTK')
end program
