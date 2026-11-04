# NBC105 ESM dialog: blank-input fix and project-data provenance (2026-11-04)

## Root causes found in current main

1. `components/equivalent_static/calculation_and_gui.py:ESMGui._load_project_inputs` passed an **undefined** `rayleigh_state` to `analysis_output_folder`. This raised `NameError` and aborted provenance export. It now uses a validated `selected_state` matching the GUI's ULS, SLS or Both selection.
2. `ESMGui._show_empirical` called `float('')` for an absent Aw. A missing workbook or wall geometry therefore broke the *whole* input refresh, rather than showing `X: needs reviewed wall Aw`. It now shows per-axis pending status and never fabricates a value.
3. The ESM GUI initially selected `NBC105_ESM_Story_Weights_Input_V108.csv`, even when the **current assembled model** had a complete `NBC105_ESM_Story_Weights_Assembled_V118.csv`. The new source selection chooses the assembled CSV only after matching count and **story-number/master-node tags** against `OpenSees_Complete_Model_Data_V118.json`. This checks mapping completeness, NOT whether the source seismic weight itself is correct.
4. Errors were previously placed only in a hard-to-see status text and swallowed by a broad `except`. The GUI now shows the import error directly, keeps the source fields blank instead of substituting zero, and offers the existing `Excel sources…` selector.

## Required input sources (do not confuse their physical meaning)

| Field | Actual import/source | Meaning and validation |
|---|---|---|
| Stories, H, diaphragm tags | Current `NBC105_ESM_Story_Weights_*.csv`, validated against current model tags | Geometry and load location only |
| Dead, storage live and other live load | Each story's `dead_load_kN`, `storage_live_load_kN`, `other_live_load_kN` | Must be reconciled with ETABS floor reactions, self-weight, wall loads, partitions and NBC seismic mass; **286448 kN total gravity load alone is insufficient** |
| Wall `Aw-X`, `Aw-Y` | Selected `SCALING SUMMARY` workbook B14/B15; optional independently calculated geometry fallback when source topology is complete | Review wall orientations, effective lengths, holes, grouping and source thickness. Do not substitute unqualified values |
| Workbook adopted periods | `SCALING SUMMARY` C14/C15 (reference only) | Not equivalent to measured eigenperiods or current Rayleigh calculation |
| Rayleigh periods | Existing case-and-source-hash checked `NBC105_Rayleigh_Preliminary_V123*.json` or explicit preliminary run | Must match actual limit state/model/seismic weights/Aw; older cache invalid |
| ETABS modal comparison periods | Live ETABS `Results.ModalParticipatingMassRatios` or clearly labeled workbook mode table | Modal comparison only. An ETABS eigenperiod does NOT replace reviewed NBC §5.1 adopted period |
| Soil `C`, `Z`, `I`, `R_mu`, `Omega_u` | Selected and verified `NBC Calculator` and source files | Do not use unrelated Soil D scaling workbook; verify actual site/hazard/dual system |

## Testing after updating GitHub

```powershell
git pull --ff-only origin main
python tests/verify_nbc105_periods.py
python tests/verify_esm_input_loader.py
python tests/verify_esm_partial_input.py
python tests/verify_esm_source_selection.py
python 12_EQUIVALENT_STATIC.py
```

In the GUI click **Excel sources…** and select the actual current model's `NBC Calculator` and `SCALING SUMMARY` workbook if not already auto-selected. Check the source provenance `NBC105_Input_Provenance_V123.xlsx` and `.json` under the current model/limit-state results folder. Before full ESM calculation verify the per-story CSV and the imported effective wall indices.

The GUI may show the expected review status of `pending Rayleigh run`. This is **correct** when the only available periods are ETABS eigenperiods or workbook-adopted references. Use **Preliminary Rayleigh run (X/Y)** for a fresh, hash-matched source calculation.

## Scientific limitation

**NBC 105:2025 §3.2.1 ESM eligibility must be independently checked for this ~95m asymmetric-plan building.** An ESM calculation can serve as a research check without proving ESM is an allowed final design analysis method. Loading/diaphragm matching and gravity reaction balance are necessary but not sufficient for source seismic weight accuracy.

Neither the ESM GUI fix nor GitHub Python CI establishes native building validation, nonlinear stability or NBC compliance.
