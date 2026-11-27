! Bounded exact memoization of the native calc_Kel Chebyshev table.
module cached_kel
  use kinds, only: DP
  use iso_fortran_env, only: int64
  implicit none
  integer,parameter :: cache_slots=4096
  real(DP),allocatable :: tables(:,:,:),context_mf(:)
  integer(int64) :: keys(cache_slots)=0, hits=0, misses=0
  logical :: valid(cache_slots)=.false.
contains
  subroutine reset_kel_cache()
    valid=.false.
    hits=0
    misses=0
  end subroutine
  subroutine begin_kel_context()
    use sctk_val, only: mf,nmf,nci
    logical :: changed
    changed=.true.
    if(allocated(tables)) then
      if(size(tables,1)==nmf.and.size(tables,2)==nci) then
        changed=any(transfer(context_mf,[0_int64],nmf)/=transfer(mf(1:nmf),[0_int64],nmf))
      end if
    end if
    if(.not.changed) return
    if(allocated(tables)) deallocate(tables,context_mf)
    allocate(tables(nmf,nci,cache_slots),context_mf(nmf))
    context_mf=mf(1:nmf)
    call reset_kel_cache()
  end subroutine
  integer function kel_slot(x) result(slot)
    real(DP),intent(in) :: x
    integer(int64) :: bits
    bits=transfer(x,bits)
    bits=ieor(bits,ishft(bits,-33))
    bits=ieor(bits,ishft(bits,-17))
    slot=1+int(iand(bits,int(cache_slots-1,int64)))
  end function
  function calc_Kel_cached(x,Vc0) result(Kel)
    use constants, only: pi
    use sctk_val, only: mf,nmf,wmf,nci
    real(DP),intent(in) :: x,Vc0(nci)
    real(DP) :: Kel,Vc1(nmf),mf1(nmf),x0
    integer :: ici,slot
    integer(int64) :: bits
    slot=kel_slot(x)
    bits=transfer(x,bits)
    if(.not.valid(slot).or.keys(slot)/=bits) then
      misses=misses+1
      mf1(1:nmf)=x*mf(1:nmf)
      x0=COS(pi/REAL(2*nci,dp))
      mf1(1:nmf)=x0*(mf1(1:nmf)-1.0_dp)/(mf1(1:nmf)+1.0_dp)
      mf1(1:nmf)=ACOS(mf1(1:nmf))
      do ici=1,nci
        tables(1:nmf,ici,slot)=COS(REAL(ici-1,dp)*mf1(1:nmf))
      end do
      keys(slot)=bits
      valid(slot)=.true.
    else
      hits=hits+1
    end if
    Vc1(1:nmf)=MATMUL(tables(1:nmf,1:nci,slot),Vc0(1:nci))
    Kel=DOT_PRODUCT(wmf(1:nmf,1),Vc1(1:nmf))
  end function
  integer(int64) function cache_bytes() result(n)
    n=0
    if(allocated(tables)) n=int(size(tables),int64)*storage_size(tables)/8+ &
      int(size(context_mf),int64)*storage_size(context_mf)/8
    n=n+int(size(keys),int64)*storage_size(keys)/8+int(size(valid),int64)*storage_size(valid)/8+16
  end function
end module
