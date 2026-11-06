# ESM source geometry can prefill diagnostic Aw for openings

**2026-11-06 Windows screenshot issue:** clicking `Sync from OpenSees model` left Aw-X and Aw-Y empty because first-storey wall shell segments differed across elevation slices. The read-only ETABS fallback independently reported the same nonuniform footprint. Gravity load ~286447.790 kN and reactions ~286447.789 kN converged but do not determine NBC Aw.

## New computational behavior

The converter already computes every first-storey horizontal wall section from the current model, with actual plane, thickness, mesh-element physical length and z bounds. This change **intersects the merged wall-length intervals at each successive elevation** for each (axis, plane, thickness). Only the projection that physically exists in every one of the first-storey height slices is included as a potential **full-height continuous pier**.

For each eligible axis, the CLI and GUI now expose a positive `PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC` geometric Aw and set the formerly blank Aw box to its computed number. X and Y are computed separately using actual current-export geometry. If one direction has no through-height pier, that axis **remains blank**; no generic default, unrelated workbook, or fabricated value is permitted.

These numbers support *preliminary research comparisons and input diagnostics* only. **They are NOT approved NBC 105:2025 §5.1.2 effective Aw:** a perforated RC wall may have coupled pier/spandrel action, and a source-geometry intersection does not validate effective length grouping or code acceptance. The conservative geometric subset is not a certified lower bound on actual demand or a substitute for the full perforated-core structure. Review the actual wall elevation and physical pier grouping before issuing ULS/SLS design findings.

## Output / verification

- `NBC105_OpenSees_Input_Sync.json`: `aw_candidate_m2`, `aw_evidence[X/Y].status`, `code_accepted=false`, per-elevation source segments and `continuous_pier_diagnostic` with full-height segments.
- `NBC105_OpenSees_Input_Sync.xlsx`: newly generated workbook with nonuniform slices and **continuous-through-height candidate segments**, plus source and candidate status; no overwriting original NBC calculator, response-spectrum scale or source EDB.
- ESM GUI: positive source-derived candidates prefill Aw fields with a prominent **DIAGNOSTIC ONLY** status; exported ESM result metadata records each source classification and `wall_aw_code_accepted=false`. The pre-existing Rayleigh calculation uses these input values only as a separately labelled preliminary diagnostic, not design compliance.
- Repeated use without a native source model gives no hard-coded numbers. The historical scaling workbook with header strings in B15/C15/E7 remains invalid.

## Windows local procedure

1. Update repository: `git pull --ff-only origin main`. Close/reopen the main converter + ESM dialog.
2. Select the exact Ultimate→ULS export, and click `Sync from OpenSees model`. Confirm nonblank candidate values for X/Y, each labelled `PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC`. If no full-height projection exists for an axis, it will explicitly remain blocked.
3. Inspect newly created `NBC105_OpenSees_Input_Sync.xlsx` and `.json`. The `continuous_pier_diagnostic` section identifies each actual projected interval.
4. If geometry candidates are meaningful for a **preliminary diagnostic**, click `Preliminary Rayleigh run (X/Y)` to obtain actual directional OpenSees Rayleigh periods. Its convergence and source-state/mass hashes still need review.
5. Before **NBC code acceptance**, independently verify first-storey wall openings, piers, spandrels, coupling, dimension `H`, boundary zones and §5.1.2 directional effective area. Enter those reviewed effective areas and rerun Rayleigh/ESM. For an asymmetric high-rise, retain ESM ULS as diagnostic where §3.2.1 requires a dynamic design method.

## Limitations

No private EDB, current exported wall slice JSON, or native OpenSees analysis was available for executing this actual building. A software-generated candidate is not guaranteed to be nonblank in both axes; it can only fill if actual wall material is continuous through all first-storey slices. Numeric project-specific values are intentionally not guessed.

**Tests:** `tests/verify_esm_continuous_pier_diagnostic.py` and `tests/verify_opensees_first_nbc_sync.py`. Existing geometry uniform and source mismatch tests remain mandatory.
