# Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/study/Study_Config.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/study/Study_Config.json](../../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/study/Study_Config.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** b4bbdae2217c0cab150572d7810ade4b2edb418c219f3467237eaad44c08eab7
**Size:** 1692 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.storeys | integer |
| $.height_m | number |
| $.geometry_basis | str |
| $.roof_cap_storey | integer |
| $.positions | array |
| $.positions[] | integer |
| $.configurations | object |
| $.configurations.O | str |
| $.configurations.O_B | str |
| $.configurations.O_B_C | str |
| $.devices | array |
| $.devices[] | str |
| $.pairs | integer |
| $.orientations | array |
| $.orientations[] | str |
| $.hazards | array |
| $.hazards[] | str |
| $.mass_rule | str |
| $.objective | str |
| $.FVD_research_sizing | object |
| $.FVD_research_sizing.Fref_kN_per_device | number |
| $.FVD_research_sizing.vref_m_s | number |
| $.FVD_research_sizing.alpha | number |
| $.FVD_research_sizing.Cd | number |
| $.FVD_research_sizing.K_kN_m | number |
| $.FVD_research_sizing.basis | str |
| $.sensitivity | object |
| $.sensitivity.concrete_cylinder_strength_MPa | array |
| $.sensitivity.concrete_cylinder_strength_MPa[] | number |
| $.sensitivity.steel_yield_MPa | array |
| $.sensitivity.steel_yield_MPa[] | number |
| $.sensitivity.steel_b | array |
| $.sensitivity.steel_b[] | number |
| $.sensitivity.background_damping_ratio | array |
| $.sensitivity.background_damping_ratio[] | number |
| $.sensitivity.wall_web_reinforcement_ratio_scale | array |
| $.sensitivity.wall_web_reinforcement_ratio_scale[] | number |
| $.sensitivity.FSAM_friction | array |
| $.sensitivity.FSAM_friction[] | number |
| $.sensitivity.status | str |
| $.scope | str |

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

[All JSON files](../../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../../00_RESEARCH_REFERENCES.md)
