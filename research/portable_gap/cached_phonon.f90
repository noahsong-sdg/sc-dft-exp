! Exact bounded memoization of unchanged native ordered phonon weights.
module cached_phonon
  use kinds,only:DP
  use iso_fortran_env,only:int64
  implicit none
  integer,parameter :: phonon_slots=65536
  integer(int64) :: phonon_keys(3,phonon_slots)=0,phonon_hits=0,phonon_misses=0,beta_bits=0
  real(DP) :: phonon_values(phonon_slots)=0d0
  logical :: phonon_valid(phonon_slots)=.false.,context_ready=.false.,context_zero=.false.
  integer :: context_kernel=0
contains
  subroutine reset_phonon_cache()
    phonon_valid=.false.
    phonon_hits=0
    phonon_misses=0
  end subroutine
  subroutine begin_phonon_context(beta)
    use sctk_val,only:scdft_kernel,zero_kelvin
    real(DP),intent(in) :: beta
    integer(int64) :: bits
    bits=transfer(beta,bits)
    if(.not.context_ready.or.bits/=beta_bits.or.context_kernel/=scdft_kernel.or. &
       (context_zero.neqv.zero_kelvin)) then
      call reset_phonon_cache()
      beta_bits=bits
      context_kernel=scdft_kernel
      context_zero=zero_kelvin
      context_ready=.true.
    end if
  end subroutine
  integer function phonon_slot(x,y,z) result(slot)
    real(DP),intent(in) :: x,y,z
    integer(int64) :: a,b,c,h
    a=transfer(x,a)
    b=transfer(y,b)
    c=transfer(z,c)
    h=ieor(a,ishft(a,-29))
    h=ieor(h,ishftc(b,21))
    h=ieor(h,ishftc(c,43))
    h=ieor(h,ishft(h,-17))
    slot=1+int(iand(h,int(phonon_slots-1,int64)))
  end function
  function Kweight_cached(beta,x,y,z) result(weight)
    use sctk_kernel_weight,only:Kweight
    real(DP),intent(in) :: beta,x,y,z
    real(DP) :: weight
    integer :: slot
    integer(int64) :: key(3)
    key=[transfer(x,0_int64),transfer(y,0_int64),transfer(z,0_int64)]
    slot=phonon_slot(x,y,z)
    if(.not.phonon_valid(slot).or.any(phonon_keys(:,slot)/=key)) then
      phonon_misses=phonon_misses+1
      weight=Kweight(beta,x,y,z)
      phonon_keys(:,slot)=key
      phonon_values(slot)=weight
      phonon_valid(slot)=.true.
    else
      phonon_hits=phonon_hits+1
      weight=phonon_values(slot)
    end if
  end function
  integer(int64) function phonon_cache_bytes() result(n)
    n=8_int64*(size(phonon_keys,kind=int64)+size(phonon_values,kind=int64))+ &
      4_int64*size(phonon_valid,kind=int64)+8*3+4*3
  end function
end module
