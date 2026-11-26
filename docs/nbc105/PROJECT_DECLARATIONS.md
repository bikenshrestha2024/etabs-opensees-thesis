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

## 3. Gravity constant: g = 9.81 m/s^2 (per NBC 105:2025 printed p. 7)

USER_DECLARED 2026-11-21: `GRAVITY_M_S2 = 9.81` m/s^2, the value printed in the NBC 105:2025 notation list (printed p. 7, "g: acceleration due to gravity, to be taken as 9.81 m/s^2"). `NBC_NOTATION_GRAVITY_M_S2` equals it. Single source: `components/nbc105/constants.py`.

SUPERSEDED (same day): the earlier USER_DECISION to use the higher-precision standard gravity 9.80665 m/s^2 is withdrawn. Its record, kept as history: it deviated from the printed value by (9.81 - 9.80665) / 9.81 = 0.0341 %; the Rayleigh period (Eq. 5.1(1), T proportional to 1/sqrt(g)) was longer by +0.0171 % than with 9.81.

Numeric effect of restoring 9.81 relative to 9.80665 (computed):
- Weight to mass, mass = W / g: mass is lower by 0.0341 % (ratio 9.80665 / 9.81 = 0.999659). Mass to weight is higher by 0.0342 %.
- Rayleigh period, T proportional to 1/sqrt(g): shorter by 0.0171 %.
- Acc(g) record conversion to m/s^2 (Path factor 9.81 instead of 9.80665): ground acceleration is higher by 0.0342 % (ratio 9.81 / 9.80665 = 1.000342). Earlier records of "0.0306 % or 0.03 %" in this repository are superseded by these figures.

Consequence for saved evidence: a saved Rayleigh result (`NBC105_Rayleigh_Preliminary_*.json`) made with g = 9.80665 no longer passes `verify_saved_rayleigh_axis` (period rebuilt with 9.81 differs by 1.7e-4, tolerance rel 1e-8, deliberately not loosened; `RAYLEIGH_METHOD_VERSION` is not bumped). Results saved with 9.80665 are rejected on import and must be re-run: `import_project_inputs` drops such periods (`rayleigh_tx/ty` not filled) and its notes state the recorded g, the g of this release and the superseded value, and that the Rayleigh analysis must be re-run. Until then the ESM adopted period falls back to 1.25 x empirical. Saved model exports and NLTHA/RS result folders made with 9.80665 (mass from `assembly.py`, Path factor 9.80665 in the Input Record Audit) are history and are not rewritten; re-assemble and re-run to obtain 9.81 results. Pinned by `tests/test_rayleigh_saved_g_note.py`.

`SUPERSEDED_GRAVITY_M_S2 = 9.80665` is kept in `components/nbc105/constants.py` only so that old results can be recognised and rejected; no calculation uses it. A scan test (`tests/test_nbc105_constants.py`) fails if a 9.80665 or 9806.65 literal appears in any `.py` file under `components/` or `tools/` other than `constants.py`.

| File group | Use of g |
|---|---|
| `components/nbc105/constants.py` | single definition (and the superseded value, history only) |
| `components/nbc105/clause_05_dynamic_characteristics.py`, `components/modal/rayleigh.py`, `rayleigh_ledger_audit.py`, `rayleigh_mass_audit.py` | Eq. 5.1(1), audits |
| `components/model/assembly.py`, `components/sections/area_elements.py`, `components/gravity/load_path_formulas.py`, `components/validation/irregularity_review.py` | weight/mass conversion |
| `components/shared/transient_runtime.py`, `components/nonlinear_time_history/*`, `components/linear_time_history/runner_and_gui.py`, `components/response_spectrum/*`, `components/ui/history_inspection.py` | Acc(g) to m/s^2 record conversion and Cd(T) x g |
| `tools/etabs_period_review/reconcile.py`, `tools/plot_results.py`, `tools/verify_matched_waveforms.py` | import the constant |
| `tools/verification_studio/*` (three single-file tools) | standalone literal 9.81, pinned equal to the constant by test |

Details: [constants guide](../source/components/nbc105/constants.py.md) and [clause 5 matrix](clause_05_dynamic_characteristics_matrix.md).

## 4. Vs,30 is optional for this thesis; the clause 4.1.3 requirement stays documented

USER_DECLARED 2026-11-21: Vs,30 testing is optional for this thesis. The NBC 105:2025 requirement is unchanged and is recorded here by paraphrase (the agent did not verify it against a second source):
- Clause 4.1.3.1 (printed p. 24): the subsoil class is taken from Vs,30 where available, otherwise from N_SPT (Table 4-2), and Vs,30 is required for buildings higher than 40 m.
- Clause 4.1.3.3 with Table 4-3 (printed pp. 25-26): for listed Kathmandu Valley sites Soil Type D is the default unless tests to 30 m show another class.

Code behaviour (`components/nbc105/clause_04_seismic_hazard.py` `select_soil_type`): for height above 40 m without Vs,30 it does not raise. It returns an `issues` entry that begins with the code `VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED`, cites clause 4.1.3.1 and the text "optional for this thesis, USER_DECLARED 2026-11-21". `soil` comes from N_SPT when N_SPT is given (basis `N_SPT`) and is None otherwise. With Vs,30 supplied the result is the same as before and carries no such issue. The production `code_basis.calculate_esm` is unchanged and still reports `site_subsoil_status` NOT VERIFIED above 40 m without Vs,30.

Consequence: a soil class for a building above 40 m that rests on N_SPT is not code-compliant under clause 4.1.3.1 as printed; the project accepts that as a declared deviation, visible as the issue code in every such result. No engineering acceptance is implied.

## 5. Ground motions: N_GM = 8 (more than 7)

USER_DECLARED 2026-11-26: the project uses 8 ground motions. `components/nbc105/clause_08_elastic_time_history.py` records it as `PROJECT_DECLARED_GROUND_MOTION_COUNT = 8`. Not verified by code; it must match the matched-pair set (see AGENTS.md Soil C invariants).

Printed rule re-read (printed p. 42, 8.1.3; printed pp. 47, 9.3.3): "If less than 7 numbers of ground motion records are used, maximum values of the response quantities ... shall be used. If the number of ground motions used is more than 7, then average values of the considered number of ground motions shall be used." Exactly 7 is not defined in the print.

Consequence in code (`project_record_set_evaluation`, `nonlinear_time_history/nbc105_2025_audit.py::project_response_aggregation`): all 8 accepted -> AVERAGE; fewer than 7 accepted -> MAXIMUM (status `OK_BUT_DECLARED_COUNT_NOT_MET`); exactly 7 accepted (for example one of the 8 failed or did not converge) -> `BLOCKED`, fail-closed as printed. The owner phrase "average for >= 7" is not applied to 7 because the print does not say so. Failed or non-converged records never enter the accepted set.
