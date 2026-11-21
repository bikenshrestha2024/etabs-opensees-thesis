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

## Task 2: clause 4 module

Changed
- New `components/nbc105/clause_04_seismic_hazard.py`, `tests/test_nbc105_clause04.py`, guide `docs/source/components/nbc105/clause_04_seismic_hazard.py.md`, CANONICAL_MODULES.csv row `nbc105_clause4_seismic_hazard`, source-guide index row. No existing file's behaviour changed.
- Tables 4-1, 4-2, 4-3 and 4-4, Eq. 4.1(2), 4.2(1), 4.3(1) and the Vs,30 formula were transcribed by viewing the printed page images (PDF pages 43-50), not from memory. Table 4-3 has 21 rows (10 Kathmandu, 7 Lalitpur, 4 Bhaktapur); the transcription test pins row counts, the KMC, Lalitpur MC, Tokha and Tarakeswor ward sets.
- Printed-page notes: Table 4-3 and Table 4-4 are both on a page numbered 26; the Figure 4-3 page is numbered 25; the last sentence of 4.1.4 says "Figure 4-4" (Figure 4-3 intended); KMC wards print "...,30,32,32" (kept as 32, possible misprint).
- `zoning_factor_from_table` not created (Annex C Table C-1 and Figure 4-3 interpolation not transcribed).

Verification: `python -m pytest -q`, `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees; not engineering acceptance.

## Task 3: clause 4 parity audit and matrix

Changed
- New `tests/test_nbc105_clause04_parity.py` (compares `esm_spectral_shape_factor` in `code_basis.py` and `legacy_code_basis.py`, `spectral_shape_ch`, `elastic_site_spectrum_g`, `ch_modal_nltha`, `target_nltha_g`, `reconcile.soil_c_*`/`static_parameters`, `soil_type_from_vs30`/`soil_type_from_n_spt`, `calculate_esm` ULS/SLS coefficients against the clause module on a dense T grid; scans for 0.20 and 2/3 Z use; `site_spectrum_and_scaling` is imported with an inert tkinter stand-in). New `docs/nbc105/clause_04_seismic_hazard_matrix.md` with a Findings section.
- Code fix (only proven mismatch, F1): `components/equivalent_static/code_basis.py` and `legacy_code_basis.py`, `esm_spectral_shape_factor` now rejects non-finite T and T > 6 s (printed p. 23, Eq. 4.1(2) defined for T <= 6 s). LF line endings kept; 7 lines changed per file (`git diff --stat`).

Numeric changes (before -> after)
- Soil C, T = 6.5 s, ESM: 0.23669 (extrapolated) -> ValueError. T = 10 s likewise.
- NaN period: returned NaN -> ValueError. `calculate_esm` already rejected non-finite T.
- 0 <= T <= 6 s: no change for any soil (parity test, 1e-12).

Not changed: other implementations (spectral_shape_ch, elastic_site_spectrum_g, ch_modal_nltha, target_nltha_g, reconcile soil C helpers, Table 4-2 classifiers) matched the clause module; no production code applies the vertical 2/3 Z; importance factor is a user input.

Verification: `python -m pytest -q` (1315 passed, 34 skipped), `python tests/verify_ref_tags.py`. No tkinter file edited. Unit tests only; no native ETABS/OpenSees; not engineering acceptance.
