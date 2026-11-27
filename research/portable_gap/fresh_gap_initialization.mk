include $(RESEARCH)/public_response_probe.mk

fresh-gap-init.x: fresh_gap_initialization.o native_state_io.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
native_state_io.o: $(RESEARCH)/portable_gap/native_state_io.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
fresh_gap_initialization.o: $(RESEARCH)/portable_gap/fresh_gap_initialization.f90 native_state_io.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
qualify-initialization: fresh-gap-init.x
	./fresh-gap-init.x -in $(NATIVE_INPUT)
