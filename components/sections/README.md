# Section/material/element mapping and device definitions

**Active owner:** `components/sections/` · **Current Python modules:** 7 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Source ETABS section assignments and explicit material/device input records.

**Cross-module contracts:** Shared section definitions, element tags and mapping audits for model assembly.

**Output ownership:** Reused by MODEL, solver stages and VALIDATION; not an independent source of loads.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [area_elements.py](area_elements.py)
- [definitions.py](definitions.py)
- [devices.py](devices.py)
- [library_excel.py](library_excel.py)
- [mapping_audit.py](mapping_audit.py)
- [mapping_gui.py](mapping_gui.py)
- [wall_adapters.py](wall_adapters.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/sections/` where available.
