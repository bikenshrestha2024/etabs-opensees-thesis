# mapping_gui.py — source documentation

**Python source:** [components/sections/mapping_gui.py](../../../../components/sections/mapping_gui.py)
**Git baseline content SHA:** 61af8f7cff5015a78bdc3d2063ff1271a403b74c
**Subsystem:** Sections, nonlinear walls, FVD/BRB devices
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the sections implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R07 R08 R09 R13. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-23 — post-conversion source-ID and on-demand audit fixes

The uploaded V125 workbook contains 2,092 source objects, of which 55 `BEAM / UNASSIGNED` storey-0 records have **empty solver tags**, alongside 14,262 actual assembled solver elements. These source-only objects are not automatically missing beams nor OpenSees solver elements; retain the topology until original ETABS assignments are checked. The additive `assembly_status` in the mapping/Excel sheet explicitly distinguishes `ASSEMBLED_SOLVER_ELEMENT`, `SOURCE_TOPOLOGY_ONLY_NO_SOLVER_ELEMENT` and unverified assembly. A source-only object in an otherwise completed assembly cannot be assigned a nonexistent nonlinear solver mapping. Repetitive frame-release messages are summarized only in the GUI; original full per-ID warnings remain in the untouched export report.

**ID bug fixed:** `export_id_audit` previously calculated `assembled_area` but never read it when generating the Excel/HTML table's solver-tag column. ETABS frame 1 and area 1 may coexist with distinct OpenSees tags. The exporter now selects the correct dimension-specific map for frame or area; existing columns retain their positions and the header accurately says assembled solver element tags. No source ID or real element tag is renumbered.

**Performance:** `MappingGUI.reload()` and `show_load_audit()` no longer automatically generate the large workbook. `Export / open Excel audit` remains an explicit user-requested action, keeping the locked-workbook timestamped fallback. `MappingGUI.populate()` uses indexed solver-tag/property lookup. The inline node picker starts blank, so opening the inspector no longer falsely highlights `NODE:1`. Exact Plotly source IDs and separate solver tags remain available.

Reference: [23 November source-grounded handoff report](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/REVIEW_MAIN/01_ETABS_IMPORT/20261123_POSTCONVERSION_ID_MAPPING_WORKFLOW_AUDIT.md). Tests: `tests/test_postconversion_handoff_20261123.py`, `tests/verify_v125.py`, `tests/test_shared_3d_prefix_selector.py`. These checks are not a new native ETABS–OpenSees equivalence or NLTHA run.


### Explicit frame/area visual selection

`plotly_query_for_key(key,data)` carries exact ETABS **dimension** to the common Plotly HTML inspector through `category=frame/area`, so frame ID 1 is never mistaken for area ID 1. `SOLVER:` elements derive the category from their actual parent mapping. `inline_source_keys` supports separate ETABS frame/area selectors and reports an ambiguous legacy number rather than highlighting both. `Highlight selected ID in 3D` now reports a missing saved HTML file to the GUI rather than silently doing nothing.

Regression: `tests/test_postconversion_handoff_20261123.py`.


## 2026-11-24 — V126 partial mapping tree and blank 3D root cause

The GUI tree had a concrete Python error in the immediate solver-row creation path: `map(str(sr['node_tags']))` passes one argument to `map` instead of the required function and iterable. It raised `TypeError: map() must have at least two arguments` after inserting the **first source object**, explaining a one-row mapping tree despite a complete topology export. `MappingGUI.reload` previously caught the exception into a **bottom-only status label** and never reached `draw_source()`, leaving Matplotlib's default empty 0–1 cube. The initial deterministic regression committed before the source fix observed four RED failures: `map()` error, missing deferred expansion method, and missing visible geometry failure status.

The new browser renders property-group roots first, **loads source objects only on property expansion**, and **loads solver segments only on source-object expansion**. It maintains the original source `FRAME:/AREA:` IDs and independent solver tag namespace. Selecting the collapsed property group still yields its full underlying source-key set; selecting an object or segment targets its exact keys. A source-only unassembled object never generates a fake solver-child row. Indexed `solver_by_tag` is used at expansion. This reduces initial Tcl/Tk widget insertion from potentially thousands of source/solver rows to a handful of property rows.

`reload` still reads the selected source evidence on demand and does **not** regenerate Excel. It independently attempts the tree and 3D rendering, clears a partially populated tree, and puts `MAPPING DISPLAY INCOMPLETE` plus the actual exception in a banner **near the top**. No resolved source edges likewise produces an explicit 3D warning rather than an apparently normal empty cube. The selected source ID, topology/solver mapping, model input and saved nonlinear candidate assignments are unchanged.

**Provenance/acceptance:** This is a GUI display correction. Source extraction may be complete while source section/material assignments or native solver equivalence remain open. In particular, no native section is invented for unassigned frames, and a source 76-ID topology/restraint skeleton must not be treated as 76 physical foundations: the primary model uses 32 actual supports plus 44 shell-mesh transfer points. Gravity 1.0D+1.0L is separate from NBC 105:2025 §5.2 seismic weight. New deterministic `tests/test_mapping_browser_lazy_source_20261124.py` uses fake Treeview and synthetic geometry data; complete Windows GUI/ETABS native evidence remains unverified.
