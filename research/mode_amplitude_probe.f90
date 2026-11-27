! Reuse a declared conventional Ritz mode; GPL-2.0-or-later.
! Projected amplitudes are diagnostics, not full nonlinear solutions.
module mode_amplitude_probe
  use kinds, only: dp
  use constants, only: RYTOEV
  use sctk_val, only: ngap,ngapmax,nx,nmf,nci,scdft_kernel,beta,xi,dk,emin,Z
  use tiled_operator, only: build_tile
  use slab_operator, only: clear_slab
  use nonlinear_tile_apply, only: apply_tile
  use, intrinsic :: ieee_arithmetic, only: ieee_is_finite
  implicit none
contains
  subroutine run_mode_amplitudes()
    integer,parameter :: batches=8
    real(dp),parameter :: amplitudes(7)=[.025_dp,.05_dp,.1_dp,.15_dp,.2_dp,.3_dp,.5_dp]
    real(dp),allocatable :: mode(:,:),saved_r(:,:),weights(:,:,:),images(:,:,:),block(:,:,:),res(:,:)
    real(dp) :: lambda,reported,norm,scales(7),average(2),denominator,energy,derivative
    real(dp) :: stored_beta,linear_error,bound,relative,start,elapsed,projection,fermi(2)
    integer :: unit,ios,first,last,g,i,k,index,columns,n,m,config(6),bytes,actual
    character(1024) :: directory
    character(256) :: header,context,expected_context,trailing
    open(newunit=unit,file='mode-control.in',status='old')
    read(unit,'(a)')directory
    read(unit,'(a)')expected_context
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0.or.len_trim(expected_context)/=64)error stop 'Invalid declared mode context'
    open(newunit=unit,file=trim(directory)//'/basis.meta',status='old')
    read(unit,'(a)')header
    read(unit,*)n,m
    read(unit,*)stored_beta
    read(unit,'(a)')context
    read(unit,*)config
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0.or.header/='tc-basis-v1'.or.n/=2*ngapmax.or.m<1.or.stored_beta/=beta) &
      error stop 'Stale mode basis dimensions/temperature'
    if(context/=expected_context.or.any(config/=[nx,nmf,nci,scdft_kernel,ngap])) &
      error stop 'Stale declared mode operator context'
    open(newunit=unit,file=trim(directory)//'/selected.meta',status='old')
    read(unit,*)index,columns
    read(unit,*)lambda,reported
    read(unit,'(a)',iostat=ios)trailing
    close(unit)
    if(ios>=0.or.columns/=m.or.index<1.or.index>m.or.lambda<=1.or.reported<0.or.reported>1.e-9_dp) &
      error stop 'Unqualified saved superconducting candidate'
    if(.not.ieee_is_finite(lambda).or..not.ieee_is_finite(reported))error stop 'Nonfinite mode metadata'
    allocate(mode(ngapmax,2),saved_r(ngapmax,2),weights(ngapmax,2,batches), &
      images(ngapmax,2,batches),res(ngapmax,2))
    inquire(iolength=bytes)mode,saved_r
    inquire(file=trim(directory)//'/selected.bin',size=actual)
    if(actual/=bytes)error stop 'Stale mode payload shape'
    open(newunit=unit,file=trim(directory)//'/selected.bin',status='old',access='stream',form='unformatted')
    read(unit)mode,saved_r
    close(unit)
    if(.not.all(ieee_is_finite(mode)).or..not.all(ieee_is_finite(saved_r)))error stop 'Nonfinite mode payload'
    norm=sqrt(sum(mode**2))
    if(abs(norm-1)>1.e-10_dp)error stop 'Mode normalization changed'
    do g=1,2
      if(any(mode(ngap(g)+1:,g)/=0).or.any(saved_r(ngap(g)+1:,g)/=0))error stop 'Mode padding changed'
      denominator=sum(dk(:,g),abs(xi(:,g))<emin)
      if(denominator<=0)error stop 'Invalid mode Fermi normalization'
      average(g)=sum(mode(:,g)*dk(:,g),abs(xi(:,g))<emin)/denominator
    end do
    if(average(1)*average(2)<=0)error stop 'Opposite or zero Fermi signs'
    if(average(1)<0)then
      mode=-mode;saved_r=-saved_r;average=-average
    end if
    scales=amplitudes/(1000*RYTOEV)/(sum(average)/2)
    weights=0;images=0
    do g=1,2
      do i=1,ngap(g)
        energy=abs(xi(i,g))
        if(energy==0)then
          derivative=dk(i,g)*beta/4
        else
          derivative=dk(i,g)/2*tanh(beta*energy/2)/energy
        end if
        weights(i,g,1)=derivative*mode(i,g)
        do k=1,7
          energy=hypot(xi(i,g),scales(k)*mode(i,g))
          if(energy/=0)weights(i,g,k+1)=dk(i,g)/2*scales(k)*mode(i,g)*tanh(beta*energy/2)/energy
        end do
      end do
    end do
    if(.not.all(ieee_is_finite(weights)))error stop 'Nonfinite amplitude weights'
    call clear_slab()
    call cpu_time(start)
    open(newunit=unit,file='mode-progress.txt',status='new')
    do first=1,ngap(1),32
      last=min(first+31,ngap(1))
      allocate(block(ngap(2),first:last,2))
      call build_tile(first,last,block,1)
      call apply_tile(block,first,ngap(1),ngap(2),weights,images)
      deallocate(block)
      if(mod(first-1,1024)==0.or.last==ngap(1))then
        call cpu_time(elapsed)
        write(unit,*)last,ngap(1),elapsed-start
        flush(unit)
      end if
    end do
    close(unit)
    call cpu_time(elapsed)
    do k=1,batches
      images(:,:,k)=-images(:,:,k)/(1+Z)
    end do
    if(.not.all(ieee_is_finite(images)))error stop 'Nonfinite amplitude image'
    linear_error=maxval(abs(images(:,:,1)-lambda*mode-saved_r))
    bound=2.e-13_dp+2.e-12_dp*maxval(abs(images(:,:,1)))
    relative=sqrt(sum((images(:,:,1)-lambda*mode)**2))/max(sqrt(sum(images(:,:,1)**2)),lambda*norm)
    if(linear_error>bound.or.relative>1.e-9_dp)error stop 'Fresh conventional mode action mismatch'
    open(newunit=unit,file='mode-amplitudes.txt',status='new')
    write(unit,'(a)') '# mode-amplitudes-v1; projected candidates; NOT solved gaps'
    write(unit,*)ngap,ngapmax,batches
    write(unit,*)beta,lambda,linear_error,bound,relative,elapsed-start
    do k=1,7
      res=images(:,:,k+1)-scales(k)*mode
      projection=sum(mode*res)/sum(mode**2)
      do g=1,2
        denominator=sum(dk(:,g),abs(xi(:,g))<emin)
        fermi(g)=sum(res(:,g)*dk(:,g),abs(xi(:,g))<emin)/denominator
      end do
      write(unit,*)amplitudes(k),scales(k),projection,maxval(abs(res)), &
        sqrt(sum(res**2)/sum(ngap)),fermi
    end do
    close(unit)
    open(newunit=unit,file='mode-amplitudes.bin',status='new',access='stream',form='unformatted')
    write(unit)mode,images
    close(unit)
  end subroutine
end module
