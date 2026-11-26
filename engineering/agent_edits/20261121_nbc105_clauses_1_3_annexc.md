# NBC 105:2025 clauses 1-3, Annex C and g = 9.81

Editor Claude Code, model UNKNOWN. Branch `feat/nbc105-clauses-1-3-annexc`. Plan `docs/superpowers/plans/2026-11-21-nbc105-clauses-1-3-annexc.md`.

## Task 1: restore g = 9.81, make Vs,30 optional with the requirement documented

Decision (USER_DECLARED 2026-11-21, not verified by the agent): g = 9.81 m/s^2 per NBC 105:2025 printed p. 7; this reverses the earlier same-day decision to use 9.80665. Vs,30 is optional for the thesis; the clause 4.1.3.1 requirement above 40 m stays documented and is reported, not raised.

Changed
- `components/nbc105/constants.py`: `GRAVITY_M_S2 = 9.81` (equal to `NBC_NOTATION_GRAVITY_M_S2`); new `SUPERSEDED_GRAVITY_M_S2 = 9.80665` used only to recognise old saved results.
- Every 9.80665 / 9806.65 literal in `components/` and `tools/` removed. Routed through `GRAVITY_M_S2`: `components/shared/transient_runtime.py` (`acceleration_conversion`), `components/ui/history_inspection.py`, `components/nonlinear_time_history/` (`ground_acceleration.py`, `nbc105_horizontal_input.py`, `soil_c_nltha_suite.py`, `soil_c_physics_preflight.py`, `soil_c_run_matrix.py`, `building_exploratory.py`, `literature_demo.py`, `runner_and_gui.py`), `components/linear_time_history/runner_and_gui.py`, `components/response_spectrum/` (`site_spectrum_and_scaling.py`, `model_analysis.py`), `tools/etabs_period_review/reconcile.py` (adds a repo-root `sys.path` insert), `tools/plot_results.py`, `tools/verify_matched_waveforms.py`. Message/docstring text only: `literature_demo_gui.py`, `reports.py`, `nbc105_dual_target.py`, `clause_05_dynamic_characteristics.py`. Standalone single-file tools keep a commented literal 9.81 (cannot import `components`): `tools/verification_studio/ETABS_OpenSees_Verification_Studio.py`, `..._ALL_IN_ONE.py`, `expanded_benchmarks.py`; a test pins them equal to the constant.
- `components/nbc105/clause_04_seismic_hazard.py` `select_soil_type`: no longer returns early with `soil=None` above 40 m. Without Vs,30 it adds the issue `VS30_REQUIRED_ABOVE_40M_NOT_SUPPLIED` (new `VS30_REQUIRED_ISSUE_CODE`, `VS30_REQUIRED_ISSUE`) citing clause 4.1.3.1 and "optional for this thesis, USER_DECLARED 2026-11-21"; soil comes from N_SPT when given. With Vs,30 supplied nothing changes. `code_basis.calculate_esm` is untouched.
- `components/inputs/project_workbooks.py`: import note wording only; it now names the recorded g, the current g, the printed page and the superseded value (symmetrical for either direction). Tolerance (rel 1e-8) and `RAYLEIGH_METHOD_VERSION` unchanged.
- Documentation: `docs/nbc105/PROJECT_DECLARATIONS.md` (section 3 rewritten, 9.80665 kept as superseded history; new section 4 for Vs,30), clause 4 and clause 5 matrices, `docs/nbc105/README.md`, `docs/source` guides (constants, clause 4, and every guide that quoted the 9.80665 Path factor), runbooks under `docs/programs`, `docs/rtfc`, `docs/ground_motions`, `.github` prompts, root `README.md`, `AGENTS.md`, `START_HERE.md`, `Research_Components/02_MODELLING_BASIS.md`, registry row for `nbc105_constants`. Left as history: earlier agent_edits notes, dated review/audit documents, `archive/`, versioned decision files, `Saved_Project_V156/`, `Worked_Example_*`, `Diagnostic_Evidence/`, `REVIEW_MAIN/`, `LITERATURE/`, the log fixture `tests/fixtures/ltha_v115_prelim_log_excerpt.txt`.
- Tests: `tests/test_nbc105_constants.py` (values, superseded-value record, repo-wide literal scan, standalone-literal pin, `reconcile.G`), `tests/test_nbc105_clause04.py` and `tests/test_nbc105_clause04_parity.py` (Vs,30 issue code, no raise), `tests/test_rayleigh_saved_g_note.py` (9.81 imports cleanly with no gravity note; 9.80665 is rejected with the cause note), and pinned values in `verify_soil_c_physics_preflight.py`, `verify_v134.py` (19620.0 for 2 x 9810), `verify_nltha_ground_acceleration.py`, `verify_nbc105_horizontal_input.py`, `verify_rtfc_prompt_contract.py`, `verify_review_fixes.py`, `test_rayleigh_mass_audit.py`, `test_etabs_empirical_first.py`.

Numeric effect (computed): restoring 9.81 relative to 9.80665 changes mass = W/g by 9.80665/9.81 - 1 = -0.0341 % (lower mass), Rayleigh T (1/sqrt(g)) by -0.0171 %, mass-to-weight by +0.0342 %, and the Acc(g) to m/s^2 conversion (ground acceleration, Path factor) by 9.81/9.80665 - 1 = +0.0342 %. The weight-to-mass sites had used 9.80665 on the previous commit, so assembled masses and the Acc(g) conversions in the time-history, response-spectrum and tool code move by these amounts; saved result folders are not rewritten.

Not touched: source EDBs, `Saved_Project_V156/`, solver, material and damping numerics. Saved Rayleigh results recorded with 9.80665 are rejected on import and must be re-run.

Evidence: unit tests only (`python -m pytest -q`, `python tests/verify_ref_tags.py`); no native ETABS or OpenSees run. PASS here is not engineering acceptance.

## Task 2: clause 1 title, scope, definitions and notations (printed pp. 1-9)

Editor Claude Code, model UNKNOWN. Source: printed pp. 1-9 read from the page images of the user-supplied PDF (PDF pages 22-30; foot numbers 1 to 9 checked on every page, offset 21 holds). Authority for g = 9.81 is the notation row on printed p. 7.

Added
- `components/nbc105/clause_01_scope_definitions.py`: scope applicability (`SCOPE_MATERIALS`, `SPECIALIST_LITERATURE_SYSTEMS`, `SCOPE_HEIGHT_LIMIT_M` = None, `scope_check`), the 68-row printed notation table (`NOTATIONS`, `notation`, per page 19 + 22 + 21 + 6; unit basis PRINTED only for g and H, SI_DERIVED from clause 1.5 elsewhere, NOT_STATED for loads), `printed_gravity_m_s2()` (literal 9.81 as printed, not imported from the constants), the definition thresholds (dual system 25 percent, soft story 70/80 percent, flexible diaphragm 2 times, design basis earthquake 2/3 MCE, 5 percent commonly taken damping) with `is_soft_story`, `is_flexible_diaphragm`, `dual_system_frame_share(_ok)`, `design_basis_earthquake_from_mce`, `ductility_factor`, `overstrength_factor`, `eccentricity_m`, `pdf_page_for_printed`.
- `tests/test_nbc105_clause01.py` (23 tests, written first and seen failing on the missing module) and `tests/test_nbc105_clause01_parity.py` (6 tests: g single source and `reconcile.G`, no 9.80665 literal in `assembly.py` and `rayleigh.py`, soft-story parity of `components/validation/response_checks.py::irregularity` on 33 stiffness combinations incl. boundaries, repo-wide absence of production dual-share/flexible-diaphragm checks).
- `docs/nbc105/clause_01_scope_definitions_matrix.md` (118 rows: 81 IMPLEMENTED_AND_TESTED, 37 DEFINITION_ONLY; findings F1 to F10), `docs/source/components/nbc105/clause_01_scope_definitions.py.md`.

Modified (docs and registry only)
- `engineering/registry/CANONICAL_MODULES.csv` (row `nbc105_clause1_scope_definitions`, NEW_WITH_JUSTIFICATION), `docs/nbc105/README.md` (register row 1 status CLAUSE_1, status legend, test naming), `docs/source/00_SOURCE_GUIDE_INDEX.md` (module row and matrix link).

Audit of existing code against the printed notation (details in the matrix): no production code changed and no before/after numbers, because no existing value is proved wrong by the printed text. Findings: T1 naming (adopted design period vs printed approximate period), Aw printed as "Area of Web" on p. 6 but an effective wall area in printed §5.1.2 (code follows 5.1.2), kN/MPa/tonne unit convention vs clause 1.5 SI, symbol clashes (damper alpha, Cd, E), Tn90 not a printed symbol, Rs has no repo variable (SLS coefficient divides by Omega_s only; deferred to the clause 6 audit), notation list omits Ta, Td, kt. Soft-story and g parity PASS.

Not touched: source EDBs, `Saved_Project_V156/`, solver, material and damping numerics. Evidence: unit tests only (`python -m pytest -q`, `python tests/verify_ref_tags.py`); no native ETABS or OpenSees run. PASS here is not engineering acceptance.

## Task 7: NBC 105 documentation consistency audit

Editor Claude Code, model UNKNOWN. Scope: only what exists today (clauses 1, 4, 5, constants, PROJECT_DECLARATIONS, WALL_GROUPING_AW_METHOD, matrices, module guides, registry rows). Clauses 2 and 3, Annex C and the UBC/SEAOC sources are deferred; the test accepts `NOT_STARTED` register rows without a module or matrix.

Added
- `tests/test_nbc105_docs_consistency.py` (18 tests, written first, run before any doc edit): register rows other than `NOT_STARTED` link an existing module and matrix; one register status vocabulary (`NOT_STARTED` or `CLAUSE_<n>` for the row's own clause); g appears as 9.81 and any 9.80665 or 9806.65 value sits only in a paragraph marked superseded, withdrawn or history; page-offset statements agree (21 up to printed p. 26, 23 from p. 27) with `PRINTED_PAGE_OFFSET = 21`; every matrix row has a code location or an explicit `DEFINITION_ONLY`, `NOT_APPLICABLE`, `PRINCIPLE_ONLY`, `NOT_TRANSCRIBED`, `USER_RESPONSIBILITY` or `CALLER_RESPONSIBILITY` status from one matrix vocabulary; the clause 1 row-count statement equals the table; every module under `components/nbc105/` has a guide and (except `__init__.py`) a `CANONICAL_MODULES.csv` row; every relative link in `docs/nbc105/*.md` and the module guides resolves.

First run: 17 passed, 1 failed (g history outside a superseded marker). Offsets, statuses, links, guides and registry rows were already consistent.

Modified (docs only, no production code, no numeric value changed)
- `docs/nbc105/PROJECT_DECLARATIONS.md`: section 3 numeric-effect list now labelled superseded history and named as the single source of the 0.0341 % and related percentages; scan-test sentence names the superseded value.
- `docs/source/components/nbc105/constants.py.md`: removed the repeated 0.0341 % statement and linked to PROJECT_DECLARATIONS section 3; scan-test sentence marks the value superseded and links.
- `docs/nbc105/clause_01_scope_definitions_matrix.md` (F10) and `docs/nbc105/clause_05_dynamic_characteristics_matrix.md` (open item): 9.80665 mentions now say superseded.

Line endings unchanged (all touched files are LF). Evidence: unit tests only (`python -m pytest -q`, `python tests/verify_ref_tags.py`); no native ETABS or OpenSees run. PASS here is not engineering acceptance.

## Follow-up: record-pair review checklist text (g = 9.81)

- `OpenSees_Workflow_V144.py` line 25: the `how_to_obtain_missing_values.record_pair_units_scales_and_nbc_limits_reviewed` guidance said "g-to-m/s2 factor is 9.80665 once". Changed to 9.81 once (NBC 105:2025 printed p. 7; `components/nbc105/constants.py`), separate from the motion scale. Text only; no numerics changed.
- Not changed: generated evidence `Verification_V144/Available_Inputs_Inventory.json` (an earlier run's output still carries the old text; regenerate by re-running the workflow).
- Record audit not run: no accelerogram files were supplied in this session. Required inputs for `components/response_spectrum/nbc_pair_spectrum_audit.py::pair_spectrum_audit`: X and Y original record files, soil type, Z, I, omega_u, R_mu, T1_x/T1_y, Tn90_x/Tn90_y. Model label UNKNOWN.
