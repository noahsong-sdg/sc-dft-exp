include $(RESEARCH)/portable_gap/z_build.mk

qualify-partial: z-partial.x
	./z-partial.x -in $(NATIVE_INPUT)
z-partial.x: z_partial_driver.o prefix_operator.o zsf_workspace.o native_rotation.o slab_operator.o native_state_io.o native_coefficients.o hash_stream.o hash_pipe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
prefix_operator.o: $(RESEARCH)/portable_gap/prefix_operator.f90 slab_operator.o zsf_workspace.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
native_state_io.o native_coefficients.o: %.o: $(RESEARCH)/portable_gap/%.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
hash_stream.o hash_pipe.o: %.o: $(RESEARCH)/portable_gap/%.c
	/usr/bin/clang -O2 -Wall -Wextra -c $< -o $@
z_partial_driver.o: $(RESEARCH)/portable_gap/z_partial_driver.f90 prefix_operator.o native_state_io.o native_coefficients.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
