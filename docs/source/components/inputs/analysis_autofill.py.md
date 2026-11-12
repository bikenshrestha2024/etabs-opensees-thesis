# analysis_autofill.py — source documentation

**Python source:** [components/inputs/analysis_autofill.py](../../../../components/inputs/analysis_autofill.py)
**Git baseline content SHA:** b8d4f27b0f546a20f5caba2b10f677ae30396f4e
**Subsystem:** ETABS/source inputs and earthquake motions
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the inputs implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-12 modal source validity gate

`populate_linear` now **does not auto-populate** elastic-modal TnX/TnY nor Rayleigh damping P1/P2 when any of source-model SHA256, ULS/SLS limit-state or supported numerical implementation fingerprint mismatches. It logs which source was rejected, instructs a matching modal run and reminds the user that the *nonlinear* initial-tangent eigenmodel is an independent check.

For a matching source, imported TnX/TnY come only from the first `NBC105_Modal_V111.json` modal row whose cumulative directional mass reaches ≥90%; the selected mode number and mass percentage are logged. They are explicitly labeled elastic-modal references. If 90% is not reached, keep that field empty and **never** substitute the last inspected eigenmode.

Separately, workbook adopted empirical/Rayleigh T1 values remain NBC-design-period references and are **not** used as material-dependent nonlinear initial modal T1 nor assumed damping reference eigenperiods.
