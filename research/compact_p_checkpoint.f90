! Restart an ordered first pass only; no full-space norm or material acceptance.
module compact_p_checkpoint
  use iso_fortran_env,only:dp=>real64,int64,int8,iostat_end
  use ieee_arithmetic,only:ieee_is_finite
  implicit none
  private
  public::write_p_checkpoint,read_p_checkpoint
contains
  subroutine context(counts,rank,completed,identity,cpu)
    integer,intent(in)::counts(2),rank,completed
    character(*),intent(in)::identity
    real(dp),intent(in)::cpu(2)
    integer(int8)::endian(8)
    endian=transfer(1_int64,endian)
    if(endian(1)/=1.or.storage_size(0._dp)/=64)error stop 'Unsupported P checkpoint platform'
    if(int(counts(1),int64)+int(counts(2),int64)>int(huge(0),int64))error stop 'P checkpoint dimension overflow'
    if(minval(counts)<1.or.rank<1.or.rank>64.or.completed<0.or.completed>counts(1))error stop 'Invalid P checkpoint context'
    if(completed/=counts(1).and.mod(completed,32)/=0)error stop 'P checkpoint splits a native tile'
    if(len_trim(identity)/=64.or.verify(trim(identity),'0123456789abcdef')/=0)error stop 'Invalid P checkpoint identity'
    if(.not.all(ieee_is_finite(cpu)).or.any(cpu<0))error stop 'Invalid P checkpoint timings'
  end subroutine
  subroutine values(counts,rank,completed,p,cpu)
    integer,intent(in)::counts(2),rank,completed
    real(dp),intent(in)::p(:,:),cpu(2)
    if(any(shape(p)/=[rank,sum(counts)]).or..not.all(ieee_is_finite(p)))error stop 'Invalid P checkpoint values'
    if(completed<counts(1))then
      if(any(p(:,completed+1:counts(1))/=0))error stop 'Nonzero unvisited P checkpoint columns'
    end if
    if(completed==0.and.(any(p/=0).or.any(cpu/=0)))error stop 'Nonzero initial P checkpoint'
  end subroutine
  subroutine write_p_checkpoint(root,counts,rank,completed,identity,p,cpu)
    character(*),intent(in)::root,identity
    integer,intent(in)::counts(2),rank,completed
    real(dp),intent(in)::p(:,:),cpu(2)
    integer::file
    logical::exists
    call context(counts,rank,completed,identity,cpu);call values(counts,rank,completed,p,cpu)
    inquire(file=trim(root)//'/compact-p.meta',exist=exists)
    if(exists)error stop 'Fresh P checkpoint metadata required'
    inquire(file=trim(root)//'/compact-p.bin',exist=exists)
    if(exists)error stop 'Fresh P checkpoint binary required'
    open(newunit=file,file=trim(root)//'/compact-p.bin',status='new',access='stream',form='unformatted')
    write(file)p
    close(file)
    open(newunit=file,file=trim(root)//'/compact-p.meta',status='new')
    write(file,'(a)')'compact-P-checkpoint-v1; little-endian binary64 Fortran order'
    write(file,*)counts,rank
    write(file,*)completed
    write(file,'(a)')trim(identity)
    write(file,'(2es26.17e3)')cpu
    close(file)
  end subroutine
  subroutine read_p_checkpoint(root,counts,rank,completed,identity,p,cpu)
    character(*),intent(in)::root,identity
    integer,intent(in)::counts(2),rank,completed
    real(dp),intent(out)::p(:,:),cpu(2)
    integer::file,ios,stored_counts(2),stored_rank,stored_completed
    integer(int64)::size_bytes
    logical::exists
    character(4096)::line,extra
    call context(counts,rank,completed,identity,[0._dp,0._dp])
    if(any(shape(p)/=[rank,sum(counts)]))error stop 'Invalid P checkpoint destination'
    size_bytes=-1
    inquire(file=trim(root)//'/compact-p.meta',exist=exists,size=size_bytes)
    if(.not.exists.or.size_bytes<1.or.size_bytes>4096)error stop 'Invalid P checkpoint metadata size'
    open(newunit=file,file=trim(root)//'/compact-p.meta',status='old')
    read(file,'(a)',iostat=ios)line
    if(ios/=0.or.line/='compact-P-checkpoint-v1; little-endian binary64 Fortran order')error stop 'Stale P checkpoint schema'
    read(file,'(a)',iostat=ios)line
    if(ios/=0)error stop 'Missing P checkpoint dimensions'
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid P checkpoint integer syntax'
    read(line,*,iostat=ios)stored_counts,stored_rank
    if(ios/=0)error stop 'Invalid P checkpoint dimensions'
    read(line,*,iostat=ios)stored_counts,stored_rank,extra
    if(ios>=0.or.any(stored_counts/=counts).or.stored_rank/=rank)error stop 'Different P checkpoint dimensions'
    read(file,'(a)',iostat=ios)line
    if(ios/=0)error stop 'Missing P checkpoint coverage'
    if(verify(trim(line),'0123456789 +-')/=0)error stop 'Invalid P checkpoint integer syntax'
    read(line,*,iostat=ios)stored_completed
    if(ios/=0)error stop 'Invalid P checkpoint coverage'
    read(line,*,iostat=ios)stored_completed,extra
    if(ios>=0.or.stored_completed/=completed)error stop 'Different P checkpoint coverage'
    read(file,'(a)',iostat=ios)line
    if(ios/=0.or.line/=identity)error stop 'Different P checkpoint identity'
    read(file,'(a)',iostat=ios)line
    if(ios/=0)error stop 'Missing P checkpoint timings'
    if(verify(trim(line),'0123456789 +-.EeDd')/=0)error stop 'Invalid P checkpoint real syntax'
    read(line,*,iostat=ios)cpu
    if(ios/=0)error stop 'Invalid P checkpoint timings'
    read(line,*,iostat=ios)cpu,extra
    if(ios>=0)error stop 'Trailing P checkpoint timing'
    read(file,'(a)',iostat=ios)line
    if(ios/=iostat_end)error stop 'Trailing P checkpoint metadata'
    close(file)
    call context(counts,rank,completed,identity,cpu)
    size_bytes=-1
    inquire(file=trim(root)//'/compact-p.bin',exist=exists,size=size_bytes)
    if(.not.exists.or.size_bytes/=8_int64*rank*sum(counts))error stop 'Stale P checkpoint binary shape'
    open(newunit=file,file=trim(root)//'/compact-p.bin',status='old',access='stream',form='unformatted')
    read(file,iostat=ios)p
    close(file)
    if(ios/=0)error stop 'Invalid P checkpoint binary'
    call values(counts,rank,completed,p,cpu)
  end subroutine
end module
