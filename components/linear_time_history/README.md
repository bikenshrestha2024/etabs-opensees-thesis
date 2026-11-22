# Linear time-history analysis

**Active owner:** `components/linear_time_history/` · **Current Python modules:** 1 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Model/mass/damping, verified motions and source-aligned gravity preload.

**Cross-module contracts:** Linear transient response and evidence for comparisons.

**Output ownership:** 06_LINEAR_TIME_HISTORY; every run gets an immutable manifest.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [runner_and_gui.py](runner_and_gui.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/linear_time_history/` where available.
