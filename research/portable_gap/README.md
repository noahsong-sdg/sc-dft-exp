# Source-only gap dependency migration

This directory is the first slice of the active fourteen-day campaign. Cached
kernel sources are copied byte-for-byte from the user's retained SCTK-derived
implementation; `source_provenance.json` records their origin and hashes.
They derive from Mitsuaki Kawamura's GPL SCTK kernel work; original SCTK copyright
and license remain applicable. This directory's Fortran code is GPL-2.0-or-later;
see ../../licenses/GPL-2.0.txt. No upstream source or binary is relicensed as CC-BY.

The qualification compares cache calls with the original public SCTK functions,
including context changes and colliding cache slots. It establishes arithmetic
preservation for these cases, not physical response accuracy or a complete gap build.
Public QE/SCTK libraries were source-built separately; this slice rebuilds only
the migrated custom modules. Historical object/module files are not consumed.
