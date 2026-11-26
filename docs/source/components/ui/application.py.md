# application.py — source documentation

**Python source:** [components/ui/application.py](../../../../components/ui/application.py)
**Git baseline content SHA:** 161215192a5a81092db6bc79f54170bde1996848
**Subsystem:** Modern GUI and data display
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the ui implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: See module's underlying computational dependencies. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 13 November 2026 — Main launcher information architecture

**Purpose / source:** The existing Python Tk application shell in `components/ui/application.py` has been reorganized for a sequential structural-engineering workflow without changing the ETABS COM extractor, source mappings, solver entrypoints or numerical code.

**Seven operational stages:** Import & audit; Build the model; Gravity & NBC setup; Linear analysis; Nonlinear analysis; Material laboratory; Review & results. Each stage has two specifically labelled tool groups. Previously always-visible 3-column button stacks have been replaced with a native `ttk.Notebook`; no physical analysis is run when navigating tabs.

**Operator controls:** The original ETABS .EDB, output folder, read-only import action and assembled-model rebuild remain above the stages. All 41 static tool actions (plus four dynamically listed saved visualizations) retain their original Python callbacks. A global text search indexes all registered buttons and opens the exact original action on selection. It does not invent or infer sources and is not a search of model results.

**Responsiveness and accessibility:** Reduced minimum window to 1000×700 and form minimum width to 1000. Each tab contains two groups rather than three full-height columns. Standard Windows controls remain keyboard focusable. The main conversion log has both scrollbars, Copy Log and first/latest controls. Source directory utilities are compact rather than occupying three full-width rows. Notebook tab visibility on narrower Windows/DPI installations requires manual QA.

**Engineering gates:** Visual categorization is not approval. The workflow preserves existing source-read-only ETABS import, prerequisite checks and independently launched analytical modules. Tab order is explanatory, not a batch dependency solver; do not interpret a later tab as passed unless its real gate evidence exists.

**Verification:** `tests/test_main_launcher_workflow_layout.py` checks compile-time AST, original callback registration count, known module launch handlers, search and log. Native Windows 125%/150% scaling, ETABS COM and dynamic menu keyboard navigation still require manual verification.


## 2026-11-15 — export organization and readiness message

The ETABS export GUI now exposes a default-on **Create SHA-verified categorized export copies** checkbox. After native extraction+assembly, the app uses the existing `components.inputs.export_mirror.export_mirror` to copy root generated evidence into `01_ETABS_EXPORT/01_SOURCE..09_REVIEW`, and writes `01_ETABS_EXPORT/00_MANIFEST/analysis_stage_index.json`. It **never relocates/removes** original flat files or changes solver source paths. An already-existing categorized file with different content causes a distinct `EXPORT_ORGANIZATION_NEEDS_REVIEW` log, not a false model conversion failure; the operator must inspect the file hash conflict. Running export a second time is not a reason to overwrite evidence. This is a synchronous copy stage and may take time for the project's large generated HTML/JSON files.

The success dialog now distinguishes `elastic_assembled` from `analysis_ready` and `nonlinear_ready`: a clean assembly error list is **not** physics, source equivalence or material-calibration acceptance. Stage viewers only discover candidates until SHA/case status and native engineering checks pass.


## 2026-11-15 V162 — compact source filters in storey Plotly view

The `structure_postscript` within `components/ui/application.py` previously created a separate two-column/tall source-filter card above the Plotly 3D scene, showing Storey, Element, Section, ETABS object ID and topology tag simultaneously. It is now a compact flexible filter row with the frequently needed Storey / Element / ETABS property controls always visible, while exact source object/topology filters remain accessible under an HTML `Source object filters` disclosure. The original Plotly hover/clicked object detail is preserved and occupies its own readable row.

**Concrete correctness fix:** the original source filter had `gd.data.forEach(... original[i] ...)` using an original trace snapshot. The shared ID highlighter adds a temporary Plotly selection trace after that snapshot. Running a storey/section filter after highlighting could dereference `original[i] === undefined` and fail; the loop is now confined to `gd.data.slice(0,original.length)`, and visibility changes target exactly `meta.map((_,i)=>i)`. The selected highlight overlay is therefore not modified/hidden by source filters. These are purely visualization trace changes, not OpenSees geometry, physical stiffness, links, or engineering calculations.

The prefix/storey/member selector is injected separately by `components/model/id_audit.py` into all three exported Plotly 3D/browser views (and related Plotly HTML). See `REVIEW_MAIN/00_MODEL/20261115_V162_PLOTLY_VIEW_ID_CLASSIFICATION_AND_USABILITY.md`. Regression: `tests/test_shared_3d_prefix_selector.py`. Native ETABS and actual local Chrome UI interaction are not tested by the CI source checks.


## 2026-11-16 — runtime stage visibility, ID lookup guard and on-demand assembled mesh

The Import tab's ID lookup button now checks for an actual nonempty HTML before invoking the browser. While an ETABS worker is active, it refuses to show a possibly stale prior-run lookup and explains that the audit is generated during late assembly. After the run, a missing file produces a Tk warning identifying its expected path and the Excel audit status, not Edge ERR_FILE_NOT_FOUND.

The conversion status parses the worker's [STEP START]/[STEP OK] records and displays the current stage, elapsed time, and time since a log line. It logs the selected saved floor_subdivisions at worker start, explicitly distinguishing FE mesh refinement from visualization resolution. The value is never changed by this UI improvement.

The new Import action "3D actual assembled 4×4 mesh (on demand; no ETABS rerun)" creates the view in a background thread from fingerprint-matched, already-assembled OpenSees V118 model files. It neither invokes ETABS nor changes real ShellMITC4 or gravity elements; see docs/source/components/ui/assembled_mesh_view.py.md.

Four ETABS source 3D/load HTML views are still generated during conversion and remain available by their existing buttons, but the converter no longer automatically opens four browser tabs at completion. They share a single local plotly.min.js via Plotly's include_plotlyjs='directory' output; this avoids repeating the library payload in each HTML. Browser output is local/offline; keep plotly.min.js alongside the source views if moving them. Actual runtime reduction is not established until the user's ETABS_Conversion_Worker.log stages are profiled.

Validation: tests/test_assembled_mesh_view.py and existing GUI workflow layout checks. Native ETABS OAPI and Windows GUI QA remain required. No structural calculation, source EDB or mesh-count policy was altered.


### Performance regression follow-up: November 15 to November 16

Source comparison 9041cb6 (November 15) to cb4c296 (November 16) shows 119 intervening commits. A separate ETABS child worker was introduced with mandatory project EDB hash and optional workbook preflight, plus default enabled SHA verified export mirror. The optional role preflight had independently digested the full EDB for every one of the four source roles, even when no registry was configured. It now computes that EDB checksum once per preflight. Workbook hashes still require source equality, and the EDB is still hashed by the separate project-output provenance stage; no source verification has been disabled.

SHA verified categorized export mirroring is now optional/off by default. The original model and existing categorization mechanism remain available through the checkbox for deliberate use. This prevents hashing/copying all flat artifacts as mandatory import completion work. More granular worker logs mark project hash/layout, optional workbook verification, ETABS CreateObjectProgID, ApplicationStart, OpenFile, source point/diaphragm progress, area/frame extraction, assembly, and optional mirroring. An Import button opens the current worker log and a prolonged-no-output warning remains advisory, never forcibly kills ETABS.

This instrumentation does not prove which stage took ~19 minutes on the actual Windows machine. The private time-stamped worker log is the required discriminating evidence. No 4x4 FEM shell mesh, column offsets, ETABS assignments, gravity loads, or analysis solver is changed by this patch.


### Same-export concurrency protection

The Import-stage separate 4/8/16 slab-mesh workflow and "Rebuild assembled model from saved ETABS export" now reject invocation while the main ETABS worker is still writing the same export folder. Previously users could start a second whole-building mesh assembly and large formula workbook while the original conversion was incomplete, increasing disk/CPU contention and risking inconsistent source inputs. This is a real concurrency risk, not proof that the current 19-minute worker run suffered such overlap. The read-only on-demand assembled 3D viewer also remains unavailable until conversion finishes. No physical mesh reductions or sources are applied.

### November 16 batched source inspector and assembly heartbeat
The original ETABS source structural view remains a grouped high-rise overview. The detailed connectivity inspector now compresses all source-element lines by (category, story, ETABS section/property), serializing every source object to indexed metadata for the exact ID dropdown, click-to-select and single spotlight. No engineering mesh is rebinned; the original ETABS object geometry is the source of this display. The 3D load inspector groups identical pattern/story/UDL-value surfaces and frame arrow records, preserving per-point original hover IDs and numeric values. Trace counts are logged with `[VISUALIZATION COMPACTION]`. All source audit CSV/JSON output remains unchanged.

The Tk main conversion status consumes `[ASSEMBLY PHASE START]` and `[ASSEMBLY HEARTBEAT]` lines emitted by `components/model/assembly.py`, providing measured progress through conforming source-panel ShellMITC4 refinement, spatial node indexing, frame splitting and load-path stages. This visibility does not imply numerical solver progress. A Windows ETABS native run and browser interaction benchmark are required for final performance acceptance; test source figure compaction with `tests/test_source_view_compaction.py`.

### 2026-11-17: optional detailed gravity formula workbook

The Gravity & NBC tab now provides **Generate detailed storey-gravity Excel from saved model (no ETABS)**. The operation is available only after the main conversion ends and only when the selected export contains the complete assembled model, matching config and final report. A background worker starts the distinct Python CLI, so Excel's formula expansion does not freeze Tk or start CSI ETABS. Duplicate clicks are guarded; the user receives the workbook path or an explicit error. It does not alter the numerical model, supports or gravity load pattern.

The normal ETABS Import and `prepare_complete_export` keep the source ledger, reconciliation and CSV/JSON mandatory but defer the expensive mesh-level formula workbook by default. `Gravity_Storey_Workbook_Status_V131.json` makes the deferred status explicit. See `docs/source/components/gravity/storey_loads.py.md` and `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261117_GRAVITY_EXCEL_EXPORT_PERFORMANCE_ROOT_CAUSE.md`.


### 2026-11-17 — Import-stage gravity Excel call to action
The Import tab's source audits group now includes **Generate full gravity load-path Excel (on demand; no ETABS rerun)**. This invokes the same validated, asynchronous `_generate_storey_gravity_excel` callback already on the Gravity/NBC stage. It requires a completed source export, compatible assembled model/config and a successful report, and never calls ETABS or rebuilds ShellMITC4 cells. The workbook is `Gravity_Storey_Load_Breakdown_V131.xlsx`: mesh-cell pressure formulas and node-level gravity source-load path for ETABS/Excel source-load review, available when needed rather than blocking all conversions. **It is not a native support reaction calculation** and does not, by itself, resolve differences among 32, 76 and 97 restraints. Actual solved reactions require separate ETABS/OpenSees joint reaction comparison, support ID crosswalk, fixity checks and equilibrium gates. Both GUI access points share a single guarded callback. Regression: `tests/test_gravity_excel_import_action.py`.

## Import audit terminology
Lowest-elevation six-DOF fixities in the topology/load-only preview are explicitly preview-only. The connected solver chooses its own support profile. The primary thesis model retains 32 physical supports and 44 additional wall mesh points pending source-matched edge transfer. Production readiness and literature-based exploratory execution are distinct; import success does not approve either physical model.

## Import to Model handoff

Use **Review selected export in Model** to continue from Import. Model shows the current export folder and passes it to the mapping, slab mesh and area integration tools. These actions wait for the active Import worker to finish. The completed worker's saved load view stays associated with the folder used for that worker, even if the folder field changes before completion. Read the worker's report separately for assembly errors and engineering readiness.


2026-11-26: Gravity/NBC exposes the existing elastic comparison rebuild through a manifest-bound shortcut. Results exposes the existing full migration audit using the selected export root, explicit confirmation, SHA duplicate and format checks, and a child process; logs and reports remain local. Nonlinear displays the selected folder, without altering the newer native launchers or engineering gates.


2026-11-26: the main import callback validates the original export-root boundary before writing conversion logs. Case-dependent specialist actions in Import, Linear/Results and Nonlinear use `_launch_selected_tool` and the existing `_model_review_folder` guard, rather than reading an unvalidated entry. Saved source-view actions prefer the selected export, not a previously completed worker from another case. Native solver behavior and model acceptance are unchanged.
