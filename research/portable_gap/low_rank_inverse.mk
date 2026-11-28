# Separate source-only diagnostic; preserves all existing native targets.
ifndef QE_ROOT
$(error QE_ROOT must identify the isolated configured source tree)
endif
RESEARCH := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
include $(QE_ROOT)/make.inc
FF := $(F90FLAGS) -ffp-contract=off -ffree-line-length-none -fcheck=all
.DEFAULT_GOAL := inverse-actions.x

inverse-actions.x: reduced_nonlinear_core.o low_rank_inverse.o low_rank_inverse_driver.o
	$(LD) $(LDFLAGS) -o $@ $^ $(LAPACK_LIBS) $(BLAS_LIBS)

reduced_nonlinear_core.o: $(RESEARCH)/reduced_nonlinear_core.f90
	$(MPIF90) $(FF) -c $< -o $@
low_rank_inverse.o: $(RESEARCH)/low_rank_inverse.f90
	$(MPIF90) $(FF) -c $< -o $@
low_rank_inverse_driver.o: $(RESEARCH)/low_rank_inverse_driver.f90 reduced_nonlinear_core.o low_rank_inverse.o
	$(MPIF90) $(FF) -c $< -o $@
