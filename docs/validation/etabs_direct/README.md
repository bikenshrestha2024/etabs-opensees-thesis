# Direct ETABS v23 ↔ OpenSeesPy equivalence workflow (2026-11-05)

## Current implementation and status

**Software contract only until Windows ETABS native test is completed.** This feature reads the *currently opened and already analysed* ETABS `.EDB` through its **COM API**, rather than requiring the user to normalize an ETABS CSV by hand. This is not direct binary parsing and does not run ETABS analysis. Its existing normalized-CSV workflow is retained as a fallback. No source EDB is saved, unlocked, overwritten or uploaded.

The GUI entry point is the existing **ETABS comparison** view, `components/validation/etabs_comparison.py:launch`, now containing **Direct ETABS API / EDB…**.

### First use in Windows / Spyder

1. Activate your conda-forge Python environment with `comtypes`, `openpyxl` and `matplotlib`; ETABS v23 must be installed, under the same user/elevation.
2. Open your **intended source EDB in ETABS** and run the appropriate modal and response-spectrum cases **in ETABS itself**, using the correct ULS/SLS stiffness, seismic mass, 5% modal damping, soil spectrum, NBC §7.5 force-scaling settings and eccentricity cases. **Do not let the script silently switch EDBs or recalculate a model.**
3. Run your existing numbered Python research UI; open its ETABS comparison tab. Click **Direct ETABS API / EDB…** and choose the identical already-open `.EDB`. On first attempt, cancel the mapping JSON chooser; this creates `OpenSees_Analysis_Results/ETABS_Comparison_V148/ETABS_API_Mapping_TEMPLATE.json`.
4. Edit the template into a review-approved JSON mapping. Use the **exact** ETABS case names and OpenSees case IDs (`X_E0`, `X_Eplus`, `X_Eminus`, `Y_E0`, `Y_Eplus`, `Y_Eminus`) for each ULS/SLS run. The same ETABS load-case name is not automatically the equivalent case; it must represent the same spectrum, CQC, damping, 5% accidental torsion, plan axis and load effect.
5. Include every story name mapping (`Story25` → numeric OpenSees `25`, etc.), based on the actual ETABS story definition and model-diaphagm tags. For roof displacement, specify a real ETABS point whose coordinates are comparable with the selected OpenSees response location; DO NOT use an arbitrary diaphragm master centroid that has no matching ETABS point.
6. Run Direct API again, choose the saved JSON, and inspect `ETABS_API_Normalized.csv`, `OpenSees_Normalized.csv`, `Comparison.csv`, `ETABS_OpenSees_Equivalence.xlsx`, `ETABS_API_Provenance.json`, and any reported missing/conflicting data in the output folder.
7. `assumptions_verified` starts **false**. After *independent actual physical source reconciliation* and documented matched output bases, it may be set true for a **numerical screening** result. A PASS is only against the explicitly chosen research tolerances, never a Nepal code-compliance certificate.

### Example mapping (illustrative names only, do not treat as your actual ETABS cases)

```json
{
  "source_edb": "D:/Thesis/ACTUAL_MATCHED_ULTIMATE_MODEL.EDB",
  "assumptions_verified": false,
  "percent_limits": {"period": 2.0, "base_shear": 5.0, "drift_ratio": 5.0, "displacement": 5.0},
  "cases": [
    {
      "etabs_case": "MODAL_ULTIMATE_ACTUAL",
      "method": "MODAL", "limit_state": "ULS", "case": "MODAL",
      "axis": "X", "modal_mode_pairing_verified": false
    },
    {
      "etabs_case": "SPECTRUM_X_CENTERED_ACTUAL",
      "method": "MRSM", "limit_state": "ULS", "case": "X_E0", "axis": "X",
      "story_map": {"Roof": 25, "Story24": 24},
      "points": [{"etabs_point": "ETABS_ROOF_POINT_OBJECT_NAME", "story_number": 25}],
      "force_basis_verified": false, "force_scale_note": "",
      "displacement_basis_verified": false, "displacement_scale_note": ""
    }
  ]
}
```

To use another ETABS model (e.g. different ULS/SLS stiffness), open it first in ETABS and change `source_edb` and case mapping explicitly. Do not rely on one active EDB representing both independent ULS/SLS stiffness states.

## CSI API calls and recorded units

| Method | Official ETABS API output | Normalized quantity / limits |
|---|---|---|
| `Results.ModalPeriod` | Mode number/period | `period` in seconds, separate modal-case mapping; **not** NBC empirical/Rayleigh T |
| `Results.ModalParticipatingMassRatios` | Per-mode UX, UY, cumulative mass | Per-mode fractions converted to percentage for audit; this does **not** automatically pair modal eigenvectors |
| `Results.BaseReact` | FX/FY etc | Absolute base-reaction component [kN], labeled `CQC_force_scaled` **only** if ETABS/solver force basis is explicitly checked |
| `Results.StoryDrifts` | Story, load case, direction, drift, critical location | Maximum ETABS drift ratio, only same-result-basis when reviewer checks actual perimeter/edge definition and NBC drift amplification. Older CSI versions had a historical unit-conversion bug (ETABS v18 release notes); current output assumed dimensionless |
| `Results.JointDispl` | Object/element/case/step/U1/U2/U3 | Point-specific translational displacement [m] only with an explicit ETABS point-object mapping and matching displacement basis |
| `Results.Setup` | Output selection | All selected cases/combos are read and restored, including after API errors |
| `SapModel.SetPresentUnits(6)` | `kN_m_C` | Restored to original units in `finally`; output source file not saved |

Official API references:
- [ModalPeriod](https://docs.csiamerica.com/help-files/etabs-api-2016/html/07dd92be-7f20-d55e-676a-22af467bfa9c.htm)
- [ModalParticipatingMassRatios](https://docs.csiamerica.com/help-files/etabs-api-2016/html/342290a6-d7ba-e872-50cc-168f64bac318.htm)
- [BaseReact](https://docs.csiamerica.com/help-files/etabs-api-2016/html/b1b7816f-970b-afe9-c188-1b528722134a.htm)
- [StoryDrifts](https://docs.csiamerica.com/help-files/etabs-api-2016/html/e55e16e2-b7b0-2864-f3dc-b781f4062325.htm)
- [JointDispl](https://docs.csiamerica.com/help-files/etabs-api-2016/html/1bb2ca14-4532-795c-4e5a-50160dc144a4.htm)
- [SetPresentUnits](https://docs.csiamerica.com/help-files/etabs-api-2016/html/16d95aba-00c9-f947-5e62-6b18045ef3d7.htm)

## Evidence-gated comparison contract

The exact matching key is `method/limit_state/case/axis/location/metric/unit/basis`. Unmatched source results are `MISSING_ETABS` or `MISSING_OPENSEES`; same-looking responses with different `unit` or `basis` are `NOT_COMPARABLE`. An exact key is not an independent physical-model audit, so it remains `NOT_COMPARABLE` until an explicitly reviewed mapping sets `assumptions_verified=true`.

Default optional research screening tolerances (never NBC code thresholds): period 2%, modal mass 1 percentage point **requires correct units**, base/shear/drift/displacement 5%, with separately reported absolute thresholds for zero reference. The caller may override tolerances with finite nonnegative numbers. Never divide by a zero ETABS result.

**Important methodological omissions** to audit before setting evidence approval: actual ETABS/OpenSees model geometry and seismic mass equality; cracked-section effective stiffness ULS/SLS and real wall openings; diaphragm and master/edge response location; P-Delta/gravity state; modal eigenvector pairing / MAC; mode combination CQC frequency and damping conventions; 33 Hz missing mass; design spectrum ordinates and units; minimum MRSM base-shear force scaling with **unscaled** displacements; storey drift amplification and eccentricity; actual source ETABS case definition, and response-spectrum combination definitions. The extractor does not prove those equivalences merely by querying the EDB.

## Testing and privacy

```powershell
python tests/verify_etabs_direct_equivalence.py
python tests/verify_nbc105_periods.py
python tests/verify_esm_aw_period_provenance.py
```

CI uses mocked COM arrays and confirms strict return-argument order, restoring ETABS units/case selection, failure on wrong EDB, evidence gating, zero-reference comparisons and Excel production. **There is no native Windows ETABS test in GitHub's Linux CI**. The user must independently inspect ETABS API v23 runtime return tuple signatures, actual case names, and result shape before relying on quantitative conclusions. ETABS EDB and result exports stay local; hash provenance is stored only on the local machine.
