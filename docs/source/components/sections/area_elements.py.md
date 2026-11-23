# area_elements.py — Area-element integration for floor shells and nonlinear walls

**Python source:** [components/sections/area_elements.py](../../../../components/sections/area_elements.py)
**Current Git blob SHA:** b7c79053ac2b8a2a6c33516f07a0ec5894fc6c74
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Provides ETABS area mesh import, ShellMITC4 floor sections and E-SFI wall instantiation with project FSAM materials; also audits seismic mass and uniform area-load transfer.

## Explicit assumptions and known deficiencies
The area adapter's wall macro-fiber discretization path is not necessarily equivalent to the five-macro-fiber-per-quad setting in main components/model/assembly.py. Do not claim two code routes are the same without an element-by-element geometry/response comparison.

## Required thesis engineering changes
Compare geometry, wall fiber widths/thicknesses, actual surface reinforcement, normal directions, areas, opening borders, floor-to-wall joints and density/mass handling. Add small-mesh convergence and isolated panel benchmarks using the same material card in both code paths.

## Cited scientific context
R01, R02 and R13 (R13 is an alternative element family, not identical to E-SFI).
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

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
