# analysis_autofill.py — source documentation

**Python source:** [components/inputs/analysis_autofill.py](../../../../components/inputs/analysis_autofill.py)
**Git baseline content SHA:** b8d4f27b0f546a20f5caba2b10f677ae30396f4e
**Subsystem:** ETABS/source inputs and earthquake motions
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the inputs implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 modal source validity gate

`populate_linear` now **does not auto-populate** elastic-modal TnX/TnY nor Rayleigh damping P1/P2 when any of source-model SHA256, ULS/SLS limit-state or supported numerical implementation fingerprint mismatches. It logs which source was rejected, instructs a matching modal run and reminds the user that the *nonlinear* initial-tangent eigenmodel is an independent check.

For a matching source, imported TnX/TnY come only from the first `NBC105_Modal_V111.json` modal row whose cumulative directional mass reaches ≥90%; the selected mode number and mass percentage are logged. They are explicitly labeled elastic-modal references. If 90% is not reached, keep that field empty and **never** substitute the last inspected eigenmode.

Separately, workbook adopted empirical/Rayleigh T1 values remain NBC-design-period references and are **not** used as material-dependent nonlinear initial modal T1 nor assumed damping reference eigenperiods.

## 2026-11-14 source-matched modal reference selection V8

`matching_modal_reference(folder, state, model_sha)` scans both canonical `04_MODAL` and historical analysis-result directories, excluding review snapshots. It returns the newest **explicitly model-SHA + ULS/SLS matching** saved modal result with nonempty mode rows; it never selects the first mismatched file. `populate_linear` and `populate_site` display a source-missing warning rather than auto-filling Tn or damping periods from an unrelated export. A matching serialized JSON source hash is not ETABS physical equivalence and does not establish nonlinear initial tangent stiffness. Unit tests: `tests/test_legacy_reader_migration_v8.py`.



## 2026-11-15 exec-facade source root consistency

The historical `OpenSees_Linear_Autofill_V124.py` root launcher executes this component through `exec(compile(...), globals(), globals())`: `__file__` then refers to the root facade, not to `components/inputs/analysis_autofill.py`. Previous `Path(__file__).resolve().parents[2]` arguments could resolve above the actual repository and hide original source-verified Aw/T1 workbook values. `_runtime_repo_root()` now prefers the facade's actual `_component_source` and otherwise uses the module's own `__file__`. The same root is used for workbook location, compatibility JSON and implementation fingerprint searches, with no hard-coded numerical value. Source-only tests cover direct imports, root facades and exported runtimes; actual ETABS/Excel period identity remains a separate gate.

## 2026-11-21 clause 5 period routing and DEVIATION

`workbook_adopted_period(height_m, aw_m2, rayleigh_s, factor)` applies the NBC 105:2025 §5.1 lesser-of rule through the [clause 5 module](../nbc105/clause_05_dynamic_characteristics.py.md). When the workbook `period_factor` is not 1.25 it returns no period and a DEVIATION note, and `populate_linear` clears the T1 field (including any value pre-filled from `workbook_adopted_t*`) instead of adopting a non-NBC period. Test: `tests/test_nbc105_clause5_callsites.py`.

## 2026-11-23 — site-spectrum MRSM adopted period parity

populate_site(app, folder) requires an existing selected export folder. It reads current ULS/SLS source state, imports project parameters for that state and calls components.response_spectrum.model_analysis.mrsm_period_defaults() for directional adopted T1: the same calculation and same-source/workbook fallback as Model MRSM. It clears stale period fields before loading, rather than copying workbook periods from a generic working directory. The status reports source, state and provenance. Missing adopted-period evidence remains blank; no default eigenperiod is invented.

matching_modal_reference() still requires model SHA and state matches for modal mass-derived Tn. The history-window path through populate_spectrum retains selected-source T1/Tn values and updates the site-spectrum provenance label. Actual Rayleigh / Aw and ETABS/OpenSees physical identity remain acceptance gates, not auto-certified by GUI import.

Regression: tests/test_site_spectrum_period_autofill_20261123.py.


## 2026-11-23 — policy-bound modal evidence for transient analysis

Saved modal eigenperiods imported by Linear TH must match source model JSON SHA, ULS/SLS, runtime selected support profile (32/76/97), seismic mass policy, and numerical implementation. Missing policy evidence is not trusted. The Linear TH GUI refreshes on support/mass changes; unrelated source periods remain empty. This is software provenance, not native ETABS equivalence. Synthetic regression: `tests/test_modal_history_policy_handoff.py`.


2026-11-26: shared history autofill resets automatic periods and modal-reference provenance at the start of each refresh. A missing or different-folder builder cannot retain old references or route automatic output into an unrelated case. Manual output paths are restored even if autofill raises; successful automatic paths use the canonical linear/nonlinear stage. This does not change numerical period calculations, damping ratios, solver tolerances or acceptance gates.
