! Tiny arithmetic diagnostic: original upstream routines, no SCDFT RHS or Z.
PROGRAM grid_probe
  USE kinds, ONLY: dp
  USE constants, ONLY: pi
  USE klist, ONLY: nks
  USE wvfct, ONLY: et
  USE ener, ONLY: ef
  USE el_phon, ONLY: elph_nbnd_min,elph_nbnd_max
  USE sctk_val, ONLY: nx,emin,Zemin,xi0,dx0
  USE sctk_gauss_legendre, ONLY: weightspoints_gl
  USE sctk_ini_delta, ONLY: energy_grid
  IMPLICIT NONE
  CHARACTER(1024) :: path
  INTEGER :: unit,nb,counts(7),nq(3),i
  REAL(dp) :: x(100),w(100),angle(100),seed(100)
  CALL get_command_argument(1,path)
  OPEN(NEWUNIT=unit,FILE=TRIM(path),STATUS='old')
  READ(unit,*) nb,nks
  ALLOCATE(et(nb,nks))
  READ(unit,*) et
  CLOSE(unit)
  CALL get_command_argument(2,path)
  OPEN(NEWUNIT=unit,FILE=TRIM(path),STATUS='old')
  READ(unit,*)
  READ(unit,*) counts
  READ(unit,*) ef
  CLOSE(unit)
  CALL get_command_argument(3,path)
  OPEN(NEWUNIT=unit,FILE=TRIM(path),STATUS='old')
  READ(unit,*) nq
  READ(unit,*) elph_nbnd_min,elph_nbnd_max
  CLOSE(unit)
  nx=100;emin=1.0e-7_dp
  IF(nb/=26) ERROR STOP 'Unexpected frozen bands'
  WRITE(*,'(a,3es26.17e3)') 'GRID_INPUT ',ef,MINVAL(et(elph_nbnd_min:elph_nbnd_max,:)-ef),MAXVAL(et(elph_nbnd_min:elph_nbnd_max,:)-ef)
  CALL weightspoints_gl(100,x,w)
  CALL energy_grid()
  DO i=1,counts(4)
    angle(i)=pi*(REAL(counts(4)-i+1,dp)-0.25_dp)/(REAL(counts(4),dp)+0.5_dp)
    seed(i)=COS(angle(i))
  END DO
  OPEN(NEWUNIT=unit,FILE='grid-probe.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
  WRITE(unit) x,w,xi0,dx0,angle,seed
  CLOSE(unit)
  WRITE(*,'(a,2es26.17e3)') 'GRID_SCALES ',emin,Zemin
END PROGRAM
