# Confirmed gravity self-weight finding → EQX / EQY P-Delta verification handoff

Date: 2026-11-09. This is a verification plan and evidence gate, **not**
a claim that ETABS earthquake cases or OpenSees P-Delta cases have converged.

## Closed or independently confirmed at structural quantity level

The uploaded original ETABS assignment workbook (recorded in
`docs/review/CONFIRMED_NATIVE_ETABS_BEAM_WEIGHT_20261109.md`) independently
confirms 750 source beam objects; the original source ID/length/end-offset
crosswalk agrees with the OpenSees beam audit. Native ETABS material list:
beam **45,331.6105 kN** vs original OpenSees gross beam **53,984.05488 kN**.
The **8,652.44435 kN** difference agrees with the beam clear-length
quantity hypothesis, and other listed structural self-weight types
(column, wall, slab, brace) agree at aggregate level. One nonzero
self-weight multiplier: `Self Weight = 1.0`.

**Important distinction:** quantity difference FOUND and independent
native material list CONFIRMED. The separately guarded corrected
OpenSees model, source/object load distribution and 32-support reaction
distribution are **not** verified until the fresh corrected model is
exported and solved. ETABS `Auto` self-weight option is a source
assignment label, not on its own a proof of its native algorithm. Source
insertion placements (750 beams Top Center; 350 slabs Top) invalidate any
automatic acceptance of the previously centered-box joint union.
No geometric RCC overlap deduction is authorized.

## Next validation scope: actual native EQX P Delta / EQY P Delta

The user's intended labels `EQX P Delta` and `EQY P Delta` are
**names to locate in the original EDB**, not assumed code-defined
combinations, analysis algorithms or factors. Obtain the exact native
case/combination records, gravity preload definition, second-order
geometric stiffness option, directional factors, accidental
eccentricities, and active original EDB SHA256.

This is different from the repository's existing
`PD_INIT_EL_X_PLUS/MINUS`, `PD_INIT_EL_Y_PLUS/MINUS` tests for
IS 16700:2023 initial 1.2D + 0.5IL ± 1.5EL, which are separate
project diagnostics. Do not relabel those results as native ETABS
EQX/EQY P Delta cases.

Verification phases:
1. Freeze and fingerprint **corrected** ETABS source conversion,
   weight / mass, and primary 32-reaction-bearing node support
   sensitivity. Treat the other 44 wall mesh nodes as separate source
   analytical-connectivity evidence; zero ETABS FZ does not prove free
   DOF.
2. Compare exact self-weight, DL/IL factors and lateral earthquake
   pattern assignment in both systems. Gravity-only
   `GRAVITY_1.0D_1.0L` is a check case, **not automatically the
   earthquake P-Delta preload**.
3. Determine what EQX/EQY represents in native ETABS: equivalent
   static lateral, response spectrum, nonlinear static, or specific
   P-Delta-modified initial/static result; compare **like with like**.
   For CQC envelopes, do not treat max-X/max-Y as concurrent signed
   static responses.
4. Require recorded geometric transformation/P-Delta activation,
   actual preloaded state, applied signed lateral actions, support
   constraints and solver convergence evidence. Only then compare
   signed base shear, story displacements, interstory drifts, reaction
   distribution, column/core axial loads and wall shear at identical
   coordinates and matched ULS/SLS source stiffness.
5. Preserve adopted NBC 105 Aw-X/Aw-Y and T1-X/Y **directly from the
   user's original `NBC105_RS_Scaling.xlsx` workbook**, including
   cell locations, workbook SHA256 and source EDB identity. Never
   silently recalculate substitute wall areas, periods or spectral
   scale factors. Do not reapply matched ground-motion spectral
   scaling.
6. For nonlinear transient readiness, after gravity/P-Delta source
   validation, verify a fresh preload then `loadConst('-time',0.0)`,
   unchanged mass, modal periods, and zero-input / X / Y / XY
   convergence. None is accepted by an EQ case-label match alone.

## New read-only evidence gate

`components/validation/eq_pdelta_evidence.py` accepts a separate local
JSON with exact `X` and `Y` case definitions and source evidence
paths, hashes every actual file, and reports missing or ambiguous
preload/P-Delta/directional evidence. It does NOT launch ETABS, run
OpenSees, guess factors or declare engineering acceptance.

Example input only (replace every placeholder with measured records):
```json
{
  "X": {
    "axis": "X",
    "etabs_case_name": "EQX P Delta",
    "etabs_analysis_type": "NOT_YET_VERIFIED",
    "etabs_pdelta_enabled": false,
    "etabs_combination_or_case_definition": "NOT_YET_VERIFIED",
    "etabs_evidence_path": "",
    "opensees_result_path": "",
    "opensees_preload_evidence_path": "",
    "opensees_source_model_sha256": "",
    "limit_state": "ULS",
    "pdelta_method": "NOT_YET_VERIFIED",
    "gravity_factors": {},
    "lateral_action_factors": {}
  },
  "Y": {
    "axis": "Y",
    "etabs_case_name": "EQY P Delta",
    "etabs_analysis_type": "NOT_YET_VERIFIED",
    "etabs_pdelta_enabled": false,
    "etabs_combination_or_case_definition": "NOT_YET_VERIFIED",
    "etabs_evidence_path": "",
    "opensees_result_path": "",
    "opensees_preload_evidence_path": "",
    "opensees_source_model_sha256": "",
    "limit_state": "ULS",
    "pdelta_method": "NOT_YET_VERIFIED",
    "gravity_factors": {},
    "lateral_action_factors": {}
  }
}
```

Command (Spyder-compatible Python 3.12):
```powershell
python -m components.validation.eq_pdelta_evidence EQ_PDelta_Cases.json --out EQ_PDelta_Review
python tests/verify_eq_pdelta_evidence.py
```
Output `EQ_PDelta_Review/EQX_EQY_PDelta_Evidence_Gates.json`.
Missing data is **BLOCKED**, not zero, and verified file existence
is not a physical validation result.

No native EQX/EQY results, user EDB, private source Excel or native
source-model bytes are committed.
