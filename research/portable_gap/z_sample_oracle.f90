! Independent uncached full sums at first/last/Fermi samples on both state grids.
! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
program z_sample_oracle
  use kinds,only:dp
  use constants,only:K_BOLTZMANN_RY
  use iso_fortran_env,only:int64
  use environment,only:environment_start,environment_end
  use mp_world,only:nproc
  use input_parameters,only:calculation,restart_mode
  use elph_tetra_mod,only:lshift_q
  use sctk_stdin,only:stdin_control,stdin_scdft
  use sctk_read_file,only:degenerated_band,read_a2Fsave,read_elph,read_Coulomb
  use sctk_ini_delta,only:energy_grid,ini_delta
  use native_coefficients,only:check_compact_coefficients
  use native_state_io,only:verify_initialized_state,read_full_Z,freeze_samples
  use sctk_val,only:ngap,ngapmax,nx,nmf,ne,beta,zero_kelvin,initial_delta,Z,xi,dk,kindx,bindx
  use slab_operator,only:clear_slab
  use native_oracle_z,only:make_Z
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical,intent(inout)::needwf
    end subroutine
  end interface
  character(1024)::point,completed
  integer::unit,side,i,j,full_counts(2),samples(3,2),sample_counts(2)
  integer,allocatable::saved_k(:,:),saved_b(:,:)
  real(dp),allocatable::full(:,:),saved_xi(:,:),saved_dk(:,:)
  real(dp)::expected(3,2),actual(3,2)
  logical::needwf=.false.
  open(newunit=unit,file='z-oracle-control.in',status='old')
  read(unit,'(a)')point
  read(unit,'(a)')completed
  close(unit)
  call environment_start('SCTK')
  if(nproc/=1)error stop 'Serial Z oracle required'
  call stdin_control()
  if(calculation/='scdft'.or.restart_mode/='from_scratch')error stop 'Fresh SCDFT required'
  call read_file_new(needwf)
  call degenerated_band()
  call read_a2Fsave()
  lshift_q=.true.
  call stdin_scdft()
  if(nx/=100.or.nmf/=10.or.ne/=50.or.initial_delta/='constant'.or..not.zero_kelvin) &
    error stop 'Registered initialization changed'
  call read_elph();call read_Coulomb();call check_compact_coefficients()
  call energy_grid();call ini_delta(.true.)
  call verify_initialized_state(trim(point))
  beta=1._dp/(8.05_dp*K_BOLTZMANN_RY);zero_kelvin=.false.
  allocate(full(ngapmax,2))
  call read_full_Z(trim(completed),1,full)
  call freeze_samples(samples,sample_counts)
  if(any(sample_counts/=3))error stop 'Six independent full-sum samples required'
  full_counts=ngap;saved_xi=xi;saved_dk=dk;saved_k=kindx;saved_b=bindx
  do side=1,2
    ngap=full_counts;xi=saved_xi;dk=saved_dk;kindx=saved_k;bindx=saved_b
    xi(:,side)=0;dk(:,side)=0;kindx(:,side)=0;bindx(:,side)=0
    ngap(side)=3
    do i=1,3
      j=samples(i,side)
      xi(i,side)=saved_xi(j,side);dk(i,side)=saved_dk(j,side)
      kindx(i,side)=saved_k(j,side);bindx(i,side)=saved_b(j,side)
      expected(i,side)=full(j,side)
    end do
    call clear_slab()
    call make_Z()
    actual(:,side)=Z(:3,side)
  end do
  if(any(transfer(expected,[0_int64],6)/=transfer(actual,[0_int64],6))) &
    error stop 'Uncached full-sum Z samples differ bitwise'
  ngap=full_counts;xi=saved_xi;dk=saved_dk;kindx=saved_k;bindx=saved_b;Z=full
  call read_full_Z(trim(completed),1,full)
  open(newunit=unit,file='z-oracle-samples.bin',status='new',access='stream',form='unformatted')
  write(unit)expected,actual
  close(unit)
  write(*,'(a)')'Z_SIX_UNCACHED_FULL_SUMS_BITWISE_PASS'
  call environment_end('SCTK')
end program
