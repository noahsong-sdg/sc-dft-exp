HERE := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
include $(HERE)/public_response_probe.mk

velocity-moment-probe.x: optimized_tetra.o
velocity_moment_probe.o: optimized_tetra.o
optimized_tetra.o: optimized_tetra.f90
	$(MPIF90) $(FF) -c $< -o $@
