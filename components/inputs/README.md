# Source files, project provenance and output contracts

**Active owner:** `components/inputs/` · **Current Python modules:** 18 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Exact EDB, analyzed/assignment/beam-force exports, ULS/SLS identity and two verified 12 m X-wall grouping.

**Cross-module contracts:** Manifest-bound, SHA-verified source selection for model building, seismic calculations and all analysis stages.

**Output ownership:** 01_ETABS_EXPORT / 00_SOURCE_MANIFEST; diagnostic results in 09_SOFTWARE_DIAGNOSTICS.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [analysis_autofill.py](analysis_autofill.py)
- [aw_sources.py](aw_sources.py)
- [etabs_excel_selection.py](etabs_excel_selection.py)
- [etabs_periods.py](etabs_periods.py)
- [etabs_table_bundle.py](etabs_table_bundle.py)
- [export_mirror.py](export_mirror.py)
- [folder_audit.py](folder_audit.py)
- [gravity_evidence_stage.py](gravity_evidence_stage.py)
- [grouped_wall_aw.py](grouped_wall_aw.py)
- [lfs_workbook_recovery.py](lfs_workbook_recovery.py)
- [model_aligned_reference.py](model_aligned_reference.py)
- [opensees_nbc_sync.py](opensees_nbc_sync.py)
- [output_contract.py](output_contract.py)
- [output_layout.py](output_layout.py)
- [pair_selection.py](pair_selection.py)
- [project_output_layout.py](project_output_layout.py)
- [project_workbooks.py](project_workbooks.py)
- [records.py](records.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/inputs/` where available.
