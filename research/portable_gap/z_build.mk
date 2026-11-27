include $(RESEARCH)/public_response_probe.mk

qualify-z: z-qualification.x slab_z.o
	./z-qualification.x
z-qualification.x: z_qualification.o zsf_workspace.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
zsf_workspace.o: $(RESEARCH)/portable_gap/zsf_workspace.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
z_qualification.o: $(RESEARCH)/portable_gap/z_qualification.f90 zsf_workspace.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
native_rotation.o: $(RESEARCH)/portable_gap/native_rotation.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
slab_operator.o: $(RESEARCH)/portable_gap/slab_operator.f90 native_rotation.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
slab_z.o: $(RESEARCH)/portable_gap/slab_z.f90 slab_operator.o zsf_workspace.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
