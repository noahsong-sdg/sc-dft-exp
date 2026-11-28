! Full finite-dimensional defect diagnostic; no outward/radius certificate.
module full_nonlinear_probe
  use iso_fortran_env,only:dp=>real64,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  use compact_defect_io,only:read_compact_defect
  use streamed_defect_core,only:make_c,defect_left,defect_same_right
  use compact_p_checkpoint,only:read_p_checkpoint
  use sctk_val,only:ngap,ngapmax,beta,delta,xi,dk,Z
  use tiled_operator,only:build_tile
  use cached_kel,only:reset_kel_cache
  use cached_phonon,only:reset_phonon_cache
  use slab_operator,only:clear_slab
  implicit none
contains
  subroutine run_full_map(seed_weights)
    real(dp),intent(in)::seed_weights(:,:)
    real(dp),allocatable::q(:,:),u(:,:),state(:,:),small(:,:),p(:,:),c(:,:),block(:,:,:),weights(:),rows(:)
    real(dp),allocatable::left_samples(:,:),right_samples(:,:)
    real(dp)::energy,t,derivative,scale,error,start,elapsed,denominator,pcpu(2),cpu(4)
    integer::unit,ios,rank,side,i,j,k,offset,n,first,last,next_left,next_right,stops(2),meta_bytes,progress
    integer::left_indices(3),right_indices(3)
    logical::complete
    character(4096)::line,root,extra,seedroot,previous
    character(64)::operator,candidate,source,seedoperator,fingerprint
    meta_bytes=-1
    inquire(file='compact-defect-control.in',size=meta_bytes)
    if(meta_bytes<1.or.meta_bytes>4096)error stop 'Invalid defect control size'
    open(newunit=unit,file='compact-defect-control.in',status='old')
    read(unit,'(a)')line
    if(line/='compact-full-defect-v1')error stop 'Stale defect control'
    read(unit,'(a)')root
    read(unit,'(a)')line
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid defect rank syntax'
    read(line,*,iostat=ios)rank
    if(ios/=0)error stop 'Invalid defect rank'
    read(line,*,iostat=ios)rank,extra
    if(ios>=0)error stop 'Trailing defect rank'
    call read_identity(operator);call read_identity(candidate);call read_identity(source);call read_identity(fingerprint)
    read(unit,'(a)')previous
    read(unit,'(a)')line
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid defect stops syntax'
    read(line,*,iostat=ios)stops
    if(ios/=0)error stop 'Invalid defect stops'
    read(line,*,iostat=ios)stops,extra
    if(ios>=0)error stop 'Trailing defect stops'
    read(unit,'(a)',iostat=ios)line;close(unit)
    if(ios/=iostat_end)error stop 'Trailing defect control'
    if(any(stops<3).or.any(stops>ngap))error stop 'Invalid defect coverage'
    do side=1,2
      if(stops(side)/=ngap(side).and.mod(stops(side),32)/=0)error stop 'Defect stop splits tile'
    end do
    complete=all(stops==ngap)
    open(newunit=unit,file='seed-control.in',status='old')
    read(unit,'(a)')seedroot;read(unit,'(a)')line;close(unit)
    if(len_trim(line)/=64)error stop 'Invalid defect seed operator'
    seedoperator=trim(line)
    if(operator/=seedoperator)error stop 'Different defect seed operator'
    if(any(shape(seed_weights)/=[ngapmax,2]))error stop 'Invalid defect native geometry'
    call read_compact_defect(trim(root),[ngap,ngapmax],rank,beta,operator,candidate,source,q,u,state,small)
    n=sum(ngap);error=0;allocate(weights(n))
    do side=1,2
      offset=0
      if(side==2)offset=ngap(1)
      do i=1,ngap(side)
        j=offset+i
        if(state(j,1)/=delta(i,side).or.state(j,2)/=xi(i,side).or. &
           state(j,3)/=dk(i,side).or.state(j,4)/=Z(i,side))error stop 'Different compact native state'
        denominator=beta/2
        if(xi(i,side)/=0)denominator=tanh(beta*abs(xi(i,side))/2)/abs(xi(i,side))
        weights(j)=dk(i,side)/2*denominator
        energy=hypot(xi(i,side),delta(i,side))
        if(energy==0)then
          derivative=1
        else
          t=tanh(beta*energy/2)
          derivative=((xi(i,side)/energy)**2*t/energy &
                     +beta/2*(delta(i,side)/energy)**2*(1-t*t))/denominator
        end if
        scale=max(abs(derivative),abs(state(j,5)))
        if(.not.ieee_is_finite(derivative).or.abs(derivative-state(j,5))>1.e-30_dp+1.e-12_dp*scale) &
          error stop 'Different compact native derivative'
        error=max(error,abs(derivative-state(j,5)))
      end do
    end do
    allocate(p(rank,n),c(rank,n),rows(n));rows=0;cpu=0
    call read_p_checkpoint(trim(previous),ngap,rank,ngap(1),fingerprint,p,pcpu)
    call cpu_time(start);call make_c(p,q,small,c,ngap(1)+1,ngap(1));call cpu_time(elapsed)
    cpu(1)=elapsed-start
    deallocate(p,q,small)
    open(newunit=unit,file='compact-c.bin',status='new',access='stream',form='unformatted');write(unit)c;close(unit)
    left_indices=[1,(stops(1)+1)/2,stops(1)];right_indices=[1,(ngap(2)+1)/2,ngap(2)]
    allocate(left_samples(ngap(2),3),right_samples(stops(1),3));left_samples=0;right_samples=0
    next_left=1;next_right=1
    call clear_slab();call reset_kel_cache();call reset_phonon_cache()
    open(newunit=progress,file='compact-defect-progress.txt',status='new')
    do first=1,stops(1),32
      last=min(first+31,stops(1));allocate(block(ngap(2),first:last,2))
      call cpu_time(start);call build_tile(first,last,block,1);call cpu_time(elapsed);cpu(2)=cpu(2)+elapsed-start
      do k=1,3
        if(left_indices(k)>=first.and.left_indices(k)<=last)left_samples(:,k)=block(:,left_indices(k),1)
        right_samples(first:last,k)=block(right_indices(k),:,2)
      end do
      call cpu_time(start)
      call defect_left(ngap(1),first,block,weights,state(:,4),u,c,state(:,5),rows,next_left)
      call cpu_time(elapsed);cpu(3)=cpu(3)+elapsed-start
      deallocate(block)
      if(mod(first-1,1024)==0.or.last==stops(1))then
        write(progress,*)1,last,stops(1),cpu;flush(progress)
      end if
    end do
    do first=1,stops(2),32
      last=min(first+31,stops(2));call cpu_time(start)
      call defect_same_right(ngap(1),first,last-first+1,u,c,state(:,5),rows,next_right)
      call cpu_time(elapsed);cpu(4)=cpu(4)+elapsed-start
      if(mod(first-1,1024)==0.or.last==stops(2))then
        write(progress,*)2,last,stops(2),cpu;flush(progress)
      end if
    end do
    close(progress)
    if(next_left/=stops(1)+1.or.next_right/=stops(2)+1)error stop 'Incomplete declared defect coverage'
    if(.not.all(ieee_is_finite(rows)).or.any(rows<0))error stop 'Invalid defect row sums'
    open(newunit=unit,file='compact-defect-rows.bin',status='new',access='stream',form='unformatted');write(unit)rows;close(unit)
    open(newunit=unit,file='defect-kernel-left.bin',status='new',access='stream',form='unformatted');write(unit)left_samples;close(unit)
    open(newunit=unit,file='defect-kernel-right.bin',status='new',access='stream',form='unformatted');write(unit)right_samples;close(unit)
    open(newunit=unit,file='compact-defect.meta',status='new')
    write(unit,'(a)')'compact-defect-diagnostic-v1; ordinary binary64; NOT outward certified'
    write(unit,*)ngap,rank;write(unit,*)stops;write(unit,'(a)')trim(fingerprint)
    write(unit,*)left_indices;write(unit,*)right_indices
    write(unit,'(6es26.17e3)')error,maxval(rows),cpu
    close(unit)
    call clear_slab();call reset_kel_cache();call reset_phonon_cache()
    if(complete)then
      write(*,'(a)')'COMPACT_DEFECT_COMPLETE; DIAGNOSTIC ONLY, NOT outward certified'
    else
      write(*,'(a)')'COMPACT_DEFECT_PARTIAL; NOT a full-space norm'
    end if
  contains
    subroutine read_identity(value)
      character(64),intent(out)::value
      read(unit,'(a)',iostat=ios)line
      if(ios/=0.or.len_trim(line)/=64.or.verify(trim(line),'0123456789abcdef')/=0)error stop 'Invalid defect identity'
      value=trim(line)
    end subroutine
  end subroutine
end module
