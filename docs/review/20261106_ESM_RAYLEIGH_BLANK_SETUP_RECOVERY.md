# 2026-11-06 — Rayleigh setup blank-field failure and recovery procedure

**Original Windows UI:** `Preliminary Rayleigh run (X/Y)` gave `could not convert string to float: ''` after the ESM importer refused mismatched or invalid scaling workbook effective wall indices. Gravity had already converged (~286448 kN load, 3.7e-7% equilibrium error).

## Established causes

1. `components/equivalent_static/calculation_and_gui.py::_run_rayleigh` immediately called `float(self.awx.get());float(self.awy.get())` before checking whether either field was empty.
2. The selected Ultimate/ULS source scaling workbook may contain Excel labels/formula errors: `SCALING SUMMARY!B15='Aw (m²)'`, `C15='Adopted T1 (s)'` and `E7='Target Base Shear'`. These are **not numeric values** and should never be substituted or treated as valid calculated results.
3. Candidate scaling files `SCALING SUMMARY!B4` often point to **different source EDB files** (Service or other belt/outrigger variants), while the selected current model's source is an Ultimate `...- Copy.EDB`. A workbook from another physical model cannot provide verified Aw.
4. For this model, first-storey wall footprints change across height slices due to a possible partial-height opening/discontinuity. The auto Aw calculator correctly avoids collapsing different cross-sections into a single code-compliant index. See [first-storey wall-profile audit](20261106_ESM_WALL_PROFILE_SCREENSHOT_TRIAGE.md).
5. A separate ETABS modal API session returned no modal results. This affects live ETABS reference periods, **not** imported workbook data or an OpenSees Rayleigh run.

## Software correction

`ESMGui._rayleigh_input_preflight` rejects blank/non-numeric/non-finite/nonpositive directional wall indices with actionable messages; requires assembled model JSON and source story-weight CSV; blocks explicitly opposite ULS/SLS source identification before launching. Existing advanced Both mode still calculates two separate states, but its source evidence must be independently verified. This is **input safety**, not structural model certification. Unit test: `tests/verify_esm_rayleigh_blank_preflight_20261106.py`.

## Actual engineering workflow on the private Windows model

1. Update the same working checkout: `git pull --ff-only origin main`, then launch `12_EQUIVALENT_STATIC.py` or the active main UI. Verify the model folder reads `D:\Thesis Opensees\ETABS  3 - BELT TRUSS, OUTRIGGER CAP TRUSS 11-6-2026\`. Set **ULS** for the source Ultimate EDB. Service files are ineligible in this run.
2. **Do not change gravity parameters** to fix this. The demonstrated gravity equilibrium is independent of NBC §5.1 wall index selection and does not prove correct seismic mass.
3. Click **Why are Aw/period fields blank?**. Open `ESM_Source_Diagnostics.txt`; inspect first-storey `z_bottom_m/z_top_m`, `Aw-X`, `Aw-Y` and segment counts. Compare with actual core and other wall lengths/thicknesses, slab openings, re-entrant plan, first-storey base reference and NBC §5.1.2 effective wall pier grouping.
4. Check the scaling workbook in **Excel sources…**. The required table is `SCALING SUMMARY`: `B4` original EDB path; `B14` numeric X Aw; `B15` numeric Y Aw; `C14/C15` workbook adopted T references **only** (not OpenSees Rayleigh). A formula error, column heading or unverified EDB mismatch remains a blocker. If original/copy EDB bytes are identical, the existing SHA256 comparison can establish exact copied-file identity; if not, generate project-specific scaling workbook or manually enter independently calculated Aw.
5. After reviewing the physical wall pier lengths, openings and NBC applicability, input **actual finite positive** `Aw-X/Aw-Y` into the GUI. Do not use historic `3.6779/0.8019` or unrelated `1.9582936/2.2030803` without independent source proof. Source inputs must reflect this current export.
6. Click **Preliminary Rayleigh run (X/Y)**. This separately builds current-state OpenSees model, freezes gravity, equilibrates torsion-suppressed state and applies reference lateral perturbations. Keep `ULS` selected for this Ultimate model. Check the per-state `NBC105_Rayleigh_Preliminary_V123_ULS.log` and `NBC105_Rayleigh_Preliminary_V123.json/.xlsx/.png`. A pass is diagnostic, not structural acceptance.
7. Live ETABS eigen reference: open the **exact same source EDB**, run modal analysis and use **Open ETABS / refresh X-Y periods**. Zero returned API rows must be investigated by verifying model connection, modal case and results; ETABS eigenperiod is not the independently calculated Rayleigh period.
8. Then click **Adopt lesser period** for the selected X/Y direction and calculate/export ESM cases. For this ~95-m irregular high-rise, verify NBC §3.2.1 eligibility. The ESM run may remain a comparison diagnostic rather than a permitted standalone ULS design method.

## Current verified limitations

No access to the private Windows EDB or current first-storey wall geometry/reinforcement was provided. No numerical Aw or Rayleigh T is supplied by this patch. Automated tests use synthetic fixture data and do not prove real ETABS COM or OpenSees physics. Preserve original materials, gravity profile, spectrum scaling, mass assignments and nonlinear configuration.
