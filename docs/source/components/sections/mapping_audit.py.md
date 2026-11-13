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
