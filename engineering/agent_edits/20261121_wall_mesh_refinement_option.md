# Opt-in wall mesh limit and shell mesh-quality audit

Editor: Claude Code (model label UNKNOWN). Branch `feat/wall-mesh-refinement-option`, from `feat/gravity-reaction-rayleigh-review` at 1d76ce0. Not pushed.

## Edited paths

- `components/model/assembly.py` (LF preserved):
  - `_mesh_areas` takes `wall_max_cell_size_m=None`. Line computation is factored into the inner `_panel_lines` with the same arithmetic.
  - New private helpers `_uniform_breaks` and `_seed_wall_refinement_lines`.
  - `prepare_complete_export` reads and validates the config key without writing a default, then writes `wall_max_cell_size_m` and `shell_mesh_quality_audit` to the export report.
- `components/model/shell_mesh_quality.py` (new): `audit_shell_mesh_quality` and `validate_wall_max_cell_size`.
- `components/gravity/mesh_cases.py`: `MESH_BUILD_STATUS.json` records the audit, and `wall_max_cell_size_m` in `assembly_metrics`.
- `tests/test_wall_mesh_refinement_option.py` (new, synthetic panels only).
- Docs:
  - `docs/source/components/model/shell_mesh_quality.py.md` (new);
  - `docs/source/components/model/assembly.py.md` (new section);
  - `docs/validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md` (§7.7; row 9 and D6 text) and `.json` (`wall_mesh_refinement_20261121`).
- `engineering/registry/CANONICAL_MODULES.csv`: one NEW_WITH_JUSTIFICATION row.

## Default behaviour

When the key is absent, the mesh is unchanged. The `_mesh_areas` digest of the user's MESH_04/08/16 topology is identical before (1d76ce0) and after this change: 137220fe…, c364cee5…, 8cedea29…. The synthetic golden SHA in the test was computed with the 1d76ce0 code. The model-data JSON gets no new key.

## Not changed

Solver, material, damping, load, mass and stiffness numerics. Source EDB/exports.

## Tests

- `python -m pytest -q`
- `python tests/verify_ref_tags.py`

These are unit and mesher checks only. No native ETABS run and no OpenSees solve were run for this change. OpenSeesPy is importable in the agent container, but it was not used to solve. The user's Windows re-run recipe is in §7.7 of the run finding. The wall-meshing hypothesis remains STILL OPEN.
