include $(NATIVE_MAKEFILE)

velocity-moment-probe.x: velocity_moment_probe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)

velocity_moment_probe.o: $(MOMENT_SOURCE)
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
