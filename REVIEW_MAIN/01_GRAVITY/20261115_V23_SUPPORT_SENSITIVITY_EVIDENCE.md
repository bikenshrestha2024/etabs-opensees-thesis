# V23 — 32/76/97 support sensitivity data-integrity review
**Date:** 2026-11-15  
**Status:** SOURCE_CHECKS_CORRECTED / NATIVE_SUPPORT_EQUIVALENCE_OPEN

## Confirmed defects

In `components/gravity/support_scenarios.py::compare_wall_support_gravity`, maps were previously assembled using `{str(tag): row}`; repeated source reaction/node tags therefore silently overwrote earlier rows, potentially changing support counts, reaction comparison and location evidence. Shared tags were compared without confirming the same global XYZ, and source-only tags were displayed using the continuous-model coordinate map alone.

The V23 implementation rejects repeated native node/reaction tags, missing or nonfinite recorded node coordinates, and common reaction tags whose source/continuous XYZ differ by more than 1e-6 m. It preserves source-only node locations. It also independently sums each scenario's saved finite `rz_kN` rows and compares with `report.support_vertical_reaction_kN` within `max(0.01 kN, 1e-6 × |reported kN|)`. This guards against stale or mixed-case summaries. It is **not** a tolerance for actual global equilibrium or ETABS equivalence.

Regression tests: `tests/verify_gravity_support_scenarios.py`. The existing native point-axis verification in `components/validation/gravity_node_comparison.py` remains mandatory.

## Three different support models — not interchangeable

1. **32 reaction-bearing locations:** user-preferred physical support interpretation; must be tied to exact ETABS original supports and all six DOFs.
2. **76 ETABS source-restraint nodes:** source constraint strategy; should not be equated to 32 merely because only some have nonzero reactions.
3. **97 continuous-wall base:** separately idealized fully restrained mesh-base sensitivity; must never be described as a proved ETABS foundation configuration.

For each actual comparison retain source SHA/EDB hash, supported-node IDs/XYZ, restraint six-vector and DOF axes, loads and mass, solver return, sum Fx/Fy/Fz/Mx/My/Mz, node-by-node reactions, source and target beam/wall slab load paths and model geometry. Only after 32/76/97 are individually justified against native ETABS may the project select a physical boundary condition. No new physical restraints were applied in V23.

## Output location recommendation

`<LOCAL_EXPORT>/02_GRAVITY/RUNS/<ULS_OR_SLS>/<SUPPORT_STRATEGY>/<RUN_ID>/` with `00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`, `04_FIGURES`, `05_COMPARISONS`, `06_REVIEW`, `07_EXPORT_ZIP` and manifest. Legacy producer/reader migration requires a separate compatibility-tested change; no old output has been moved here.
