include $(RESEARCH)/portable_gap/basis_compile.mk

qualify-basis-partial: basis-partial.x
	./basis-partial.x -in $(NATIVE_INPUT)
basis-partial.x: basis_partial_driver.o block_linear_operator.o tc_subspace.o native_rotation.o slab_operator.o cached_kel.o cached_phonon.o tiled_operator.o tc_native_oracle.o native_coefficients.o streamed_coulomb.o saved_coulomb.o native_state_io.o hash_stream.o hash_pipe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
basis_partial_driver.o: $(RESEARCH)/portable_gap/basis_partial_driver.f90 block_linear_operator.o tc_subspace.o native_state_io.o saved_coulomb.o tc_native_oracle.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
