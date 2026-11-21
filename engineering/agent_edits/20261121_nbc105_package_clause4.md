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

## Task 4: index, project declarations, wall grouping documentation

Editor Claude Code, model UNKNOWN. Documentation only; no code, test or numeric change.

Changed
- New `docs/nbc105/README.md` (naming convention, clause register 1-10 and Annex A-C with titles and printed pages read from the PDF contents list on PDF pages 15-21, procedure to add a clause, printed-page offset method), `docs/nbc105/PROJECT_DECLARATIONS.md` (USER_DECLARED 2026-11-21: no basement, wall grouping validated against UBC/SEAOC with details pending, g = 9.80665 with deviation 0.0341 % of 9.81, Rayleigh T +0.0171 %, revert method, affected-files table), `docs/nbc105/WALL_GROUPING_AW_METHOD.md` (what `grouped_wall_aw.py` and `aw_sources.py` do, worked example 6 x (0.2 + (3/95)^2) = 1.2059834 m^2 confirmed by running `effective_wall_area_m2`, references the repository already records).
- Clause 5 matrix: open items for basement and wall grouping now USER_DECLARED, g USER_DECISION; rows 14 and 15 annotated. Links added in `README.md`, `docs/00_REPOSITORY_ORGANIZATION.md`, `docs/NBC105_PERIODS_AND_MATERIAL_PROVENANCE.md`, `docs/source/00_SOURCE_GUIDE_INDEX.md`.
- Page 8-14 of the PDF are front matter (acknowledgements, preface, committees); the contents list is PDF pages 15-21 (roman xiv-xx). Clause registers use printed page numbers from the contents list.

Not verified: the user's declarations (no basement, wall grouping validation, g choice) are recorded as stated; the UBC/SEAOC documents were not available to the agent, so only the repository's own records of them are cited. `REFERENCE DETAILS PENDING FROM USER` for the edition and section the user validated against.

Verification: `python -m pytest -q`, `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees; not engineering acceptance.

## Fix wave after whole-branch review (I1, I2, M1-M6)

Editor Claude Code, model UNKNOWN.

- I1: saved Rayleigh results made with g = 9.81 are rejected by `verify_saved_rayleigh_axis` (period rebuilt with 9.80665 differs by 1.7e-4; tolerance rel 1e-8 NOT loosened; solver numerics and `RAYLEIGH_METHOD_VERSION` unchanged). `import_project_inputs` (`components/inputs/project_workbooks.py`, CRLF kept) now appends a note when the saved `gravity_acceleration_m_s2` differs from `GRAVITY_M_S2`: g changed 9.81 -> 9.80665 in this release, those periods are rejected on import and the Rayleigh analysis must be re-run; the ESM period falls back to 1.25 x empirical until then (which can be longer than min(empirical, Rayleigh), so the ESM base-shear reference changes until the rerun). The existing "stale, incomplete, or inconsistent" note is kept. Documented in `docs/nbc105/PROJECT_DECLARATIONS.md` §3. Test: `tests/test_rayleigh_saved_g_note.py`.
- I2: `default_soil_type_d` ignores case and whitespace and accepts the printed municipality name without its generic suffix ("Municipality", "Metropolitan City", "Rural Municipality"; Table 4-3, PDF p. 47 text, e.g. "Kirtipur"), only when the stem is unique within the district. No other alias. Unknown names still return False. Tests added, including ('Kathmandu','Kirtipur',10).
- M1: `PRINTED_PAGE_OFFSET` comment/guide/README/matrix header qualified (21 up to printed p. 26, 23 from p. 27). Value unchanged.
- M2: Table 4-1 pinned literally for A-D. M3: 2/3 Z scan regex widened. M4: revert note now names `tools/etabs_period_review/reconcile.py` `G` (value unchanged). M5: `select_soil_type` rejects height_m <= 0 (importance_factor asymmetry left). M6: module docstring and guide say PDF pages 42-50; Figure 4-1(a) docstring wording left (matrix F2).

Verification: `python -m pytest -q`, `python tests/verify_ref_tags.py`. Unit tests only; no native ETABS/OpenSees; not engineering acceptance.
