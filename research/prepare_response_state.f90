! Preparation-only diagnostic; no interaction kernels or gap solution.
program prepare_response_state
  use environment, only: environment_start, environment_end
  use input_parameters, only: calculation, restart_mode
  use elph_tetra_mod, only: lshift_q
  use sctk_stdin, only: stdin_control, stdin_scdft
  use sctk_read_file, only: degenerated_band, read_a2Fsave, read_elph
  use sctk_ini_delta, only: energy_grid, ini_delta
  use sctk_val, only: xi, delta, dk, dxq, d2xq, kindx, bindx, ngap, q_fflo, beta
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
  call ini_delta(.true.)

  open(newunit=unit, file='response-state.txt', status='new', action='write')
  write(unit,'(a)') '# preparation-only-v1; initial gap is NOT self-consistent'
  write(unit,*) ngap
  write(unit,*) beta, omega, tpiba
  write(unit,*) q_fflo
  write(unit,*) bg
  do grid = 1, 2
    do state = 1, ngap(grid)
      write(unit,'(5es25.16,3i10)') xi(state,grid), delta(state,grid), &
        dk(state,grid), dxq(state,grid), d2xq(state,grid), &
        grid, kindx(state,grid), bindx(state,grid)
    end do
  end do
  close(unit)
  call environment_end('SCTK')
end program
