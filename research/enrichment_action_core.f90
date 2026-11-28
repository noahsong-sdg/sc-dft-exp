! Ordered A actions and extra P from the same two-orientation kernel tiles.
module enrichment_action_core
  use iso_fortran_env,only:dp=>real64
  use ieee_arithmetic,only:ieee_is_finite
  use streamed_defect_core,only:accumulate_p
  implicit none
contains
  subroutine accumulate_enrichment(left,first,block,w,z,trial,qd,actions,p,next)
    integer,intent(in)::left,first
    real(dp),intent(in),contiguous::block(:,:,:),w(:),z(:),trial(:,:),qd(:,:)
    real(dp),intent(inout),contiguous::actions(:,:),p(:,:)
    integer,intent(inout)::next
    real(dp),allocatable::a(:,:)
    integer::n,right,width,r,i,j
    n=size(w);right=n-left;width=size(block,2);r=size(trial,2)
    if(r<1.or.r>13.or.size(trial,1)/=n.or.any(shape(actions)/=[n,r]).or.any(shape(qd)/=[n,r])) &
      error stop 'Invalid enrichment action geometry'
    if(.not.all(ieee_is_finite(trial)).or..not.all(ieee_is_finite(actions)))error stop 'Nonfinite enrichment input'
    if(first==1.and.any(actions/=0))error stop 'Stale initial enrichment actions'
    ! This checked routine enforces tile geometry, normalization and ordered coverage.
    call accumulate_p(left,first,block,w,z,qd,p,next)
    allocate(a(right,width))
    do j=1,width
      do i=1,right
        a(i,j)=-block(i,j,1)*w(left+i)/(1+z(first+j-1))
      end do
    end do
    call dgemm('T','N',width,r,right,1._dp,a(1,1),right,trial(left+1,1),n,0._dp,actions(first,1),n)
    do j=1,width
      do i=1,right
        a(i,j)=-block(i,j,2)*w(first+j-1)/(1+z(left+i))
      end do
    end do
    call dgemm('N','N',right,r,width,1._dp,a(1,1),right,trial(first,1),n,1._dp,actions(left+1,1),n)
    if(.not.all(ieee_is_finite(actions)))error stop 'Nonfinite enrichment actions'
  end subroutine
end module
