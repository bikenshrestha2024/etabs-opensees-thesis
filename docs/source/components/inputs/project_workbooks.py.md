# project_workbooks.py — source documentation

2026-11-10 extension: `registered_project_source(export_dir, role)` reads
`project_sources.private.json` in the selected export or code root, or the
`OPENSEES_PROJECT_SOURCES` location. It checks the current EDB and registered
source SHA256 before returning a path; changed sources raise ValueError.
Roles: etabs_assignment, etabs_full_table, nbc_calculator, nbc_engine and optional
etabs_linked_audit. No source file is changed. Unscoped drive-specific workbook
discovery was removed. `_calculator_sync_summary` reads original-engine
labelled adopted T1 (seconds) and Aw (m²), separately from modal/Rayleigh data.

**Python source:** [components/inputs/project_workbooks.py](../../../../components/inputs/project_workbooks.py)
**Git baseline content SHA:** 7fa25b152078d65fe65c964dcd48e18587a0872a
**Subsystem:** ETABS/source inputs and earthquake motions
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the inputs implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## Source-verified engineering behavior (2026-11-05)

- `source_workbooks(root,export_dir,limit_state)`: read-only spreadsheet discovery. The EDB identity in `SCALING SUMMARY!B4` is matched using portable Windows-path semantics, not the host OS `Path(...).stem` assumption. Reject a source with a different EDB/floor or state; do not bypass this via a hard-coded filename fallback. If source is ambiguous, return no scaling workbook rather than a guessed Aw.
- `import_project_inputs(...)`: `NBC Calculator!B9/B10/B11/B15/E10` imports site type, Z, I, factor and named system references. `SCALING SUMMARY!B14/B15` imports workbook Aw-X/Y; `C14/C15` contains adopted reference T, NOT a freshly computed Rayleigh period. Each value retains spreadsheet source/sheet/cell in the audit. Workbook formulas are not recalculated by openpyxl.
- `_wall_aw_from_lines(H, lines)`: computes directional NBC §5.1.2 effective first-storey wall index from axis, plane, thickness and contiguous *net* lengths. Must not bridge disconnected pier gaps. `_wall_aw_from_patches(H,base,first,patches)`: checks the wall footprint across each vertical mesh slice and rejects changing footprints/openings rather than unioning separate heights into one fictitious effective section.
- Wall construction includes normal/axis mapping only for axis-aligned shells; rotated, discontinuous, unusual openings or source thickness gaps require independent geometry interpretation. The tool does not replace ETABS plan/detail/rebar reconciliation. The general H from nodes may be unsuitable if basements are included under NBC §5.1.2; independent check of the seismic-base convention is required.
- Rayleigh imports are matched to state, model hash, seismic weight hash and Aw. No change to the source ETABS data or original workbook is allowed.

**New checks:** `tests/verify_esm_aw_period_provenance.py` and `tests/verify_nbc105_periods.py`; synthetic regression proof only. See [full professional parameter manual](../../../review/20261105_PROFESSIONAL_STRUCTURAL_ENGINEERING_PROVENANCE_MANUAL.md). Old baseline SHA is historical, not the current source blob.
