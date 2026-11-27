include $(NATIVE_MAKEFILE)

ifdef GEOMETRY_SOURCE
GEOMETRY_OBJECT = current_geometry.o
GEOMETRY_FLAG = -DCURRENT_GEOMETRY
current_geometry.o: $(GEOMETRY_SOURCE)
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
endif

ifdef ASSIGNMENT_DUMP_SOURCE
ASSIGNMENT_OBJECT = response_assignment_dump.o
ASSIGNMENT_FLAG = -DASSIGNMENT_DUMP
response_assignment_dump.o: $(ASSIGNMENT_DUMP_SOURCE)
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
endif

velocity-moment-probe.x: velocity_moment_probe.o $(GEOMETRY_OBJECT) $(ASSIGNMENT_OBJECT)
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)

velocity_moment_probe.o: $(MOMENT_SOURCE) $(GEOMETRY_OBJECT) $(ASSIGNMENT_OBJECT)
	$(MPIF90) $(FF) $(GEOMETRY_FLAG) $(ASSIGNMENT_FLAG) -fcheck=all -c $< -o $@
