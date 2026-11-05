# 2026-11-05 — ESM fields blank after model named "... Copy"

**Symptom:** Gravity remains converged, but ESM workbook-sourced Aw, zoning, importance or adopted periods appear blank. This does NOT show gravity is incorrect, nor does gravity equilibrium validate the seismic-weight ledger or ESM eligibility.

**Actual source-level causes found:**

1. After the source-matching security fix, `source_workbooks` rejected the historical scaling file when `SCALING SUMMARY!B4` referenced the original `.EDB` but the export topology referenced an `.EDB` named `... - Copy.EDB`. Previously the unreviewed values could be imported. New behavior accepts that differing model **name** only when both model files exist and their **actual bytes match via SHA256**; it does not assume Copy is identical based on text. A mismatch or unavailable source emits precise candidate diagnostics in the GUI/import audit rather than inventing an Aw or time period.
2. In `source_workbooks.workbook_info`, the workbook's B4 path was prematurely lowercased, which breaks on-disk hash lookup on case-sensitive paths. It is now kept as-is; casefold is applied only to string comparisons.
3. The GUI starts with `Both` selected, but **Preliminary Rayleigh X/Y** ran **ULS only**. Combined calculation correctly requires separate state-specific ULS and SLS Rayleigh periods and thus could not proceed. The button now launches the sequential `ULS` and `SLS` model states with separate result JSON/Excel/PNG/PDF and logs; it never reuses ULS periods as SLS.
4. Direct import from `components.equivalent_static.calculation_and_gui` previously looked for the legacy root `OpenSees_Rayleigh_Preliminary_V123.py` beside the component rather than in the repository root. Root-compatible path discovery has been added; existing launchers are intact.

## User checks

Run `git pull --ff-only origin main` after the correction is merged, then use `python 12_EQUIVALENT_STATIC.py`. In **Excel sources…**, select the actual project calculator and matching ULS scaling workbook; inspect `NBC105_Input_Provenance_V123.xlsx`, especially `Review notes` and `Wall Aw geometry`. If `B4` references a different EDB, locate the original and verify the physical model or manually provide independently reviewed actual source inputs. The code will not guess that two different EDB files represent the same wall geometry/mass.

When **Both ULS and SLS** is selected, click **Preliminary Rayleigh X/Y** once; the program should now calculate both states independently. Check both `NBC105_Rayleigh_Preliminary_V123*.json` sources and their model/weight hashes. Under **Both X/Y** there is no single meaningful `T1`; the separate directional empirical/amplified/adopted display and output cases carry X/Y period values. If either state fails, review its individual `NBC105_Rayleigh_Preliminary_V123_<STATE>.log`.

Gravity output from user-provided session: applied `286447.790000 kN`, reactions `286447.788933 kN`, equilibrium error `3.72366e-07%`, max Uz `-0.0168397578m`. These are the logged equilibrium diagnostics only and are not evidence that the seismic weight, wall Aw or X/Y periods were correctly imported.

## Verification

Tests: `tests/verify_esm_blank_copy_rayleigh.py`, `tests/verify_esm_aw_period_provenance.py`, and other ESM CI checks. Synthetic tests cover hash-equivalent and truly different copied EDB files, missing source model, and both-state Rayleigh command sequencing. Native Windows ETABS v23/OpenSees and the actual private project workbooks are **not available to CI** and remain a separate required engineering validation.

**NBC 105:2025:** §5.1 directional empirical/Rayleigh periods; §5.2 story seismic weight; §3.2.1 ESM eligibility. An irregular high-rise ULS equivalent-static calculation remains a diagnostic if not eligible by NBC conditions. Do not remove any gate to fill a blank form.
