# Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/cards/ConcreteCM.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/cards/ConcreteCM.json](../../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/cards/ConcreteCM.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 676bacc894d56486d2e4ca227288700304f37ae43bd49a7d27e040f05fa4b9ed
**Size:** 2679 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.model | str |
| $.parameters | object |
| $.parameters.fpcc | number |
| $.parameters.epcc | number |
| $.parameters.Ec | number |
| $.parameters.rc | number |
| $.parameters.xcrn | number |
| $.parameters.ft | number |
| $.parameters.et | number |
| $.parameters.rt | number |
| $.parameters.xcrp | number |
| $.parameter_basis | str |
| $.specimen_id | str |
| $.citation | str |
| $.source | str |
| $.protocol_csv | str |
| $.measured_csv | str |
| $.fit_bounds | object(empty) |
| $.train_fraction | number |
| $.scope | str |
| $.wall_formulation | str |
| $.targets | array |
| $.targets[] | number |
| $.samples_per_leg | integer |
| $.dt_s | number |
| $.sources | object |
| $.sources.Mander_theory_1988 | str |
| $.sources.Mander_experiment_1988 | str |
| $.sources.Concrete02 | str |
| $.sources.ConcreteCM | str |
| $.sources.Steel02 | str |
| $.sources.SteelMPF | str |
| $.sources.FSAM | str |
| $.sources.E_SFI_2023 | str |
| $.sources.E_SFI_authors | str |
| $.sources.PEER_2015 | str |
| $.sources.FVD | str |
| $.sources.BRB | str |
| $.sources.Outrigger_optimization_2021 | str |
| $.sources.Outrigger_2010 | str |
| $.sources.NBC2025 | str |
| $.sources.Diaphragm | str |
| $.project_transfer_approved | boolean |

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
