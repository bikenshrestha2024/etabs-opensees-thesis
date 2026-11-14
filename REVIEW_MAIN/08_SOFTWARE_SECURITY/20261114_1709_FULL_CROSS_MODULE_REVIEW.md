# Cross-module output, physical evidence and UI review — 2026-11-14 17:09 NPT

**Status:** REPOSITORY SOURCE AUDIT COMPLETE FOR LISTED MODULES; Windows/native engineering acceptance remains OPEN. Review target: `main` after PR #51 (`0edc3ef5240b6fe4b4bb1473564af81565f31559`). The checked source files were fetched from GitHub, not inferred from an older release. This report does **not** claim a complete line-by-line audit of every repository source file or direct access to the Windows `D:\Thesis Opensees` directories. Run-specific numeric results cited below are from user-provided screenshots/log excerpts, not independently re-executed.

## Verified working / preserved behavior

| Evidence | Actual source | Reviewer finding |
|---|---|---|
| Canonical seven-stage index | `components/inputs/output_layout.py` | `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`; stage index declares navigation-only state |
| Flat export mirror | `components/inputs/export_mirror.py`, `09_ORGANIZE_ETABS_EXPORT.py` | SHA-verified copy without deletion; transient `*.processing.json` excluded from *mirror*, not removed from original directory; divergent copied content fails closed |
| Folder audit | `components/inputs/folder_audit.py`, `22_AUDIT_EXPORT_FOLDERS.py` | Local JSON/Markdown reports exact folder presence/flat files/missing or conflicting mirror copies; stage existence does not prove solve/acceptance |
| New gravity GUI case path | `components/gravity/gui_and_reports.py::_inputs`, `components/inputs/output_layout.py::canonical_gravity_run_root` | Legacy-selected outputs redirected into `02_GRAVITY/RUNS/<case>` **for new runs**; historical result paths remain available |
| Project IS stiffness UI | `components/model/analysis_basis.py`, `AGENTS.md` | Conventionally supported RC slab `0.25 Ig ULS / 0.35 Ig SLS` labelled compulsory *project-adopted* IS 16700:2023 Table 5 basis; physical generated section equivalence still not demonstrated by GUI text |
| Source display aliases | `components/model/display_ids.py`, `components/sections/mapping_audit.py`, `components/sections/mapping_gui.py` | Display aliases kept separate from actual numerical OpenSees solver tags; no numeric renumbering proposed |
| Area helper safety | `components/sections/area_elements.py` | Nonlinear wall integration is explicitly a gated auxiliary stage, not a fully calibrated building; additive duplication risk remains a native acceptance gate |

Previous PR #51 CI passed ETABS export staging, repository compilation/navigation, and NLTHA Python quality checks. Those checks do not execute Windows ETABS nor certify gravity load path or seismic response.

## Discrepancy register — precise source ownership and proposed resolution

### P0-01: two competing output-taxonomy definitions — confirmed from source
- `components/inputs/output_layout.py::STAGE_FOLDERS` uses `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, 7 stage names.
- `components/inputs/project_output_layout.py::MODULES` uses `06_LINEAR_TH`, `07_NONLINEAR_TH`, plus `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES` and `REVIEW_MAIN`.
- `components/gravity/mesh_cases.py::case_base` generates `02_MODEL/SLAB_LOAD_PATH/MESH_04|08|16`, absent from both stage indices.
**Impact:** different producers can create distinct representations of the same stage, with incomplete navigation and duplicate directories. **Do not rename or relocate them yet.** Establish a shared canonical stage/alias registry plus producer/consumer inventory; migrate as an atomic writer+reader change with explicit legacy aliases and model source hash checks. The mesh-model stage must remain distinguishable from the gravity solver stage.

### P0-02: V142 case-review destination still hard-coded to legacy folder — confirmed
`components/validation/case_review.py::export` uses `out=folder/'OpenSees_Analysis_Results/Case_Review_V142'`, even though `collect` searches legacy and new stage paths. The GUI can receive an export root or individual case folder; a case-folder input can create an unintended nested `.../<case>/OpenSees_Analysis_Results/Case_Review_V142`.
**Resolution:** write a case-identified audit into a canonical cross-stage review location, keep dual-read old folders and add tests for root/stage/case invocation. Do not mislabel a present Excel file as populated drift.

### P0-03: some report consumers still read ONLY the legacy root — confirmed
`components/validation/response_inventory.py::available_response_rows` assigns `out=root/'OpenSees_Analysis_Results'` and reads `Gravity_Result_V110.json` and `Deformation_*_V132.json` from that location. New `02_GRAVITY/RUNS` records can therefore be invisible to this consumer. `components/validation/case_review.py::collect` performs newer multi-root discovery but may scan a selected subfolder and its parent canonical stage, duplicating response rows.
**Resolution:** shared read-only result registry keyed by source EDB SHA, assembled model hash, ULS/SLS, physical support case, earthquake case, and result type; exact de-duplication by canonical file path and run ID; explicit `MISSING`, `INCOMPLETE`, `STALE_MODEL` instead of plotting zeros.

### P0-04: physical slab stiffness remains a numerical gate — NOT NATIVE VERIFIED
`components/model/linear_shell_stiffness.py` explicitly documents the `ElasticMembranePlateSection` membrane vs plate stiffness proxy and warns that transverse-shear stiffness cannot always match ETABS `v13,v23` independently. `components/model/analysis_basis.py` only defines the project stiffness policy shown to users.
**Resolution:** verify generated element section commands for ULS `m11=m22=m12=0.25`, SLS `0.35` where applicable, physical thickness/self-weight and membrane properties; verify wall flexure, frame stiffness, load transfer, force/resultants and mesh 4/8/16 under matched sources. A label change cannot establish implementation.

### P0-05: globally matched gravity does not close individual support reconciliation — user screenshot/log evidence
The user-facing direct comparison reported ETABS `311367.314 kN`, OpenSees `311367.314 kN` (rounded), largest listed pair difference approximately `3041.266 kN`, and 32 matched support pairs. That is a **global equilibrium pass**, not foundation reaction equivalence. Model-source identity in screenshot was `WORKING_COPY_ANALYZED_FROM_SOURCE_EDB`. The source-reaction case reports 44 additional reference restraints beyond 32 selected diagnostic reactions.
**Resolution:** compare matching gravity combination, model SHA, node mapping and six reaction DOFs per physical support. Check restraints, wall-footing interface, slab-beam-wall connectivity, column offsets and source-matched wall/shell stiffness. Report 32, 76, 97 as distinct cases; never modify forces to make total sum match.

### P1-06: folder audit is a *top-level inventory*, not a full writer/reader dependency check — confirmed
`components/inputs/folder_audit.py` lists immediate stage children and files, legacy case directory names, root-level files and hash conflicts. It does not recursively classify *all* nested solver artifacts or detect stale absolute paths inside `*.json`, `*.py` and `*.xlsx` manifests. `STAGE_HINTS` is currently a declared but unused classification map.
**Resolution:** add opt-in recursive metadata inventory (not source content scraping), authoritative case index, and orphan/broken-reference detection for known manifest schemas; cap/hash large file operations, preserve privacy and never follow symlinks. Retain concise default report and detailed local review.

### P1-07: source mirror is not a full live writer migration — confirmed
`export_mirror()` copies only supported extensions from the flat selected export root to categorized folders; it does not recurse and intentionally does not delete flat files. `09_ORGANIZE_ETABS_EXPORT.py` produces a mirror manifest, stage index and folder audit. **A successful organizer execution does not imply 145 original flat files have disappeared or that run writers switched paths.**
**Resolution:** migrate producer+consumer pairs one stage at a time; preserve old run index and exact source SHA; suppress transient sidecar creation at source where safe; do not delete original results or overwrite authoritative input workbooks.

### P1-08: P-Delta and drift must be separately reported — user screenshot/code evidence
V142 empty graph previously showed 0 saved rows; current `collect` now adds missing-data issues. However plotting is still downstream of legitimate completed seismic case CSV/JSON and may fail or duplicate rows for cross-stage paths. Initial `1.2DL+0.5IL±1.5EL/WL` cases are compulsory project-adopted IS 16700 prerequisites but not substitutes for ULS/SLS NBC seismic drift response.
**Resolution:** provide `PDelta_Initial_Cases`, `ULS_Drift`, `SLS_Drift` separate status tabs; link to exact completed case files and reject nonmatching model+preload hashes, not just matching filenames.

### P1-09: additional GUI and NLTHA/model acceptance
Source-ID aliases and 3D export are implemented in V126 UI, but Windows interactions and active launcher version require a real native smoke test. `components/sections/area_elements.py` remains a gated additive helper; don't re-add duplicate floor/wall shells. Calibrated nonlinear wall materials, brace connection release equivalence, device parameters, full paired record durations and time-step stability are all separate model-validation gates.

## Native evidence collection (local-only; public repository must not receive private PDFs/EDB/XLSX)

1. Pull current main; run `python 22_AUDIT_EXPORT_FOLDERS.py "D:\Thesis Opensees\ETABS 11-14-2026\3"` for *read-and-report* path checking. Alternatively `python 09_ORGANIZE_ETABS_EXPORT.py ...` for categorized SHA-verified copies and stage index. Never operate while the ETABS export is actively writing. Note these commands produce new local manifest/audit files but do not rewrite the original model.
2. For gravity, supply the actual `Gravity_Evidence_Upload` ZIP and matched ETABS `1DL+1LL` joint reactions; compare node 263↔36 and 44 unpaired support records with coordinate, restraint and six DOF provenance.
3. For slab transfer, collect the independent MESH_04, 08, 16 solver reactions and frame/shell force resultants. Merely exporting MESH_04 workbook is not convergence.
4. For ULS/SLS drift, provide the exact saved case response, full model hash and loading basis, rather than screenshots of empty axes.
5. For Windows, test import, 3D viewer save, ID lookup, gravity new output path, V142 refresh/export, ESM/MRSM runner and ZIP reopening. Record links to required folders and issue status.

## Review acceptance

| Gate | Status | Why |
|---|---|---|
| New static folder-audit and export mirror software checks | PASSED_IN_PRIOR_PR_CI | Prior PR #51 CI passed, but no native Windows run |
| All active writers using same canonical output names | **FAIL / INCOMPLETE** | Dual taxonomy + 02_MODEL + legacy outputs |
| Reader compatibility for new gravity path | **FAIL / INCOMPLETE** | `response_inventory.py` remains legacy-only |
| Exact gravity reactions at every ETABS physical support | **NOT VERIFIED** | 32 diagnostic pairs include large mismatch |
| Slab/wall stiffness and MESH_04/08/16 convergence | **NOT VERIFIED** | requires independently solved responses |
| Seismic drift/P-Delta completed-source report | **NOT VERIFIED** | missing rows and variable source discovery |
| NLTHA source/material/connection calibration | **NOT VERIFIED** | requires project physical/numerical evidence |

**No source code or solver input is modified by this review file.** Follow the repo's `AGENTS.md` and engineering runbook before implementing fixes, and preserve historical code/output compatibility.
