# MODULE_INDEX_V130.json

**Source:** [MODULE_INDEX_V130.json](../../../MODULE_INDEX_V130.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** ecd7e89f24e2acaa067d7d4026ef7827b1f53e822104addefe80d8b56e48982e
**Size:** 2387 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.ETABS_to_OpenSeesPy_Section_Review_V116_NBC105_Area_NLTHA | str |
| $.Define_Section_V109 | str |
| $.NBC105_Analysis_Settings_V108 | str |
| $.NBC105_Analysis_Settings_V109 | str |
| $.NBC105_Load_Accounting_V108 | str |
| $.NBC105_Spectrum_Scaling_V115 | str |
| $.OpenSees_Analysis_Stack_V108 | str |
| $.OpenSees_Analysis_Stack_V110 | str |
| $.OpenSees_Area_Element_Integration_V116 | str |
| $.OpenSees_Complete_Export_V118 | str |
| $.OpenSees_Earthquake_Analysis_NBC105_V111 | str |
| $.OpenSees_ETABS_Periods_V125 | str |
| $.OpenSees_FVD_BRB_Devices_V115 | str |
| $.OpenSees_Gravity_GUI_V110 | str |
| $.OpenSees_ID_Audit_V120 | str |
| $.OpenSees_Initial_PDelta_V124 | str |
| $.OpenSees_Linear_Autofill_V124 | str |
| $.OpenSees_Linear_Time_History_NBC105_V115 | str |
| $.OpenSees_Literature_Validation_V117 | str |
| $.OpenSees_Mapping_Audit_V125 | str |
| $.OpenSees_Mapping_GUI_V125 | str |
| $.OpenSees_Modal_Analysis_NBC105_V111 | str |
| $.OpenSees_Modal_GUI_NBC105_V111 | str |
| $.OpenSees_Nonlinear_Time_History_NBC105_V116 | str |
| $.OpenSees_Pair_Selection_V128 | str |
| $.OpenSees_Project_Inputs_V123 | str |
| $.OpenSees_Project_Progression_V116 | str |
| $.OpenSees_Rayleigh_Preliminary_V123 | str |
| $.OpenSees_Reference_Library_V116 | str |
| $.OpenSees_Research_UI_V123 | str |
| $.OpenSees_Result_Interpretation_V115 | str |
| $.OpenSees_Results_UI_V127 | str |
| $.OpenSees_Runtime_Utilities_V117 | str |
| $.OpenSees_Step13_Analysis_Basis_V115 | str |
| $.OpenSees_Window_Manager_V129 | str |
| $.OpenSees_Timing_V130 | str |
| $.OpenSees_Model_Audit_V130 | str |
| $.OpenSees_Input_Records_V130 | str |

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

[All JSON files](../00_ALL_JSON_FILES.md) · [Research citations](../../00_RESEARCH_REFERENCES.md)
