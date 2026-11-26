# Opt-in ETABS rigid end zones, ETABS comparison preset and solved reaction ablation

Editor: Claude Code (model label UNKNOWN). Branch `feat/joint-reaction-rayleigh-fix`. It was created from `feat/wall-mesh-refinement-option` (4cbc8ef) and has `origin/main` merged in (806613c). Not pushed.

## Edited paths

- `components/model/rigid_end_zones.py` (new): reads ETABS `Frame Assignments - End Length Offsets` or the EDB `GetEndLengthOffset` record, validates the `rigid_end_zones` block, and injects `end_offsets_m`.
- `components/model/etabs_comparison_preset.py` (new): `ETABS_ELASTIC_GRAVITY_COMPARISON`, `COMPARISON_PROCEDURE`, `apply_preset`.
- `components/model/assembly.py` (LF preserved): hook before `compile_settings`. Absent or disabled key gives an unchanged export.
- `tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py`: `--comparison-preset` (mutually exclusive with `--elastic-comparison-settings`).
- `tools/etabs_comparison_ablation.py` (new): sequential ablation, wall-base lumping, Rayleigh and modal child runners.
- `docs/nbc105/clause_04_seismic_hazard_matrix.md` (separate commit b26a519): row 8 status token after the origin/main merge.
- Tests (new): `tests/test_rigid_end_zones.py`, `tests/test_etabs_comparison_ablation.py`.
- Guides: `docs/source/components/model/rigid_end_zones.py.md`, `etabs_comparison_preset.py.md`, `docs/source/tools/etabs_comparison_ablation.py.md` (all new); `assembly.py.md` (new section).
- Run finding: §8 of `docs/validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md`, new JSON block, and the new compact `GRAVITY_REACTION_ABLATION_MESH04_20261121.json`.
- Registry: three NEW_WITH_JUSTIFICATION rows.

## Evidence

- Native OpenSeesPy 3.8.0 on Linux, 16 gravity solves of MESH_04 (1.0D + 1.0L, 32 supports, 11k nodes). Run folder `/home/claude/out/MESH_04_ETABS_ELASTIC_COMPARISON_20261121/02_GRAVITY/...` (not committed).
- The baseline reproduces the user's Windows run exactly.
- No ETABS run.

## Not changed

- Production defaults: absent keys give byte-identical exports.
- Solver, material, damping, load and mass numerics.
- Source EDB and source exports.

## Correction recorded

The previous session's reading that ETABS meshes walls at 1 m was wrong. `Wall Auto Mesh = Default` leaves straight walls unmeshed. `wall_max_cell_size_m` remains a diagnostic option and is not in the preset.

Solver PASS here is not ETABS equivalence or engineering acceptance. The gap is reduced (maximum 3,041 → 911 kN), not closed.
