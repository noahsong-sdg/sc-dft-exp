! Ordered first-pass P only; no defect norm or material acceptance.
module full_nonlinear_probe
  use iso_fortran_env,only:dp=>real64,int64,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  use compact_defect_io,only:read_compact_defect
  use streamed_defect_core,only:accumulate_p
  use compact_p_checkpoint,only:write_p_checkpoint,read_p_checkpoint
  use sctk_val,only:ngap,ngapmax,beta,delta,xi,dk,Z
  use tiled_operator,only:build_tile
  use cached_kel,only:reset_kel_cache
  use cached_phonon,only:reset_phonon_cache
  use slab_operator,only:clear_slab
  implicit none
contains
  subroutine run_full_map(seed_weights)
    real(dp),intent(in)::seed_weights(:,:)
    real(dp),allocatable::q(:,:),u(:,:),state(:,:),small(:,:),qd(:,:),p(:,:),block(:,:,:),weights(:),baseline(:,:)
    real(dp)::energy,t,derivative,scale,error,start,elapsed,denominator,cpu(2),saved_cpu(2)
    integer::unit,ios,rank,side,i,j,k,offset,n,first,last,next,completed,stopat,meta_bytes,progress
    character(4096)::line,root,extra,seedroot,previous,mode
    character(64)::operator,candidate,source,seedoperator,fingerprint
    meta_bytes=-1
    inquire(file='compact-P-control.in',size=meta_bytes)
    if(meta_bytes<1.or.meta_bytes>4096)error stop 'Invalid compact tile control size'
    open(newunit=unit,file='compact-P-control.in',status='old')
    read(unit,'(a)')line
    if(line/='ordered-compact-P-pass-v1')error stop 'Stale compact tile control'
    read(unit,'(a)')root
    read(unit,'(a)')line
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid P pass rank syntax'
    read(line,*,iostat=ios)rank
    if(ios/=0)error stop 'Invalid compact tile rank'
    read(line,*,iostat=ios)rank,extra
    if(ios>=0)error stop 'Trailing compact tile rank'
    call read_identity(operator)
    call read_identity(candidate)
    call read_identity(source)
    call read_identity(fingerprint)
    read(unit,'(a)')previous
    read(unit,'(a)')line
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid P pass coverage syntax'
    read(line,*,iostat=ios)completed,stopat
    if(ios/=0)error stop 'Invalid P pass coverage'
    read(line,*,iostat=ios)completed,stopat,extra
    if(ios>=0)error stop 'Trailing P pass coverage'
    read(unit,'(a)')mode
    read(unit,'(a)',iostat=ios)line
    close(unit)
    if(ios/=iostat_end)error stop 'Trailing compact tile control'
    open(newunit=unit,file='seed-control.in',status='old')
    read(unit,'(a)')seedroot
    read(unit,'(a)')line
    if(len_trim(line)/=64)error stop 'Invalid compact seed operator'
    seedoperator=trim(line)
    close(unit)
    if(operator/=seedoperator)error stop 'Different compact seed operator'
    if(any(shape(seed_weights)/=[ngapmax,2]))error stop 'Invalid P pass native geometry'
    if(completed<0.or.stopat<=completed.or.stopat>ngap(1).or.mod(completed,32)/=0)error stop 'Invalid P pass rows'
    if(stopat/=ngap(1).and.mod(stopat,32)/=0)error stop 'P pass must end at a native boundary'
    if((completed==0).neqv.(previous=='-'))error stop 'Missing or unexpected P pass predecessor'
    if(mode/='segment'.and.mode/='qualify')error stop 'Unknown P pass mode'
    if(mode=='qualify'.and.(completed/=0.or.stopat/=64))error stop 'P pass qualification requires rows1:64'
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
    ! U/W are needed by the later full second pass, not this partial P probe.
    deallocate(u,small)
    allocate(qd(n,rank),p(rank,n));p=0
    do k=1,rank
      qd(:,k)=q(:,k)*state(:,5)
    end do
    deallocate(q)
    cpu=0;next=completed+1
    if(completed>0)call read_p_checkpoint(trim(previous),ngap,rank,completed,fingerprint,p,cpu)
    open(newunit=progress,file='compact-P-progress.txt',status='new')
    call reset_caches();call accumulate(completed+1,stopat)
    if(mode=='qualify')then
      allocate(baseline(rank,n));baseline=p;saved_cpu=cpu
      p=0;cpu=0;next=1
      call reset_caches();call accumulate(1,32)
      call write_p_checkpoint('split',ngap,rank,32,fingerprint,p,cpu)
      p=0;cpu=0
      call read_p_checkpoint('split',ngap,rank,32,fingerprint,p,cpu)
      next=33
      call reset_caches();call accumulate(33,64)
      do j=1,n
        do k=1,rank
          if(transfer(p(k,j),0_int64)/=transfer(baseline(k,j),0_int64))error stop 'P pass split restart changed bits'
        end do
      end do
      deallocate(baseline)
      open(newunit=unit,file='compact-P-qualification.txt',status='new')
      write(unit,'(a)')'compact-P-split-qualification-v1; all P bits equal'
      write(unit,'(a)')trim(fingerprint)
      write(unit,*)ngap,rank,64
      write(unit,'(4es26.17e3)')saved_cpu,cpu
      close(unit)
      ! Preserve continuous-production CPU; the owning receipt charges all replay.
      cpu=saved_cpu
    end if
    if(next/=stopat+1)error stop 'Incomplete P pass coverage'
    call write_p_checkpoint('.',ngap,rank,stopat,fingerprint,p,cpu)
    close(progress);call reset_caches()
    write(*,*)'COMPACT_P_PASS_COMPLETE rows=',stopat,' left=',ngap(1),' mode=',trim(mode)
    if(stopat<ngap(1))write(*,'(a)')'INCOMPLETE P; no coefficient or norm acceptance'
  contains
    subroutine read_identity(value)
      character(64),intent(out)::value
      read(unit,'(a)',iostat=ios)line
      if(ios/=0.or.len_trim(line)/=64.or.verify(trim(line),'0123456789abcdef')/=0)error stop 'Invalid P pass identity'
      value=trim(line)
    end subroutine
    subroutine reset_caches()
      call clear_slab();call reset_kel_cache();call reset_phonon_cache()
    end subroutine
    subroutine accumulate(from_row,to_row)
      integer,intent(in)::from_row,to_row
      do first=from_row,to_row,32
        last=min(first+31,to_row)
        allocate(block(ngap(2),first:last,2))
        call cpu_time(start);call build_tile(first,last,block,1);call cpu_time(elapsed)
        cpu(1)=cpu(1)+elapsed-start
        call cpu_time(start)
        call accumulate_p(ngap(1),first,block,weights,state(:,4),qd,p,next)
        call cpu_time(elapsed);cpu(2)=cpu(2)+elapsed-start
        deallocate(block)
        if(mod(first-1,1024)==0.or.last==to_row)then
          write(progress,*)last,ngap(1),cpu
          flush(progress)
        end if
      end do
    end subroutine
  end subroutine
end module
