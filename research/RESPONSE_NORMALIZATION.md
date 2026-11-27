# Scalar response normalization control

The slope S is lim j_code(Q)/Q in the routine's physical reciprocal norm.
Its energy is Rydberg, length is Bohr, and Q is pair momentum, not electron
momentum. For the tested spin-degenerate convention,

```
(dj/dQ)_SI = S * e * Ry / (hbar * a0)
lambda^-2 = (2*e*mu0/hbar) * (dj/dQ)_SI
```

This follows j_SI=e*Ry/(hbar*a0²)*j_code, Q_SI=Q_code/a0 and the London response
to pair momentum. The factor two belongs to the pair phase. Replacing Ry with
Hartree or adding another spin factor would change the inferred length.

## Independent continuum control

Take a parabolic band xi=k²-1 in Rydberg units, constant gap 0.1, beta=1000,
and a per-spin radial measure k² dk/(2*pi²). At this low temperature the
quasiparticle normal fraction is exponentially small. The Galilean density
identity requires the scalar code slope to equal the total two-spin density.
The density is evaluated from occupations, separately from the current:

```
n_e = integral [1 - xi/E*tanh(beta*E/2)] k² dk/(2*pi²)
```

The radial interval is 0..4 with 12000 midpoint samples. The linear-response
angular average uses <cos²>=1/3; finite-Q angular quadrature errors are allowed
to disappear with Q. This is a continuum control, not the native tetrahedron
geometry or a material approximation. No electron-phonon mass factor is used.

Density is 0.03432557115237991. Analytic code slope differs by -1.61e-11
relative. The complete pinned corrected supercurrent routine, compiled in O0
serial and O3/OpenMP four-thread modes, converges to that density: relative
errors about 1.64e-7, 1.66e-9 and 3.25e-11 at Q=1e-3/1e-4/1e-5. Both synthetic
integration grids agree. The source and fixture hashes are recorded in
free_electron_response_results.json. This independently controls the combined
spin, scalar projection and pair-momentum factors in that routine convention.

The retained native calc_dosk divides its optimized tetrahedron weights by
ntetra and applies no explicit nspin or factor two in that owning routine.
Its total-band normalization and physical material convergence remain separate
checks; the continuum fixture does not execute that tetrahedron path.

`response_units.py` implements the conditional SI conversion using constants
from the retained QE constants.f90, whose full hash is in the module docstring.
It deliberately retains that source's mu0 convention. A regression compares it
with the independent London relation lambda²=m_e/(mu0*n_e*e²); relative agreement
is better than 1e-10. This controls a conversion, not experimental accuracy.

Commands: `python3 research/free_electron_response_probe.py` (passed, pinned
network source and gfortran required); the portable analytic and conversion
regressions also run in the offline unittest suite. No self-consistent Nb gap,
full tensor response, vertex correction, or experimental validation is supplied.
