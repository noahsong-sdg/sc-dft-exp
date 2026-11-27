! Diagnostic only: constant-gap closure at matched energy quadrature.
! Interpolation adapted from SCTK sctk_ini_delta.f90:
! Copyright (C) 2017 Mitsuaki Kawamura.
! Distributed under the GNU General Public License; see licenses/GPL-2.0.txt.
! Diagnostic extensions Copyright (C) 2026 Noah Song, under the same license.
program velocity_moment_probe
#ifdef ASSIGNMENT_DUMP
  use response_assignment_dump, only: dump_assignment
#endif
  use kinds, only: dp
  use environment, only: environment_start, environment_end
  use mp_world, only: nproc
  use input_parameters, only: calculation, restart_mode
  use elph_tetra_mod, only: lshift_q
  use sctk_stdin, only: stdin_control, stdin_scdft
  use sctk_read_file, only: degenerated_band, read_a2Fsave, read_elph
  use sctk_ini_delta, only: energy_grid
#ifdef CURRENT_GEOMETRY
  use sctk_current_moment_geometry, only: compute_dosk, symm_dosk, calc_d_xi_q
#else
  use sctk_ini_delta, only: compute_dosk, symm_dosk, calc_d_xi_q
#endif
  use sctk_tetra, only: calc_dosk, interpol_indx
  use sctk_val, only: nx, nqbz, xi0, dx0, d_et, d2_et, q_fflo
  use wvfct, only: et, nbnd
  use klist, only: nks
  use start_k, only: nk1, nk2, nk3
  use disp, only: nq1, nq2, nq3
  use el_phon, only: elph_nbnd_min, elph_nbnd_max
  use cell_base, only: omega, bg, tpiba
  implicit none
  interface
    subroutine read_file_new(needwf)
      logical, intent(inout) :: needwf
    end subroutine
  end interface
  logical :: needwf=.false.
  integer :: ik,ib,ix,g,i8,iv(3),ki(8),u,t,grid,status
  character(32) :: grid_text
  real(dp) :: kv(3),wi(8),q,qv(3),beta,gap,e,thermal,curvature,w
  real(dp) :: first_s(2),second_s(2),all_s(2),fine_s(3),errors(3)
  real(dp),allocatable :: bands(:,:),fine(:,:,:),dos(:,:,:,:),m1(:,:,:,:),m2(:,:,:,:),h(:,:,:,:)
  real(dp),allocatable :: check_d(:,:,:,:),check_v(:,:,:,:),check_h(:,:,:,:),copy_d(:,:,:,:),zero(:,:,:,:)

  call environment_start('SCTK')
  if(nproc/=1) error stop 'Moment diagnostic currently qualified for serial execution only'
  call stdin_control()
  if(calculation/='scdft'.or.restart_mode/='from_scratch') error stop 'Fresh SCDFT input required'
  call read_file_new(needwf)
  call degenerated_band()
  call read_a2Fsave()
  lshift_q=.true.
  call stdin_scdft()
  call read_elph()
  call energy_grid()
  ! Refine only response-cell interpolation; retained phonon inputs are unchanged.
  call get_environment_variable('SCTK_MOMENT_GRID',grid_text,status=status)
  if(status==0) then
    read(grid_text,*,iostat=status) grid
    if(status/=0) error stop 'Invalid response-cell grid'
    if(grid<=0) error stop 'Positive response-cell grid required'
    if(any(mod([nk1,nk2,nk3],grid)/=0)) error stop 'Response grid must divide the native fine grid'
    nq1=grid;nq2=grid;nq3=grid;nqbz=grid**3
  else if(status/=1) then
    error stop 'Truncated or inaccessible response-cell grid setting'
  end if
  qv=matmul(bg,q_fflo)*tpiba
  q=sqrt(sum(qv*qv))
  if(q==0) error stop 'Nonzero directional contraction required'
  allocate(bands(nbnd,nks));bands=et(:,1:nks)
  call calc_d_xi_q()
  allocate(fine(nx,elph_nbnd_min:elph_nbnd_max,nks))
  call calc_dosk(fine)
  allocate(dos(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2))
  allocate(m1,m2,h,check_d,check_v,check_h,copy_d,zero,mold=dos)
  dos=0;m1=0;m2=0;h=0
  do ik=1,nks
    iv(1)=(ik-1)/(nk2*nk3)
    iv(2)=(ik-1-iv(1)*nk2*nk3)/nk3
    iv(3)=ik-1-iv(1)*nk2*nk3-iv(2)*nk3
    do g=1,2
      kv=real(iv,dp)/real([nk1,nk2,nk3],dp)-real(g-1,dp)*0.5_dp/real([nq1,nq2,nq3],dp)
      call interpol_indx([nq1,nq2,nq3],kv,ki,wi)
      do ib=elph_nbnd_min,elph_nbnd_max
        do i8=1,8
          dos(:,ib,ki(i8),g)=dos(:,ib,ki(i8),g)+fine(:,ib,ik)*wi(i8)
          m1(:,ib,ki(i8),g)=m1(:,ib,ki(i8),g)+fine(:,ib,ik)*d_et(ib,ik)*wi(i8)
          m2(:,ib,ki(i8),g)=m2(:,ib,ki(i8),g)+fine(:,ib,ik)*d_et(ib,ik)**2*wi(i8)
          h(:,ib,ki(i8),g)=h(:,ib,ki(i8),g)+fine(:,ib,ik)*d2_et(ib,ik)*wi(i8)
        end do
      end do
    end do
  end do
  ! Fine-grid reference uses the SAME energy quadrature and constant gap.
  gap=1.5_dp/13605.693122994_dp
  fine_s=0
  do t=1,3
    beta=157887.51240203338_dp/real(2**t,dp)
    do ik=1,nks
      do ib=elph_nbnd_min,elph_nbnd_max
        do ix=1,nx
          call coefficients(xi0(ix),gap,beta,thermal,curvature)
          fine_s(t)=fine_s(t)+fine(ix,ib,ik)*dx0(ix)* &
            (thermal*d_et(ib,ik)**2+curvature*d2_et(ib,ik))/(omega*q*q)
        end do
      end do
    end do
  end do
  open(newunit=u,file='velocity-moments.txt',status='new')
  write(u,'(a)') '# velocity-moment-diagnostic-v1; imposed constant gap; NOT a material prediction'
  write(u,*) nx,elph_nbnd_min,elph_nbnd_max,nks,nqbz
  write(u,*) q,omega
  write(u,*) count(fine<0),sum(abs(fine),mask=fine<0),sum(abs(fine))
  deallocate(fine)
  copy_d=dos;zero=0
  call symm_dosk(dos,m1,h)
  call symm_dosk(copy_d,m2,zero)
  ! Reconstruct the owning routine independently, starting from immutable bands.
  et(:,1:nks)=bands
  deallocate(d_et,d2_et)
  call compute_dosk(check_d,check_v,check_h)
  errors=[maxval(abs(dos-check_d)),0._dp,0._dp]
  do g=1,2
    do ik=1,nqbz
      do ib=elph_nbnd_min,elph_nbnd_max
        do ix=1,nx
          if(dos(ix,ib,ik,g)<=1.e-12_dp) cycle
          errors(2)=max(errors(2),abs(m1(ix,ib,ik,g)/dos(ix,ib,ik,g)-check_v(ix,ib,ik,g)))
          errors(3)=max(errors(3),abs(h(ix,ib,ik,g)/dos(ix,ib,ik,g)-check_h(ix,ib,ik,g)))
        end do
      end do
    end do
  end do
  write(u,*) errors
#ifdef ASSIGNMENT_DUMP
  call dump_assignment(dos,check_v,check_h,q,omega)
#endif
  do t=1,3
    beta=157887.51240203338_dp/real(2**t,dp)
    first_s=0;second_s=0;all_s=0
    do g=1,2
      do ik=1,nqbz
        do ib=elph_nbnd_min,elph_nbnd_max
          do ix=1,nx
            call coefficients(xi0(ix),gap,beta,thermal,curvature)
            w=dx0(ix)/(omega*q*q)
            all_s(g)=all_s(g)+w*(thermal*m2(ix,ib,ik,g)+curvature*h(ix,ib,ik,g))
            if(dos(ix,ib,ik,g)<=1.e-12_dp) cycle
            first_s(g)=first_s(g)+w*(thermal*m1(ix,ib,ik,g)**2/dos(ix,ib,ik,g)+curvature*h(ix,ib,ik,g))
            second_s(g)=second_s(g)+w*(thermal*m2(ix,ib,ik,g)+curvature*h(ix,ib,ik,g))
          end do
        end do
      end do
    end do
    write(u,*) 2**t,first_s,second_s,all_s,fine_s(t)
  end do
  close(u)
  call environment_end('SCTK')
contains
  subroutine coefficients(x,gap,beta,thermal,curvature)
    real(dp),intent(in) :: x,gap,beta
    real(dp),intent(out) :: thermal,curvature
    real(dp) :: e
    e=sqrt(x*x+gap*gap)
    thermal=beta*(sech2(0.5_dp*beta*x)-sech2(0.5_dp*beta*e))
    curvature=4*(sign(tanh(0.5_dp*beta*abs(x)),x)-x/e*tanh(0.5_dp*beta*e))
  end subroutine
  function sech2(x) result(value)
    real(dp),intent(in) :: x
    real(dp) :: value,tail
    tail=exp(-2*abs(x));value=4*tail/(1+tail)**2
  end function
end program
