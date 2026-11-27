# Scalar paper-to-code mapping

Checked 27 November 2026 against [Eq. 17 and supplemental S75–S78](https://arxiv.org/html/2603.05123v2).
The paper explicitly subtracts a zero-gap normal-state current to remove the
finite-grid residual. For nonnegative energy magnitudes x=|xi|, d=|dxq|,
define independently:

    A(y,d) = [tanh(beta*(y+d)/2)+tanh(beta*(y-d)/2)]/2
    D(y,d) = [tanh(beta*(y+d)/2)-tanh(beta*(y-d)/2)]/2

Then the code's e_d/d_e correspond to A(E,d)/D(E,d), and its x_d/d_x to
A(x,d)/D(x,d). Only E=sqrt(xi²+gap²) carries the superconducting gap. The
normal-reference factors cannot contain E at fixed xi, dxq and temperature.
This establishes the scalar discrepancy independently of source naming.

The audit does not yet certify overall current sign, projection, spin factors,
integration weights or experimental units. Those require the complete inversion
pairing and velocity-to-curvature derivation, followed by a native material check.
Do not use this limited map to claim the whole implemented current equals Eq. 17.
