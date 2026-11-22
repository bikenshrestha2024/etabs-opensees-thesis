# Equivalent static method (ESM) and source-linked Aw calculation

**Active owner:** `components/equivalent_static/` · **Current Python modules:** 7 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Current NBC 105:2025 code-reference inputs, matched 12 m wall geometry, EDB-linked workbook, mass and period.

**Cross-module contracts:** ESM seismic forces, base-shear ledger, MRSM scaling targets and comparison evidence.

**Output ownership:** 03_ESM; no adoption of old workbook from filename alone.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [aw_reconciliation.py](aw_reconciliation.py)
- [calculation_and_gui.py](calculation_and_gui.py)
- [code_basis.py](code_basis.py)
- [etabs_linked_excel.py](etabs_linked_excel.py)
- [evidence_bundle.py](evidence_bundle.py)
- [legacy_code_basis.py](legacy_code_basis.py)
- [organized_exports.py](organized_exports.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/equivalent_static/` where available.
