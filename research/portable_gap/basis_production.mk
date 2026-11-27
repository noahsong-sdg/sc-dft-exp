include $(RESEARCH)/portable_gap/basis_compile.mk

produce-basis: basis-production.x
	./basis-production.x -in $(NATIVE_INPUT)
basis-production.x: basis_production_driver.o linear_image_checkpoint.o block_linear_operator.o tc_subspace.o native_rotation.o slab_operator.o cached_kel.o cached_phonon.o tiled_operator.o tc_native_oracle.o native_coefficients.o streamed_coulomb.o saved_coulomb.o native_state_io.o hash_stream.o hash_pipe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
linear_image_checkpoint.o: $(RESEARCH)/portable_gap/linear_image_checkpoint.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
basis_production_driver.o: $(RESEARCH)/portable_gap/basis_production_driver.f90 linear_image_checkpoint.o block_linear_operator.o native_state_io.o saved_coulomb.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
