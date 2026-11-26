# NBC 105:2025 reference rules (Clauses 1–10, Annex A/B)

**Active owner:** `components/nbc105/` · **Current Python modules:** 18 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Current officially adopted standard and verified project geometry/material/soil/state inputs.

**Cross-module contracts:** Reference-only calculations and clause/annex coverage evidence; not signed building approval.

**Output ownership:** 09_SOFTWARE_DIAGNOSTICS for compliance evidence; consumes verified SOURCE_INPUTS.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [__init__.py](__init__.py)
- [__main__.py](__main__.py)
- [acceptance.py](acceptance.py)
- [annex_a_rc_detailing.py](annex_a_rc_detailing.py)
- [annex_b_steel_detailing.py](annex_b_steel_detailing.py)
- [clause_01_scope_definitions.py](clause_01_scope_definitions.py)
- [clause_02_general_principles.py](clause_02_general_principles.py)
- [clause_03_scope_of_analysis.py](clause_03_scope_of_analysis.py)
- [clause_04_seismic_hazard.py](clause_04_seismic_hazard.py)
- [clause_05_dynamic_characteristics.py](clause_05_dynamic_characteristics.py)
- [clause_06_equivalent_static.py](clause_06_equivalent_static.py)
- [clause_07_modal_response_spectrum.py](clause_07_modal_response_spectrum.py)
- [clause_08_elastic_time_history.py](clause_08_elastic_time_history.py)
- [clause_09_nonlinear_analysis.py](clause_09_nonlinear_analysis.py)
- [clause_10_parts_and_components.py](clause_10_parts_and_components.py)
- [compliance_coverage.py](compliance_coverage.py)
- [constants.py](constants.py)
- [normative_register.py](normative_register.py)
- [clause_07_missing_mass.py](clause_07_missing_mass.py)
- [annex_c_zoning.py](annex_c_zoning.py)
- [dispatch.py](dispatch.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/nbc105/` where available.
