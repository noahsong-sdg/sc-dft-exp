include $(RESEARCH)/portable_gap/z_partial.mk

qualify-sweep: z-sweep.x
	./z-sweep.x -in $(NATIVE_INPUT)
z-sweep.x: z_sweep_driver.o z_checkpoint.o prefix_operator.o zsf_workspace.o native_rotation.o slab_operator.o native_state_io.o native_coefficients.o hash_stream.o hash_pipe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
z_checkpoint.o: $(RESEARCH)/portable_gap/z_checkpoint.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
z_sweep_driver.o: $(RESEARCH)/portable_gap/z_sweep_driver.f90 z_checkpoint.o prefix_operator.o native_state_io.o native_coefficients.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
