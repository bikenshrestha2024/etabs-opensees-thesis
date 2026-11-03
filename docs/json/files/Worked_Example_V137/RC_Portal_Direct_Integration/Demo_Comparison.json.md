# Worked_Example_V137/RC_Portal_Direct_Integration/Demo_Comparison.json

**Source:** [Worked_Example_V137/RC_Portal_Direct_Integration/Demo_Comparison.json](../../../../../Worked_Example_V137/RC_Portal_Direct_Integration/Demo_Comparison.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 1c1b080f3fdf4fcb9135dadd0d5f3ac6e5a41fecb0238ce670774cdf5e3370db
**Size:** 2051 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.scope | str |
| $.started | str |
| $.finished | str |
| $.elapsed_s | number |
| $.linear | object |
| $.linear.label | str |
| $.linear.status | str |
| $.linear.duration_s | number |
| $.linear.dt_s | number |
| $.linear.periods_initial_s | array |
| $.linear.periods_initial_s[] | number |
| $.linear.gravity_reactions_kN | number |
| $.linear.peak_roof_displacement_m | number |
| $.linear.peak_drift_ratio | number |
| $.linear.record_scale_factor | number |
| $.linear.unit_conversion_g_to_m_s2 | number |
| $.linear.total_Path_factor | number |
| $.linear.fallback_steps | integer |
| $.linear.elapsed_s | number |
| $.linear.rows | integer |
| $.linear.source_record | str |
| $.linear.betaKcomm_s | number |
| $.linear.initial_modal_damping_ratios | array |
| $.linear.initial_modal_damping_ratios[] | number |
| $.nonlinear | object |
| $.nonlinear.label | str |
| $.nonlinear.status | str |
| $.nonlinear.duration_s | number |
| $.nonlinear.dt_s | number |
| $.nonlinear.periods_initial_s | array |
| $.nonlinear.periods_initial_s[] | number |
| $.nonlinear.gravity_reactions_kN | number |
| $.nonlinear.peak_roof_displacement_m | number |
| $.nonlinear.peak_drift_ratio | number |
| $.nonlinear.record_scale_factor | number |
| $.nonlinear.unit_conversion_g_to_m_s2 | number |
| $.nonlinear.total_Path_factor | number |
| $.nonlinear.fallback_steps | integer |
| $.nonlinear.elapsed_s | number |
| $.nonlinear.rows | integer |
| $.nonlinear.source_record | str |
| $.nonlinear.betaKcomm_s | number |
| $.nonlinear.initial_modal_damping_ratios | array |
| $.nonlinear.initial_modal_damping_ratios[] | number |
| $.nonlinear.peak_steel_strain | number |
| $.nonlinear.steel_yield_strain | number |
| $.nonlinear.peak_core_compressive_strain | number |

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
