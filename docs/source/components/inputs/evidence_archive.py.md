# evidence_archive.py — explicit-file case-local ZIP publisher

**Owner:** \`components/inputs/evidence_archive.py\` (imports canonical placement from \`review_zip_paths.py\`). **Purpose:** create a deterministic local review/evidence archive for a selected, already-saved modal run or source-only area-integration inventory. **Engineering acceptance:** NOT VERIFIED.

## API

\`publish_case_evidence_zip(source_run, filename=..., files=[(archive_path, source_file), ...], category=None, status=...)\` returns the saved ZIP path.

- The caller provides each source path and the corresponding portable ZIP entry; the publisher does not search other run folders or include parent projects.
- Reject an empty selection, duplicate or escaping ZIP entry, symlinked source/output, missing file and blocked archive/credential file types.
- Compute source SHA-256 and byte sizes, include an \`EVIDENCE_MANIFEST.json\`, and validate both CRC and extracted SHA-256 values before atomically publishing the ZIP.
- Use \`ensure_review_zip_directory\` so the archive belongs to the nearest selected canonical case's \`07_EXPORT_ZIP\`. Source files are read-only. This function does not upload anything.
- A ZIP may include local file paths already present in copied JSON/provenance records, so inspect it before external sharing.

## Consumers

- \`components/modal/gui_and_reports.py::package_modal_evidence\` packages one completed modal run under \`07_EXPORT_ZIP/NBC105_Modal_<ULS|SLS>_Evidence.zip\`. The GUI can also package an **existing** run without model rebuild, gravity preload or eigen solve.
- \`components/sections/area_elements.py::export_area_integration_inventory\` packages the same selected source topology JSON, area assignment CSV, configuration JSON, inventory workbook and inventory JSON under \`07_EXPORT_ZIP/AREA_INTEGRATION/Area_Integration_Inventory_<SHA10>.zip\`. Existing return API is unchanged.

**No physical model approval:** A correctly packed archive is only evidence transport. Native shell-edge/MPC restraints (32 primary vs 44 mesh nodes), ETABS/OpenSees equivalence, Rayleigh verification, area panel load/mass transfer, FSAM calibration and nonlinear convergence remain separate checks. Do not treat a SOURCE_ONLY inventory or modal mass coverage as a design or NLTHA PASS.

**Regressions:** \`python -m unittest -v tests.test_evidence_zip_publication_20261123 tests.test_model_stage_mesh_area_inventory\`; then run the repository's headless CI and Windows smoke tests. The tests do not execute native ETABS/OpenSees.
