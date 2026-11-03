# Worked_Example_V138/XY_StartUp/isolated_model/OpenSees_Complete_Gravity_Check_V118.json

**Source:** [Worked_Example_V138/XY_StartUp/isolated_model/OpenSees_Complete_Gravity_Check_V118.json](../../../../../../Worked_Example_V138/XY_StartUp/isolated_model/OpenSees_Complete_Gravity_Check_V118.json)
**Classification:** HISTORICAL_EXAMPLE_OUTPUT
**SHA-256 (source bytes):** 5c8f2a2597f66690b422c5df493338c29351b319981191240317260be157bf24
**Size:** 578 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.steps | integer |
| $.applied_vertical_load_kN | number |
| $.support_vertical_reaction_kN | number |
| $.equilibrium_error_percent | number |
| $.equilibrium_tolerance_percent | number |
| $.max_downward_vertical_displacement_m | number |
| $.elapsed_seconds_before_freeze | number |
| $.gravity_frozen | boolean |
| $.elapsed_seconds | number |
| $.diaphragm_kinematics | object |
| $.diaphragm_kinematics.max_inplane_constraint_residual | number |
| $.diaphragm_kinematics.units | str |

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
