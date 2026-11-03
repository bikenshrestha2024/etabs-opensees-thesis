# archive/previous_versions/VERIFICATION/VERIFICATION_V124.json

**Source:** [archive/previous_versions/VERIFICATION/VERIFICATION_V124.json](../../../../../../archive/previous_versions/VERIFICATION/VERIFICATION_V124.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** f84b7ef19b2ed12e5bc9bad105480dff8ea6755cc1ca945112118877031b3d99
**Size:** 4274 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.version | integer |
| $.regression_checks_passed | integer |
| $.python_syntax | str |
| $.signed_initial_PDelta_cases | integer |
| $.signed_SLS_static_cases | array |
| $.signed_SLS_static_cases[] | object |
| $.signed_SLS_static_cases[].case | str |
| $.signed_SLS_static_cases[].stories | integer |
| $.signed_SLS_static_cases[].applied_shear_kN | number |
| $.signed_SLS_static_cases[].equilibrium_error_percent | number |
| $.signed_SLS_static_cases[].max_master_design_drift_ratio | number |
| $.signed_SLS_static_cases[].roof_master_design_displacement_m | number |
| $.initial_PDelta_max_horizontal_equilibrium_error_percent | number |
| $.modal_cumulative_percent | object |
| $.modal_cumulative_percent.X | number |
| $.modal_cumulative_percent.Y | number |
| $.periods | object |
| $.periods.X | object |
| $.periods.X.Aw_m2 | number |
| $.periods.X.empirical_period_s | number |
| $.periods.X.amplified_empirical_s | number |
| $.periods.X.period_s | number |
| $.periods.X.adopted_period_s | number |
| $.periods.Y | object |
| $.periods.Y.Aw_m2 | number |
| $.periods.Y.empirical_period_s | number |
| $.periods.Y.amplified_empirical_s | number |
| $.periods.Y.period_s | number |
| $.periods.Y.adopted_period_s | number |
| $.Rayleigh_amplitude_check | object |
| $.Rayleigh_amplitude_check.reference_fractions | array |
| $.Rayleigh_amplitude_check.reference_fractions[] | number |
| $.Rayleigh_amplitude_check.relative_period_changes | object |
| $.Rayleigh_amplitude_check.relative_period_changes.X | number |
| $.Rayleigh_amplitude_check.relative_period_changes.Y | number |
| $.gui_checks | array |
| $.gui_checks[] | str |
| $.html_checks | str |
| $.limitations | array |
| $.limitations[] | str |

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

[All JSON files](../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../00_RESEARCH_REFERENCES.md)
