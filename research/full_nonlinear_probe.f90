! Full Q0 map/Jacobian diagnostic with an imposed seed, GPL-2.0-or-later.
module full_nonlinear_probe
  use kinds, only: dp
  use nonlinear_tile_apply, only: apply_tile
  use tiled_operator, only: build_tile
  use slab_operator, only: clear_slab
  use sctk_val, only: ngap,ngapmax,delta,xi,dk,beta,Z
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
contains
  subroutine run_full_map(seed_weights)
    real(dp),intent(in) :: seed_weights(:,:)
    real(dp),allocatable :: weights(:,:,:),result(:,:,:),block(:,:,:),direction(:,:),jacobian(:,:)
    real(dp) :: h,energy,t,derivative,fd_error,jbound,start,elapsed,reference,error,before(3,4)
    integer :: g,i,first,last,unit,progress,k,sample(3)
    h=1.e-8_dp
    allocate(weights(ngapmax,2,4),result(ngapmax,2,4),direction(ngapmax,2),jacobian(ngapmax,2))
    weights=0;result=0;direction=0;jacobian=0
    weights(:,:,1)=seed_weights
    do g=1,2
      do i=1,ngap(g)
        ! Different signed sides prevent a symmetry control hiding index errors.
        direction(i,g)=real(3-2*g,dp)/sqrt(1+(xi(i,g)/0.01_dp)**2)
        weights(i,g,2)=occupation(dk(i,g),xi(i,g),delta(i,g)+h*direction(i,g))
        weights(i,g,3)=occupation(dk(i,g),xi(i,g),delta(i,g)-h*direction(i,g))
        energy=hypot(xi(i,g),delta(i,g))
        if(energy==0)then
          derivative=dk(i,g)*beta/4
        else
          t=tanh(beta*energy/2)
          derivative=dk(i,g)/2*((xi(i,g)/energy)**2*t/energy &
            +beta/2*(delta(i,g)/energy)**2*(1-t*t))
        end if
        weights(i,g,4)=derivative*direction(i,g)
      end do
    end do
    if(.not.all(ieee_is_finite(weights)))error stop 'Nonfinite full-map weights'
    open(newunit=progress,file='full-map-progress.txt',status='new')
    call clear_slab()
    call cpu_time(start)
    error=0
    sample=[1,ngap(2)/2,ngap(2)]
    do first=1,ngap(1),32
      last=min(first+31,ngap(1))
      allocate(block(ngap(2),first:last,2))
      call build_tile(first,last,block,1)
      before=result(sample,2,:)
      call apply_tile(block,first,ngap(1),ngap(2),weights,result)
      ! Both orientations: left row and right partial sum, independently summed.
      reference=sum(block(:,first,1)*weights(1:ngap(2),2,1))
      error=max(error,abs(result(first,1,1)-reference))
      ! Verify each batch's tile contribution before accumulated right-side sums.
      do k=1,4
        do i=1,3
          reference=sum(block(sample(i),:,2)*weights(first:last,1,k))
          error=max(error,abs(result(sample(i),2,k)-before(i,k)-reference))
        end do
      end do
      deallocate(block)
      if(mod(first-1,1024)==0.or.last==ngap(1))then
        call cpu_time(elapsed)
        write(progress,*)last,ngap(1),elapsed-start
        flush(progress)
      end if
    end do
    call cpu_time(elapsed)
    close(progress)
    do g=1,2
      do k=1,4
        result(1:ngap(g),g,k)=-result(1:ngap(g),g,k)/(1+Z(1:ngap(g),g))
      end do
      result(1:ngap(g),g,1)=result(1:ngap(g),g,1)-delta(1:ngap(g),g)
      result(1:ngap(g),g,2)=result(1:ngap(g),g,2)-delta(1:ngap(g),g)-h*direction(1:ngap(g),g)
      result(1:ngap(g),g,3)=result(1:ngap(g),g,3)-delta(1:ngap(g),g)+h*direction(1:ngap(g),g)
      jacobian(1:ngap(g),g)=result(1:ngap(g),g,4)-direction(1:ngap(g),g)
    end do
    if(.not.all(ieee_is_finite(result)).or..not.all(ieee_is_finite(jacobian))) &
      error stop 'Nonfinite full-map result'
    fd_error=maxval(abs((result(:,:,2)-result(:,:,3))/(2*h)-jacobian))
    jbound=1.e-8_dp+2.e-6_dp*maxval(abs(jacobian))
    if(fd_error>jbound)error stop 'Full native Jacobian finite difference mismatch'
    if(error>2.e-13_dp+2.e-12_dp*maxval(abs(result(:,:,1)+delta))) &
      error stop 'Full-map left explicit-sum mismatch'
    open(newunit=unit,file='full-map.txt',status='new')
    write(unit,'(a)') '# full-nonlinear-map-v1; imposed seed; NOT a converged gap'
    write(unit,*)ngap,ngapmax,size(weights,3)
    write(unit,*)beta,h,elapsed-start,error,fd_error,jbound
    do g=1,2
      write(unit,*)g,maxval(abs(result(1:ngap(g),g,1))), &
        sqrt(sum(result(1:ngap(g),g,1)**2)/ngap(g)),maxval(abs(jacobian(1:ngap(g),g)))
    end do
    close(unit)
    open(newunit=unit,file='full-map.bin',status='new',access='stream',form='unformatted')
    write(unit)delta,result(:,:,1),direction,jacobian
    close(unit)
  end subroutine

  real(dp) function occupation(weight,x,d)
    real(dp),intent(in) :: weight,x,d
    real(dp) :: energy
    energy=hypot(x,d)
    occupation=0
    if(energy/=0)occupation=weight*d/2*tanh(beta*energy/2)/energy
  end function
end module
