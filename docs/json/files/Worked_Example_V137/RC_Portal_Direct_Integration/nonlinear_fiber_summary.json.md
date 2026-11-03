# Worked_Example_V137/RC_Portal_Direct_Integration/nonlinear_fiber_summary.json

**Source:** [Worked_Example_V137/RC_Portal_Direct_Integration/nonlinear_fiber_summary.json](../../../../../Worked_Example_V137/RC_Portal_Direct_Integration/nonlinear_fiber_summary.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 5b769c9415f5a4d13d697b54c2a4b4beb550c4e67625cf717f116a931f21a54c
**Size:** 927 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.label | str |
| $.status | str |
| $.duration_s | number |
| $.dt_s | number |
| $.periods_initial_s | array |
| $.periods_initial_s[] | number |
| $.gravity_reactions_kN | number |
| $.peak_roof_displacement_m | number |
| $.peak_drift_ratio | number |
| $.record_scale_factor | number |
| $.unit_conversion_g_to_m_s2 | number |
| $.total_Path_factor | number |
| $.fallback_steps | integer |
| $.elapsed_s | number |
| $.rows | integer |
| $.source_record | str |
| $.betaKcomm_s | number |
| $.initial_modal_damping_ratios | array |
| $.initial_modal_damping_ratios[] | number |
| $.peak_steel_strain | number |
| $.steel_yield_strain | number |
| $.peak_core_compressive_strain | number |

## Interpretation and provenance

- Source of truth: the original JSON file at the path above. This generated reference never changes original data.
- This is an OBSERVED FIELD INVENTORY, not a formal JSON Schema or proof every nested record has identical keys.
- Original units, code edition, specimen/ETABS source, record ID, solver version and experimental status must be checked within the source file or linked manifest.
- A value without documented units/source must be classified UNVERIFIED, not automatically assumed kN-m-s.
- For historical outputs do not use to populate current run configuration or calibrated material parameters.
- Material/source specimens are not project-approved RC bar schedules or manufacturer-qualified dampers.
- External data may be private. This script runs offline and does not upload file contents.

## Validation requirements

- Confirm valid UTF-8 JSON and expected field/type/units against the producing program.
- Verify hashes, compare input and output manifests, and preserve experiment/case identity.
- For nonlinear runs check G00–G10 acceptance gates and explicit failure/incomplete statuses.

[All JSON files](../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../00_RESEARCH_REFERENCES.md)
