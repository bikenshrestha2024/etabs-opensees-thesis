# Selectable storey seismic-weight convention and solved Rayleigh/eigen switches

Editor: Claude Code (model label UNKNOWN). Branch `feat/joint-reaction-rayleigh-fix`, on top of 3c63a30. Not pushed.

## Edited paths

- `components/modal/storey_mass_convention.py` (new): `NBC_MID_HEIGHT_BASE_TO_FLOOR1` (default), `ETABS_BASE_ROW`, `ETABS_BASE_ROW_LINEAR_SPLIT`, `storey_shares`.
- `components/model/assembly.py` (LF preserved): the storey ledger uses the convention when the config key `storey_mass_allocation_convention` is set. The base row is reported and reconciled in the single mass ledger, and the model data records the convention. Absent key: byte-identical export. Checked against b26a519 on the MESH_04 clear-beam export: model data, ledger CSV and config SHA-256 are equal.
- `components/modal/rayleigh_mass_audit.py`: new `convention=None` keyword (default from the model), `base_row_excluded_weight_kN` reported. Default floor weights are numerically unchanged.
- Tests (new): `tests/test_storey_mass_convention.py`. It includes a 9.80665 scan of the root-level production modules, in addition to the existing `components/` and `tools/` scan.
- Guides:
  - `docs/source/components/modal/storey_mass_convention.py.md` (new);
  - `docs/source/components/modal/rayleigh_mass_audit.py.md` and `docs/source/components/model/assembly.py.md` (sections).
- Run finding: §9 of `GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md`, a new JSON block, and the new compact `RAYLEIGH_EIGEN_SWITCHES_MESH04_20261121.json`.
- Registry: one NEW_WITH_JUSTIFICATION row.

## Evidence

- Native OpenSeesPy 3.8.0 on Linux: 6 Rayleigh runs and 3 eigen runs on MESH_04. R0 reproduces the stored V127 values (1.661966 s / 2.383341 s) exactly.
- g = 9.81 m/s². No ETABS run, and no ETABS modal periods are in the evidence.

## Not changed

Production defaults, nodal masses, gravity loads, eigen mass, solver numerics, source EDB and exports.
