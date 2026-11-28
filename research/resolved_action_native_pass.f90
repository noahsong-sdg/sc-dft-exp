! Ordered nine-column A actions and extra P; no inverse or physical acceptance.
module full_nonlinear_probe
  use iso_fortran_env,only:dp=>real64,int64,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  use compact_defect_io,only:read_compact_defect
  use enrichment_action_core,only:accumulate_enrichment
  use sctk_val,only:ngap,ngapmax,beta,delta,xi,dk,Z
  use tiled_operator,only:build_tile
  use cached_kel,only:reset_kel_cache
  use cached_phonon,only:reset_phonon_cache
  use slab_operator,only:clear_slab
  implicit none
  integer,parameter::trialrank=9
contains
  subroutine run_full_map(seed_weights)
    real(dp),intent(in)::seed_weights(:,:)
    real(dp),allocatable::q(:,:),u(:,:),state(:,:),small(:,:),qd(:,:),p(:,:),block(:,:,:),weights(:),trial(:,:),actions(:,:),leftsamples(:,:),rightsamples(:,:)
    real(dp)::energy,t,derivative,scale,error,start,elapsed,denominator,cpu(2),saved_cpu(2)
    integer::unit,ios,rank,side,i,j,k,offset,n,first,last,next,stopat,meta_bytes,progress
    integer::leftindices(6),rightindices(3)
    integer(int64)::trialbytes
    character(4096)::line,root,extra,seedroot,trialroot
    character(64)::operator,candidate,source,seedoperator
    meta_bytes=-1
    inquire(file='enrichment-action-control.in',size=meta_bytes)
    if(meta_bytes<1.or.meta_bytes>4096)error stop 'Invalid compact tile control size'
    open(newunit=unit,file='enrichment-action-control.in',status='old')
    read(unit,'(a)')line
    if(line/='enrichment-action-pass-v1')error stop 'Stale compact tile control'
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
    read(unit,'(a)')trialroot
    read(unit,'(a)')line
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid P pass coverage syntax'
    read(line,*,iostat=ios)stopat
    if(ios/=0)error stop 'Invalid P pass coverage'
    read(line,*,iostat=ios)stopat,extra
    if(ios>=0)error stop 'Trailing P pass coverage'
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
    if(stopat<64.or.stopat>ngap(1))error stop 'Invalid enrichment coverage'
    if(stopat/=ngap(1).and.mod(stopat,32)/=0)error stop 'Enrichment stop splits tile'
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
    trialbytes=-1
    inquire(file=trim(trialroot)//'/trial-inputs.bin',size=trialbytes)
    if(trialbytes/=8_int64*n*trialrank)error stop 'Stale enrichment trial shape'
    allocate(trial(n,trialrank),actions(n,trialrank),qd(n,trialrank),p(trialrank,n));actions=0;p=0
    open(newunit=unit,file=trim(trialroot)//'/trial-inputs.bin',status='old',access='stream',form='unformatted')
    read(unit)trial;close(unit)
    if(.not.all(ieee_is_finite(trial)))error stop 'Nonfinite enrichment trial'
    do k=1,trialrank
      qd(:,k)=trial(:,k)*state(:,5)
    end do
    deallocate(q)
    allocate(leftsamples(ngap(2),6),rightsamples(ngap(1),3));leftsamples=0;rightsamples=0
    leftindices=[1,32,64,min(66,ngap(1)),(ngap(1)+3)/4,3*ngap(1)/4]
    rightindices=[2,ngap(2)/4,3*ngap(2)/4]
    cpu=0;next=1
    open(newunit=progress,file='enrichment-progress.txt',status='new')
    call reset_caches();call accumulate(1,stopat)
    if(next/=stopat+1)error stop 'Incomplete enrichment coverage'
    close(progress)
    call save('enrichment-actions.bin',actions);call save('enrichment-p.bin',p)
    call save('enrichment-kernel-left.bin',leftsamples);call save('enrichment-kernel-right.bin',rightsamples)
    open(newunit=unit,file='enrichment-action.meta',status='new')
    write(unit,'(a)')'enrichment-action-v1; diagnostic only, NOT an adopted inverse'
    write(unit,*)ngap,rank,trialrank,stopat
    write(unit,'(a)')operator;write(unit,'(a)')candidate;write(unit,'(a)')source
    write(unit,*)leftindices;write(unit,*)rightindices
    write(unit,'(3es26.17e3)')error,cpu
    close(unit);call reset_caches()
    write(*,*)'ENRICHMENT_ACTION_PASS_COMPLETE rows=',stopat,' left=',ngap(1)
    if(stopat<ngap(1))write(*,'(a)')'INCOMPLETE A/P; no inverse qualification'
  contains
    subroutine save(path,values)
      character(*),intent(in)::path
      real(dp),intent(in)::values(:,:)
      integer::f
      if(.not.all(ieee_is_finite(values)))error stop 'Nonfinite enrichment output'
      open(newunit=f,file=path,status='new',access='stream',form='unformatted');write(f)values;close(f)
    end subroutine
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
        do k=1,6
          if(leftindices(k)>=first.and.leftindices(k)<=last)leftsamples(:,k)=block(:,leftindices(k),1)
        end do
        do k=1,3
          rightsamples(first:last,k)=block(rightindices(k),:,2)
        end do
        call accumulate_enrichment(ngap(1),first,block,weights,state(:,4),trial,qd,actions,p,next)
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
