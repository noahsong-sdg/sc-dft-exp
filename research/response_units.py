"""SI bridge for the audited Rydberg-current slope, not a material predictor.

Compatibility constants copied from the retained QE Modules/constants.f90,
SHA256 56c39e90c6f0592aff13972cd090292024a3d4e9e86d0ce4fdfdb5643f1ac1c0.
Its mu0=4*pi*1e-7 convention is retained for reproducibility, not metrology.
"""
import math

ELECTRON_CHARGE=1.602176634e-19
HBAR=6.62607015e-34/(2*math.pi)
RYDBERG=4.3597447222071e-18/2
BOHR=0.529177210903e-10
MU0=4*math.pi*1e-7


def penetration_depth_nm(slope):
    """Convert positive lim j_code/Q_code to the corresponding London length.

    Assumes the tested scalar pair-Q, single-spin quadrature convention.
    Supplying an unconverged or imposed-gap slope does not validate that slope.
    """
    if not math.isfinite(slope) or slope<=0:
        raise ValueError('Positive finite stiffness required for a real London length')
    slope_si=slope*ELECTRON_CHARGE*RYDBERG/(HBAR*BOHR)
    return 1e9*math.sqrt(HBAR/(2*ELECTRON_CHARGE*MU0*slope_si))
