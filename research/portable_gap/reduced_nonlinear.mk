# Source-only reduced solve; existing configured public QE modules are required.
ifndef QE_ROOT
$(error QE_ROOT must identify the isolated configured source tree)
endif
RESEARCH := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
include $(QE_ROOT)/make.inc
FF := $(F90FLAGS) -ffp-contract=off -ffree-line-length-none $(MOD_FLAG)$(QE_ROOT)/Modules
.DEFAULT_GOAL := reduced-nonlinear-solve.x

reduced-nonlinear-solve.x: reduced_nonlinear_core.o reduced_nonlinear_driver.o
	$(LD) $(LDFLAGS) -o $@ $^ $(LAPACK_LIBS) $(BLAS_LIBS)

reduced_nonlinear_core.o: $(RESEARCH)/reduced_nonlinear_core.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@

reduced_nonlinear_driver.o: $(RESEARCH)/reduced_nonlinear_driver.f90 reduced_nonlinear_core.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
