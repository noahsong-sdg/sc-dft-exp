! Indexed equivalent-point lookup for an explicitly uniform reciprocal mesh.
module mesh_equivalence
  use iso_fortran_env, only: real64
  use ieee_arithmetic, only: ieee_is_finite
  implicit none
contains
  subroutine uniform_equivalence_map(nks,nsym,grid,shift,kstep,s,t_rev, &
      time_reversal,colin_mag,xk,xkg,eps,equiv,missing_grid,missing_input)
    integer,intent(in)::nks,nsym,grid(3),shift(3),kstep,s(3,3,48),t_rev(48),colin_mag
    logical,intent(in)::time_reversal
    real(real64),intent(in)::xk(3,nks),xkg(3,product(grid)),eps
    integer,intent(out)::equiv(product(grid)),missing_grid,missing_input
    integer::jk,isym,side,ik,index(3)
    real(real64)::rotated(3),point(3),delta(3),scaled(3)
    logical::seen(nks)
    if(nks<1.or.nsym<1.or.nsym>48.or.kstep<1.or.any(grid<1) &
        .or.any(shift<0).or.any(shift>1).or..not.ieee_is_finite(eps)) &
      error stop 'Invalid uniform-mesh mapping context'
    ! Distinct mesh centres must have disjoint matching neighbourhoods.
    if(eps<=0.or.eps*maxval(grid)>=0.5_real64) &
      error stop 'Ambiguous uniform-mesh tolerance'
    equiv=0;missing_grid=0;missing_input=0
    do jk=1,nks,kstep
      do isym=1,nsym
        rotated=matmul(real(s(:,:,isym),real64),xk(:,jk))
        if(t_rev(isym)==1.and.colin_mag<2)rotated=-rotated
        if(.not.all(ieee_is_finite(rotated)))error stop 'Nonfinite reciprocal point'
        do side=1,merge(2,1,time_reversal)
          point=rotated
          if(side==2)point=-point
          scaled=point*real(grid,real64)-0.5_real64*real(shift,real64)
          if(any(abs(scaled)>real(huge(ik)-2,real64))) &
            error stop 'Reciprocal index exceeds integer range'
          index=modulo(nint(scaled),grid)
          ik=1+index(3)+grid(3)*index(2)+grid(3)*grid(2)*index(1)
          ! Retain the owning comparison, including its floating-point order.
          if(side==1)then
            delta=rotated-xkg(:,ik)-nint(rotated-xkg(:,ik))
          else
            delta=rotated+xkg(:,ik)-nint(rotated+xkg(:,ik))
          end if
          if(sqrt(delta(1)**2+delta(2)**2+delta(3)**2)<eps)then
            if(equiv(ik)==0)equiv(ik)=jk
          end if
        end do
      end do
    end do
    do ik=1,size(equiv)
      if(equiv(ik)==0)then
        missing_grid=ik
        return
      end if
    end do
    seen=.false.
    do ik=1,size(equiv)
      seen(equiv(ik))=.true.
    end do
    do jk=1,nks,kstep
      if(.not.seen(jk))then
        missing_input=jk
        return
      end if
    end do
  end subroutine
end module
