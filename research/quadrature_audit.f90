! Fresh native quadrature audit; no Coulomb reader, gap geometry or saved-Z reuse.
program quadrature_audit
  use environment, only: environment_start, environment_end
  use input_parameters, only: calculation, restart_mode
  use elph_tetra_mod, only: lshift_q
  use sctk_stdin, only: stdin_control, stdin_scdft
  use sctk_read_file, only: degenerated_band, read_a2Fsave, read_elph
  use sctk_ini_delta, only: energy_grid, ini_delta
  use sctk_val, only: xi0,dx0
  use cell_base, only: omega, bg, tpiba
  implicit none
  integer :: unit, grid, state
  logical :: needwf = .false.
  interface
    subroutine read_file_new(needwf)
      logical, intent(inout) :: needwf
    end subroutine
  end interface

  call environment_start('SCTK')
  call stdin_control()
  if (calculation /= 'scdft' .or. restart_mode /= 'from_scratch') &
    error stop 'Preparation requires a fresh SCDFT state'
  call read_file_new(needwf)
  call degenerated_band()
  call read_a2Fsave()
  lshift_q = .true.
  call stdin_scdft()
  call read_elph()
  call energy_grid()
  open(newunit=unit,file='quadrature.bin',status='new',access='stream',form='unformatted')
  write(unit) xi0,dx0
  close(unit)
  call environment_end('SCTK')
end program
