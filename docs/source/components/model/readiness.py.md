# readiness.py — source documentation

**Python source:** [components/model/readiness.py](../../../../components/model/readiness.py)
**Git baseline content SHA:** 6ace6b1fa69fd64188eac643415cd55e08ab3ff1
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

## 2026-11-23 — exact-source selection of a readiness draft

`select_model_bound_readiness(model_script, candidates)` chooses the first valid existing JSON file in caller priority order with an exact resolved nonlinear-builder path and matching `model_script_sha256`. A generic V116 template, wrong project, changed Python source, unreadable document and absent file are not selectable. It does **not** create a replacement, reset a checklist, validate engineering approval, or modify source materials. The main model auto-selector chooses the bound V134 draft before any legacy V116 manifest. Regression: `tests/test_readiness_model_selection_20261123.py`.
