include $(RESEARCH)/portable_gap/full_link.mk

basis-compile: block_linear_operator.o tc_subspace.o
block_linear_operator.o: $(RESEARCH)/portable_gap/block_linear_operator.f90 tiled_operator.o
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
tc_subspace.o: $(RESEARCH)/portable_gap/tc_subspace.f90
	$(MPIF90) $(FF) -fcheck=all -c $< -o $@
