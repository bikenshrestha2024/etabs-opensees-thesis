# ETABS/OpenSees independent comparison and engineering review

**Active owner:** `components/validation/` · **Current Python modules:** 46 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Matching original EDB, source results, native stiffness, model SHA, supports, local axes and load cases.

**Cross-module contracts:** Gravity/ESM/MRSM/time-history pointwise and global discrepancies, traceable review evidence.

**Output ownership:** 08_ETABS_COMPARISONS and stage-owned 05_COMPARISONS.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [case_review.py](case_review.py)
- [design_checks.py](design_checks.py)
- [eq_pdelta_case_contract.py](eq_pdelta_case_contract.py)
- [eq_pdelta_comparison.py](eq_pdelta_comparison.py)
- [eq_pdelta_evidence.py](eq_pdelta_evidence.py)
- [etabs_assignment_gravity_audit.py](etabs_assignment_gravity_audit.py)
- [etabs_comparison.py](etabs_comparison.py)
- [etabs_direct_api.py](etabs_direct_api.py)
- [etabs_eq_pdelta_native_extract.py](etabs_eq_pdelta_native_extract.py)
- [etabs_equivalence_report.py](etabs_equivalence_report.py)
- [etabs_floor_end_api.py](etabs_floor_end_api.py)
- [etabs_beam_force_shards.py](etabs_beam_force_shards.py)
- [etabs_lot_consistency.py](etabs_lot_consistency.py)
- [etabs_native_quantity_tables.py](etabs_native_quantity_tables.py)
- [etabs_split_beam_forces.py](etabs_split_beam_forces.py)
- [expanded_workbench_tabs.py](expanded_workbench_tabs.py)
- [floor_end_extraction.py](floor_end_extraction.py)
- [grade_cards.py](grade_cards.py)
- [gravity_etabs_direct.py](gravity_etabs_direct.py)
- [gravity_etabs_latest.py](gravity_etabs_latest.py)
- [gravity_etabs_offline.py](gravity_etabs_offline.py)
- [gravity_native_equivalence_preflight.py](gravity_native_equivalence_preflight.py)
- [gravity_node_comparison.py](gravity_node_comparison.py)
- [gravity_reactions_3d.py](gravity_reactions_3d.py)
- [irregularity_review.py](irregularity_review.py)
- [material_benchmarks.py](material_benchmarks.py)
- [material_catalog.py](material_catalog.py)
- [material_sensitivity.py](material_sensitivity.py)
- [nonlinear_performance.py](nonlinear_performance.py)
- [parameter_gui.py](parameter_gui.py)
- [parameter_studies.py](parameter_studies.py)
- [reaction_common_cut.py](reaction_common_cut.py)
- [reference_library.py](reference_library.py)
- [research_results_gui.py](research_results_gui.py)
- [response_checks.py](response_checks.py)
- [response_inventory.py](response_inventory.py)
- [result_interpretation.py](result_interpretation.py)
- [saved_case_identity.py](saved_case_identity.py)
- [saved_stiffness.py](saved_stiffness.py)
- [seismic_review_bundle.py](seismic_review_bundle.py)
- [settings_audit.py](settings_audit.py)
- [sfi_worker.py](sfi_worker.py)
- [steel_calibration_gui.py](steel_calibration_gui.py)
- [thesis_evidence_dashboard.py](thesis_evidence_dashboard.py)
- [torsion_check.py](torsion_check.py)
- [visual_materials.py](visual_materials.py)
- [visual_workbench.py](visual_workbench.py)
- [wall_validation.py](wall_validation.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/validation/` where available.
