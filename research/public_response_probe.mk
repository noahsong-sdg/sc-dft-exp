# Relocatable response diagnostic; requires a configured serial QE/SCTK tree.
ifndef QE_ROOT
$(error QE_ROOT must identify the isolated configured source tree)
endif
include $(QE_ROOT)/make.inc
RESEARCH := $(abspath $(dir $(lastword $(filter %public_response_probe.mk,$(MAKEFILE_LIST)))))
MODFLAGS := $(MOD_FLAG). $(BASEMOD_FLAGS) $(foreach d,PW/src dft-d3 LR_Modules PP/src PHonon/PH SCTK/src,$(MOD_FLAG)$(QE_ROOT)/$(d))
FF := $(F90FLAGS) -ffp-contract=off -ffree-line-length-none $(MODFLAGS)
CORELIBS := $(QE_ROOT)/SCTK/src/libsctk.a $(QE_ROOT)/PP/src/libpp.a $(QE_ROOT)/PHonon/PH/libph.a $(QE_ROOT)/LR_Modules/liblrmod.a $(QE_ROOT)/PW/src/libpw.a $(QE_ROOT)/KS_Solvers/libks_solvers.a $(QE_ROOT)/dft-d3/libdftd3qe.a $(BASEMODS) $(QELIBS)
.NOTPARALLEL:
velocity-moment-probe.x: velocity_moment_probe.o current_geometry.o response_assignment_dump.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)
current_geometry.o: current_geometry.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
response_assignment_dump.o: $(RESEARCH)/response_assignment_dump.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
velocity_moment_probe.o: $(RESEARCH)/velocity_moment_probe.f90 current_geometry.o response_assignment_dump.o
	$(MPIF90) $(FF) -DCURRENT_GEOMETRY -DASSIGNMENT_DUMP -DMOMENT_CACHE -fcheck=all -c $< -o $@
