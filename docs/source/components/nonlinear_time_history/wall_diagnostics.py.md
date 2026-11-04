# wall_diagnostics.py — audited E-SFI 3D wall geometry

**Implementation:** [wall_diagnostics.py](../../../../components/nonlinear_time_history/wall_diagnostics.py) → `inspect_wall_geometry`, `write_wall_audit`.

New physical input check: 3D quadrilateral is not sufficient. For OpenSees `E_SFI_MVLEM_3D`, the **i–j bottom edge is wall fiber width** (m) and the **i–l edge rises vertically** (m). The preflight blocks reversed/inclined/misoriented edges before they can be used by `build_complete_model` to allocate macrofiber width. Checks: 4 distinct nodes, finite 3D coordinates, quadrilateral parallelogram closure, positive area, vertical normal, positive thickness, correct i–j / i–l orientation. Actual source tags 110280/112778 are *suspects only*; solver tag mapping is dependent on current frame/shell assembly.

**Test:** [verify_wall_geometry_preflight.py](../../../../tests/verify_wall_geometry_preflight.py) includes valid, duplicate node, NaN thickness, vertical-edge-as-width and upside-down panel cases.

**Scientific basis:** OpenSees [E-SFI-MVLEM-3D](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html) (Kolozvari, Lopez & Massone, 2023, https://doi.org/10.1016/j.engstruct.2023.116700). The official command uses 4 counterclockwise nodes and per-fiber thicknesses/widths/nDMaterial tags. The added horizontal/vertical screening is an **implementation-specific geometric constraint** for the current strict vertical-panel mesher, not a claim that the published element cannot model other orientations.

[Complete P0 audit and native follow-up](../../../review/01_WALL_GEOMETRY_MATERIALS_FIRST_STEP.md).
