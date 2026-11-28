include $(RESEARCH)/portable_gap/operator_compile.mk

full-link: full-gap-check.x cache-qualification.x

full-gap-check.x: native_rotation.o slab_operator.o cached_kel.o cached_phonon.o tiled_operator.o tc_native_oracle.o native_coefficients.o streamed_coulomb.o saved_coulomb.o native_state_io.o hash_stream.o hash_pipe.o compact_defect_io.o streamed_defect_core.o enrichment_action_core.o full_nonlinear_probe.o gap_seed_io.o full_driver.o
	$(LD) $(LDFLAGS) -o $@ $^ $(DEFECT_BLAS) $(CORELIBS)

native_coefficients.o: $(RESEARCH)/portable_gap/native_coefficients.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
streamed_coulomb.o: $(RESEARCH)/portable_gap/streamed_coulomb.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
saved_coulomb.o: $(RESEARCH)/portable_gap/saved_coulomb.f90 native_coefficients.o streamed_coulomb.o slab_operator.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
native_state_io.o: $(RESEARCH)/portable_gap/native_state_io.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
hash_stream.o hash_pipe.o: %.o: $(RESEARCH)/portable_gap/%.c
	/usr/bin/clang -O2 -Wall -Wextra -c $< -o $@
compact_defect_io.o: $(RESEARCH)/compact_defect_io.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
streamed_defect_core.o: $(RESEARCH)/streamed_defect_core.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
enrichment_action_core.o: $(RESEARCH)/enrichment_action_core.f90 streamed_defect_core.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
full_nonlinear_probe.o: $(RESEARCH)/resolved_action_native_pass.f90 compact_defect_io.o streamed_defect_core.o enrichment_action_core.o tiled_operator.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
gap_seed_io.o: $(RESEARCH)/gap_seed_io.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
full_driver.o: $(RESEARCH)/nonlinear_map_probe.f90 full_nonlinear_probe.o gap_seed_io.o native_state_io.o saved_coulomb.o tc_native_oracle.o
	$(MPIF90) $(FF) -DFULL_MAP -DVERIFY_SEED -fcheck=all -c $< -o $@
