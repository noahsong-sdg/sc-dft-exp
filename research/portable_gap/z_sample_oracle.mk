include $(RESEARCH)/portable_gap/z_partial.mk

qualify-oracle: z-oracle.x
	./z-oracle.x -in $(NATIVE_INPUT)
z-oracle.x: z_sample_oracle.o native_oracle_z.o native_rotation.o slab_operator.o native_state_io.o native_coefficients.o hash_stream.o hash_pipe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
native_oracle_z.o: $(RESEARCH)/portable_gap/native_oracle_z.f90 slab_operator.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
z_sample_oracle.o: $(RESEARCH)/portable_gap/z_sample_oracle.f90 native_oracle_z.o native_state_io.o native_coefficients.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
