# 22 — Wall failure preflight

Before gravity/eigen/transient, the exploratory runner now writes `NLTHA_Wall_Geometry_Preflight.json` from its isolated model. It checks every wall quad for finite coordinates, distinct nodes, verticality, thickness and nonzero area, and flags the earlier V168 suspects AREA:354/482. Invalid geometry stops analysis. It does **not** prove solver convergence, adjacent-panel compatibility, wall openings or experimental calibration.

Source formulation: Kolozvari, Lopez & Massone (2023), https://doi.org/10.1016/j.engstruct.2023.116700.

Run `python tests/verify_wall_geometry_preflight.py` for solver-free tests, then run ZERO/X/Y/XY fresh nonlinear probe processes. The earliest accepted solution and the failure step still require native OpenSees review.
