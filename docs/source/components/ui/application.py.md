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
