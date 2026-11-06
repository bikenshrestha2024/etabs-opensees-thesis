# ESM first-storey openings: geometric deduction and ETABS↔OpenSees crosscheck

**Purpose:** respond to the persistent `PROVISIONAL_CONTINUOUS_PIER_DIAGNOSTIC` user request by showing exactly **which wall projections were excluded by openings** and enabling a separate, direct read-only ETABS geometry crosscheck.

## Governing equation and what must not be conflated

NBC 105:2025 §5.1.2 uses the directional effective wall index
`Aw = sum_i [Awi * (0.2 + (min(Lwi/H,0.9))²)]`, with **Awi the effective first-storey cross-sectional area of physical wall i** and **Lwi the wall length**. It does NOT prescribe a general rule of deducting vertical door/window *opening surface area* from the final scalar Aw. Opening geometry changes the definition of the real first-storey wall piers, their effective lengths and their coupling; therefore the weighting must be recomputed per supported physical pier. Subtracting a gross elevation opening-area number from Aw would be dimensionally and mechanically wrong.

The source model contains nonuniform first-storey wall shell cross-sections. Our existing per-z OpenSees wall profile and through-height pier intersection already compute a **provisional** source-specific Aw candidate from physical wall material that exists across the entire first-storey height. The new code reports:
- gross projected geometry contribution (union of wall segments present at *any* first-storey z slice);
- continuous-through-height pier contribution (intersection of physical wall intervals present at *every* slice);
- excluded/noncontinuous projected contribution = gross - through-height, by X/Y;
- individual piers, plane coordinates, lengths, thicknesses, dimensions, slice bounds and weighted contributions.
These are m² directional **wall-index contributions**. The subtraction is NOT the vertical surface area of an opening and the continuous pier estimate is not a general lower-bound on seismic demand.

## What automated ETABS comparison now verifies

Click `Check live ETABS geometry (read-only)` on the ULS model after opening the exact exported source EDB in ETABS. It calls the existing read-only API wall extraction and, when it returns model-matched wall panels, calls `compare_wall_profiles()`, which:
1. verifies the same first-storey base and top elevations;
2. samples **every combined z-slice interval** from the two models;
3. merges physical shell mesh subdivisions per (axis, wall plane, thickness);
4. compares actual X/Y pier/void interval counts and start/end coordinates, not just Aw totals;
5. flags mismatches, skipped nonorthogonal panels, failed ETABS API object reads, and missing response metadata.

A matching numerical geometry report uses `GEOMETRY_MATCHED_REVIEW_REQUIRED`. It is only an evidence upgrade over an unverified geometric candidate; it does **not** prove the expected NBC physical pier grouping, perforated RC coupled shear wall behavior, nonlinear wall material calibration, ETABS analysis settings, or code acceptance. A mismatch is `GEOMETRY_MISMATCH`; incomplete API coverage is `INCOMPLETE_ETABS_EXTRACTION`. The default 1-mm tolerance is a disclosed internal geometry screen, **not an NBC prescribed tolerance**.

## ESM workflow

1. Select the same Ultimate→ULS export in the primary ESM program. Never silently import a Service EDB or another outriggers/floor variant.
2. `Sync from OpenSees model` gives current geometric candidate Aw for both horizontal axes where full-height wall material exists. The auto-prefilled values and empirical periods are **research diagnostics** until physical code-effective pier grouping is reviewed.
3. `Check live ETABS geometry (read-only)` performs the independent model's per-slice geometry check; review `NBC105_OpenSees_Input_Sync.json` under `opening_reduction_audit`, `geometry_crosscheck` and `etabs_fallback`. The Excel **OpenSees Source Sync** sheet includes source slices, opening reductions, physical pier segments and mismatch details. Original EDB, calculator workbook, RS scale factors and source OpenSees geometry files remain unchanged.
4. Engineer independently reviews pier groups and openings under §5.1.2, including possible coupling/spandrel action and any local axis/nonorthogonal walls not captured by the axis-aligned extractor. Only then should a qualified Aw be entered for code design; both original source records and the accepted calculation basis must be retained.
5. Run source-state-matched Rayleigh X/Y and compare independently with ETABS modal/RSA results. A successful configured gravity load equilibrium does not establish modal equivalence.

## Software limitations

- This PR does **not** claim a project-specific reviewed Aw or a certified ULS ESM design method. The native Windows ETABS COM API was not available in CI and the source EDB's live unsaved changes cannot be determined from on-disk path identity alone.
- Some ETABS area objects may be non-axis-aligned, partial panels or slab/other shell types. A recorded skipped/failed object blocks matching status. Existing extraction still requires a native integration test on the user's real 25-storey export.
- For an asymmetric high-rise, assess NBC §3.2.1 ESM eligibility separately: successful ESM scalar comparison is not a replacement for MRSM/NLTHA acceptance.
- No material, gravity, mass, damping, user force-pattern, target spectrum, nonlinear wall stiffness or source file has been modified.

**Tests:** `tests/verify_esm_opening_etabs_crosscheck.py`, existing `tests/verify_opensees_first_nbc_sync.py`, full CI.
