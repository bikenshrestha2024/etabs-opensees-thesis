# 2026-11-06 engineering decision — Excel effective wall area is authoritative

## Decision
For the current ETABS-to-OpenSeesPy NBC 105:2025 Equivalent Static Method (ESM), use the user's existing Excel effective-wall-area calculation, including its wall-opening and pier-grouping treatment. **Do not** silently substitute a shell-mesh geometric index for the Excel Aw.

## Executable source mapping
- Import: `components/inputs/project_workbooks.py::import_project_inputs`.
- Source: a source-verified calculation workbook with `SCALING SUMMARY`.
- `Aw-X`: labelled X effective-wall-area row (historically `B14`).
- `Aw-Y`: labelled Y effective-wall-area row (historically `B15`).
- Period references (not independent Rayleigh evidence): historically `C14` and `C15`.
- Model identity: source EDB recorded in the workbook, conventionally `B4`, cross-checked against the export's source EDB or byte-identical file.
- XLSX cached results: `openpyxl.load_workbook(data_only=True)` does **not** calculate formulas. Recalculate/save in Excel if the cached numeric cells are blank or stale.

## Implementation rule
If the workbook is verified and yields finite positive X/Y values, these directly populate `values['awx']` and `values['awy']`, retaining field/source/sheet/cell in `audit`. If there is no valid workbook Aw, leave the respective effective-area value absent, explain why, and require workbook selection or reviewed manual input. Do not assign `geometry_aw_x` or `geometry_aw_y` as a fallback to `awx`/`awy`.

The independent OpenSees wall-profile analysis may still generate `geometry_aw_x/y`, first-storey elevation slices and segment diagnostics. A disagreement is logged, **not resolved by automatic replacement**. For nonuniform wall profiles or openings, the geometric index is not an approved substitute for pier grouping from the Excel method.

## Engineering verification still required
1. Review the exact current ULS/SLS Excel file and ETABS source model identity separately.
2. Audit opening sizes, wall-pier lengths, wall above openings and height/first-storey definition against the Excel logic and NBC 105:2025 section 5.1.2.
3. Check correct units and period formula usage; distinguish independently calculated Rayleigh T from workbook period references.
4. Compare source-matched workbook values and model geometry, retaining discrepancies as open issues. A numerically converged gravity/model run is not code acceptance.

## Commit scope
This is an **input-precedence and traceability** correction, not a change to nonlinear wall material parameters, NLTHA solver convergence, or certified seismic design.
