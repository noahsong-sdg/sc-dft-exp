! Native accumulation expressions; residency extent does not change physical lsf.
MODULE slab_operator
  USE kinds
  USE sctk_val
  USE modes
  USE el_phon
  USE disp
  USE symm_base,ONLY: nsym
  USE native_rotation,ONLY: k_kplusq_sym
  IMPLICIT NONE
  INTEGER :: reloads=0
CONTAINS
  SUBROUTINE clear_slab()
    IF(ALLOCATED(Vc)) DEALLOCATE(Vc)
    IF(ALLOCATED(gg)) DEALLOCATE(gg)
    IF(ALLOCATED(omg)) DEALLOCATE(omg)
  END SUBROUTINE
  INTEGER FUNCTION stored_channels() RESULT(channels)
    IF(.NOT.ALLOCATED(Vc0)) ERROR STOP 'Compact Coulomb required'
    channels=SIZE(Vc0,1)
    IF(channels/=nci.AND.channels/=nci*lsf) ERROR STOP 'Invalid compact channel residency'
  END FUNCTION
  SUBROUTINE ensure_slab(ik,width)
    INTEGER,INTENT(IN) :: ik,width
    INTEGER :: first,last,channels
    IF(width<1.OR.ik<1.OR.ik>nqbz) ERROR STOP 'Invalid slab request'
    channels=stored_channels()
    IF(ALLOCATED(Vc)) THEN
      IF(SIZE(Vc,1)==channels.AND.ik>=LBOUND(Vc,5).AND.ik<=UBOUND(Vc,5)) RETURN
    END IF
    first=1+((ik-1)/width)*width
    last=MIN(nqbz,first+width-1)
    CALL expand_slab(first,last)
  END SUBROUTINE
  SUBROUTINE expand_slab(first,last)
    INTEGER,INTENT(IN) :: first,last
    INTEGER,ALLOCATABLE :: nqsym(:,:),iks(:,:,:,:)
    INTEGER :: ik,iq,ii,jk,ik2,multiplicity,channels
    IF(first<1.OR.last>nqbz.OR.last<first) ERROR STOP 'Invalid slab bounds'
    IF(.NOT.ALLOCATED(gg0).OR..NOT.ALLOCATED(omg0)) ERROR STOP 'Compact interactions required'
    channels=stored_channels()
    CALL clear_slab()
    ALLOCATE(Vc(channels,fbee:lbee,nqbz,fbee:lbee,first:last), &
      gg(nmodes,elph_nbnd_min:elph_nbnd_max,nqbz,elph_nbnd_min:elph_nbnd_max,first:last), &
      omg(nmodes,nqbz,first:last),nqsym(nqs,first:last),iks(2,nsym*2,nqs,first:last))
    CALL k_kplusq_sym(first,last,nqsym,iks)
    Vc=0d0; gg=0d0; omg=0d0
    DO ik=first,last
      DO iq=1,nqs
        DO ii=1,nqsym(iq,ik)
          jk=iks(1,ii,iq,ik); ik2=iks(2,ii,iq,ik)
          Vc(:,:,jk,:,ik)=Vc(:,:,jk,:,ik)+Vc0(1:channels,fbee:lbee,fbee:lbee,ik2,iq)
          gg(:,:,jk,:,ik)=gg(:,:,jk,:,ik)+gg0(:,:,:,ik2,iq)
          omg(:,jk,ik)=omg(:,jk,ik)+omg0(:,iq)
        END DO
      END DO
      DO jk=1,nqbz
        multiplicity=COUNT(iks(1,1:nsym*2,1:nqs,ik)==jk)
        IF(multiplicity==0) ERROR STOP 'Uncovered symmetry target'
        Vc(:,:,jk,:,ik)=Vc(:,:,jk,:,ik)/REAL(multiplicity,DP)
        gg(:,:,jk,:,ik)=gg(:,:,jk,:,ik)/REAL(multiplicity,DP)
        omg(:,jk,ik)=omg(:,jk,ik)/REAL(multiplicity,DP)
      END DO
    END DO
    DEALLOCATE(nqsym,iks)
    reloads=reloads+1
  END SUBROUTINE
END MODULE
