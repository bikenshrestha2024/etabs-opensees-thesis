# Research_Components/paper_specimens/PEER_2015_12_RW_A15_B3_SFI_INPUTS.json

**Source:** [Research_Components/paper_specimens/PEER_2015_12_RW_A15_B3_SFI_INPUTS.json](../../../../../Research_Components/paper_specimens/PEER_2015_12_RW_A15_B3_SFI_INPUTS.json)
**Classification:** EXPERIMENTAL_SOURCE_REGISTER
**SHA-256 (source bytes):** 3db6916d5ebd97100061364857e93aa26a9b6edbb3dd667095b1fbd528aa62ba
**Size:** 2737 bytes
**Root JSON type:** object
**Content inspection:** Directly parsed from checkout; value units and validation status are NOT inferred.

## Fields actually present

| JSON path | Observed type |
|---|---|
| $.schema_version | str |
| $.purpose | str |
| $.source | object |
| $.source.report | str |
| $.source.appendix | str |
| $.source.printed_pages | str |
| $.source.pdf_pages | str |
| $.source.url | str |
| $.specimen | str |
| $.units | str |
| $.wall | object |
| $.wall.height_in | integer |
| $.wall.thickness_in | integer |
| $.wall.width_in | integer |
| $.wall.axial_kips | integer |
| $.wall.vertical_node_elevations_in | array |
| $.wall.vertical_node_elevations_in[] | integer |
| $.wall.fibers_width_in | array |
| $.wall.fibers_width_in[] | integer |
| $.wall.fiber_regions | array |
| $.wall.fiber_regions[] | str |
| $.wall.height_elements | integer |
| $.steel_mpf | object |
| $.steel_mpf.steelX | object |
| $.steel_mpf.steelX.fy_ksi | number |
| $.steel_mpf.steelX.E_ksi | integer |
| $.steel_mpf.steelX.b | number |
| $.steel_mpf.steelY_web | object |
| $.steel_mpf.steelY_web.fy_ksi | number |
| $.steel_mpf.steelY_web.E_ksi | integer |
| $.steel_mpf.steelY_web.b | number |
| $.steel_mpf.steelY_boundary | object |
| $.steel_mpf.steelY_boundary.fy_ksi | integer |
| $.steel_mpf.steelY_boundary.E_ksi | integer |
| $.steel_mpf.steelY_boundary.b | number |
| $.steel_mpf.transition | object |
| $.steel_mpf.transition.R0 | integer |
| $.steel_mpf.transition.cR1 | number |
| $.steel_mpf.transition.cR2 | number |
| $.steel_mpf.transition.note | str |
| $.concrete_cm | object |
| $.concrete_cm.web_unconfined | object |
| $.concrete_cm.web_unconfined.fpcc_ksi | number |
| $.concrete_cm.web_unconfined.epcc | number |
| $.concrete_cm.web_unconfined.Ec_ksi | number |
| $.concrete_cm.web_unconfined.rc | integer |
| $.concrete_cm.web_unconfined.xcrn | number |
| $.concrete_cm.web_unconfined.ft_ksi | number |
| $.concrete_cm.web_unconfined.et | number |
| $.concrete_cm.web_unconfined.rt | number |
| $.concrete_cm.web_unconfined.xcrp | integer |
| $.concrete_cm.confined_boundary | object |
| $.concrete_cm.confined_boundary.fpcc_ksi | number |
| $.concrete_cm.confined_boundary.epcc | number |
| $.concrete_cm.confined_boundary.Ec_ksi | number |
| $.concrete_cm.confined_boundary.rc | number |
| $.concrete_cm.confined_boundary.xcrn | number |
| $.concrete_cm.confined_boundary.ft_ksi | number |
| $.concrete_cm.confined_boundary.et | number |
| $.concrete_cm.confined_boundary.rt | number |
| $.concrete_cm.confined_boundary.xcrp | integer |
| $.fsam | object |
| $.fsam.web | object |
| $.fsam.web.rho_x | number |
| $.fsam.web.rho_y | number |
| $.fsam.web.concrete | str |
| $.fsam.web.steel_x | str |
| $.fsam.web.steel_y | str |
| $.fsam.boundary | object |
| $.fsam.boundary.rho_x | number |
| $.fsam.boundary.rho_y | number |
| $.fsam.boundary.concrete | str |
| $.fsam.boundary.steel_x | str |
| $.fsam.boundary.steel_y | str |
| $.fsam.nu | number |
| $.fsam.dowel_alpha | number |
| $.scope | str |
| $.paper_transverse_hoop_detail_verified | boolean |
| $.building_rebar_approved | boolean |
| $.building_confinement_approved | boolean |
| $.experimentally_reproduced_in_this_repo | boolean |
| $.important_note | str |

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
