# gui_and_reports.py — source documentation

**Python source:** [components/gravity/gui_and_reports.py](../../../../components/gravity/gui_and_reports.py)
**Git baseline content SHA:** 05de2fb0d5a91641fb4ea9ddb5ef7e0edb45d4b3
**Subsystem:** Gravity-load and support equilibration
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the gravity implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
The selected output root contains `Gravity_Case_Reaction_Index.json` and
`Gravity_Output_Index.txt`. `_selected_result_path` verifies the selected model,
load profile and support condition before PDF export, direct ETABS comparison or
manual evidence packaging. Nested diagnostic and batch results are consumed at
their actual paths. Missing or stale cases produce an explicit message instead of
substituting another condition.

Run controls occupy the first action row, with the selected profile and support
strategy visible; report/comparison tools occupy the second row. Both run buttons
are disabled during a run. `GRAVITY_CASE_START`, `GRAVITY_CASE_COMPLETED` and
`DUAL_GRAVITY_DONE` distinguish solver completion, source-load reconciliation and
ETABS validation status. Dialog line breaks use actual newlines.

Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-12 verified support-case default and labels

**Revised gravity diagnostic GUI default (at author's explicit request): `32 nonzero-reaction nodes (diagnostic)`**; underlying solver mode is `ETABS_NONZERO_REACTION_DIAGNOSTIC`. This is NOT an equivalent ETABS analysis-mesh representation; the separate modal/MRSM/TH production baseline continues using exported `ETABS_SOURCE_SUPPORTS` with 76 source-point restraints until native ETABS auto-mesh and interpolation constraints are independently matched. The 32-node menu is now `32 nonzero-reaction nodes (diagnostic)` (`ETABS_NONZERO_REACTION_DIAGNOSTIC`); it **releases 44 originally restrained source-export wall-base nodes**, even if the exported ETABS gravity case shows zero reactions there. The 97-node option is labeled `97 wall-base idealization (sensitivity)` (`CONTINUOUS_WALL_BASE_FIXED`) and **adds 21 new fixed wall-base mesh nodes**, not assumed source EDB restraints. Previously saved display labels and all stable solver IDs remain backward compatible.

This GUI change does not change a source EDB, exported mesh, support stiffness, physical load or an old solver run. For a new analysis, it changes the selected **boundary-condition case** by default to the one closest to the exported source restraint DOFs; native ETABS actual analysis meshing and DOF propagation still require confirmation. The 32/76/97 source review and original data are recorded in [20261112_32_76_97_SUPPORT_AND_LOAD_PATH_REVIEW.md](../../../../REVIEW_MAIN/01_GRAVITY/20261112_32_76_97_SUPPORT_AND_LOAD_PATH_REVIEW.md).

**Validation:** `sum(Rz) = applied` for each completed run only demonstrates internal gravity equilibrium. It does not demonstrate that all support reactions are individually comparable. For the uploaded 2026-11-12 reference solve the 44 formerly restrained nodes carry 104,463.013534 kN in the 76 case and the new 21 fixed nodes carry 30,032.220953 kN in the 97 case. These are not negligible reaction transfers.

## 2026-11-12 mesh-node mechanics correction

The initial 76-node gravity GUI default was too definitive because actual ETABS wall auto-mesh may propagate source restraints and may enforce multi-master edge interpolation. Conversely, the user's 32 original reaction-bearing nodes are not necessarily a complete mesh boundary-value problem. **32 is only the requested default screening case in this GUI**, not a source-validated substitute for all modes. See [mesh support + slab load-path validation](../../../../REVIEW_MAIN/01_GRAVITY/20261112_MESH_SUPPORT_AND_SLAB_TRANSFER_VALIDATION.md). No source node, beam, shell or restraint data is deleted.
