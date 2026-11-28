! Diagnostic finite row sums only: no outward error/radius certificate.
module streamed_defect_core
  use iso_fortran_env, only: dp=>real64
  use ieee_arithmetic, only: ieee_is_finite
  implicit none
  private
  public::accumulate_p,make_c,defect_left,defect_same_right
contains
  subroutine context(left,block,w,z,n,right,width)
    integer,intent(in)::left
    real(dp),intent(in)::block(:,:,:),w(:),z(:)
    integer,intent(out)::n,right,width
    n=size(w);right=n-left;width=size(block,2)
    if(left<1.or.right<1.or.size(z)/=n)error stop 'Invalid defect state dimensions'
    if(size(block,1)/=right.or.size(block,3)/=2.or.width<1.or.width>32)error stop 'Invalid native defect tile'
    if(.not.all(ieee_is_finite(block)).or..not.all(ieee_is_finite(w)).or. &
       .not.all(ieee_is_finite(z)))error stop 'Nonfinite defect context'
    if(any(1._dp+z<=0))error stop 'Invalid defect normalization'
  end subroutine
  subroutine ordered(first,width,total,next)
    integer,intent(in)::first,width,total,next
    if(first/=next.or.first<1.or.width<1.or.first+width-1>total)error stop 'Noncontiguous defect coverage'
  end subroutine
  subroutine accumulate_p(left,first,block,w,z,qd,p,next)
    integer,intent(in)::left,first
    real(dp),intent(in),contiguous::block(:,:,:),w(:),z(:),qd(:,:)
    real(dp),intent(inout),contiguous::p(:,:)
    integer,intent(inout)::next
    real(dp),allocatable::a(:,:)
    integer::n,right,width,r,i,j
    call context(left,block,w,z,n,right,width);r=size(qd,2)
    call ordered(first,width,left,next)
    if(size(qd,1)/=n.or.r<1.or.r>64.or.size(p,1)/=r.or.size(p,2)/=n)error stop 'Invalid P shape'
    if(.not.all(ieee_is_finite(qd)).or..not.all(ieee_is_finite(p)))error stop 'Nonfinite P input'
    if(first==1.and.any(p/=0))error stop 'Stale initial P'
    allocate(a(right,width))
    ! A01 is transpose(a): output-row Zleft and input-column wright.
    do j=1,width
      do i=1,right
        a(i,j)=-block(i,j,1)*w(left+i)/(1+z(first+j-1))
      end do
    end do
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite A01'
    call dgemm('T','T',r,right,width,1._dp,qd(first,1),n,a(1,1),right,1._dp,p(1,left+1),r)
    ! A10: different kernel, output-row Zright and input-column wleft.
    do j=1,width
      do i=1,right
        a(i,j)=-block(i,j,2)*w(first+j-1)/(1+z(left+i))
      end do
    end do
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite A10'
    call dgemm('T','N',r,width,right,1._dp,qd(left+1,1),n,a(1,1),right,0._dp,p(1,first),r)
    if(.not.all(ieee_is_finite(p)))error stop 'Nonfinite accumulated P'
    next=first+width
  end subroutine
  subroutine make_c(p,q,small,c,next,left)
    real(dp),intent(in),contiguous::p(:,:),q(:,:),small(:,:)
    real(dp),intent(out),contiguous::c(:,:)
    integer,intent(in)::next,left
    real(dp),allocatable::difference(:,:)
    integer::n,r
    n=size(q,1);r=size(q,2)
    if(left<1.or.left>=n.or.next/=left+1)error stop 'Incomplete P coverage'
    if(r<1.or.r>64.or.any(shape(p)/=[r,n]).or.any(shape(c)/=[r,n]).or. &
       any(shape(small)/=[r,r]))error stop 'Invalid coefficient shape'
    if(.not.all(ieee_is_finite(p)).or..not.all(ieee_is_finite(q)).or. &
       .not.all(ieee_is_finite(small)))error stop 'Nonfinite coefficient input'
    allocate(difference(r,n));difference=p-transpose(q)
    if(.not.all(ieee_is_finite(difference)))error stop 'Nonfinite coefficient difference'
    call dgemm('N','N',r,n,r,1._dp,small(1,1),r,difference(1,1),r,0._dp,c(1,1),r)
    if(.not.all(ieee_is_finite(c)))error stop 'Nonfinite coefficient output'
  end subroutine
  subroutine row_inputs(n,left,u,c,d,rows,r)
    integer,intent(in)::n,left
    real(dp),intent(in)::u(:,:),c(:,:),d(:),rows(:)
    integer,intent(out)::r
    r=size(u,2)
    if(left<1.or.left>=n.or.r<1.or.r>64.or.size(u,1)/=n.or.any(shape(c)/=[r,n]).or. &
       size(d)/=n.or.size(rows)/=n)error stop 'Invalid defect row shape'
    if(.not.all(ieee_is_finite(u)).or..not.all(ieee_is_finite(c)).or. &
       .not.all(ieee_is_finite(d)).or..not.all(ieee_is_finite(rows)))error stop 'Nonfinite defect row input'
    if(any(rows<0))error stop 'Negative partial row sum'
  end subroutine
  subroutine defect_left(left,first,block,w,z,u,c,d,rows,next)
    integer,intent(in)::left,first
    real(dp),intent(in),contiguous::block(:,:,:),w(:),z(:),u(:,:),c(:,:),d(:)
    real(dp),intent(inout),contiguous::rows(:)
    integer,intent(inout)::next
    real(dp),allocatable::work(:,:)
    integer::n,right,width,r,i,j
    call context(left,block,w,z,n,right,width);call row_inputs(n,left,u,c,d,rows,r)
    call ordered(first,width,left,next)
    if(any(rows(first:first+width-1)/=0))error stop 'Stale left defect rows'
    allocate(work(width,n))
    call dgemm('N','N',width,n,r,1._dp,u(first,1),n,c(1,1),r,0._dp,work(1,1),width)
    do j=1,right
      do i=1,width
        work(i,left+j)=work(i,left+j)-block(j,i,1)*w(left+j)/(1+z(first+i-1))
      end do
    end do
    do i=1,width
      rows(first+i-1)=sum(abs(work(i,:)*d))
    end do
    deallocate(work);allocate(work(right,width))
    call dgemm('N','N',right,width,r,1._dp,u(left+1,1),n,c(1,first),r,0._dp,work(1,1),right)
    do j=1,width
      do i=1,right
        work(i,j)=work(i,j)-block(i,j,2)*w(first+j-1)/(1+z(left+i))
      end do
      rows(left+1:n)=rows(left+1:n)+abs(work(:,j)*d(first+j-1))
    end do
    if(.not.all(ieee_is_finite(work)).or..not.all(ieee_is_finite(rows)))error stop 'Nonfinite defect rows'
    next=first+width
  end subroutine
  subroutine defect_same_right(left,first,width,u,c,d,rows,next)
    integer,intent(in)::left,first,width
    real(dp),intent(in),contiguous::u(:,:),c(:,:),d(:)
    real(dp),intent(inout),contiguous::rows(:)
    integer,intent(inout)::next
    real(dp),allocatable::work(:,:)
    integer::n,right,r,j
    n=size(d);right=n-left;call row_inputs(n,left,u,c,d,rows,r)
    call ordered(first,width,right,next)
    if(width>32)error stop 'Right defect width exceeds native tile cap'
    allocate(work(right,width))
    call dgemm('N','N',right,width,r,1._dp,u(left+1,1),n,c(1,left+first),r,0._dp,work(1,1),right)
    do j=1,width
      rows(left+1:n)=rows(left+1:n)+abs(work(:,j)*d(left+first+j-1))
    end do
    if(.not.all(ieee_is_finite(work)).or..not.all(ieee_is_finite(rows)))error stop 'Nonfinite same-side rows'
    next=first+width
  end subroutine
end module
