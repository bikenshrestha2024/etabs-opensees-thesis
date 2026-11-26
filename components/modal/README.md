# Modal/Rayleigh analysis and directional periods

**Active owner:** `components/modal/` · **Current Python modules:** 7 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Source-model stiffness/mass/constraints and gravity state where applicable.

**Cross-module contracts:** Mode shapes, participation, frequencies and independent Rayleigh evidence for ESM/MRSM/time history.

**Output ownership:** 04_MODAL; adopted design period is not automatically an eigenperiod.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [analysis.py](analysis.py)
- [gui_and_reports.py](gui_and_reports.py)
- [nbc105_clause5.py](nbc105_clause5.py)
- [rayleigh.py](rayleigh.py)
- [rayleigh_ledger_audit.py](rayleigh_ledger_audit.py)
- [rayleigh_mass_audit.py](rayleigh_mass_audit.py)
- [storey_mass_convention.py](storey_mass_convention.py)
- [rayleigh_xy_evidence.py](rayleigh_xy_evidence.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/modal/` where available.
