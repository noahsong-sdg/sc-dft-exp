! Selected native tiles only; incomplete P is never a full norm certificate.
module full_nonlinear_probe
  use iso_fortran_env,only:dp=>real64,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  use compact_defect_io,only:read_compact_defect
  use streamed_defect_core,only:accumulate_p
  use sctk_val,only:ngap,ngapmax,beta,delta,xi,dk,Z
  use tiled_operator,only:build_tile
  use cached_kel,only:reset_kel_cache
  use cached_phonon,only:reset_phonon_cache
  use slab_operator,only:clear_slab
  implicit none
contains
  subroutine run_full_map(seed_weights)
    real(dp),intent(in)::seed_weights(:,:)
    real(dp),allocatable::q(:,:),u(:,:),state(:,:),small(:,:),qd(:,:),p(:,:),block(:,:,:),weights(:)
    real(dp)::energy,t,derivative,scale,error,start,elapsed,reference,bound,denominator,before(3,3)
    integer::unit,ios,rank,side,i,j,k,offset,n,first,last,next,rr(3),cc(3),tile,meta_bytes
    character(4096)::line,root,extra,seedroot
    character(64)::operator,candidate,source,seedoperator
    character(32)::name
    inquire(file='compact-tile-control.in',size=meta_bytes)
    if(meta_bytes<1.or.meta_bytes>4096)error stop 'Invalid compact tile control size'
    open(newunit=unit,file='compact-tile-control.in',status='old')
    read(unit,'(a)')line
    if(line/='selected-compact-native-tiles-v1')error stop 'Stale compact tile control'
    read(unit,'(a)')root
    read(unit,'(a)')line
    read(line,*,iostat=ios)rank
    if(ios/=0)error stop 'Invalid compact tile rank'
    read(line,*,iostat=ios)rank,extra
    if(ios>=0)error stop 'Trailing compact tile rank'
    call read_identity(operator)
    call read_identity(candidate)
    call read_identity(source)
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
    if(ngap(1)<64.or.any(shape(seed_weights)/=[ngapmax,2]))error stop 'Invalid selected native geometry'
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
    call clear_slab();call reset_kel_cache();call reset_phonon_cache()
    next=1;rr=[1,(rank+1)/2,rank];cc=[1,(ngap(2)+1)/2,ngap(2)]
    open(newunit=unit,file='compact-tile-checks.txt',status='new')
    write(unit,'(a)')'selected-compact-native-tiles-v1; partial P only; NOT a norm'
    write(unit,*)error
    do tile=1,2
      first=1+32*(tile-1);last=first+31
      allocate(block(ngap(2),first:last,2))
      call cpu_time(start)
      call build_tile(first,last,block,1)
      call cpu_time(elapsed)
      write(unit,*)tile,' kernel_cpu_s ',elapsed-start
      write(name,'(a,i0,a)')'compact-kernel-',tile,'.bin'
      call save(trim(name),block)
      do k=1,3
        before(k,:)=p(rr(k),ngap(1)+cc)
      end do
      call cpu_time(start)
      call accumulate_p(ngap(1),first,block,weights,state(:,4),qd,p,next)
      call cpu_time(elapsed)
      write(unit,*)tile,' contraction_cpu_s ',elapsed-start
      ! Independent direct sums check both orientations at actual native strides.
      do k=1,3
        do j=first,last,31
          reference=sum(qd(ngap(1)+1:,rr(k))*(-block(:,j,2)*weights(j)/(1+state(ngap(1)+1:,4))))
          bound=1.e-28_dp+1.e-11_dp*sum(abs(qd(ngap(1)+1:,rr(k))* &
                     (-block(:,j,2)*weights(j)/(1+state(ngap(1)+1:,4)))))
          if(.not.ieee_is_finite(reference).or..not.ieee_is_finite(bound))error stop 'Nonfinite left P control'
          if(abs(p(rr(k),j)-reference)>bound)error stop 'Native left P control failed'
          write(unit,*)'left',rr(k),j,p(rr(k),j),reference,bound
        end do
      end do
      do k=1,3
        do i=1,3
          j=cc(i)
          reference=sum(qd(first:last,rr(k))*(-block(j,:,1)*weights(ngap(1)+j)/(1+state(first:last,4))))
          bound=1.e-28_dp+1.e-11_dp*(abs(before(k,i))+sum(abs(qd(first:last,rr(k))* &
                    (-block(j,:,1)*weights(ngap(1)+j)/(1+state(first:last,4))))))
          reference=before(k,i)+reference
          if(.not.ieee_is_finite(reference).or..not.ieee_is_finite(bound))error stop 'Nonfinite right P control'
          if(abs(p(rr(k),ngap(1)+j)-reference)>bound)error stop 'Native right P control failed'
          write(unit,*)'right',rr(k),j,p(rr(k),ngap(1)+j),reference,bound
        end do
      end do
      deallocate(block)
      flush(unit)
    end do
    if(next/=65)error stop 'Incomplete selected native coverage'
    close(unit)
    call clear_slab();call reset_kel_cache();call reset_phonon_cache()
    open(newunit=unit,file='compact-partial-p.bin',status='new',access='stream',form='unformatted')
    write(unit)p
    close(unit)
    write(*,'(a)')'COMPACT_NATIVE_TILES_PASS rows=64; DIAGNOSTIC ONLY, incomplete P'
  contains
    subroutine read_identity(value)
      character(64),intent(out)::value
      read(unit,'(a)',iostat=ios)line
      if(ios/=0.or.len_trim(line)/=64.or.verify(trim(line),'0123456789abcdef')/=0) &
        error stop 'Invalid compact tile identity'
      value=trim(line)
    end subroutine
    subroutine save(path,values)
      character(*),intent(in)::path
      real(dp),intent(in)::values(:,:,:)
      integer::file
      open(newunit=file,file=path,status='new',access='stream',form='unformatted')
      write(file)values
      close(file)
    end subroutine
  end subroutine
end module
