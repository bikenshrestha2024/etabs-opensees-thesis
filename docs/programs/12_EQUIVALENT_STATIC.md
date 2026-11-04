# 12 — NBC 105 equivalent static forces

**Current launcher:** [`12_EQUIVALENT_STATIC.py`](../../12_EQUIVALENT_STATIC.py)  
**Previous launcher:** [`05_EQUIVALENT_STATIC.py`](../../05_EQUIVALENT_STATIC.py) (compatibility alias)

## Goal
NBC 105 equivalent static forces. Run from the complete repository with a compatible Windows Python/OpenSeesPy environment. This entry point retains the original launcher's numerical implementation unchanged.

## Input checklist
Confirm the current export folder, validated geometry and section mapping, gravity and mass data, analysis units, selected material cards, and output destination as applicable to this subprogram. Do not mix old saved V156 exports with source modules from the new checkout.

## Execution
In Spyder open `12_EQUIVALENT_STATIC.py` and run. Alternatively from the repository root invoke `python 12_EQUIVALENT_STATIC.py`. If the script requires arguments (particularly the two diagnostic scripts), inspect the Python source usage and supply an appropriate export or failed-run folder.

## Validation and results
Review the program's actual run logs, input assumptions, generated files and solver status before interpreting engineering output. Material examples and smoke tests are not experimental calibration, and an incomplete nonlinear earthquake history must not be ranked. The building transient first-step failure remains unresolved.

[Complete run order](00_PROGRAM_INDEX.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)


## 2026-11-04 ESM Aw / period fail-closed correction

- Scaling workbook source matching uses the **portable Windows EDB stem** in `SCALING SUMMARY!B4`, not the path parser of the host OS. A known wrong EDB is excluded even if its workbook filename looks relevant. A default filename no longer bypasses this gate.
- Review both `SCALING SUMMARY!B14/B15` and the exported first-storey wall segment estimates in `NBC105_Input_Provenance_V123.xlsx`. The geometry importer now rejects **changing first-storey wall footprints with elevation**, including partial-height openings, instead of merging those projections into an overestimated automatic Aw. The geometric estimate still does not by itself verify effective pier grouping, basement H, or seismic-direction wall participation. Reconcile any mismatch with ETABS and documented NBC §5.1.2 interpretation.
- The **Use documented workbook adopted-period references** checkbox now starts **off**. A reference can be used only after explicit selection, with imported workbook Aw matching the selected directional Aw, and no unresolved conflict with the geometry estimate; this route must not be called a fresh Rayleigh calculation.
- **Both ULS and SLS:** the program now requires independently source-matched X/Y preliminary Rayleigh periods for both stiffness states. It will stop rather than silently reuse ULS periods in SLS. Where only the ULS model is available, select ULS for the audit and run the SLS modal/Rayleigh case before exporting Both. ESM ULS of a high-rise irregular building can still be a diagnostic reference only, not a permitted standalone method under §3.2.1.
- The case JSON `period_selection.selected_period_s` is written from the actual state-specific computed result, not a shared GUI display value.

Verification (synthetic only until real ETABS data are reconciled):
```powershell
python tests/verify_esm_aw_period_provenance.py
python tests/verify_nbc105_periods.py
python tests/verify_esm_input_loader.py
python tests/verify_esm_partial_input.py
python tests/verify_esm_source_selection.py
```
