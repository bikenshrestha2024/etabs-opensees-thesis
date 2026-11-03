# Worked_Example_V132/Modal_ULS/NBC105_Modal_V111.json

**Source:** [Worked_Example_V132/Modal_ULS/NBC105_Modal_V111.json](../../../../../Worked_Example_V132/Modal_ULS/NBC105_Modal_V111.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 617182a4a6b5491a67a4ed7570a53c57dbc96d16257070b8d6e55b9323a9fe13
**Size:** 39159 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.standard | str |
| $.clauses | array |
| $.clauses[] | str |
| $.requested_modes | integer |
| $.returned_modes | integer |
| $.eigensolver | str |
| $.target_directional_mass_percent | number |
| $.minimum_modal_combination_frequency_hz | number |
| $.cumulative_UX_percent | number |
| $.cumulative_UY_percent | number |
| $.UX_90_percent_reached | boolean |
| $.UY_90_percent_reached | boolean |
| $.first_mode_reaching_target | object |
| $.first_mode_reaching_target.X | integer |
| $.first_mode_reaching_target.Y | integer |
| $.NBC_5_1_period_check | null |
| $.increase_requested_modes_if_target_not_reached | boolean |
| $.modes_at_or_above_33_Hz | array |
| $.modes_at_or_above_33_Hz[] | array(empty) |
| $.missing_mass_correction | str |
| $.horizontal_resisting_system_mode_review | str |
| $.modal_combination | str |
| $.base_shear_scaling | str |
| $.rows | array |
| $.rows[] | object |
| $.rows[].classification_candidate | str |
| $.rows[].classification_basis | str |
| $.rows[].mode | integer |
| $.rows[].eigenvalue_lambda_s-2 | number |
| $.rows[].omega_rad_s | number |
| $.rows[].frequency_Hz | number |
| $.rows[].period_s | number |
| $.rows[].UX_participation_percent | number |
| $.rows[].UX_cumulative_percent | number |
| $.rows[].UY_participation_percent | number |
| $.rows[].UY_cumulative_percent | number |
| $.rows[].RZ_participation_percent | number |
| $.rows[].RZ_cumulative_percent | number |
| $.rows[].below_33_Hz | boolean |
| $.rows[].mode_in_lateral_resisting_system | str |
| $.rows[].modal_combination_included_by_frequency_rule | boolean |
| $.rows[].above_33_Hz_missing_mass_followup_required | boolean |
| $.elapsed_seconds | number |
| $.limit_state | str |
| $.model_sha256 | str |
| $.implementation_sha256 | str |
| $.modal_numeric_sha256 | str |

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
