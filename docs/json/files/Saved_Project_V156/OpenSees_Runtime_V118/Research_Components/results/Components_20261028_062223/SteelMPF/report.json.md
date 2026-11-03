# Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/results/Components_20261028_062223/SteelMPF/report.json

**Source:** [Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/results/Components_20261028_062223/SteelMPF/report.json](../../../../../../../../../Saved_Project_V156/OpenSees_Runtime_V118/Research_Components/results/Components_20261028_062223/SteelMPF/report.json)
**Classification:** IMMUTABLE_HISTORICAL_PROJECT
**SHA-256 (source bytes):** 538ea3b4b40401f42efdc156c8c723e8c682baef4fce963d94668ef5856a876c
**Size:** 3068 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.fyp | number |
| $.input.parameters.fyn | number |
| $.input.parameters.E0 | number |
| $.input.parameters.bp | number |
| $.input.parameters.bn | number |
| $.input.parameters.R0 | number |
| $.input.parameters.cR1 | number |
| $.input.parameters.cR2 | number |
| $.input.parameters.a1 | number |
| $.input.parameters.a2 | number |
| $.input.parameters.a3 | number |
| $.input.parameters.a4 | number |
| $.input.parameter_basis | str |
| $.input.specimen_id | str |
| $.input.citation | str |
| $.input.source | str |
| $.input.protocol_csv | str |
| $.input.measured_csv | str |
| $.input.fit_bounds | object(empty) |
| $.input.train_fraction | number |
| $.input.scope | str |
| $.input.wall_formulation | str |
| $.input.targets | array |
| $.input.targets[] | number |
| $.input.samples_per_leg | integer |
| $.input.dt_s | number |
| $.input.sources | object |
| $.input.sources.Mander_theory_1988 | str |
| $.input.sources.Mander_experiment_1988 | str |
| $.input.sources.Concrete02 | str |
| $.input.sources.ConcreteCM | str |
| $.input.sources.Steel02 | str |
| $.input.sources.SteelMPF | str |
| $.input.sources.FSAM | str |
| $.input.sources.E_SFI_2023 | str |
| $.input.sources.E_SFI_authors | str |
| $.input.sources.PEER_2015 | str |
| $.input.sources.FVD | str |
| $.input.sources.BRB | str |
| $.input.sources.Outrigger_optimization_2021 | str |
| $.input.sources.Outrigger_2010 | str |
| $.input.sources.NBC2025 | str |
| $.input.sources.Diaphragm | str |
| $.input.project_transfer_approved | boolean |
| $.input._output | str |
| $.optimizer | object(empty) |
| $.metrics | object(empty) |
| $.status | str |
| $.elapsed_s | number |
| $.finished_at | str |
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

[All JSON files](../../../../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../../../../00_RESEARCH_REFERENCES.md)
