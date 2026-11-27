include $(RESEARCH)/public_response_probe.mk

grid-probe.x: grid_probe.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
grid_probe.o: $(RESEARCH)/portable_gap/grid_probe.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
qualify-grid: grid-probe.x
	./grid-probe.x $(BANDS) $(REFERENCE) $(ELPH)
