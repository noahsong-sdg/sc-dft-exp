! Batched rectangular kernel application; GPL-2.0-or-later.
module nonlinear_tile_apply
  use iso_fortran_env, only: real64
  implicit none
contains
  subroutine apply_tile(block,first,nleft,nright,weights,result)
    integer,intent(in) :: first,nleft,nright
    real(real64),intent(in) :: block(:,:,:),weights(:,:,:)
    real(real64),intent(inout) :: result(:,:,:)
    integer :: width,k,last
    width=size(block,2);last=first+width-1
    if(first<1.or.last>nleft.or.size(block,1)/=nright.or.size(block,3)/=2) &
      error stop 'Invalid rectangular kernel tile'
    if(size(weights,1)<max(nleft,nright).or.size(weights,2)/=2.or. &
       any(shape(result)/=shape(weights)))error stop 'Invalid batched vectors'
    do k=1,size(weights,3)
      call dgemv('T',nright,width,1._real64,block(:,:,1),nright, &
        weights(:,2,k),1,1._real64,result(first:last,1,k),1)
      call dgemv('N',nright,width,1._real64,block(:,:,2),nright, &
        weights(first:last,1,k),1,1._real64,result(:,2,k),1)
    end do
  end subroutine
end module
