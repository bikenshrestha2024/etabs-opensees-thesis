# ETABS-linked Excel adapter — source guide

Source: [etabs_linked_excel.py](../../../../components/equivalent_static/etabs_linked_excel.py)

## Role
The ESM GUI's **ETABS Linked Equivalent Static** mode invokes `run_etabs_excel()`. It loads the user-selected original Windows ETABS NBC 105 integrated Python engine without embedding or replacing the engineering formulas. ETABS OAPI reads the existing EDB; the original calculator workbook is copied and populated, and the original engine computes the X/Y Aw, adopted T, C and k.

## Input provenance
User-selected EDB, workbook (.xlsx), legacy Python engine, separate output folder. No ETABS analysis or EDB edits and no response-spectrum scaling. Generated workbook and provenance audit contain SHA256 source identities, wall count, condition and numeric results.

## Validation
A correct Excel output is not a completed model-equivalence or NBC 105 design-acceptance check. Independently check pier/spandrel opening geometry, ULS/SLS, ETABS vs OpenSees seismic weights, modal periods and base reactions. Tests: [dual ESM adapter smoke checks](../../../../tests/verify_esm_dual_module.py).

## Engineering limitation
Original source engine and workbook are selected locally; they have not been tested in GitHub-hosted CI against the user's Windows ETABS model.

## Direct wall thickness check (2026-11-07)

`direct_wall_thickness_inventory(sap)` reads every wall-oriented area object's property and its **numeric** `PropArea.GetWall` thickness. Section names such as "Outrigger Wall 250" are never parsed. `check_excel_wall_thickness` compares each Excel `NBC Calculator!G<row>` thickness the original engine wrote against those values (0.5 mm tolerance). The result is stored in the provenance JSON as `direct_thickness_check`. A MISMATCH sets the audit status to `THICKNESS_MISMATCH_DO_NOT_USE`, and the ESM and modal windows then refuse to use that Aw.
