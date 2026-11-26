# area_elements.py — Area-element integration for floor shells and nonlinear walls

**Python source:** [components/sections/area_elements.py](../../../../components/sections/area_elements.py)
**Current Git blob SHA:** 42dad75f133aa2768eced2f40b03e4b1323d32fc
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Provides ETABS area mesh import, ShellMITC4 floor sections and E-SFI wall instantiation with project FSAM materials; also audits seismic mass and uniform area-load transfer.

## Explicit assumptions and known deficiencies
The area adapter's wall macro-fiber discretization path is not necessarily equivalent to the five-macro-fiber-per-quad setting in main components/model/assembly.py. Do not claim two code routes are the same without an element-by-element geometry/response comparison.

## Required thesis engineering changes
Compare geometry, wall fiber widths/thicknesses, actual surface reinforcement, normal directions, areas, opening borders, floor-to-wall joints and density/mass handling. Add small-mesh convergence and isolated panel benchmarks using the same material card in both code paths.

## Cited scientific context
R01 provides specimen material context, R02 details E-SFI-MVLEM-3D, and R13 evaluates the alternative LFSAFE layered-shell formulation. NBC 105:2025 §9.3.1.1 gives the general 3D nonlinear modeling requirements. Annex A §§5.5–5.6 address coupling-beam detailing and wall openings. [Research source register](../../../00_RESEARCH_REFERENCES.md), [NBC 105:2025](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)


## 2026-11-13 — Stage 02 model mesh / area-integration output update

For the full rationale, mesh procedure, distinctions between **source quads** and **assembled meshed ShellMITC4 cells**, evidence requirements and safety warnings, read [the numbered Stage 02 review](../../../../REVIEW_MAIN/00_MODEL/20261113_STAGE02_AREA_INTEGRATION_AND_SLAB_MESH_STUDY.md). Mesh 04/08/16 files are separate case outputs and never a single rebadged baseline. Area inventory is source-only Excel + JSON; it does not instantiate OpenSees elements or validate gravity transfer.


## 2026-11-15 — Open output folder UI
The Area Element Integration V116 window now offers **Open output folder**. It uses `area_output_directory` to open the existing saved integration-call parent directory, else the existing `02_MODEL/AREA_INTEGRATION/` folder (where Excel/JSON source inventory belongs), else the existing export root. It creates no directories and never initiates OpenSees. On Windows it opens File Explorer using `os.startfile`; macOS/Linux use their system openers. It does not approve a wall config or modify the original EDB. A linked canonical output stage is refused. Source-only test: `tests/test_area_folder_and_hinged_brace_review.py`; engineering evidence `REVIEW_MAIN/00_MODEL/20261115_AREA_HINGED_BRACE_AND_MESH_EVIDENCE.md`.


## 2026-11-15 — default Python integration-call export location

The Area Integration GUI now opens its `Save area integration call` dialog in the selected ETABS export root's `02_MODEL/AREA_INTEGRATION/PYTHON/` directory (the default is `OpenSees_Area_Integration_Call_V116.py`). The directory is created if absent so Windows Save As does not silently fall back to the previous arbitrary folder. Selecting an alternate `.py` file still works; non-`.py` targets and symlink final file are rejected. This action creates an **inactive** review snippet (`AREA_STAGE_EXECUTION=False`), not an OpenSees assembled area model or permission to run nonlinear FSAM walls. Original ETABS source input files and folders remain unchanged. Pure helper `default_area_integration_script_path` may be tested independently of Tk/Windows.

## 2026-11-23 — source inventory versus saved instantiated-element ZIP

Area integration now has **two separate evidence exports**.

1. Export area inventory (Excel + JSON + ZIP) packages source topology and assignments. It is a source-only preview; no OpenSees domain was built.
2. Export saved instantiated element ZIP packages an already-saved area-element instantiation audit, including explicit ShellMITC4 / E_SFI_MVLEM_3D element counts, tags and provenance, plus the selected source topology, assignments and config. It requires the report and verifies that the recorded source paths, category counts and element tags agree; otherwise it fails closed. It does NOT rebuild elements or run gravity or NLTHA.

Relative audit_output_json filenames in the area config now save under the selected config's directory rather than the launcher's working directory. Legacy outputs in unrelated directories are not silently selected. Evidence is published with SHA-256 and an NOT_VERIFIED engineering-acceptance status. Historical packages remain readable at their original locations.

Native ETABS constraint/MPC equivalence, material/FSAM calibration, element response, diaphragm compatibility, mass transfer, and full-building NLTHA remain separate unresolved gates.

Synthetic test: tests/test_area_instantiation_evidence_zip_20261123.py.

## 2026-11-23 — model-owned output and nested-folder guard

New area inventory and instantiated-element archives belong under the *same* selected model stage:

```text
<ETABS export>/02_MODEL/AREA_INTEGRATION/
  excel/                 # source-only inventory workbook
  json/                  # source-only inventory and provenance
  PYTHON/                # inactive integration-call template
  07_EXPORT_ZIP/         # area inventory and instantiated-element packages
```

`model_area_directory` recovers the original export root from selections inside `02_MODEL`, `AREA_INTEGRATION`, and `07_EXPORT_ZIP`; callers must not append another `02_MODEL` to an existing module path. New area ZIPs are no longer published under `<export>/07_EXPORT_ZIP/AREA_INTEGRATION`. Existing archives are left intact and are not deleted or moved. The archive manifest still contains source SHA-256 provenance and `NOT_VERIFIED` acceptance. **This fixes output ownership, not element numerical equivalence or NLTHA readiness.**

Regression coverage: `tests/test_model_stage_mesh_area_inventory.py`, `tests/test_area_instantiation_evidence_zip_20261123.py`, and `tests/test_area_folder_and_hinged_brace_review.py`.


## 2026-11-24 — source inventory shown, but no instantiated-element report

A user-selected 25-storey model's source-only area inventory contained **350 FLOOR** quads and **375 SHEAR WALL** quads with zero recorded geometry errors, but no `OpenSees_Area_Element_Integration_Audit_V116.json`. Its selected area configuration intentionally recorded `source_reviewed_by_user=false` and a null FSAM material tag. The separate MESH_04 elastic assembly had >10,000 ShellMITC4 cells; that is **not** an `instantiate_area_elements` audit, nor proof that nonlinear E-SFI-MVLEM wall materials/solver elements were created by the optional V116 helper. The GUI's raw missing-file error from `package_area_instantiation_audit` was technically correct but did not explain this fundamental distinction.

The new **read-only** `inspect_instantiated_area_evidence(config_json=...)` returns a clearly named status: `SOURCE_ONLY_NO_INSTANTIATION_REPORT` when the selected audit does not exist, versus `SAVED_REPORT_PRESENT_NOT_VALIDATED` when a file exists. It identifies the report path relative to the selected configuration, the explicit review flag and missing FSAM target tags. It **never** generates a report, edits the configuration, invokes OpenSees, creates model/fiber elements or upgrades `analysis_ready` or `engineering_accepted`. The GUI uses it before the instantiated ZIP action: absent report → informative warning with independent source/material prerequisites and direction to the existing source-only Excel+JSON+ZIP action. If a report exists, **the existing fail-closed packager still validates** matching source input paths, positive and matching element counts, unique tags and categories; it refuses stale/invalid evidence.

**Do not simply enable** `AREA_STAGE_EXECUTION` in the saved Python call on an already assembled model with floor/wall shells. The optional additive `instantiate_area_elements` is only valid in a compatible domain that does not already contain those same elements, after verified source, material and constraint review. Config templates and literature references are not calibration. Area gravity loads and seismic mass are still separate, and the 32-physical-support + 44-mesh-transfer distinction remains unaffected.

Regression: `tests/test_area_instantiation_evidence_zip_20261123.py` now covers missing report/false approval/null FSAM, read-only source state, untrusted present report and rejected directory traversal. No private EDB, source workbook, active model JSON or Windows absolute path is committed. Native ETABS/OpenSees comparison, wall cyclic validation and NLTHA remain NOT_VERIFIED.

## Source binding in instantiated area evidence

The optional helper checks selected area categories, geometry, tags, inputs and audit destination before issuing the planned OpenSees commands. Floor tags are outside the collision check when only walls are selected. If the solver fails after command execution starts, rebuild the domain before retrying. Use **Export area inventory** for source review, then **Save inactive area script** if the inputs and receiving domain warrant instantiation.

An instantiated area ZIP uses the topology, assignment table, area config and optional section-mapping file digests recorded by the successful helper. The packager checks the saved files against those digests and verifies the ZIP payload before publication. Existing archives remain readable. A legacy report without source digests requires a new run in a compatible domain for packaging. Gravity, seismic mass, wall calibration and NLTHA still require independent evidence.
