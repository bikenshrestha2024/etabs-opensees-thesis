# Modal response spectrum method (MRSM)

**Active owner:** `components/response_spectrum/` · **Current Python modules:** 5 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Verified modal evidence, NBC spectra, ESM scaling and model/state identity.

**Cross-module contracts:** Response spectrum cases and scale/response reports for design review.

**Output ownership:** 05_MRSM; require current source and ULS/SLS pairing.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [model_analysis.py](model_analysis.py)
- [nbc105_dual_target.py](nbc105_dual_target.py)
- [nbc_pair_spectrum_audit.py](nbc_pair_spectrum_audit.py)
- [reports.py](reports.py)
- [site_spectrum_and_scaling.py](site_spectrum_and_scaling.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/response_spectrum/` where available.
