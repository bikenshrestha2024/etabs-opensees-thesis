# NBC 105:2025 package, clause 4 audit and project declarations

Editor Claude Code, model UNKNOWN. Branch `feat/nbc105-package-clause4`. Plan `docs/superpowers/plans/2026-11-21-nbc105-package-clause4.md`.

## Task 1: package scaffold, shared gravity constant, clause 5 move

Changed
- New package `components/nbc105/` (`__init__.py`, `constants.py`). `GRAVITY_M_S2 = 9.80665` (USER_DECISION, recorded as USER_DECLARED 2026-11-21, not verified by the agent); `NBC_NOTATION_GRAVITY_M_S2 = 9.81` (printed p. 7, reference only); `PRINTED_PAGE_OFFSET = 21`.
- `git mv components/modal/nbc105_clause5.py components/nbc105/clause_05_dynamic_characteristics.py` (added `__all__`, `rayleigh_period_s` default g is `GRAVITY_M_S2`); `components/modal/nbc105_clause5.py` is a shim re-exporting the same objects. Guide and matrix moved with `git mv` to `docs/source/components/nbc105/clause_05_dynamic_characteristics.py.md` and `docs/nbc105/clause_05_dynamic_characteristics_matrix.md`; links fixed in docs, source-guide index, registry and the earlier agent_edits note. New guides for `constants.py`, `__init__.py` and the shim.
- Call sites switched to the new import path: `analysis_autofill.py`, `grouped_wall_aw.py`, `modal/analysis.py`, `modal/rayleigh.py`, `model/assembly.py`, `equivalent_static/calculation_and_gui.py` (tkinter, `py_compile` only).
- Gravity routed through `GRAVITY_M_S2` (same weight/mass conversion only): `modal/rayleigh.py` (Eq. 5.1(1) denominator, audit JSON, `verify_rayleigh_sum` default, workbook formula), `modal/rayleigh_ledger_audit.py`, `modal/rayleigh_mass_audit.py`, `model/assembly.py` (3 sites), `sections/area_elements.py`, `gravity/load_path_formulas.py`, `validation/irregularity_review.py`. Acc(g) record conversions in time-history/response-spectrum code are left unchanged.
- Tests: new `tests/test_nbc105_constants.py`; `tests/test_nbc105_clause5.py` and `tests/test_nbc105_clause5_callsites.py` use the new path.

Numeric changes (before -> after)
- Rayleigh period in `rayleigh.py`, `rayleigh_ledger_audit.py` and `rayleigh_period_s`: g 9.81 -> 9.80665, T about +0.017 % (sqrt(9.81/9.80665) = 1.000171).
- `assembly.py`, `area_elements.py`, `load_path_formulas.py`, `irregularity_review.py`, `rayleigh_mass_audit.py`: already 9.80665, so no numeric change (literal replaced by the shared constant).
- Tests that pinned 9.81 for the default Rayleigh g (`tests/test_rayleigh_ledger_audit.py`, `tests/verify_nbc105_periods.py` synthetic evidence) now use `GRAVITY_M_S2`.

Verification: `python -m pytest -q`, `python tests/verify_ref_tags.py`, `py_compile` of edited tkinter files. Unit tests only; no native ETABS/OpenSees; not engineering acceptance.
