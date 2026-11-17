# Root-cause investigation: ~28-minute ETABS conversion (2026-11-17)

## Source and evidence

Original private ETABS conversion worker log for 2026-11-16, source EDB SHA256 `8d09a2367fcdf17f969c77226d17a8668ab7989122aea59f6328aabbca9434bc`, output root `.../ETABS 11-16-2026/3`. Do not commit the original ETABS EDB or private source data.

| Stage | Recorded duration |
| --- | ---: |
| ETABS source extraction | 16.64 s |
| Interactive 3D / floor-plan source views | 2.78 s |
| ETABS source metadata | 2.251 s |
| **Storey gravity classification AND workbook** | **1614.536 s** |
| Load-path and diaphragm assembly audit | 0.133 s |
| Mapping/load audit workbook | 5.024 s |
| Model assembly and export | **1628.883 s** |
| Total converter | **1656.46 s** |

The gravity/workbook combined stage accounts for **99.12% of model assembly**. Measured 4x4 export: 3862 frame segments, 10400 shell cells, 25 storeys, 76 source supports, applied seismic preload 286419.758231 kN; `assembly_errors=[]`. These are *source-run log facts*, not independently rerun solver evidence.

## Precise code cause

`components/model/assembly.py::prepare_complete_export` synchronously calls `components/gravity/storey_loads.py::export_storey_gravity`. That routine:

1. Classifies precise source nodal gravity contributions and checks numerical equilibrium.
2. Writes storey-level and per-source CSV/JSON.
3. **Also** generates `Gravity_Storey_Load_Breakdown_V131.xlsx`, calls `components/gravity/load_path_formulas.py::add_formula_audit`, and blocks until `openpyxl` finishes constructing and serializing many mesh-cell surface and four-node load-path formula records. It additionally duplicates the surface pressure sheet for the seismic-preload view and creates cross-sheet SUMIFS formulas.
4. The original `ws.columns` width calculation iterated every cell of each populated source sheet just to size header columns.

The worker log only measures step (1–3) as a combined 1614.536 s, so it does NOT identify the exact internal fraction consumed by worksheet construction vs serialization. The new explicit `[OPTIONAL EXCEL START/DONE]` markers isolate those substeps when the workbook is generated separately.

## Model-preserving correction

Mandatory import retains **all numerical model construction**, exact source loads, gravity load and mass factors, 4x4 ShellMITC4 grid, source ID crosswalk, member offsets and all 32/76/97 support review cases. Gravity ledger classification, its reconciled source totals, CSV and JSON are still required; failure remains an engineering failure.

The heavy **human-facing spreadsheet** is now deferred by default; normal import writes `Gravity_Storey_Workbook_Status_V131.json` and emits an explicit `FORMULA_XLSX=DEFERRED` log marker. A previous same-name XLSX is preserved under `09_SOFTWARE_DIAGNOSTICS/DEFERRED_GRAVITY_WORKBOOKS/`, not presented as current evidence. The existing source config may explicitly set `export_gravity_formula_workbook_on_import=true` for legacy behavior.

After model assembly, use the Gravity & NBC GUI action **Generate detailed storey-gravity Excel from saved model (no ETABS)** or:

```powershell
python -m components.gravity.storey_loads --workbook "D:\Thesis Opensees\ETABS 11-16-2026\4"
```

This checks complete export report, original model/config SHA, no assembly errors and source load audit before generating detailed Excel using saved arrays. No ETABS OAPI, OpenSees solver, remeshing, changed supports or load redistribution is involved. The workbook still may be slow, but it no longer blocks conversion and engineering checks. The separate user-requested Slab Load Path / MESH_04 workbook workflow remains unchanged.

## Acceptance gates / remaining risk

1. Run identical EDB SHA and `floor_subdivisions=4` in fresh output. Compare stage timings against the precise recorded baseline. Accept a throughput improvement only with measured Windows elapsed time.
2. Confirm both runs have the same frame segment and shell cell counts, source loading patterns, total gravity and seismic mass factors; no engineering tolerance is relaxed.
3. Inspect `Gravity_Storey_Workbook_Status_V131.json`: deferred is not a failure; XLSX absence must never be silently interpreted as missing model.
4. Compare new mandatory `Gravity_Storey_Load_Breakdown_V131.json` and `Gravity_Source_Load_Detail_V131.csv` to baseline (source IDs, pattern classification, values and reconciliation) and ensure original support configurations remain unchanged.
5. Test separate full XLSX generation; ensure 4x4 pressure cells, per-node load paths, sheet overflow logic and source IDs remain complete. Record workbook expansion versus serialization timing separately.
6. Regression suite: `tests/test_deferred_storey_workbook.py`; GitHub CI can verify logical and artifact contracts, but cannot assert Windows ETABS performance or native structural equivalence.

**Important**: This resolves the **code-level blocking dependency** responsible for the 28-minute import stage. Restoring the historical ~5-minute wall-clock time is plausible, not yet measured on the user's machine. Gravity joint-reaction discrepancies remain a separate unresolved engineering-validation issue.
