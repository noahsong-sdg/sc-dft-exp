include $(NATIVE_MAKEFILE)

# Reuse immutable, already-built dependencies; all new outputs stay in cwd.
RETAINED_OBJECTS = $(addprefix $(NATIVE)/build/,$(OBJECTS))

nonlinear-map-probe.x: nonlinear_map_probe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(RETAINED_OBJECTS) $(MAP_EXTRA_OBJECTS) $(CORELIBS)

nonlinear_map_probe.o: $(MAP_SOURCE)
	$(MPIF90) $(FF) $(MAP_FLAGS) -I$(NATIVE)/build -fcheck=all -c $< -o $@
