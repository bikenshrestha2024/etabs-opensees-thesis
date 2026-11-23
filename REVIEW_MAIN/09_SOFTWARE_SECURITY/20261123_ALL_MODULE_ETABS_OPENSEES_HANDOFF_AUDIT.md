# ETABS 23 → OpenSeesPy: all-module handoff, consistency and efficiency review

**Date:** 2026-11-23 | **Base:** `main@e3e14d884de38c3a4d9d9de0567795a887b16db1` | **Scope:** selected active source in all engineering module families, existing GitHub Actions static-audit output and the user's 2026-11-23 ESM screenshot/run log.

**Status:** `BOUNDED_SOURCE_REVIEW`, `SOFTWARE_GATES_IN_CI`, `NATIVE_ETABS_OPENSEES_EQUIVALENCE_NOT_VERIFIED`. This is NOT a semantic inspection of each of the 404 active Python files. The actual EDB, local workbook SHA, full model/input ZIP, executed 12-runner ESM statuses and Windows native solvers were unavailable. Current source paths/links and a completed AST audit are not substitutes for native source data.

## 0. Read-first invariants and acceptance

Preflight reads: `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/CORE_RULES.md`, `engineering/rules/ENGINEERING_GATES.md`, `KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md`, the active module index, output architecture and converter/residual audits.

- Actual primary supports **32**; 44 other mapped joints are wall mesh/edge-constraint points, not new physical supports. 76/97 sensitivity configurations must not overwrite primary.
- Physical gravity verification **100% D + 100% L**, purpose `GRAVITY_1.0D_1.0L`; separate seismic weight based on NBC 105:2025 §5.2/Table 5-1. Current classification D=1.0, Storage L=0.6 where applicable, Other L=0.3, Roof L=0 where applicable; classify every ETABS source pattern rather than guess.
- Physical 25-storey source model: **2×12m X walls with openings** and **3×6m Y walls**, 600-mm reported thickness; 6m X historical spreadsheet remains a research reference only.
- ULS/SLS, original EDB SHA, source model JSON SHA, source workbook SHA/cells, support and mass operator, gravity preload, signed direction, eccentricity and runner SHA belong to immutable case identity.
- Acceptance flags remain independent: `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED`. An ordinary PASS exit code proves none of the last three.
- NBC 105:2025 governs seismic cases; the adopted IS 16700 exceptions are separately identified; never silently replace NBC.

## 1. Current integrated static-audit evidence

GitHub tracked tree query returned **3,488 tracked files** (**4,042** tree entries including directories), **924** .py entries including historical project snapshots and root launchers. Under `components/` there are **212** active .py files. The source-intentional static audit at `tools/audit_cross_module_consistency.py` scanned **404** active Python source files across components/src/tools/root, reporting **0 parse errors, 0 shadowed-scope definitions, 32 exact AST-body cross-file clone groups, 0 current V10_0...V10_6 workbook literals**. The writer-reader inventory reports **98 total legacy literal occurrences, 14 inside docstrings and 84 executable**. These are review queues, not proof of redundant source or broken runtime paths. GitHub workflow: `actions/runs/45098712422` on main base. Historic snapshots are purposefully excluded from the active AST scan.

The large active source files reveal a maintainability/performance risk (not necessarily a bug): `components/ui/application.py` ≈297 kB, `components/equivalent_static/calculation_and_gui.py` ≈164 kB, `components/gravity/gui_and_reports.py` ≈154 kB, `components/model/assembly.py` ≈115 kB, `components/nonlinear_time_history/runner_and_gui.py` ≈104 kB, `components/linear_time_history/runner_and_gui.py` ≈78 kB. Split only after caller and import-graph tests, keeping old launchers as compatible facades.

## 2. Source-to-solver handoff by module

| Module / canonical owner | Actual source contract inspected | Risk and required acceptance | Priority |
| --- | --- | --- | --- |
| 01 ETABS adapter/export — `OpenSees_Complete_Export_V118.py`, `components/inputs/` | Read-only EDB sources, source registry, complete raw object/loads/metadata and hashes; `project_workbooks.registered_project_source` validates registered workbook/model identity | Exact EDB/EDB-synced Excel/assignment/beam split parts must match; avoid fallback to V10.6/V156 or same-filename files | P0 |
| 02 Source identity / model — `components/model/assembly.py`, `source_node_identity.py` | Source nodes/frame/areas and sections; quad shell meshing, unique coordinate/source IDs, releases, rigid end zones and object-derived properties | Native ETABS auto-mesh, edge/MPC load transfer, local axes, rigid-end-zone stiffness and shell/shear modifiers not proven equivalent. Unmatched source objects must not be silent | P0 |
| 03 Sections/material/device mapping — `components/sections/`, `components/nonlinear_time_history/research_building_materials.py` | RCC/steel/frame/FSAM/FVD/BRB target elements use source or explicitly transferred literature assumptions | Literature-based specimen ratios are research transfers; correct project source reinforcement and walls remain verification gates. Never label smoke test = calibration | P0 |
| 04 Gravity — `components/gravity/solver_stack.py`, `comparison_bundle.py`, `reaction_case_registry.py` | Full D+L source-purpose ledger, 32-primary support tags, support reactions and conserved applied loads | Current source-matched reconstructed elastic case still has max 32-support |ΔRz|≈768.045 kN, Σ|ΔRz|≈10,072.106 kN. The 3041.266 kN historical gross-shell run is distinct. Native force recovery/rigid zones open | P0 |
| 05 Initial P-Delta — `components/model/eq_pdelta_initial_tangent.py`, `analysis_basis.py` | Separate user-adopted signed initial EQ checks; cannot add held initial static EQ to full transient motion without no-double-counting evidence | Verify actual initial case run, tangent stiffness and gravity-preserving state transfer per purpose; not inferred from ESM JSON sidecar | P0 |
| 06 Modal/Rayleigh — `components/modal/analysis.py`, `rayleigh.py` | Source-matched ULS/SLS, exact diaphragm ledger and elevation, mass operator, torsion-suppressed preliminary reference; eigen solver and periods | Native COM / mass eccentricity / 32-support stiffness / mass operator match open; greater-than-90% modal sum alone does not certify physical equivalence | P0 |
| 07 ESM — `components/equivalent_static/calculation_and_gui.py`, `organized_exports.py` | Each X/Y uses own selected §5.1 Rayleigh/amplified period; ±force and E+/E-/E0 per axis; case runner separated from force export | ULS ≈95m ESM comparison-only; geotechnical Vs30 absent; generated scripts ≠ solver. Legacy/canonical split fixed in #161. Existing CASE_STATUS matches only filenames → regenerated script can appear previously successful | P0 |
| 08 MRSM — `components/response_spectrum/model_analysis.py` | Source-state and support policy gates, actual spectrum, CQC, modal mass, per-axis model build, E0/E+/E- and independent scaled response | Compare current ETABS RSX/RSY source-specific base shear, spectra, modal DOFs and recovered forces; distinguish force scaling from unscaled drift. Repeated per-axis model construction is a measured performance candidate, not automatically removable | P1 |
| 09 Linear TH — `components/linear_time_history/runner_and_gui.py` | Independent fresh model per record/orientation; source motion pairing, dt, g conversion, 32 support/mass policy and time history statuses | Exact same-source motion manifest, XY/YX, full record length, signed PDelta and acceleration relative/absolute need completed evidence; no generic shortened trial equals full record | P1 |
| 10 NLTHA — `components/nonlinear_time_history/runner_and_gui.py`, `direct_existing_model.py` | Separate existing-model CLI, readiness, source/motion SHA, optional truncation, full-duration gate, source literature material basis | First-step X wall/localForce failure unresolved; 224 planned M0–M6/orientation cases not demonstrated as full-duration solved; full-length and energy convergence gates remain mandatory | P0 |
| 11 NBC 105 — `components/nbc105/` | Dedicated clauses and source evidence/coverage, Kirtipur/Soil C inputs, user-approved project code exceptions | Static equations/screens ≠ complete code certification; Vs30 required for >40m; high-rise ULS ESM eligibility fails in provided log; code adoption and Annex footnotes require explicit review | P0 |
| 12 ETABS comparison/validation — `components/validation/`, `saved_case_identity.py` | Model SHA-based saved response identity; compared loads/drifts/member/support 6 DOFs and source-record provenance | Independently prove source point-to-joint/physical section cuts, signed loads, local axes/units and case stability; no inferred source parity from matching totals | P0 |
| 13 GUI/viewers — `components/ui/application.py`, analysis GUIs | Inputs, 3D element IDs, status indicators, model-specific saved-case selection, lazy optional exports | Separate 'script generated', 'solver completed', 'source matched', 'code accepted' indicators. Do not freeze UI during heavy Excel or full 3D rebuild | P1 |
| 14 Shared output/audits — `components/inputs/output_contract.py`, `output_layout.py`, `components/shared/`, `tools/` | Canonical numbered stages, unique run-id schema, automatic manifest and 07_EXPORT_ZIP; AST writer-reader inventory, status ledger | 84 executable legacy path literals require writer+reader migration; avoid duplicate ZIPs, stale results and cross-state reads; current saved ESM runner status needs script SHA | P0 |

## 3. Confirmed source-level defect: old ESM script status may be replayed

`components/equivalent_static/calculation_and_gui.py::_run_generated` records per-case `case`, `runner_path`, `status`, `return_code` to `ESM_Runner_Status/<batch>/CASE_STATUS.json`. Prior to this review it did not store the executed runner file SHA. `organized_exports.py::_latest_batch_status` considered a matching case basename, SUCCESS and exit code 0 complete. Re-exporting a physically different runner with the **same basename** could therefore inherit a stale success status in the combined workbook/ZIP. The prior source guide already identified this exact gap.

Reproduction test: preserve `CASE_STATUS`, modify source script contents under the same filename, re-open combined export. Correct behavior: `PARTIAL_OR_FAILED`, with `STALE_RUNNER_SHA256` and no completed solver count. Legacy rows lacking executed-runner digest must not be upgraded automatically; old evidence remains visible but unverified. The source fix belongs to the existing ESM writer and reader. This does not validate the underlying EDB or prevent a separate source-model mutation; source/solver SHA gates remain distinct.

## 4. Cross-stage source identity (mandatory manifest)

Every new analysis handoff should carry these **distinct** identifiers, without copying one file's digest into another's field:

```text
project_source_edb_sha256   # original CSI native EDB
etabs_export_manifest_sha256
model_json_sha256           # OpenSees_Complete_Model_Data_V118.json
model_config_sha256         # ULS/SLS, geometry, material, mass/support choices
workbook_sha256 + sheet_cell_source
story_weight_csv_sha256     # NBC §5.2, separate from D+L gravity
runner_script_sha256
run_id, analysis_stage, axis, polarity, eccentricity, orientation
solver_status               # separate from source / native / code acceptance
numeric_result_sha256       # concrete saved result bytes, not just filename
parent_run_id or exact parent source hash
```

A previous-run reference may be used **only** when the same input/configuration hashes and result digests are demonstrated. A manually selected historic workbook may remain a visible research reference; it is not a replacement for a matching-source production input.

## 5. Efficiency: safe versus unsafe changes

| Observed source-level cost | Safe targeted improvement | Must not do |
| --- | --- | --- |
| 12 ESM scripts generated with common X/Y `W, Fi, Cd, k` calculation | Precalculate shared per-axis force ledger once; emit per-case Mz/signed force and independent runner metadata; on-demand XLSX/plots | Treat 12 scripts as 12 solved cases; reuse solved nonlinear gravity tangent without proof |
| MRSM `run_model_spectrum` builds model separately inside axis loop | Profile builder, modal solve and recorder stages; cache fingerprinted *input/reference* data and numerical mode results only when state/solver conditions truly identical | Reuse modes/stiffness after different support/mass/state/eccentricity, or scale MRSM drift with force scaling |
| LTHA loops all record × XY/YX with independent `runpy.run_path` | Persist a hash-based source/record lookup; optional bounded parallel fresh processes after memory benchmark, streaming logs and cancellation | Collapse separate cases into one stateful domain / crop records silently |
| NLTHA full records × M0–M6 × ULS/SLS, first-step X failure | Run smallest ZERO/X/Y isolated verified source mesh and material probe before scheduling 224 jobs; save early failure state | Force permissive convergence, tune foundation reactions, mark 0.005s trial as full-duration success |
| Giant GUI files / optional Excel & 3D model views | Separate pure workers from Tk callbacks, build only visible tabs, defer ZIP/XLSX/PNG to explicit export, use indexed source ID dictionaries | Duplicate Vxxx files or change established filter/source namespaces |
| Repeated repository output inventory, legacy readers | Reuse `tools/audit_cross_module_consistency.py`, `tools/audit_output_writer_reader_pairs.py`, `tools/audit_uniform_output_structure.py` | New competing folder nomenclature, root-level result dumping, blind file moves |
| Duplicate AST function candidates and 84 executable legacy paths | File/line owner-and-caller reviews, regression before coordinated migration, preserve historical snapshots | Deleting all exact-body matches or renaming source files by string search |

The preceding are source-supported optimization opportunities. **No measured runtime speed-up is claimed** by this audit. Establish baseline times (source read; 3D assembly; gravity; eigen; X/Y ESM; MRSM; single XY and YX record; Excel/ZIP) and compare identical source/problem sizes after each change.

## 6. Canonical output contract and GUI workflow

Keep the current per-stage taxonomy `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY` and optional auxiliary review folders, plus per-run contract `00_INPUT_SOURCE`, `01_LOGS`, `02_RESULTS`, `03_EXCEL`, `04_PLOTS`, `05_COMPARISONS`, `06_REVIEW`, `07_EXPORT_ZIP` as already defined. Do not migrate old writers/readers independently.

Recommended single workflow screen:
1. **Source readiness** — actual EDB/Excel/weight/mesh geometry/support source hashes, missing review items.
2. **Model/gravity acceptance** — D+L ledger, physical 32 supports, elements, wall/beam load path, section cuts, P-Delta state.
3. **Modal/Spectrum** — ULS/SLS T, modes/mass participation, soil hazard and Rayleigh, exact force/drift semantics.
4. **Analysis planner** — ESM reference, MRSM, LTHA, NLTHA intent and configured case counts with explicit engineering eligibility.
5. **Execution monitor** — script generated N, running M, converged K, failed J, full-duration accepted L, wall-time/log/cancel, deterministic retry without overwriting evidence.
6. **Comparison and export** — source-verified ETABS/OpenSees table, per-stage immutable workbook/ZIP, `NOT_VERIFIED` source/code blockers.

## 7. Prioritized acceptance work orders

**P0 Engineering (native Windows required):** Freeze one current EDB, V10.7 input source and hashes; reconcile 32 physical support six-component cuts and the exact elastic case's 768.045-kN pointwise gravity mismatch; recover native frame rigid zones and wall shell edge transfer; classify full D+L versus NBC §5.2 seismic weight by source ETABS load pattern; confirm actual Vs30 and code method eligibility.

**P0 Software:** Enforce executed-runner SHA and case output identity; eliminate ambiguous current vs legacy case re-selection; prohibit automatic ZIP `EXPORTED` state from being presented as `NUMERICALLY_CONVERGED` or `CODE_ACCEPTED`.

**P1 Analysis:** Native ULS/SLS period and MRSM parity with ETABS; E+/E-/E0 torsion/edge drift, modal mass and scaling; independent full XY/YX record completion and orientation/scaling evidence.

**P1 Performance/UX:** Profile cost centers, on-demand Excel/ZIP/3D, bounded independent execution and fully cancelable child process, concise stage-specific logs and module-owned outputs.

**P0 Thesis NLTHA:** Reproduce first-step X-wall failure in a source-matched isolated full 3D wall and force-transfer test before the 224-case matrix; keep directly published PEER specimen values flagged as transferred research inputs, not project-calibrated reinforcement.

**P2 Migration:** Replace selected legacy output references only after exact consumer graph coverage and saved-case reopen tests; triage 32 AST clone groups one at a time; preserve old archives.

## 8. Honest completion boundaries

- This audit analyzed selected current source at module boundaries and trusted the project's automated AST metadata for repository-wide *syntactic* coverage only. No full per-function semantic verification of the 404 active Python files has been performed in this task.
- The supplied 2026-11-23 ESM X base shear 29,849.619 kN, Y base shear 26,450.735 kN and 2×12m X wall Aw 2.07317452 m² were copied from the user's log, **not recomputed**. Eccentricity changes Mz and solved response, not total applied V.
- The user's real source EDB, Excel workbooks, analysis outputs and confidential logs were not published here. The code review has no permission to rewrite their scientific evidence.
- Native ETABS 23 → OpenSees structural equivalence remains **OPEN**; the latest 768.045-kN pointwise gravity residual, site Vs30 and first-step X-wall failure remain priority blockers. Passing CI is software evidence, not engineering certification.

## 9. Source references

- `components/model/assembly.py`, `components/model/support_case_contract.py`, `components/model/load_case_purpose.py`
- `components/inputs/project_workbooks.py`, `components/inputs/output_contract.py`, `components/inputs/output_layout.py`
- `components/gravity/solver_stack.py`, `components/gravity/comparison_bundle.py`, `components/gravity/reaction_case_registry.py`
- `components/modal/rayleigh.py`, `components/modal/analysis.py`
- `components/equivalent_static/calculation_and_gui.py`, `components/equivalent_static/organized_exports.py`
- `components/response_spectrum/model_analysis.py`
- `components/linear_time_history/runner_and_gui.py`
- `components/nonlinear_time_history/direct_existing_model.py`, `runner_and_gui.py`
- `components/validation/saved_case_identity.py`, `components/nbc105/acceptance.py`, `components/shared/case_status.py`, `components/ui/application.py`
- `docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md`, `UNIFORM_OUTPUT_STRUCTURE_20261122.md`
- `REVIEW_MAIN/02_MODEL/20261122_NATIVE_ETABS_OPENSEES_CONVERSION_AUDIT.md`
- `docs/validation/20261122_REBUILT_ELASTIC_768KN_RESIDUAL_AUDIT.md`
- GitHub Actions integration run `45098712422`.
