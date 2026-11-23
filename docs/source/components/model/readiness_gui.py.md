# readiness_gui.py — source documentation

**Python source:** [components/model/readiness_gui.py](../../../../components/model/readiness_gui.py)
**Git baseline content SHA:** 780d4cdcbf9e304eab1c28f63bad9907f2fc7a21
**Subsystem:** ETABS geometry/mass/constraint and model assembly
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the model implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R01 R02 R10 R12. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 research-vs-production material qualification

The native full-building NLTHA gate checks the model's `OpenSees_Complete_Model_Config_V118.json` for `nonlinear_parameters_reviewed`, `nonlinear_materials_file`, `nonlinear_wall_fsam_tags` and independent qualification evidence. The exploratory builder assigns a PEER-based `Research_Material_Assignment_V161.json` dynamically under a **different copied** analysis model. Its presence is not the same as a reviewed production material file and cannot sign off the original configuration.

The readiness window says `PRODUCTION MODEL ... NOT CONFIGURED` rather than generically implying no literature materials have been implemented. It offers **Create isolated PEER 2015/12 material/FSAM draft (not approval)**. The action creates a new dated copy under the analysis outputs, writes `Research_Wall_Materials.py` and `Research_Wall_Parameters.json` with full source provenance, leaves `nonlinear_parameters_reviewed=false`, does not alter the ETABS EDB or production export and explicitly warns that historical assumed two-curtain 20-mm/200-mm reinforcement is not project-reinforcement evidence.

## 2026-11-23 — evidence suggestions, reviewer metadata and local index

`available_evidence(model_script)` continues returning historical GUI hint text; `with_metadata=True` additionally provides structured source paths for local indexing. `evidence_inventory(model_script)` creates a read-only per-check source inventory with the exact builder SHA, serialized source-model SHA (when available), each candidate file SHA/size and, for saved modal files, source-model identity label. `MATCHING_SERIALIZED_MODEL` is only a source JSON hash match, **not** model equivalence, nonlinear material validation or an engineering PASS. The index always states approved_for_nltha=false. Exporting this report uses a user-chosen local path; no connector or web upload is performed.

The editor separates read-only `AVAILABLE FOR REVIEW` suggestions from independent reviewer-cited references. `review_metadata_problems` checks an explicitly ticked item for a non-placeholder reference, named reviewer and actual ISO date. Review metadata is saved in `review_metadata` in the model-bound JSON, but the review flags are never inferred from filenames/metadata and the 16 physical checks remain user decisions. Unchecked items do not require reviewer metadata. The existing backend's source binding and actual materials/FSAM requirements are unchanged.
