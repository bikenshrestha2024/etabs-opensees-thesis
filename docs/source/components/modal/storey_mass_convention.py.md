# storey_mass_convention.py: selectable storey seismic-weight allocation

**Implementation:** [storey_mass_convention.py](../../../../components/modal/storey_mass_convention.py) (`validate_convention`, `storey_shares`). Used by `assembly.prepare_complete_export` (storey ledger `NBC105_ESM_Story_Weights_Assembled_V118.csv`) and by [rayleigh_mass_audit.py](rayleigh_mass_audit.py.md).

**Status:** opt-in bookkeeping convention. It changes only the storey weights Wi in the ledger (Rayleigh, ESM, mass audit). Nodal masses in the eigen problem stay at their nodes for every convention, so OpenSees eigen periods do not depend on it.

## Config key

`OpenSees_Complete_Model_Config_V118.json` → `storey_mass_allocation_convention`. Absent = default; the key is never written as a default, so existing exports stay byte-identical.

| Value | Free nodes at the base elevation | Nodes between levels |
|---|---|---|
| `NBC_MID_HEIGHT_BASE_TO_FLOOR1` (default) | to floor 1 | §5.2 mid-height rule (`storey_index_for_elevation`) |
| `ETABS_BASE_ROW` | excluded (base row, outside W) | §5.2 mid-height rule |
| `ETABS_BASE_ROW_LINEAR_SPLIT` | excluded | split linearly between the level below and the level above; below storey 1 the level below is the base (excluded) |

`storey_shares(z, floors, base_z, convention)` returns `[(floor_index, fraction)]`; index `BASE` (-1) is the excluded base row.

## Relation to NBC 105:2025 §5.2 (printed p. 30)

§5.2 defines Wi as the load between the mid-heights of the adjacent storeys. The default follows it between floors and keeps the lower half of storey 1 in floor 1 so the total is preserved (the base carries no lateral level). In this building the only masses below the storey-1 mid-height (1.9 m) sit at z = 0, so `ETABS_BASE_ROW` gives the same Wi as a strict §5.2 reading in which the base owns the lower half of storey 1. `ETABS_BASE_ROW_LINEAR_SPLIT` is not the §5.2 rule: it reproduces the ETABS `Mass Summary by Story` values (Lump Mass = Yes), inferred from the exact ±215.463 kN roof/base fit in the [run finding §7.2](../../../validation/run_findings/GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.md). It preserves the first moment of mass about the base exactly.

## Single mass ledger

The assembler still checks floors + base row = active nodal seismic weight (`story_ledger_mass_error_percent` ≤ 1e-7 %). For a non-default convention the export report records `storey_mass_allocation_convention` and `story_ledger_base_row_excluded_weight_kN`, and the model data JSON records the convention so `audit_rayleigh_mass_elevations` applies the same rule. g = 9.81 m/s² (`components/nbc105/constants.py`).

Tests: `tests/test_storey_mass_convention.py`.
