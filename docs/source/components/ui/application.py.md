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
