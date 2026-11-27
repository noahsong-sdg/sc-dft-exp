! Genuine upstream initialization and exact serialization roundtrip, not a gap solution.
! Copyright (C) 2026 Noah Song. GNU GPL-2.0-or-later.
program fresh_gap_initialization
  use kinds, only: dp
  use environment, only: environment_start, environment_end
  use input_parameters, only: calculation, restart_mode
  use elph_tetra_mod, only: lshift_q
  use sctk_stdin, only: stdin_control, stdin_scdft
  use sctk_read_file, only: degenerated_band, read_a2Fsave, read_elph
  use sctk_ini_delta, only: energy_grid, ini_delta
  use native_state_io, only: verify_initialized_state, fermi_averages
  use sctk_val, only: ngap, ngapmax, nx, nmf, ne, nqbz, initial_delta, zero_kelvin, &
    xi0, dx0, xi, delta, dk, dxq, d2xq, kindx, bindx, emin, Zemin, beta
  use wvfct, only: nbnd
  use klist, only: nks
  use ener, only: ef
  use mp_world, only: nproc
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical, intent(inout) :: needwf
    end subroutine
  end interface
  logical :: needwf=.false.
  integer :: unit
  real(dp) :: denominator(2)

  call environment_start('SCTK')
  if(nproc/=1) error stop 'Serial fresh initialization required'
  call stdin_control()
  if(calculation/='scdft'.or.restart_mode/='from_scratch') error stop 'Fresh SCDFT input required'
  call read_file_new(needwf)
  call degenerated_band()
  call read_a2Fsave()
  lshift_q=.true.
  call stdin_scdft()
  if(nx/=100.or.nmf/=10.or.ne/=50.or.initial_delta/='constant'.or..not.zero_kelvin) &
    error stop 'Registered fresh initialization context changed'
  call read_elph()
  call energy_grid()
  call ini_delta(.true.)
  if(any(dxq/=0).or.any(d2xq/=0)) error stop 'Expected fresh Q0 state'
  call fermi_averages(denominator)
  ! Same public native-init-v1 schema, produced from current arrays, never old bytes.
  open(newunit=unit,file='native-init.meta',status='new')
  write(unit,'(a)') 'native-init-v1; arrays are native binary64/int32, Fortran order'
  write(unit,*) ngap,ngapmax,nx,nqbz,nbnd,nks
  write(unit,'(7es26.17e3)') ef,emin,Zemin,beta,denominator,maxval(abs(delta))
  write(unit,*) zero_kelvin
  close(unit)
  open(newunit=unit,file='native-init.bin',status='new',access='stream',form='unformatted')
  write(unit) xi0,dx0,xi,delta,dk,dxq,d2xq,kindx,bindx
  close(unit)
  call verify_initialized_state('.')
  write(*,'(a)') 'FRESH_GAP_INITIALIZATION_ROUNDTRIP_PASS'
  call environment_end('SCTK')
end program
