include $(NATIVE_MAKEFILE)

# Reuse immutable, already-built dependencies; all new outputs stay in cwd.
RETAINED_OBJECTS = $(addprefix $(NATIVE)/build/,$(OBJECTS))

nonlinear-map-probe.x: nonlinear_map_probe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(RETAINED_OBJECTS) $(MAP_EXTRA_OBJECTS) $(CORELIBS)

nonlinear_map_probe.o: $(MAP_SOURCE)
	$(MPIF90) $(FF) $(MAP_FLAGS) -I$(NATIVE)/build -fcheck=all -c $< -o $@

# Explicit target: one full pass, never the default selected-row diagnostic.
full-nonlinear-probe.x: nonlinear_tile_apply.o full_nonlinear_probe.o full_nonlinear_driver.o
	$(LD) $(LDFLAGS) -o $@ $^ $(RETAINED_OBJECTS) $(MAP_EXTRA_OBJECTS) $(CORELIBS)

nonlinear_tile_apply.o: $(RESEARCH_SOURCE_DIR)/nonlinear_tile_apply.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@

full_nonlinear_probe.o: $(RESEARCH_SOURCE_DIR)/full_nonlinear_probe.f90 nonlinear_tile_apply.o
	$(MPIF90) $(FF) -I$(NATIVE)/build -fcheck=all -c $< -o $@

full_nonlinear_driver.o: $(MAP_SOURCE) full_nonlinear_probe.o
	$(MPIF90) $(FF) $(MAP_FLAGS) -DFULL_MAP -I$(NATIVE)/build -fcheck=all -c $< -o $@

mode-amplitude-probe.x: nonlinear_tile_apply.o mode_amplitude_probe.o mode_amplitude_driver.o
	$(LD) $(LDFLAGS) -o $@ $^ $(RETAINED_OBJECTS) $(MAP_EXTRA_OBJECTS) $(CORELIBS)

mode_amplitude_probe.o: $(RESEARCH_SOURCE_DIR)/mode_amplitude_probe.f90 nonlinear_tile_apply.o
	$(MPIF90) $(FF) -I$(NATIVE)/build -fcheck=all -c $< -o $@

mode_amplitude_driver.o: $(MAP_SOURCE) mode_amplitude_probe.o
	$(MPIF90) $(FF) $(MAP_FLAGS) -DMODE_AMPLITUDE -I$(NATIVE)/build -fcheck=all -c $< -o $@

reduced-nonlinear-solve.x: reduced_nonlinear_core.o reduced_nonlinear_driver.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)

reduced_nonlinear_core.o: $(RESEARCH_SOURCE_DIR)/reduced_nonlinear_core.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@

reduced_nonlinear_driver.o: $(RESEARCH_SOURCE_DIR)/reduced_nonlinear_driver.f90 reduced_nonlinear_core.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
