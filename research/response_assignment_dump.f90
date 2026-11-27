! Native response assignment export; no gap transfer or physical prediction.
! Counting/assignment path follows SCTK sctk_ini_delta::compute_d3k.
! Original Copyright (C) 2017 Mitsuaki Kawamura.
! Diagnostic Copyright (C) 2026 Noah Song. GPL-2.0-or-later.
module response_assignment_dump
  use kinds, only: dp
  use sctk_ini_delta, only: store_d3k
  use sctk_val, only: nx,nqbz,fbee,lbee,xi0,dx0
  use el_phon, only: elph_nbnd_min,elph_nbnd_max
  implicit none
contains
  subroutine dump_assignment(dos,velocity,curvature,q,volume)
    real(dp),intent(in) :: dos(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2)
    real(dp),intent(in) :: velocity(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2)
    real(dp),intent(in) :: curvature(nx,elph_nbnd_min:elph_nbnd_max,nqbz,2),q,volume
    real(dp),allocatable :: x(:,:),weight(:,:),v(:,:),h(:,:)
    integer,allocatable :: k(:,:),band(:,:)
    integer :: counts(2),maximum,g,ik,ib,unit
    counts=0
    do g=1,2
      do ik=1,nqbz
        do ib=fbee,lbee
          if(elph_nbnd_min<=ib.and.ib<=elph_nbnd_max)then
            counts(g)=counts(g)+max(1,count(dos(:,ib,ik,g)>1.e-12_dp))
          else
            counts(g)=counts(g)+1
          end if
        end do
      end do
    end do
    maximum=maxval(counts)
    allocate(x(maximum,2),weight(maximum,2),v(maximum,2),h(maximum,2),k(maximum,2),band(maximum,2))
    x=0;weight=0;v=0;h=0;k=0;band=0
    do g=1,2
      call store_d3k(dos(:,:,:,g),velocity(:,:,:,g),curvature(:,:,:,g),real(g-1,dp)/2, &
        counts(g),x(:counts(g),g),weight(:counts(g),g),k(:counts(g),g), &
        band(:counts(g),g),v(:counts(g),g),h(:counts(g),g))
    end do
    open(newunit=unit,file='response-assignment.txt',status='new')
    write(unit,'(a)') '# response-assignment-v1; native geometry only; NOT a gap transfer'
    write(unit,*) counts,maximum,nx,nqbz,fbee,lbee
    write(unit,*) q,volume
    close(unit)
    open(newunit=unit,file='response-assignment.bin',status='new',access='stream',form='unformatted')
    write(unit) xi0,dx0,x,weight,v,h,k,band
    close(unit)
  end subroutine
end module
