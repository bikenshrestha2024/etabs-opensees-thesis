# etabs_comparison_preset.py: named ETABS elastic comparison preset

**Implementation:** [etabs_comparison_preset.py](../../../../components/model/etabs_comparison_preset.py) (`preset_settings`, `apply_preset`). Used by `tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py --comparison-preset ETABS_ELASTIC_GRAVITY_COMPARISON`.

**Status:** opt-in diagnostic configuration for ETABS-vs-OpenSees elastic comparisons (gravity reactions, modal and Rayleigh). Production defaults are not changed. Solver agreement obtained with it is `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.

## `ETABS_ELASTIC_GRAVITY_COMPARISON`

Every item is set because an ETABS table in the user's assignment export (`Assignment_Export_ULS_3_storey_latest.xlsx`, SHA-256 8b3a6b33…) says so. Nothing is included to fit reactions.

| Config key set | Value | ETABS table evidence |
|---|---|---|
| `elastic_etabs_comparison.ULS.use_native_shell_modifiers` | `true` | `Wall Property Def - Specified`, `Wall 600` (every wall object, `Area Assigns - Sect Prop`): Shell-Thin, f11 = f22 = f12 = 0.5, m11 = m22 = m12 = 0.1, v = 1. `Slab Property Definitions`, `Slab 150`: f = 1, m = 0.25 |
| `elastic_etabs_comparison.ULS.use_native_frame_modifiers` | `true` | `Frame Sec Def - Conc Rect`: `Beam 600*800` A 1, J 0.01, I22 = I33 = 0.35; `Col 1100*1100` / `Col 1250*1250` A 1, J 1, I 0.7. This includes the ETABS beam torsion J 0.01 |
| `elastic_etabs_comparison.ULS.allow_shell_shear_approximation` | `true` | needed to accept m = 0.1 with v = 1 (OpenSees couples plate shear to the plate modulus; see [linear_shell_stiffness.py](linear_shell_stiffness.py.md)) |
| `rigid_end_zones` | `{"enabled": true, "source": "ASSIGNMENT_WORKBOOK", "factor": "SOURCE"}` | `Frame Assigns - End Len Offsets`: Auto × 1,367, Rigid Factor 1; beams 550/625 mm at column ends and 0 at wall ends, columns 800 mm at the top. See [rigid_end_zones.py](rigid_end_zones.py.md) |
| prerequisite (not set): `etabs_beam_weight_policy = ETABS_BEAM_CLEAR_LENGTH`, confirmed | must already be true | `Material List by Story`: beams 1,813.2644 kN per storey (clear length). Set only by the verified clear-beam rebuild |

## Comparison procedure that goes with the preset

`COMPARISON_PROCEDURE` records it. It is a run option, not a model config key:

- Run the gravity case with the existing strategy `CONTINUOUS_WALL_BASE_FIXED`, which fixes the wall-base mesh nodes on source wall edges whose two ends are supports.
- Lump each intermediate wall-base reaction onto the two adjacent ETABS corner supports with the linear edge weights (1 − t, t). Use `tools/etabs_comparison_ablation.py`, step option `"support_strategy": "CONTINUOUS_WALL_BASE_FIXED", "lump_to_reference": true`.

The ETABS evidence for this:

- `Area Assigns - Wall Auto Mesh` is `Default` × 375, and straight walls with `Default` are not meshed. Each wall base is therefore one shell edge between two restrained corner joints.
- The 44 restrained ETABS base points inside those edges report FZ = 0 in `1. DL + LL`.

Without this procedure, the core shortens 0.7 mm too much in storey 1, and every ETABS setting looks worse than it is ([run finding §8.3](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md)).

Solved result on MESH_04 (X8):

- maximum support difference 911 kN, RMS 502 kN;
- core 105,623 kN against the ETABS 109,278 kN.

The gap is not closed; §8.5 of the run finding gives the residual.

## Deliberately not included

| Setting | Why not |
|---|---|
| `wall_max_cell_size_m = 1.0` | `Area Assigns - Wall Auto Mesh`: `Default` × 375. For a straight wall, ETABS `Default` means the object is not meshed; the 1 m `Analysis - Wall Mesh Settings` value applies only to walls that use auto rectangular meshing (CSI help, Assign > Shell > Wall Auto Mesh Options and Analyze > Automatic Rectangular Mesh Settings for Walls). ETABS therefore models each wall object (for example a 6 × 3.8 m pier) with a single shell. The historical OpenSees wall mesh is already finer than that, and with the wall-base kinematics fixed the 1 m refinement changes the RMS difference by less than 1 kN (X11) |
| `shear_flexible_sections` | ETABS frames include shear deformation (As modifiers 1), but OpenSees `ElasticTimoshenkoBeam` with `-jntOffset` is not qualified here; `compile_settings` rejects the combination. Measured cost without rigid zones: 7 kN on the maximum support difference (run finding §8) |
| `floor_subdivisions = 1` | ETABS floors are `No Auto Mesh`, but the assembler requires 2…16 by design (a corner-only slab cell is rejected). Not changed |

`apply_preset` refuses to overwrite a preset key that already holds a different value and refuses to run unless the clear-beam policy is already confirmed. Solved effect on MESH_04: [run finding §8](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md).

Tests: `tests/test_rigid_end_zones.py`.
