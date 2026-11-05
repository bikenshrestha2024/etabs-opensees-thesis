# calculation_and_gui.py — source documentation

**Python source:** [components/equivalent_static/calculation_and_gui.py](../../../../components/equivalent_static/calculation_and_gui.py)
**Git baseline content SHA:** 13bafcf41eeb52944a564cb9f1b248f269a7a2a5
**Subsystem:** NBC 105 equivalent-static analysis
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the equivalent_static implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## 2026-11-04 missing-value diagnosis

The ESM initialization previously referenced an undefined `rayleigh_state`; now validates and uses the actual GUI state. The `_show_empirical` display must tolerate unavailable Aw and leave periods pending rather than aborting the whole project input load. `recommended_story_weight_input` prefers a populated assembled ledger only when current diaphragm IDs match the model. Existing manually reviewed CSV choices remain supported. [Full ESM blank-input diagnosis and tests](../../../00_ESM_INPUT_IMPORT_BLANK_FIX.md).


## Period adoption and GUI contract (2026-11-05)

- `resolve_esm_state_periods(height_m,aw_by_axis,factor,states,rayleigh_by_state)`: selects the *matching limit-state* X and Y periods as min(calculated Rayleigh period, amplified `0.075H^.75/sqrt(Aw)`). Strict units: H [m], Aw [m²], period [s]. A `Both` state request fails if separate SLS Rayleigh evidence is absent, rather than silently reusing ULS stiffness-period values.
- `ESMGui._adopted_axis_period`: workbook adopted-period reference is now *opt-in* and is never labelled a native Rayleigh result; verifies selected Aw against the imported workbook Aw and, when available, independent exported geometry. A mismatched workbook value or reference beyond 1.25 empirical is rejected.
- `recommended_story_weight_input`: prefers model-tag-matched assembled story CSV, retaining the historical manual-CSV override. Story weights and effective wall areas are physical inputs requiring ETABS verification: source correctness is not implied by tag equality.
- `ESMGui._calculate`: if Both ULS/SLS, retrieve separate hash-checked state periods and write `result.period_s` into per-case `period_selection`; preserve X/Y, ± sign and eccentricity cases. The ULS ESM for a tall irregular building is diagnostic only where §3.2.1 does not permit static design.
- §6.5 Table 6-1 permits deflection factor 0.85 for 6+ storeys; it does **not** authorize scaling of MRSM drift/displacement by the §7.5 member-force factor.

All automatic calculations must report source model hash, source wall opening interpretation, seismic base and load-path reconciliation. Do not claim native ETABS reproduction until outputs are independently compared. See [parameter manual](../../../review/20261105_PROFESSIONAL_STRUCTURAL_ENGINEERING_PROVENANCE_MANUAL.md).
