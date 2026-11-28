! Fixed nine-row inverse diagnostic; ordinary binary64, no physical acceptance.
program enriched_inverse_rows
  use iso_fortran_env,only:dp=>real64,int64,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  implicit none
  integer::left,right,oldr,r,n,f,ios,i,j,k,info,indices(9)
  integer,allocatable::pivots(:)
  character(4096)::compact,trials,full,previous,oldc,line,extra
  real(dp)::beta,b,checkerror,unused_left(1,1),unused_right(1,1)
  real(dp),allocatable::q(:,:),u(:,:),state(:,:),temp(:,:),m(:,:),w(:,:),factor(:,:),singular(:),work(:)
  real(dp),allocatable::p(:,:),c(:,:),rows(:,:),oldrows(:,:),selected(:,:),kl(:,:),kr(:,:),norms(:,:),gram(:,:)
  open(newunit=f,file='enriched-inverse-control.in',status='old')
  read(f,'(a)')line
  if(line/='enriched-inverse-rows-v1')error stop 'Stale enriched inverse control'
  read(f,'(a)')compact;read(f,'(a)')trials;read(f,'(a)')full;read(f,'(a)')previous;read(f,'(a)')oldc
  read(f,'(a)')line
  if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid enriched dimensions'
  read(line,*,iostat=ios)left,right,oldr
  if(ios/=0)error stop 'Missing enriched dimensions'
  read(line,*,iostat=ios)left,right,oldr,extra
  if(ios>=0)error stop 'Trailing enriched dimensions'
  read(f,'(a)',iostat=ios)line;close(f)
  if(ios/=iostat_end)error stop 'Trailing enriched inverse control'
  if(left<65.or.right<65.or.oldr<1.or.oldr>61.or.int(left,int64)+right>huge(n))error stop 'Invalid enriched shape'
  n=left+right;r=oldr+3
  allocate(q(n,r),u(n,r),state(n,5),m(r,r),w(r,r),factor(r,r),singular(r),work(10*r),pivots(r),gram(r,r))
  call load(trim(compact)//'/compact-q.bin',q(:,:oldr));call load(trim(compact)//'/compact-u.bin',u(:,:oldr))
  call load(trim(compact)//'/compact-state.bin',state)
  call load(trim(trials)//'/trial-inputs.bin',q(:,oldr+1:));call load(trim(full)//'/enrichment-actions.bin',u(:,oldr+1:))
  if(any(1+state(:,4)<=0))error stop 'Invalid enriched Z normalization'
  allocate(temp(n,r))
  do k=1,r
    temp(:,k)=state(:,5)*u(:,k)
  end do
  call dgemm('T','N',r,r,n,-1._dp,q,n,temp,n,0._dp,m,r)
  deallocate(temp)
  do k=1,r
    m(k,k)=m(k,k)+1
  end do
  if(.not.all(ieee_is_finite(m)))error stop 'Nonfinite enriched small matrix'
  factor=m;w=0
  do k=1,r
    w(k,k)=1
  end do
  call dgesv(r,r,factor,r,pivots,w,r,info)
  if(info/=0.or..not.all(ieee_is_finite(w)))error stop 'Enriched small solve failed'
  factor=m
  call dgesvd('N','N',r,r,factor,r,singular,unused_left,1,unused_right,1,work,size(work),info)
  if(info/=0.or..not.all(ieee_is_finite(singular)).or.minval(singular)<=0)error stop 'Enriched spectrum failed'
  call dgemm('N','N',r,r,r,1._dp,m,r,w,r,0._dp,gram,r)
  do k=1,r
    gram(k,k)=gram(k,k)-1
  end do
  checkerror=maxval(abs(gram))
  call dgemm('N','N',r,r,r,1._dp,w,r,m,r,0._dp,gram,r)
  do k=1,r
    gram(k,k)=gram(k,k)-1
  end do
  if(max(checkerror,maxval(abs(gram)))>1.e-9_dp)error stop 'Enriched inverse calibration failed'
  call dgemm('T','N',r,r,n,1._dp,q,n,q,n,0._dp,gram,r)
  allocate(p(r,n),c(r,n),temp(oldr,n))
  call load(trim(previous)//'/compact-p.bin',temp);p(:oldr,:)=temp;deallocate(temp)
  allocate(temp(3,n));call load(trim(full)//'/enrichment-p.bin',temp);p(oldr+1:,:)=temp;deallocate(temp)
  p=p-transpose(q)
  call dgemm('N','N',r,n,r,1._dp,w,r,p,r,0._dp,c,r);deallocate(p,q)
  indices=[1,32,64,65,(left+1)/2,left,left+1,left+(right+1)/2,n]
  allocate(selected(9,r),rows(9,n),oldrows(9,n),norms(9,2),kl(right,6),kr(left,3))
  do i=1,9
    selected(i,:)=u(indices(i),:)
  end do
  call dgemm('N','N',9,n,r,1._dp,selected,9,c,r,0._dp,rows,9)
  allocate(temp(oldr,n));call load(trim(oldc)//'/compact-c.bin',temp)
  call dgemm('N','N',9,n,oldr,1._dp,selected,9,temp,oldr,0._dp,oldrows,9);deallocate(temp,u)
  call load(trim(full)//'/enrichment-kernel-left.bin',kl);call load(trim(full)//'/enrichment-kernel-right.bin',kr)
  open(newunit=f,file=trim(compact)//'/compact-state.meta',status='old');read(f,*);read(f,*);read(f,*)beta;close(f)
  if(.not.ieee_is_finite(beta).or.beta<=0)error stop 'Invalid enriched beta'
  do j=1,n
    b=beta/2
    if(state(j,2)/=0)b=tanh(beta*abs(state(j,2))/2)/abs(state(j,2))
    if(j>left)then
      do i=1,6
        rows(i,j)=rows(i,j)-kl(j-left,i)*state(j,3)*b/2/(1+state(indices(i),4))
        oldrows(i,j)=oldrows(i,j)-kl(j-left,i)*state(j,3)*b/2/(1+state(indices(i),4))
      end do
    else
      do i=7,9
        rows(i,j)=rows(i,j)-kr(j,i-6)*state(j,3)*b/2/(1+state(indices(i),4))
        oldrows(i,j)=oldrows(i,j)-kr(j,i-6)*state(j,3)*b/2/(1+state(indices(i),4))
      end do
    end if
    rows(:,j)=rows(:,j)*state(j,5);oldrows(:,j)=oldrows(:,j)*state(j,5)
  end do
  do i=1,9
    norms(i,1)=sum(abs(oldrows(i,:)));norms(i,2)=sum(abs(rows(i,:)))
  end do
  call save('enriched-m.bin',m);call save('enriched-w.bin',w);call save('enriched-c.bin',c)
  call save('enriched-rows.bin',rows);call save('baseline-rows.bin',oldrows);call save('enriched-norms.bin',norms)
  call save('enriched-qgram.bin',gram)
  open(newunit=f,file='enriched-singular.bin',status='new',access='stream',form='unformatted');write(f)singular;close(f)
  write(*,'(a)')'ENRICHED_INVERSE_ROWS_COMPLETE; DIAGNOSTIC ONLY, no adopted inverse'
contains
  subroutine load(path,a)
    character(*),intent(in)::path
    real(dp),intent(out)::a(:,:)
    integer::unit
    integer(int64)::bytes
    bytes=-1;inquire(file=path,size=bytes)
    if(bytes/=8_int64*size(a,kind=int64))error stop 'Stale enriched input shape'
    open(newunit=unit,file=path,status='old',access='stream',form='unformatted');read(unit)a;close(unit)
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite enriched input'
  end subroutine
  subroutine save(path,a)
    character(*),intent(in)::path
    real(dp),intent(in)::a(:,:)
    integer::unit
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite enriched output'
    open(newunit=unit,file=path,status='new',access='stream',form='unformatted');write(unit)a;close(unit)
  end subroutine
end program
