# shell_mesh_quality.py: shell mesh-quality audit and wall cell-size validator

**Implementation:** [shell_mesh_quality.py](../../../../components/model/shell_mesh_quality.py), with `audit_shell_mesh_quality` and `validate_wall_max_cell_size`.

**Status:** geometry diagnostic only (`DIAGNOSTIC_MESH_GEOMETRY_ONLY_NOT_ACCEPTANCE`). The audit never changes nodes, cells, loads, mass, stiffness or solver input. A small aspect ratio is not engineering acceptance: you still need a native OpenSees re-solve compared with ETABS.

## `audit_shell_mesh_quality(nodes, shells, *, wall_max_cell_size_m=None, floor_subdivisions=None)`

- **Inputs:** `nodes` maps tag to `[x, y, z]` in metres. `shells` are four-node cells with `nodes`, `category` and optional `area`, as written by `assembly._mesh_areas`.
- **Per category** (`SHEAR WALL`, `FLOOR`, ...): `cell_count`, `min_edge_m`, `max_edge_m`, `max_aspect_ratio` (max/min cell edge), `total_area_m2` and `cells_aspect_gt_4/10/50`. Wall cells also report horizontal width (i→j edge) and vertical extent (i→l edge, the assembly wall convention), plus the distinct vertical extents.
- **`hanging_node_count`:** the number of nodes that lie strictly inside another cell edge on the same line (T-junctions, non-conforming). Edges are grouped by line direction and foot point, rounded to 1e-6 m.
- **`wall_max_cell_size_satisfied`:** `None` when no limit is set. Otherwise it is true when every wall cell edge is ≤ the limit, with a relative tolerance of 1e-6.
- **Where it is written:** `prepare_complete_export` puts the audit in `OpenSees_Complete_Export_Report_V118.json` (`shell_mesh_quality_audit`, `wall_max_cell_size_m`). `mesh_cases.build_case` copies it into `MESH_BUILD_STATUS.json`. No new output file is created, and the model-data JSON is unchanged.

## `validate_wall_max_cell_size(value)`

The value `None` (key absent) keeps the historical mesh. Positive finite numbers (metres) are returned as `float`. Booleans, strings, NaN, inf and values ≤ 0 raise `ValueError`.

## Measured on the user's MESH_04/08/16 exports (2026-11-21)

These values come from `OpenSees_Complete_Model_Data_V118.json` in each run. They are recorded in [the gravity run finding §7.7](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md).

| Mesh | Wall cells | Wall width (m) | Wall vertical extent (m) | Max wall aspect | Wall cells >4 / >10 / >50 | Floor max edge (m) | Hanging nodes |
|---|---|---|---|---|---|---|---|
| MESH_04 | 3,400 | 0.1–1.2 | 1.5 / 2.3 / 3.8 | 23 | 2,350 / 750 / 0 | 1.5 | 1,250 |
| MESH_08 | 4,700 | 0.05–0.75 | 1.5 / 2.3 / 3.8 | 46 | 4,000 / 1,500 / 0 | 0.75 | 1,250 |
| MESH_16 | 7,500 | 0.025–0.375 | 1.5 / 2.3 / 3.8 | 92 | 7,400 / 5,100 / 550 | 0.375 | 1,250 |

Tests: `tests/test_wall_mesh_refinement_option.py` (synthetic panels only).
