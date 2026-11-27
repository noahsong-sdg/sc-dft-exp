! Serialize existing XML bands through the owning QE reader and writer.
program a2f_serialization
  use environment, only: environment_start, environment_end
  use mp_world, only: nproc
  use sctk_stdin, only: stdin_control
  use a2f, only: a2Fsave
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical, intent(inout) :: needwf
    end subroutine
  end interface
  logical :: needwf=.false.
  call environment_start('SCTK')
  if(nproc/=1) error stop 'Serial band serialization required'
  call stdin_control()
  call read_file_new(needwf)
  call a2Fsave()
  call environment_end('SCTK')
end program
