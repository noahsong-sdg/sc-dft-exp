include $(RESEARCH)/public_response_probe.mk

cache-qualification.x: cached_kel.o cached_phonon.o cache_qualification.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)

cached_kel.o: $(RESEARCH)/portable_gap/cached_kel.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
cached_phonon.o: $(RESEARCH)/portable_gap/cached_phonon.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
cache_qualification.o: $(RESEARCH)/portable_gap/cache_qualification.f90 cached_kel.o cached_phonon.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
