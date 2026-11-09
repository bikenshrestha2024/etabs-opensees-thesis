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
