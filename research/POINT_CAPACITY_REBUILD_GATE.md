# Prospective dense-grid storage qualification

Latest qualification: fresh npk300000 build PASS265.485s/474333184B peak
individual RSS; unchanged32cubed native diagnostic PASS35.672s/187219968B.
All8exports match the original public run bit for bit, all declared inputs
remain unchanged and the native controls/cache reader pass. See
public_capacity_build_result.json and public_capacity_response_result.json.
The protocol below was registered before these executions; this result
qualifies only the tested storage change, not finer-grid or physical accuracy.


The owning path is `read_file_new -> read_a2fsave -> calc_d_xi_q`.
`read_a2fsave` expands the irreducible bands into a full mesh and writes
`klist.xk(:,1:nk1*nk2*nk3)`. Pinned QE defines `npk=40000` in
`Modules/parameters.f90`; `PW/src/pwcom.f90` declares `xk(3,npk)`, `wk(npk)`
and `isk(npk)`. Thus32³ fits,48³ does not. In plain terms, the coordinate
storage is too short even if the laptop has enough RAM. This is a concrete
storage invariant, not evidence that the physics or hardware cannot scale.

The smallest coherent intervention is a fresh, consistent build with only that
constant enlarged to300000, supporting up to64³ full-grid points. Reusing old
module/object files would risk inconsistent array layouts. Changing the grid
reader or response equations is unnecessary for this bound and would introduce
a separate numerical change. The original default build remains40000.

`build_public_response.py --point-capacity 300000` records the one-line source
patch and the capacity in its result. All previously qualified archive pins,
compiler/library controls and compatibility exports remain unchanged. The exact
original declaration must be present once; changed/repeated declarations are
rejected. A compiled bounds-checking fixture fails at48³ with40000 and passes
after consistently rebuilding the module/client with300000. That fixture does
not substitute for full native qualification.

Launch decision remains conditional on the all897-point saved-density replay.
If it reproduces all23322 eigenvalues at the declared1e-6Ry target within its
600s guard, one fresh capacity build is justified: forecast about262s from the
previous complete build,1200s/3GiB guard,120s normal-pressure launch window,
no concurrent heavy job. Use the already hash-qualified source archive cache;
no retained objects or configured tree. Keep its complete destination under the
public guard run root so workspace accounting includes its output.

After a passing build, repeat the exact32³ public response diagnostic at
`SCTK_MOMENT_GRID=8`, unchanged input hashes and native controls. Require all
eight exported files to match the original public diagnostic bit for bit.
Any difference must be investigated before larger-grid response runs. A passing
baseline only qualifies this storage change on the tested path.

A subsequent48³/64³ study still requires its own prospective protocol: saved
charge-density reuse, exact generated band-grid provenance, unchanged phonon
inputs, response-cell grid and imposed-gap controls, measured cost and resource
bounds. Keep derivative-grid refinement distinct from response-cell interpolation
and from stationary-gap accuracy. Neither a successful rebuild nor a converged
constant-gap diagnostic proves a material penetration depth or newly practical
physical prediction.
