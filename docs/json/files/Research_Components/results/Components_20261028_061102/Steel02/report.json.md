# Research_Components/results/Components_20261028_061102/Steel02/report.json

**Source:** [Research_Components/results/Components_20261028_061102/Steel02/report.json](../../../../../../../Research_Components/results/Components_20261028_061102/Steel02/report.json)
**Classification:** PROJECT_DATA_OR_REPORT
**SHA-256 (source bytes):** f8e83728b1ffaaea7a8fc6a520ccee09ed6d6c91c17514465a5cdc8d86df97ee
**Size:** 3145 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.input | object |
| $.input.model | str |
| $.input.parameters | object |
| $.input.parameters.Fy_MPa | number |
| $.input.parameters.E_MPa | number |
| $.input.parameters.b | number |
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

[All JSON files](../../../../../00_ALL_JSON_FILES.md) · [Research citations](../../../../../../00_RESEARCH_REFERENCES.md)
