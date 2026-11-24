# Cross-module workflow, code ownership and output-folder audit — 2026-11-24

**Base reviewed:** GitHub `main` at `1cd4fcadfa4ffda40ca73443d6830548e45ddad7`. **Source:** repository tree/API, active module files, tests and mandatory project contracts. **Scope:** source-only integration review with targeted code changes; NOT a complete function-by-function semantic audit or a 25-storey native ETABS/OpenSees acceptance. See source edit PR #190 and Issues #177 / #186.

## Actual discovery

| Observation | Source-grounded finding | Classification |
| --- | --- | --- |
| Repository tree | GitHub recursive tree returned `truncated=false`, **4,079 tracked entries**, **947 Python files including historical snapshots**, **131 root Python files**, **264 `docs/source/*.py.md` guides** | Verified static discovery only |
| Competing launcher names | Root `01`–`22` include many reused numeric prefixes, e.g. `01_MAIN_GUI.py`, `01_WORKFLOW_START.py`, `01_START_ETABS_TO_OPENSEES.py`; `10_GRAVITY.py` and `10_WALL_VALIDATION.py` | Active canonical program index required; do not bulk rename |
| Oversized active modules | `components/ui/application.py` ~297 kB, ESM `calculation_and_gui.py` ~172 kB, Gravity `gui_and_reports.py` ~154 kB, Model `assembly.py` ~116 kB, NLTHA `runner_and_gui.py` ~105 kB | Maintainability hotspot, not numerical error |
| Canonical stage folders | `components/inputs/output_layout.py`: ETABS_EXPORT, MODEL, GRAVITY, ESM, MODAL, MRSM, LTHA, NLTHA, ETABS_COMPARISONS, SOFTWARE_DIAGNOSTICS and UPLOAD_PACKAGES | One stage registry exists |
| Manifested run folders | `components/inputs/output_contract.py`: source-hash-aware compact ID already used for `prepare_history_run` LTHA/NLTHA, but long `create_case_run` caller labels were not compacted | Fixed in PR #190 for NEW source-hashed manifested runs |
| Existing long direct ESM folders | `components/inputs/project_workbooks.py::analysis_output_folder` uses source-name-derived `ULS_Floor_3_...` scope and `components/equivalent_static/calculation_and_gui.py::write_outputs` writes directly to that folder | OPEN: requires paired writer/reader and saved-case identity migration |
| Existing modal folder provenance | `components/modal/gui_and_reports.py` obtains an `analysis_output_folder(...).name` label, then calls `create_case_run` without a source/assembled-model SHA, though it stores script SHA separately | OPEN: do not equate script hash with assembled-model SHA just to shorten names |
| Folder audit | `components/inputs/folder_audit.py` inventories stage owners, loose source files, legacy cases and SHA mirrors but did not identify overlong case components across stages | Extended in PR #190; review only, no source moves |
| ESM timing evidence | User-provided 2026-11-23 log: first of 12 child runs 1,137.812 s; later runs roughly 163–183 s. Existing issue #186 discusses repeated model+gravity construction. | Benchmark is case-specific; no demonstrated optimization of native 12-case total |
| Physics gates | Legacy gross-shell vs rebuilt ETABS-elastic 32-support gravity residuals are separate cases (3041.266 kN and 768.045 kN max respectively). | Both **NOT_ETABS_EQUIVALENT**; no approval based on FZ sum |

## Cross-module ownership / targeted follow-up gates

| Stage | Active source and entry | Main consistency / efficiency gate | Action |
| --- | --- | --- | --- |
| ETABS source import | `OpenSees_Complete_Export_V118.py`, `components/model/assembly.py`, `components/inputs/export_mirror.py` | ETABS authored IDs, shell auto-edge/MPC, actual offsets/releases, source EDB digest and read-only import | Native source-matched benchmark required; preserve `01_ETABS_EXPORT` |
| Model, materials/sections | `02_MODEL`, `components/model/`, `components/sections/` | 2 × 12 m opening-bearing X walls, 3 × 6 m solid Y walls, distinct material/rebar/stiffness provenance | No geometry/model changes in this PR; area integration remains within MODEL owner |
| Gravity/P-Delta | `components/gravity/solver_stack.py`, `components/gravity/gui_and_reports.py`, `components/model/initial_pdelta.py` | Primary **32 physical foundation supports**, 44 mesh points; 1.0D + 1.0L is not reduced seismic weight; per-joint 6DOF mismatch | Preserve 76/97 as sensitivity; re-evaluate auto-edge transfer and rigid offsets with native ETABS |
| ESM | `components/equivalent_static/calculation_and_gui.py`, `organized_exports.py` | Source-identifiable ULS/SLS, X/Y signed ±E; output state; archive owner; costly fresh model build | Previous PR #189 consolidates module-owned STATUS/ZIP; new direct case name migration remains OPEN |
| Modal | `components/modal/analysis.py`, `gui_and_reports.py` | Mass coverage is not physical equivalence; ensure genuine T1/Tn90 and ULS/SLS stiffness provenance | Avoid using ESM/legacy label alone as source identity |
| MRSM | `components/response_spectrum/model_analysis.py` | `create_case_run` receives assembled-model SHA; stage carries source/response spectrum/scaling and eccentricity | New long, SHA-bound manifested case label now compact; native model/cut still unverified |
| Linear time history | `components/linear_time_history/runner_and_gui.py`, `components/inputs/output_contract.py` | P-Delta initial signed cases and motion-state transfer; source waveform hash, dt and no double counting | Do not label linear check as prerequisite for nonlinear solver |
| Nonlinear time history | `components/nonlinear_time_history/runner_and_gui.py`, `direct_existing_model.py` | First-step X-wall failure, literature material assumptions, full 8 pairs XY/YX for M0–M6, independent run states | Native nonlinear wall/force and complete motion records not verified |
| Comparisons/validation | `components/validation/response_checks.py`, `seismic_review_bundle.py` | Source-equivalent reactions/displacements/sections, archive SHA, honest case status | 2026-11-23 ESM route-comparison log indicates reviewed ETABS-linked ULS workbook missing for 12 reported cases |
| GUI/orchestration | `01_MAIN_GUI.py`, `components/ui/application.py`, stage GUI adapters | Single current case and source manifest throughout, cancellable worker, no stale copied runtime | Split giant files by stable responsibilities only with GUI smoke tests and no duplicated GUI modules |
| Auditing/docs | `tools/audit_active_repository.py`, `tools/audit_output_stage_ownership.py`, `22_AUDIT_EXPORT_FOLDERS.py`, `09_ORGANIZE_ETABS_EXPORT.py` | One active registry, strict source provenance, long-name path warnings, no arbitrary historical migration | PR #190 extends existing output_contract and folder_audit only |

## Recommended tight stage layout for newly generated results

```text
<actual selected ETABS export>/
  01_ETABS_EXPORT/              # immutable source mirrors and manifests
  02_MODEL/                     # model + area integration owner
  02_GRAVITY/RUNS/<state>/<compact-case>/<run-id>/
  03_ESM/RUNS/<state>/<compact-case>/<run-id>/
  03_ESM/STATUS/
  03_ESM/REVIEW_SNAPSHOTS/
  03_ESM/07_EXPORT_ZIP/
  04_MODAL/RUNS/<state>/<compact-case>/<run-id>/
  05_MRSM/RUNS/<state>/<compact-case>/<run-id>/
  06_LINEAR_TIME_HISTORY/RUNS/<state>/<compact-case>/<run-id>/
  07_NONLINEAR_TIME_HISTORY/RUNS/<state>/<compact-case>/<run-id>/
  08_ETABS_COMPARISONS/
  09_SOFTWARE_DIAGNOSTICS/
  90_UPLOAD_PACKAGES/
```

This is an **ownership illustration**, not a claim that every stage currently uses `create_case_run`. The eight standard per-run subfolders remain `00_INPUT_SOURCE` to `07_EXPORT_ZIP` as defined by `RUN_SUBFOLDERS`; stage-level `STATUS` is an ESM-specific existing convention. Keep the non-destructive `OpenSees_Analysis_Results` legacy directory until all readers and outputs are positively matched by SHA.

## Next validation / remaining work (not implemented by this audit)

1. Source-matched original ETABS EDB and V10.7 workbook identity, including 1.0D+1.0L/32-support six-component reactions and native shell-edge transfer.
2. ESM direct writer/reader compact-name migration, with legacy complete-case discovery and GUI reopen, followed by a benchmark on 12 **real** Windows processes with current source hashes.
3. Modal source model hash semantics and source-bound casing; MRSM eccentricity and initial P-Delta integrity; LTHA/NLTHA independent-state and recorder/first-step wall validations.
4. Function-level semantic review of active source with exact line, physical assertion, reference DOI/clause, test and human reviewer. GitHub static compilation is only a portion of this.
5. Local long-path audit via `python 22_AUDIT_EXPORT_FOLDERS.py "<export directory>" --skip-hash` (do **not** commit the generated output containing local pathnames).

**Native gate summary:** SOURCE_CHECKED=NOT_VERIFIED_FOR_ACTIVE_EDB; NUMERICALLY_CONVERGED=NOT_VERIFIED_FOR_NEW_RUN; ETABS_OPENSEES_MATCHED=NOT_VERIFIED; EXPERIMENT_VALIDATED=NOT_VERIFIED; CODE_ACCEPTED=NOT_VERIFIED. Green CI and saved files are only software/process evidence.
