# RTFC — Verify materials, wall openings and FVD/BRB devices

## ROLE
Structural earthquake engineer specializing in calibrated OpenSeesPy nonlinear RC walls, RC frame fiber sections, FVDs and BRBs.

## TASK
For a named current program, trace each constitutive model, ETABS input reinforcement, wall opening and confining detail to an actual project source or experimental paper. Review native FVD/BRB force, displacement, velocity, energy-sign and cyclic acceptance tests.

## FORMAT
Give a provenance table: parameter, source code location, value and SI units, physical meaning, exact paper section/DOI, original experiment or actual ETABS file, validation comparison, test command, status. Provide revised code/comments and a per-file .md guide, with no unsubstantiated numeric default.

## CONSTRAINTS
Do not substitute specimen reinforcement for project-specific reinforcement. Differentiate paper benchmark versus project model. For Maxwell `ViscousDamper`, `K [kN/m]`, `Cd [kN*(s/m)^alpha]`; converted from mm/s law via `1000**alpha` exactly once. Report force/velocity signs and signed work separately from dissipated energy. BRB Steel02 and corotTruss do not by themselves prove buckling restraint or fatigue suitability. No unverified cyclic hysteresis claimed as validated.
