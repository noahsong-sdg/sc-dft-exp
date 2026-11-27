# Uses the pre-existing historical native libraries without rebuilding them.
# Invoke in a fresh ignored research/raw directory; specify NATIVE_MAKEFILE.
include $(NATIVE_MAKEFILE)

response-preparation.x: response-preparation.o
	$(LD) $(LDFLAGS) -o $@ $^ $(CORELIBS)

response-preparation.o: $(RESPONSE_SOURCE)
	$(MPIF90) $(FF) -c $< -o $@
