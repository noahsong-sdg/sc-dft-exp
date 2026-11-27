include $(RESEARCH)/portable_gap/cache_qualification.mk

operator-compile: native_rotation.o slab_operator.o tiled_operator.o tc_native_oracle.o cache-qualification.x

native_rotation.o: $(RESEARCH)/portable_gap/native_rotation.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
slab_operator.o: $(RESEARCH)/portable_gap/slab_operator.f90 native_rotation.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
tiled_operator.o: $(RESEARCH)/portable_gap/tiled_operator.f90 slab_operator.o cached_kel.o cached_phonon.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
tc_native_oracle.o: $(RESEARCH)/portable_gap/tc_native_oracle.f90 slab_operator.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
