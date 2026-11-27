HERE := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
include $(HERE)/public_response_probe.mk

a2f-serialize.x: a2f_serialization.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
a2f_serialization.o: $(HERE)/a2f_serialization.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
