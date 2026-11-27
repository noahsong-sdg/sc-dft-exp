! Checkpointed real nonsymmetric block Rayleigh-Ritz; no physical-kernel approximation.
MODULE tc_subspace
  USE kinds, ONLY: dp
  USE sctk_val, ONLY: ngapmax,ngap,nx,nqbz,nmf,nci,scdft_kernel,emin,Zemin,beta,zero_kelvin, &
    xi0,dx0,xi,delta,dk,dxq,d2xq,kindx,bindx
  USE wvfct, ONLY: nbnd
  USE klist, ONLY: nks
  USE ener, ONLY: ef
  USE,INTRINSIC :: ieee_arithmetic, ONLY: ieee_is_finite
  IMPLICIT NONE
  INTEGER,PARAMETER :: max_basis=64
CONTAINS
  SUBROUTINE write_initial_state()
    INTEGER :: unit,side
    REAL(dp) :: denominator(2)
    IF(ANY(ngap<1).OR.ngapmax/=MAXVAL(ngap)) ERROR STOP 'Invalid native initialization counts'
    IF(.NOT.ALL(ieee_is_finite(xi)).OR..NOT.ALL(ieee_is_finite(dk)).OR.ANY(dxq/=0)) &
      ERROR STOP 'Invalid Q0 initialized state'
    DO side=1,2
      denominator(side)=SUM(dk(:ngap(side),side),ABS(xi(:ngap(side),side))<emin)
      IF(denominator(side)<=0.OR..NOT.ieee_is_finite(denominator(side))) ERROR STOP 'Invalid Fermi norm'
    END DO
    OPEN(NEWUNIT=unit,FILE='native-init.meta',STATUS='new')
    WRITE(unit,'(a)') 'native-init-v1; arrays are native binary64/int32, Fortran order'
    WRITE(unit,*) ngap,ngapmax,nx,nqbz,nbnd,nks
    WRITE(unit,'(7es26.17e3)') ef,emin,Zemin,beta,denominator,MAXVAL(ABS(delta))
    WRITE(unit,*) zero_kelvin
    CLOSE(unit)
    OPEN(NEWUNIT=unit,FILE='native-init.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
    WRITE(unit) xi0,dx0,xi,delta,dk,dxq,d2xq,kindx,bindx
    CLOSE(unit)
  END SUBROUTINE

  SUBROUTINE project_out(vector,basis,ncols)
    REAL(dp),INTENT(INOUT) :: vector(:)
    REAL(dp),INTENT(IN) :: basis(:,:)
    INTEGER,INTENT(IN) :: ncols
    INTEGER :: pass,j
    DO pass=1,2
      DO j=1,ncols
        vector=vector-DOT_PRODUCT(basis(:,j),vector)*basis(:,j)
      END DO
    END DO
  END SUBROUTINE

  SUBROUTINE make_trials(vectors,nvec,seed,informed)
    INTEGER,INTENT(IN) :: nvec,seed
    REAL(dp),INTENT(OUT) :: vectors(ngapmax,2,nvec)
    REAL(dp),INTENT(IN),OPTIONAL :: informed(2*ngapmax)
    REAL(dp),ALLOCATABLE :: q(:,:)
    REAL(dp) :: energy,value,norm
    INTEGER :: i,side,j,index
    ALLOCATE(q(2*ngapmax,nvec)); q=0
    DO j=1,nvec
      DO side=1,2
        DO i=1,ngap(side)
          index=i+(side-1)*ngapmax; energy=ABS(xi(i,side))
          SELECT CASE(j)
          CASE(1)
            value=1.0_dp
          CASE(2)
            value=(1.0_dp-energy/0.002_dp)/(1.0_dp+energy/0.002_dp)
          CASE(3)
            value=EXP(-energy/0.003_dp)*(1.0_dp+0.05_dp*REAL(bindx(i,side),dp))
          CASE(4)
            value=EXP(-energy/0.0005_dp)*(1.0_dp+0.3_dp*SIN(REAL(bindx(i,side),dp)))
          CASE(5)
            value=REAL(3-2*side,dp)/(1.0_dp+energy/0.002_dp)
          CASE DEFAULT
            value=SIN(REAL(index,dp)*(0.123_dp+0.017_dp*j)+REAL(seed*j,dp)) &
              /(1.0_dp+energy/(0.0002_dp*REAL(j,dp)))
          END SELECT
          ! Independent seeds perturb every informed shape without removing its channel.
          q(index,j)=value+0.02_dp*SIN(REAL(index*(j+1),dp)+REAL(seed,dp))/(1+energy/0.001_dp)
        END DO
      END DO
      IF(j==1.AND.PRESENT(informed)) q(:,j)=informed
      CALL project_out(q(:,j),q,j-1)
      norm=SQRT(DOT_PRODUCT(q(:,j),q(:,j)))
      IF(norm<1e-12_dp) ERROR STOP 'Initial trial block lost rank'
      q(:,j)=q(:,j)/norm
    END DO
    vectors=RESHAPE(q,SHAPE(vectors))
  END SUBROUTINE

  SUBROUTINE conventional_channel(vector,residual_inf,code,averages,margin)
    REAL(dp),INTENT(IN) :: vector(:),residual_inf
    INTEGER,INTENT(OUT) :: code
    REAL(dp),INTENT(OUT) :: averages(2),margin
    REAL(dp) :: denominator,orientation,value,norm
    INTEGER :: side,i,index,nfermi
    LOGICAL :: node,ambiguous
    norm=SQRT(DOT_PRODUCT(vector,vector)); nfermi=0; averages=0
    DO side=1,2
      denominator=0
      DO i=1,ngap(side)
        IF(dk(i,side)<=0.OR.ABS(xi(i,side))>=emin) CYCLE
        index=i+(side-1)*ngapmax
        averages(side)=averages(side)+dk(i,side)*vector(index)
        denominator=denominator+dk(i,side); nfermi=nfermi+1
      END DO
      IF(denominator<=0) ERROR STOP 'No Fermi support for branch check'
      averages(side)=averages(side)/denominator
    END DO
    margin=MAX(1e-10_dp*MAXVAL(ABS(vector)),100.0_dp*residual_inf)
    code=0
    IF(ANY(ABS(averages)<=margin)) THEN
      code=-1; RETURN
    END IF
    IF(SIGN(1.0_dp,averages(1))/=SIGN(1.0_dp,averages(2))) RETURN
    orientation=SIGN(1.0_dp,averages(1)); node=.FALSE.; ambiguous=.FALSE.
    DO side=1,2
      DO i=1,ngap(side)
        IF(dk(i,side)<=0.OR.ABS(xi(i,side))>=emin) CYCLE
        index=i+(side-1)*ngapmax; value=orientation*vector(index)
        IF(value < -margin) node=.TRUE.
        IF(ABS(value)<=margin) ambiguous=.TRUE.
      END DO
    END DO
    IF(node) RETURN
    code=1
    IF(ambiguous) code=-1
  END SUBROUTINE

  SUBROUTINE ritz_checkpoint(vectors,images,nvec,source,directory,context)
    INTEGER,INTENT(IN) :: nvec
    REAL(dp),INTENT(IN) :: vectors(ngapmax,2,nvec),images(ngapmax,2,nvec)
    CHARACTER(*),INTENT(IN) :: source,directory,context
    REAL(dp),ALLOCATABLE :: q(:,:),aq(:,:),h(:,:),a(:,:),wr(:),wi(:),vr(:,:),work(:), &
      vector(:),image(:),residual(:),next(:,:),chosen(:),chosen_r(:),dummy(:,:)
    REAL(dp) :: expected_beta,saved_beta,norm,error,relative,averages(2),margin,selected,best_error,orth
    INTEGER :: n,old,m,unit,ios,info,j,k,code,count_next,best,nbytes,actual_bytes,config(6)
    CHARACTER(256) :: header,saved_context
    n=2*ngapmax; old=0; expected_beta=beta
    IF(LEN_TRIM(context)/=64.OR.VERIFY(TRIM(context),'0123456789abcdef')/=0) &
      ERROR STOP 'Invalid operator context identity'
    ALLOCATE(q(n,max_basis),aq(n,max_basis)); q=0; aq=0
    IF(source/='-') THEN
      OPEN(NEWUNIT=unit,FILE=TRIM(source)//'/basis.meta',STATUS='old')
      READ(unit,'(a)') header
      IF(header/='tc-basis-v1') ERROR STOP 'Stale Krylov schema'
      READ(unit,*) k,old
      READ(unit,*) saved_beta
      READ(unit,'(a)') saved_context
      READ(unit,*) config
      READ(unit,*,IOSTAT=ios)
      CLOSE(unit)
      IF(ios>=0.OR.k/=n.OR.old<1.OR.old+nvec>max_basis.OR.saved_beta/=expected_beta) &
        ERROR STOP 'Stale Krylov dimensions/temperature'
      IF(saved_context/=context.OR.ANY(config/=[nx,nmf,nci,scdft_kernel,ngap])) &
        ERROR STOP 'Stale Krylov operator context'
      INQUIRE(IOLENGTH=nbytes) q(:,:old),aq(:,:old)
      INQUIRE(FILE=TRIM(source)//'/basis.bin',SIZE=actual_bytes)
      IF(actual_bytes/=nbytes) ERROR STOP 'Stale Krylov binary size'
      OPEN(NEWUNIT=unit,FILE=TRIM(source)//'/basis.bin',STATUS='old',ACCESS='stream',FORM='unformatted')
      READ(unit) q(:,:old),aq(:,:old)
      CLOSE(unit)
    END IF
    m=old+nvec
    IF(m>max_basis) ERROR STOP 'Registered Krylov dimension exhausted'
    q(:,old+1:m)=RESHAPE(vectors,[n,nvec]); aq(:,old+1:m)=RESHAPE(images,[n,nvec])
    IF(.NOT.ALL(ieee_is_finite(q)).OR..NOT.ALL(ieee_is_finite(aq))) ERROR STOP 'Nonfinite Krylov state'
    orth=0
    DO j=1,m
      DO k=1,m
        norm=DOT_PRODUCT(q(:,j),q(:,k))
        IF(j==k) norm=norm-1
        orth=MAX(orth,ABS(norm))
      END DO
    END DO
    IF(orth>1e-10_dp) ERROR STOP 'Krylov orthogonality failed'
    ALLOCATE(h(m,m),a(m,m),wr(m),wi(m),vr(m,m),work(MAX(1,16*m)),dummy(1,1))
    h=MATMUL(TRANSPOSE(q(:,:m)),aq(:,:m)); a=h
    CALL dgeev('N','V',m,a,m,wr,wi,dummy,1,vr,m,work,SIZE(work),info)
    IF(info/=0) ERROR STOP 'Projected nonsymmetric eigensolver failed'
    ALLOCATE(vector(n),image(n),residual(n),chosen(n),chosen_r(n)); selected=-HUGE(1.0_dp); best=0
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/ritz.meta',STATUS='new')
    WRITE(unit,'(a)') 'tc-ritz-v1; index real imag normalized-residual channel avg1 avg2 margin'
    DO j=1,m
      IF(wi(j)/=0.0_dp) THEN
        WRITE(unit,'(i6,2es26.17e3)') j,wr(j),wi(j)
        CYCLE
      END IF
      vector=MATMUL(q(:,:m),vr(:,j)); image=MATMUL(aq(:,:m),vr(:,j))
      residual=image-wr(j)*vector
      error=SQRT(DOT_PRODUCT(residual,residual))
      relative=error/MAX(SQRT(DOT_PRODUCT(image,image)),ABS(wr(j))*SQRT(DOT_PRODUCT(vector,vector)),TINY(1.0_dp))
      CALL conventional_channel(vector,MAXVAL(ABS(residual)),code,averages,margin)
      WRITE(unit,'(i6,3es26.17e3,i4,3es26.17e3)') j,wr(j),wi(j),relative,code,averages,margin
      IF(wr(j)>0.AND.code==1.AND.wr(j)>selected) THEN
        selected=wr(j); best=j; best_error=relative; chosen=vector; chosen_r=residual
      END IF
    END DO
    CLOSE(unit)
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/reduced.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
    WRITE(unit) h,wr,wi,vr
    CLOSE(unit)
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/selected.meta',STATUS='new')
    WRITE(unit,*) best,m
    IF(best>0) WRITE(unit,'(2es26.17e3)') selected,best_error
    CLOSE(unit)
    IF(best>0) THEN
      OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/selected.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
      WRITE(unit) chosen,chosen_r
      CLOSE(unit)
      OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/selected-coefficients.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
      WRITE(unit) vr(:,best)
      CLOSE(unit)
    END IF
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/basis.meta',STATUS='new')
    WRITE(unit,'(a)') 'tc-basis-v1'
    WRITE(unit,*) n,m
    WRITE(unit,'(es26.17e3)') beta
    WRITE(unit,'(a)') TRIM(context)
    WRITE(unit,*) nx,nmf,nci,scdft_kernel,ngap
    CLOSE(unit)
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/basis.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
    WRITE(unit) q(:,:m),aq(:,:m)
    CLOSE(unit)
    ALLOCATE(next(n,nvec)); next=0; count_next=0
    DO j=old+1,m
      vector=aq(:,j)
      CALL project_out(vector,q,m)
      CALL project_out(vector,next,count_next)
      norm=SQRT(DOT_PRODUCT(vector,vector))
      IF(norm<1e-12_dp) CYCLE
      count_next=count_next+1; next(:,count_next)=vector/norm
    END DO
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/next.meta',STATUS='new')
    WRITE(unit,*) count_next
    CLOSE(unit)
    OPEN(NEWUNIT=unit,FILE=TRIM(directory)//'/next-vectors.bin',STATUS='new',ACCESS='stream',FORM='unformatted')
    WRITE(unit) next(:,:count_next)
    CLOSE(unit)
    WRITE(*,'(a,2i8,2es26.17e3)') 'TC_SUBSPACE ',m,count_next,orth,selected
  END SUBROUTINE
END MODULE
