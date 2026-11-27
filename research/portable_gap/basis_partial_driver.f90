! Bounded fresh-basis operator timing and independent uncached controls.
! Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
program basis_partial_driver
  use kinds,only:dp
  use constants,only:K_BOLTZMANN_RY
  use environment,only:environment_start,environment_end
  use mp_world,only:nproc
  use input_parameters,only:calculation,restart_mode
  use elph_tetra_mod,only:lshift_q
  use sctk_stdin,only:stdin_control,stdin_scdft
  use sctk_read_file,only:degenerated_band,read_a2Fsave,read_elph
  use sctk_ini_delta,only:energy_grid,ini_delta
  use saved_coulomb,only:read_saved_coulomb,check_saved_coefficients
  use native_state_io,only:verify_initialized_state,read_full_Z
  use sctk_val,only:ngap,ngapmax,nx,nmf,ne,beta,zero_kelvin,initial_delta,Z,kindx
  use tc_subspace,only:make_trials
  use block_linear_operator,only:linear_weights
  use tiled_operator,only:build_tile
  use slab_operator,only:ensure_slab,clear_slab
  use tc_native_oracle,only:native_pair
  use,intrinsic::ieee_arithmetic,only:ieee_is_finite
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical,intent(inout)::needwf
    end subroutine
  end interface
  character(1024)::geometry,completed
  integer::unit,b,first,last,v,i,j,k,starts(4),left(3),right(3),rate,t0,t1
  real(dp),allocatable::full(:,:),vectors(:,:,:),images(:,:,:),weights(:,:),chi(:,:,:),tile(:,:,:)
  real(dp)::pair(2),direct(3),prior(3),error,bound,seconds(4),reference,largest
  logical::needwf=.false.
  open(newunit=unit,file='basis-partial-control.in',status='old')
  read(unit,'(a)')geometry
  read(unit,'(a)')completed
  close(unit)
  call environment_start('SCTK')
  if(nproc/=1)error stop 'Serial basis qualification required'
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
  call make_trials(vectors,16,29)
  call linear_weights(weights)
  do v=1,16
    chi(:,:,v)=weights*vectors(:,:,v)
  end do
  images=0;error=0;largest=0
  starts=[1,16717,33434,66804];right=[1,ngap(2)/2,ngap(2)]
  call clear_slab();call system_clock(count_rate=rate)
  do b=1,4
    first=starts(b);last=first+63;left=[first,first+31,last]
    allocate(tile(ngap(2),first:last,2))
    prior=images(right,2,1)
    call system_clock(t0)
    call build_tile(first,last,tile,1)
    do v=1,16
      call dgemv('T',ngap(2),64,1._dp,tile(:,:,1),ngap(2),chi(:,2,v),1, &
        1._dp,images(first:last,1,v),1)
      call dgemv('N',ngap(2),64,1._dp,tile(:,:,2),ngap(2),chi(first:last,1,v),1, &
        1._dp,images(:,2,v),1)
    end do
    call system_clock(t1);seconds(b)=real(t1-t0,dp)/rate
    ! Independently reconstruct complete selected left sums with uncached pairs.
    do k=1,3
      i=left(k);reference=0
      call ensure_slab(kindx(i,1),1)
      do j=1,ngap(2)
        call native_pair(i,j,pair)
        reference=reference+pair(1)*chi(j,2,1)
      end do
      error=max(error,abs(images(i,1,1)-reference));largest=max(largest,abs(reference))
    end do
    direct=0
    do i=first,last
      call ensure_slab(kindx(i,1),1)
      do k=1,3
        j=right(k);call native_pair(i,j,pair)
        direct(k)=direct(k)+pair(2)*chi(i,1,1)
      end do
    end do
    error=max(error,maxval(abs(images(right,2,1)-prior-direct)))
    largest=max(largest,maxval(abs(direct)))
    deallocate(tile)
    write(*,*)'BASIS_PARTIAL_BLOCK_WALL',first,last,seconds(b)
    flush(6)
  end do
  bound=2.e-13_dp+2.e-12_dp*largest
  if(error>bound.or..not.all(ieee_is_finite(images)))error stop 'Uncached partial basis mismatch'
  do v=1,16
    images(:,:,v)=-images(:,:,v)/(1._dp+Z)
  end do
  open(newunit=unit,file='basis-partial.meta',status='new')
  write(unit,'(a)')'fresh-basis-partial-v1; four64row blocks; not full images or solved gap'
  write(unit,*)ngap,ngapmax,16,29
  write(unit,*)beta,error,bound,seconds
  close(unit)
  open(newunit=unit,file='basis-partial.bin',status='new',access='stream',form='unformatted')
  write(unit)vectors,images
  close(unit)
  write(*,'(a)')'BASIS_PARTIAL_UNCACHED_CONTROL_PASS'
  call environment_end('SCTK')
end program
