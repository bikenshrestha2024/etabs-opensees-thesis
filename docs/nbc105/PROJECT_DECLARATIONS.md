# Project declarations for NBC 105:2025 calculations

Date 2026-11-21. Every item below is `USER_DECLARED 2026-11-21`: a fact or decision stated by the project author. The agent did not verify any of them against the building, the ETABS model or the cited references. None of them is engineering acceptance, and no native ETABS or OpenSees run supports them. Index: [NBC 105:2025 clause register](README.md).

## 1. No basement: H is the full height from base to roof

USER_DECLARED: the structure has no basement.

Consequence recorded in the code base:
- NBC 105:2025 §5.1.2 defines H as the height from the base to the roof; the Figure 5-1 rule that lets a basement be excluded from H (printed p. 29) is not applicable because there is no basement.
- `components/inputs/analysis_autofill.py` takes H = max node z - `base_z_m`. `base_z_m` must therefore be the base level (foundation/ground base of the structure). If `base_z_m` is set to any higher level, H is under-stated and the empirical period `Temp = kt H^0.75` and the wall index Aw change with it.
- `components/nbc105/clause_05_dynamic_characteristics.py` `building_height_m(basement_excluded=...)` defaults to the basement being included, which matches this declaration. The function is a reference implementation; production callers compute H inline.

Affects: `analysis_autofill.py` (H), `components/modal/analysis.py` (`nbc105_period_estimate`), `components/modal/rayleigh.py` (empirical and amplified period), `components/equivalent_static/calculation_and_gui.py`, and `grouped_wall_aw.py` (Lwi/H).

Revert / change: if a basement is ever added, set `base_z_m` and the clause 5 basement flag according to Figure 5-1, and re-run the period estimate. Matrix row 14 in the [clause 5 matrix](clause_05_dynamic_characteristics_matrix.md) is then CALLER_RESPONSIBILITY again.

## 2. Wall grouping of Aw validated against UBC and SEAOC references

USER_DECLARED: the project's grouping of walls for the effective wall area Aw has been validated by the user against UBC and SEAOC references. `REFERENCE DETAILS PENDING FROM USER` for which edition, section and example the user checked; the repository's own records of these references are listed in [WALL_GROUPING_AW_METHOD.md](WALL_GROUPING_AW_METHOD.md). NBC 105:2025 itself does not define grouping around openings.

Affects: `components/inputs/grouped_wall_aw.py`, `components/inputs/aw_sources.py`, and the Aw shown in the modal and ESM windows. Every result of this code carries `code_accepted: false`.

Revert / change: `aw_sources.resolve_aw` prefers the reviewed-geometry candidate only when the exported first-storey geometry passes its checks; otherwise it falls back to the ETABS-linked original Excel value (`ORIGINAL_EXCEL_METHOD_ETABS_LINKED`) or the OpenSees geometry candidate. See the method note.

## 3. Gravity constant: g = 9.80665 m/s^2 (USER_DECISION)

USER_DECLARED: use the higher-precision standard gravity `GRAVITY_M_S2 = 9.80665` m/s^2 where weight and mass are converted, by the user's instruction. NBC 105:2025 notation list (printed p. 7) says "g: acceleration due to gravity, to be taken as 9.81 m/s^2". This is a recorded deviation from the printed value.

Size of the deviation: (9.81 - 9.80665) / 9.81 = 0.0341 % of the printed value (ratio 9.81 / 9.80665 = 1.000342). Rayleigh period (Eq. 5.1(1), T proportional to 1/sqrt(g)) is longer by sqrt(1.000342) - 1 = +0.0171 % compared with 9.81. Earlier text in this repository that says 0.0306 % or 0.03 % is superseded by these figures. The weight-to-mass conversion in `assembly.py` and four other modules already used 9.80665 before this change, so those numbers did not move.

`NBC_NOTATION_GRAVITY_M_S2 = 9.81` is kept in `components/nbc105/constants.py` as a reference value only and is not used in any calculation.

How to revert: change the single constant `GRAVITY_M_S2` in `components/nbc105/constants.py` to 9.81, update the value pins in `tests/test_nbc105_constants.py`, and re-run `python -m pytest -q`. Reverting also changes the weight-to-mass conversions that already used 9.80665 (mass from a given weight becomes about 0.0341 % smaller), so previously exported model data would need re-assembly.

| File | Use of g |
|---|---|
| `components/nbc105/constants.py` | single definition |
| `components/nbc105/clause_05_dynamic_characteristics.py` | `rayleigh_period_s` default g |
| `components/modal/rayleigh.py` | Eq. 5.1(1) denominator, audit JSON, `verify_rayleigh_sum` default, workbook formula |
| `components/modal/rayleigh_ledger_audit.py` | Rayleigh ledger audit |
| `components/modal/rayleigh_mass_audit.py` | mass audit (already 9.80665) |
| `components/model/assembly.py` | weight to mass, 3 sites (already 9.80665) |
| `components/sections/area_elements.py` | weight/mass conversion (already 9.80665) |
| `components/gravity/load_path_formulas.py` | gravity load path (already 9.80665) |
| `components/validation/irregularity_review.py` | review helper (already 9.80665) |
| `tests/test_nbc105_constants.py`, `tests/test_rayleigh_ledger_audit.py`, `tests/verify_nbc105_periods.py` | pin or use `GRAVITY_M_S2` |

Acc(g) record conversions in the time-history and response-spectrum code were left unchanged. Details: [constants guide](../source/components/nbc105/constants.py.md) and [clause 5 matrix](clause_05_dynamic_characteristics_matrix.md) (open items).
