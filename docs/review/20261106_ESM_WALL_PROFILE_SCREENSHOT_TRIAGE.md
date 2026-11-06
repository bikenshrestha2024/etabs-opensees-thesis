# 2026-11-06: ESM Aw remains blank with a nonuniform first-storey wall footprint

The source report from the user's current **Ultimate/ULS** export says:

> First-storey wall footprint changes with elevation (possible partial-height opening or discontinuity); automatic Aw cannot merge these wall patches.

**Separate issues visible in the provided GUI screenshots:** (1) invalid/unmatched Excel source `SCALING SUMMARY!B4` EDB path; (2) a wall profile with cross-sections differing by height; (3) connected ETABS modal case with no result rows. These are not the same defect. Numerically balanced gravity (286447.790 kN applied, 286447.788933 kN reactions) does **not** validate the NBC effective wall area, cracked stiffness, eigenperiod or Rayleigh estimate.

## Code changes

- `components.inputs.project_workbooks._wall_aw_profile(H, base, first, patches)` independently computes audited wall segments and candidate `Aw-X/Aw-Y` **at each height slice** bounded by actual wall element lower/upper Z coordinates.
- When the wall footprint is nonuniform, the pre-existing fail-closed `_wall_aw_from_patches` decision is unchanged: **do not automatically adopt a single Aw**, or take minimum/maximum/average values, especially for openings or discontinuous walls.
- `import_project_inputs()` retains `values['wall_aw_profile']` and explanatory notes **even if the eventual effective-Aw automatic adoption fails**. User-supplied independently justified X/Y wall values remain possible in the GUI; they are not generated from unrelated scaling workbooks.
- GUI `Why are Aw/period fields blank?` now opens a readable, selectable, scrollable **source audit** showing each wall elevation slice and values, then candidate workbook provenance; it also persists `ESM_Source_Diagnostics.txt` locally. No source-model file is modified.
- Existing source EDB/limit-state hash checking, exclusion of nonnumeric Excel cells, separate Rayleigh calculation and optional live ETABS COM connection remain unchanged.

## Current evidence required

1. Use **only the Ultimate ULS export** `D:\Thesis Opensees\ETABS  3 - BELT TRUSS, OUTRIGGER CAP TRUSS 11-6-2026\`. Do not import Service or other-floor scaling workbook values just because their cells are numeric.
2. Reopen the ESM module after `git pull --ff-only origin main`, then click **Why are Aw/period fields blank?**. Review the first-storey wall slices, the list of changing wall segment geometry and the original EDB source recorded by `OpenSees_Element_Connectivity.json`.
3. Verify all first-storey wall piers, openings, actual basement/base-to-roof height, aligned wall lengths and correct physical grouping using the original EDB and NBC 105:2025 §5.1.2. An opening can divide the effective lengths, so never substitute another model's gross wall area.
4. Provide separately checked and traceable `Aw-X`, `Aw-Y` in the GUI, or regenerate a model-matched workbook from that reviewed calculation. Empirical/amplified periods will show; adopted periods still require **current-state directional Rayleigh** calculations, or an explicitly justified compatible reference accepted only as preliminary diagnostic.
5. If user explicitly clicks ETABS live modal results and the API returns zero rows, run and select the actual modal case in the correct ETABS EDB first. This does not block local workbook/geometry diagnostic inspection, and `T1\_ETABS` is a comparison value, not Rayleigh.

## Validation limit

The new unit test `tests/verify_esm_wall_profile_slices_20261106.py` checks uniform vertically split panels, nonuniform first-storey openings, and missing wall-patch input. This is **synthetic structural geometry**; it does not reconstruct the user's privately held original ETABS EDB and therefore does not certify a numeric Aw. Do not describe the gravity equilibrium as a code acceptance test for ESM.

No wall material, gravity load, stiffness modifier, wall-element formulation, or mass assignment is changed. No numerical value is invented for blank input fields.
