# Solver-independent shared utilities and runtime conventions

**Active owner:** `components/shared/` · **Current Python modules:** 8 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Explicit model/load/solver inputs from module callers.

**Cross-module contracts:** Reusable eigen, transient, timing, response and status helpers.

**Output ownership:** No standalone results root; callers own their stages and evidence.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [case_status.py](case_status.py)
- [eigen_solver.py](eigen_solver.py)
- [gravity_transient_handoff.py](gravity_transient_handoff.py)
- [legacy_solver_stack.py](legacy_solver_stack.py)
- [response_recorders.py](response_recorders.py)
- [runtime_utilities.py](runtime_utilities.py)
- [timing.py](timing.py)
- [transient_runtime.py](transient_runtime.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/shared/` where available.
