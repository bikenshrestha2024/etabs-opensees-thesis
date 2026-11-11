# Windows retest — conversion LFS prompt, gravity setup identity and empty output directory
Status: CODE FIX COMMITTED; NATIVE WINDOWS RETEST REQUIRED
Date: 2026-11-11

## User evidence
- Main conversion GUI V161 still showed an original-workbook selector for `etabs_full_table` Git LFS pointer even though this large export is required only for native Gravity validation.
- Embedded Matplotlib plot lacked a direct declaration of whether plotted reactions/displacements used primary 32, source 76 or wall-base 97 supports.
- Numbered `02_GRAVITY` directory was empty while legacy `OpenSees_Analysis_Results/ULS_Floor_3_.../Gravity_Reaction_Diagnostic` and `Gravity_Wall_Base_Comparison` folders contained output.

## Evidence ZIP findings (Gravity_Review_UPLOAD(2).zip)
Verified (source file `Gravity/Analysis/Gravity_Case_Reaction_Index.json`):
- 32-support `ETABS_NONZERO_REACTION_DIAGNOSTIC`: applied/summed 311367.314 kN.
- 76-support `ETABS_SOURCE_SUPPORTS`: applied/summed 311367.314 kN.
- 97-support `CONTINUOUS_WALL_BASE_FIXED`: applied/summed 311367.314 kN.
- All three are `GRAVITY_1.0D_1.0L` and report numerical equilibrium.
- All three case fingerprints point to the same verified-clear-beam generated model, but differ in restraint sets.
- `GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json` records `engineering_acceptance: NOT_VALIDATED`, 44 originally restrained nodes released in primary32, and outstanding rigid-end-zone equivalence checks.
- Successful equilibrium does NOT certify nodal ETABS reactions or stiffness equivalence.

## Root cause and changes
1. `components/ui/application.py` no longer invokes the main workbook preflight; however, `copy_project_workbooks()` invoked `registered_project_source()`, and that resolver still ran the interactive `select_original_workbook_for_registered_pointer()` path on the registered full-table LFS placeholder. The resolver now supports `missing_lfs='skip'` only for optional workbook propagation. Explicit native source resolution defaults to strict noninteractive error and cannot silently accept a pointer.
2. Matplotlib tab now has the same shared 32/76/97 dropdown as the gravity setup. `Load selected setup plots` only displays a registered source/limit-state/profile matched result and verifies saved case ID and support count. The selected scenario, support count, gravity profile, and exact source result filename are shown prominently.
3. On successful case registration, `publish_gravity_case_index()` populates `<selected main output>/02_GRAVITY/<scenario>/<timestamp-id>` with `CASE_SUMMARY.json`, `README_FIRST.txt`, a direct legacy-run link and lightweight PNG previews. The original complete solver data and previous output paths are NOT moved or overwritten.
4. `Organize existing 32 / 76 / 97 outputs` indexes already completed, current-model hash-verified runs without executing a structural solver. The user may thus populate Gravity now rather than rerunning costly analyses.

## Windows review checklist
- Fully close old V161 and relaunch from freshly updated repository, not a previously downloaded frozen ZIP/runtime.
- Confirm running-code path in GUI and commit/package version; select original EDB and output directory.
- Re-run ETABS model conversion, confirming no LFS dialog before or during conversion. Check `Optional_Workbook_Conversion_Audit.json` records a missing workbook as incomplete evidence.
- Open Gravity with the same verified-clear-beam model currently indexed. Click `Organize existing 32 / 76 / 97 outputs`; inspect `02_GRAVITY` for three separate source-linked folders.
- Choose each case in Matplotlib dropdown, `Load selected setup plots`; confirm 32, 76, 97 nodes and proper source, not stale plots.
- Confirm original result JSON/Excel/PDF files still exist at the old locations, and no physical model or EDB was changed.
- Report native Windows failure logs if any and keep acceptance `NOT_VALIDATED` until ETABS reaction and rigid-end equivalence evidence is reviewed.

These are software routing and visualization changes, not a structural model correction.
