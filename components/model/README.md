# Structural model and physical load assembly

**Active owner:** `components/model/` · **Current Python modules:** 24 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Source model geometry, sections, material modifiers, loads, offsets, diaphragms, supports and EDB identity.

**Cross-module contracts:** Gravity, Modal, ESM, MRSM, LTHA, NLTHA and validation consumers.

**Output ownership:** 02_MODEL; model/config/source files must retain immutable identity.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [analysis_basis.py](analysis_basis.py)
- [assembly.py](assembly.py)
- [beam_weight_convention.py](beam_weight_convention.py)
- [display_ids.py](display_ids.py)
- [elastic_conversion_settings.py](elastic_conversion_settings.py)
- [eq_pdelta_initial_tangent.py](eq_pdelta_initial_tangent.py)
- [id_audit.py](id_audit.py)
- [initial_pdelta.py](initial_pdelta.py)
- [joint_volume_ownership.py](joint_volume_ownership.py)
- [linear_shell_stiffness.py](linear_shell_stiffness.py)
- [load_accounting.py](load_accounting.py)
- [load_and_diaphragm_audit.py](load_and_diaphragm_audit.py)
- [load_case_purpose.py](load_case_purpose.py)
- [nonlinear_preflight.py](nonlinear_preflight.py)
- [physical_weight_modifiers.py](physical_weight_modifiers.py)
- [readiness.py](readiness.py)
- [readiness_dashboard.py](readiness_dashboard.py)
- [readiness_dashboard_gui.py](readiness_dashboard_gui.py)
- [readiness_gui.py](readiness_gui.py)
- [reinforcement_mapping.py](reinforcement_mapping.py)
- [section_tags.py](section_tags.py)
- [single_count_self_weight.py](single_count_self_weight.py)
- [source_node_identity.py](source_node_identity.py)
- [support_case_contract.py](support_case_contract.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/model/` where available.
