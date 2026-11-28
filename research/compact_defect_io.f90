! Strict compact diagnostic state reader; no material or full-space qualification.
module compact_defect_io
  use iso_fortran_env,only:dp=>real64,int64,int8,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  implicit none
  private
  public::read_compact_defect
contains
  subroutine read_compact_defect(root,expected,rank,beta,operator,candidate,source,q,u,state,small)
    character(*),intent(in)::root,operator,candidate,source
    integer,intent(in)::expected(3),rank
    real(dp),intent(in)::beta
    real(dp),allocatable,intent(out)::q(:,:),u(:,:),state(:,:),small(:,:)
    character(4096)::line,extra
    integer::unit,status,counts(3),stored_rank,n
    integer(int8)::endian(8)
    integer(int64)::meta_bytes
    logical::exists
    real(dp)::stored_beta
    if(minval(expected)<=0.or.expected(3)/=maxval(expected(:2)).or.rank<1.or.rank>64)error stop 'Invalid expected compact dimensions'
    if(.not.ieee_is_finite(beta).or.beta<=0.or.len_trim(operator)/=64.or. &
       len_trim(candidate)/=64.or.len_trim(source)/=64)error stop 'Invalid expected compact context'
    endian=transfer(1_int64,endian)
    if(endian(1)/=1.or.storage_size(0._dp)/=64)error stop 'Unsupported compact binary platform'
    meta_bytes=-1
    inquire(file=trim(root)//'/compact-state.meta',exist=exists,size=meta_bytes)
    if(.not.exists.or.meta_bytes<1.or.meta_bytes>4096)error stop 'Invalid compact metadata size'
    open(newunit=unit,file=trim(root)//'/compact-state.meta',status='old',action='read',iostat=status)
    if(status/=0)error stop 'Missing compact state metadata'
    read(unit,'(a)',iostat=status)line
    if(status/=0.or.line/='compact-defect-state-v1; little-endian binary64 Fortran order')error stop 'Unsupported compact state format'
    read(unit,'(a)',iostat=status)line
    if(status/=0)error stop 'Missing compact dimensions'
    read(line,*,iostat=status)counts,stored_rank
    if(status/=0)error stop 'Invalid compact dimensions'
    read(line,*,iostat=status)counts,stored_rank,extra
    if(status>=0.or.any(counts/=expected).or.stored_rank/=rank)error stop 'Different compact dimensions'
    read(unit,'(a)',iostat=status)line
    if(status/=0)error stop 'Missing compact temperature'
    read(line,*,iostat=status)stored_beta
    if(status/=0)error stop 'Invalid compact temperature'
    read(line,*,iostat=status)stored_beta,extra
    if(status>=0.or..not.ieee_is_finite(stored_beta).or.stored_beta/=beta)error stop 'Different compact temperature'
    read(unit,'(a)',iostat=status)line
    if(status/=0.or.line/=operator)error stop 'Different compact operator'
    read(unit,'(a)',iostat=status)line
    if(status/=0.or.line/=candidate)error stop 'Different compact candidate'
    read(unit,'(a)',iostat=status)line
    if(status/=0.or.line/=source)error stop 'Different compact source'
    read(unit,'(a)',iostat=status)line
    if(status/=iostat_end)error stop 'Trailing compact metadata'
    close(unit)
    n=counts(1)+counts(2)
    call bytes('compact-q.bin',8_int64*n*rank)
    call bytes('compact-u.bin',8_int64*n*rank)
    call bytes('compact-state.bin',8_int64*n*5)
    call bytes('compact-w.bin',8_int64*rank*rank)
    allocate(q(n,rank),u(n,rank),state(n,5),small(rank,rank))
    call matrix('compact-q.bin',q)
    call matrix('compact-u.bin',u)
    call matrix('compact-state.bin',state)
    call matrix('compact-w.bin',small)
    if(any(1._dp+state(:,4)<=0))error stop 'Invalid compact Z normalization'
  contains
    subroutine bytes(name,expected_bytes)
      character(*),intent(in)::name
      integer(int64),intent(in)::expected_bytes
      integer(int64)::actual_bytes
      logical::exists
      actual_bytes=-1
      inquire(file=trim(root)//'/'//name,exist=exists,size=actual_bytes)
      if(.not.exists.or.actual_bytes/=expected_bytes)error stop 'Stale compact binary shape'
    end subroutine
    subroutine matrix(name,values)
      character(*),intent(in)::name
      real(dp),intent(out)::values(:,:)
      integer::file,ios
      open(newunit=file,file=trim(root)//'/'//name,status='old',action='read',access='stream',form='unformatted',iostat=ios)
      if(ios/=0)error stop 'Cannot open compact binary'
      read(file,iostat=ios)values
      close(file)
      if(ios/=0.or..not.all(ieee_is_finite(values)))error stop 'Invalid compact binary values'
    end subroutine
  end subroutine
end module
