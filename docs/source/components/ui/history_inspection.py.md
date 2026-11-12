# history_inspection.py — source documentation

**Python source:** [components/ui/history_inspection.py](../../../../components/ui/history_inspection.py)
**Git baseline content SHA:** 101d6fb3b9e05e00fc6d127118ec62b06c56f6ec
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

## 2026-11-12 — saved-analysis scope separation

**What:** the Time Histories window has an explicit *Analysis run scope* selector to distinguish `LTH_ULS_Trial...` from `EXPLORATORY_FRAME_NL...` and other unrelated subdirectories. **When:** opening saved histories after a run or reviewing multiple run folders. **Why:** earlier UI recursively mixed 40.94-second full Kobe LTH and 0.1-second assumed-material exploratory-frame NL data in one menu, which could mislead engineering interpretation.

**How:** `history_scope_name(root, path)` categorizes files by the first run-directory component; `choose_default_history_scope` selects an existing LTH scope when available, preserving explicit user selection. Manual Refresh traverses the directory tree once and then filters history CSV, input audit and log/performance output within selected scope. The *All analyses (mixed)* option remains available explicitly and is clearly labelled as mixed. All numeric CSV samples remain unchanged, and no physical analysis commands have been edited.

**Where:** `components/ui/history_inspection.py`, regression `tests/test_history_inspection_scopes.py`. **Which evidence:** selected study's full histories, drift and compatible run logs. **Who:** software maintainer checks Tk responsiveness and provenance; structural researcher confirms source/model/record compatibility before comparisons.

**Limits:** a scope name is folder-based grouping, not validation that every result shares source model SHA. In case a user selects the entire analysis-results tree, initial inventory traversal is still synchronous and may take noticeable time; a future background indexer with stop/cancel should be considered after a Windows benchmark. No native Tk test is claimed by CI.
