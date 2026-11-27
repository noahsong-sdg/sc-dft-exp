HERE := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
include $(HERE)/public_response_probe.mk

velocity-moment-probe.x: indexed_tetra.o mesh_equivalence.o
velocity_moment_probe.o: indexed_tetra.o
indexed_tetra.o: indexed_tetra.f90 mesh_equivalence.o
	$(MPIF90) $(FF) -c $< -o $@
mesh_equivalence.o: $(HERE)/mesh_equivalence.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
