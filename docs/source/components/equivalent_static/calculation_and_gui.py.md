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


### 2026-11-05 bounded review — sidecar path and per-state metadata

Source review of `_calculate` identified an unverified/blank `model_script` path previously resolving to current working directory when writing `OpenSees_Initial_PDelta_Input_V124.json`. The new `validated_pdelta_sidecar_path` returns a target **only** for an explicitly selected existing `.py` script, preserving the legacy filename and sidecar location for valid working cases. ESM standalone computations remain usable, but they do not emit a P-Delta model sidecar absent a real model path.

A separate mismatch existed when a combined SLS case used its SLS period `result.period_s` but the output `period_selection.Rayleigh_T1_X_s/Y_s` described the ULS GUI periods. `state_rayleigh_provenance` now attaches the matching SLS imported evidence to SLS outputs and labels the evidence state. These are program integrity corrections, not proof that source modal/period properties are physically correct.

Regressions: `tests/verify_esm_output_safety.py` (seven synthetic tests). No native ETABS comparison is asserted.


## 2026-11-12 complete §6 calculation audit added to every generated direct ESM workbook

`write_outputs` now includes `NBC 5-6 Derivation` with the source-period, Ch, Z, I, C(T), Cs(T), Rmu, Ωu, Ωs, Cd(T1), W, V, k, distribution denominator, full floor force sum and V–ΣFi. It also states force polarity, eccentricity and that P–Delta initial/final physical response remains independently gated. `Storey Formula Audit` lists each source-story `Wi,hi,Wi*hi^k,normalized fraction, Fi, cumulative applied force` and source master node. This is distinct from physical recovered floor shears; original direct ESM JSON and CSV still record individual floor forces.

**This does not recalculate or alter the original ETABS-linked Excel engine.** That historical workbook preserves the older X=1.9582936m² four-6m interpretation. On verified `EXPORT_NODE_GEOMETRY_MATCHED_12M_X_WALL_POLICY`, the GUI now creates a **separate** `*_GROUPED_WALL_REVIEW.xlsx` beside the generated ETABS-linked workbook, recording historical X and verified two-12m X (2.0731745m²), respective Y, the discrepancy and actual source SHA. The original ETABS-linked generated workbook is unchanged (its registered hash remains meaningful); the grouped review is **research source-matched, not NBC structural acceptance**. If source verification fails, no new alternative wall area is silently created. This helper runs in Windows with existing OpenPyXL dependency; do not commit project-owned XLSX to the public repository.

Synthetic arithmetic regressions: `tests/test_esm_section6_arithmetic.py` (ULS/SLS Ch, C, Cd, W, V, k, floor sum). Physical native EDB tests still outstanding.


## 2026-11-12 source-period labels and export status

Historical workbook adopted periods are now explicitly labelled **reference only**, distinct from the current computed §5.1.1 OpenSees Rayleigh period and §5.1.3 minimum adopted design period. Importing the original workbook no longer automatically checks the advanced `use_workbook_periods` fallback. User opt-in remains possible for explicitly labelled historical research when current Rayleigh evidence is absent; source state/matching constraints are unchanged. For the 2026-11-12 run: historical workbook X≈2.0385674s differs from current adopted X≈1.9812809s, and historical Y≈1.9219798s matches coincidentally.

The GUI button names now explicitly show `Complete ESM export ZIP (all evidence)` and verified comparison action. The pre-existing status bar now reports ZIP **EXPORTING / EXPORTED / FAILED** distinctly, rather than the only proof being a log line. Packaging status is not native solver acceptance.
