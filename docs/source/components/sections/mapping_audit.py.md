# mapping_audit.py — source documentation

**Python source:** [components/sections/mapping_audit.py](../../../../components/sections/mapping_audit.py)
**Git baseline content SHA:** 49e001effb05935507adbe08b79947a2a6592a01
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

## 2026-11-13 import review: Excel in-use fallback

`export_excel(folder,path=None)` retains the original path and workbook when Excel holds a Windows file lock. If saving it raises `PermissionError`, the function saves a new timestamped workbook with suffix `_OPEN_WORKBOOK_YYYYMMDD_HHMMSS_microseconds.xlsx` in the same directory and returns that *actual* path. It does not close Excel, delete the old workbook or silently claim that old and new workbooks are identical. If the output directory itself is unwritable, a clear permission error still propagates. Re-check source identity before using the alternate audit workbook in thesis results. Static tests are at `tests/test_import01_audit_and_workflow.py`.

## 2026-11-23 — post-conversion source-ID and on-demand audit fixes

The uploaded V125 workbook contains 2,092 source objects, of which 55 `BEAM / UNASSIGNED` storey-0 records have **empty solver tags**, alongside 14,262 actual assembled solver elements. These source-only objects are not automatically missing beams nor OpenSees solver elements; retain the topology until original ETABS assignments are checked. The additive `assembly_status` in the mapping/Excel sheet explicitly distinguishes `ASSEMBLED_SOLVER_ELEMENT`, `SOURCE_TOPOLOGY_ONLY_NO_SOLVER_ELEMENT` and unverified assembly. A source-only object in an otherwise completed assembly cannot be assigned a nonexistent nonlinear solver mapping. Repetitive frame-release messages are summarized only in the GUI; original full per-ID warnings remain in the untouched export report.

**ID bug fixed:** `export_id_audit` previously calculated `assembled_area` but never read it when generating the Excel/HTML table's solver-tag column. ETABS frame 1 and area 1 may coexist with distinct OpenSees tags. The exporter now selects the correct dimension-specific map for frame or area; existing columns retain their positions and the header accurately says assembled solver element tags. No source ID or real element tag is renumbered.

**Performance:** `MappingGUI.reload()` and `show_load_audit()` no longer automatically generate the large workbook. `Export / open Excel audit` remains an explicit user-requested action, keeping the locked-workbook timestamped fallback. `MappingGUI.populate()` uses indexed solver-tag/property lookup. The inline node picker starts blank, so opening the inspector no longer falsely highlights `NODE:1`. Exact Plotly source IDs and separate solver tags remain available.

Reference: [23 November source-grounded handoff report](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/REVIEW_MAIN/01_ETABS_IMPORT/20261123_POSTCONVERSION_ID_MAPPING_WORKFLOW_AUDIT.md). Tests: `tests/test_postconversion_handoff_20261123.py`, `tests/verify_v125.py`, `tests/test_shared_3d_prefix_selector.py`. These checks are not a new native ETABS–OpenSees equivalence or NLTHA run.
