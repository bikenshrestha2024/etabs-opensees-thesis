# Gravity solver, 32/76/97 supports and native reaction evidence

**Active owner:** `components/gravity/` · **Current Python modules:** 19 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Source-matched assembled model and complete 1.0D+1.0L load ledger; selected support policy.

**Cross-module contracts:** Verified saved-case registry and comparison of local reactions with ETABS.

**Output ownership:** 02_GRAVITY; 32/76/97 remain separate runs; global equilibrium is not pointwise ETABS equivalence.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [comparison_bundle.py](comparison_bundle.py)
- [etabs_reaction_support_filter.py](etabs_reaction_support_filter.py)
- [evidence_workflow.py](evidence_workflow.py)
- [gui_and_reports.py](gui_and_reports.py)
- [joint_overlap_review.py](joint_overlap_review.py)
- [joint_weight_reconciliation.py](joint_weight_reconciliation.py)
- [load_path_formulas.py](load_path_formulas.py)
- [load_review.py](load_review.py)
- [mesh_cases.py](mesh_cases.py)
- [output_ownership.py](output_ownership.py)
- [reaction_case_registry.py](reaction_case_registry.py)
- [slab_self_weight_audit.py](slab_self_weight_audit.py)
- [solver_stack.py](solver_stack.py)
- [source_load_reconciliation.py](source_load_reconciliation.py)
- [storey_loads.py](storey_loads.py)
- [support_scenarios.py](support_scenarios.py)
- [three_case_comparison.py](three_case_comparison.py)
- [validation_scorecard.py](validation_scorecard.py)
- [workbook_publishing.py](workbook_publishing.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/gravity/` where available.
