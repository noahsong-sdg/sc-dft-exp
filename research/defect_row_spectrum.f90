! Diagnose retained row errors only; candidate directions are not an adopted inverse.
program defect_row_spectrum
  use iso_fortran_env,only:dp=>real64,iostat_end,int64
  use ieee_arithmetic,only:ieee_is_finite
  implicit none
  integer::n,left,right,r,m,unit,ios,tile,first,last,i,j,k,info,lwork,kept
  character(4096)::compact,defect,tiles,line,extra
  real(dp)::beta,b,scale
  real(dp),allocatable::u(:,:),q(:,:),c(:,:),state(:,:),e(:,:),kernel(:,:,:),gram(:,:),eig(:),vectors(:,:),work(:)
  real(dp),allocatable::directions(:,:),qprojection(:,:),qgram(:,:),vgram(:,:),adrows(:)
  open(newunit=unit,file='spectrum-control.in',status='old')
  read(unit,'(a)')line
  if(line/='retained-defect-row-spectrum-v1')error stop 'Stale row spectrum control'
  read(unit,'(a)')compact;read(unit,'(a)')defect;read(unit,'(a)')tiles
  read(unit,'(a)')line
  if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid row spectrum dimensions'
  read(line,*,iostat=ios)left,right,r,m
  if(ios/=0)error stop 'Missing row spectrum dimensions'
  read(line,*,iostat=ios)left,right,r,m,extra
  if(ios>=0)error stop 'Trailing row spectrum dimensions'
  read(unit,'(a)',iostat=ios)line;close(unit)
  if(ios/=iostat_end)error stop 'Trailing spectrum control'
  if(int(left,int64)+int(right,int64)>int(huge(0),int64))error stop 'Spectrum dimension overflow'
  if(left<64.or.right<64.or.r<1.or.r>64.or.m/=64)error stop 'Invalid retained spectrum shape'
  n=left+right
  open(newunit=unit,file=trim(compact)//'/compact-state.meta',status='old')
  read(unit,*);read(unit,*);read(unit,*)beta;close(unit)
  if(.not.ieee_is_finite(beta).or.beta<=0)error stop 'Invalid spectrum beta'
  allocate(u(n,r),q(n,r),c(r,n),state(n,5),e(m,n),kernel(right,32,2),adrows(m));adrows=0
  call load(trim(compact)//'/compact-u.bin',u);call load(trim(compact)//'/compact-q.bin',q)
  call load(trim(compact)//'/compact-state.bin',state);call load(trim(defect)//'/compact-c.bin',c)
  if(any(1+state(:,4)<=0))error stop 'Invalid spectrum normalization'
  call dgemm('N','N',m,n,r,1._dp,u(1,1),n,c(1,1),r,0._dp,e(1,1),m)
  deallocate(u,c)
  do tile=1,2
    write(extra,'(i0)')tile
    call load3(trim(tiles)//'/compact-kernel-'//trim(extra)//'.bin',kernel)
    first=32*(tile-1)
    do j=1,32
      do i=1,right
        b=beta/2
        if(state(left+i,2)/=0)b=tanh(beta*abs(state(left+i,2))/2)/abs(state(left+i,2))
        scale=-kernel(i,j,1)*state(left+i,3)*b/2/(1+state(first+j,4))
        e(first+j,left+i)=e(first+j,left+i)+scale
        adrows(first+j)=adrows(first+j)+abs(scale*state(left+i,5))
      end do
    end do
  end do
  deallocate(kernel)
  do j=1,n
    e(:,j)=e(:,j)*state(j,5)
  end do
  if(.not.all(ieee_is_finite(e)))error stop 'Nonfinite retained row errors'
  deallocate(state)
  allocate(gram(m,m),eig(m),vectors(m,m),work(3*m),qgram(r,r))
  call dgemm('N','T',m,m,n,1._dp,e(1,1),m,e(1,1),m,0._dp,gram(1,1),m)
  vectors=gram;lwork=size(work)
  call dsyev('V','U',m,vectors,m,eig,work,lwork,info)
  if(info/=0.or..not.all(ieee_is_finite(eig)).or.eig(m)<=0)error stop 'Row spectrum eigensolver failure'
  kept=min(3,count(eig>1.e-10_dp*eig(m)))
  if(kept<1)error stop 'No resolved sensitivity direction'
  allocate(directions(n,kept),qprojection(r,kept),vgram(kept,kept))
  call dgemm('T','N',n,kept,m,1._dp,e(1,1),m,vectors(1,m-kept+1),m,0._dp,directions(1,1),n)
  do k=1,kept
    directions(:,k)=directions(:,k)/sqrt(eig(m-kept+k))
  end do
  call dgemm('T','N',r,kept,n,1._dp,q(1,1),n,directions(1,1),n,0._dp,qprojection(1,1),r)
  call dgemm('T','N',r,r,n,1._dp,q(1,1),n,q(1,1),n,0._dp,qgram(1,1),r)
  call dgemm('T','N',kept,kept,n,1._dp,directions(1,1),n,directions(1,1),n,0._dp,vgram(1,1),kept)
  if(.not.all(ieee_is_finite(directions)).or..not.all(ieee_is_finite(qprojection)))error stop 'Nonfinite sensitivity directions'
  call save('row-errors.bin',e);call save('row-gram.bin',gram);call save('row-eigenvectors.bin',vectors)
  call save('sensitivity-directions.bin',directions);call save('basis-overlap.bin',qprojection)
  call save('basis-gram.bin',qgram);call save('direction-gram.bin',vgram)
  open(newunit=unit,file='row-spectrum.txt',status='new')
  write(unit,'(a)')'retained-row-spectrum-v1; diagnostic, NOT an inverse or certificate'
  write(unit,*)left,right,r,m,kept
  write(unit,'(es26.17e3)')eig
  close(unit)
  open(newunit=unit,file='row-baselines.bin',status='new',access='stream',form='unformatted');write(unit)adrows;close(unit)
  write(*,'(a)')'RETAINED_ROW_SPECTRUM_COMPLETE; no new kernels or adopted directions'
contains
  subroutine load(path,a)
    character(*),intent(in)::path
    real(dp),intent(out)::a(:,:)
    integer::f
    integer(kind=8)::bytes
    bytes=-1
    inquire(file=path,size=bytes)
    if(bytes/=8_8*size(a,kind=8))error stop 'Stale row spectrum input shape'
    open(newunit=f,file=path,status='old',access='stream',form='unformatted');read(f)a;close(f)
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite row spectrum input'
  end subroutine
  subroutine load3(path,a)
    character(*),intent(in)::path
    real(dp),intent(out)::a(:,:,:)
    integer::f
    integer(kind=8)::bytes
    bytes=-1
    inquire(file=path,size=bytes)
    if(bytes/=8_8*size(a,kind=8))error stop 'Stale retained kernel shape'
    open(newunit=f,file=path,status='old',access='stream',form='unformatted');read(f)a;close(f)
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite retained kernel'
  end subroutine
  subroutine save(path,a)
    character(*),intent(in)::path
    real(dp),intent(in)::a(:,:)
    integer::f
    if(.not.all(ieee_is_finite(a)))error stop 'Nonfinite spectrum output'
    open(newunit=f,file=path,status='new',access='stream',form='unformatted');write(f)a;close(f)
  end subroutine
end program
