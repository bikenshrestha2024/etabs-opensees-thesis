# Source guide — project_output_layout.py

Scope: local output organization and immutable original ETABS EDB provenance. No ETABS API, OpenSees numerical solver, load conversion or structural interpretation is executed.

## Units
Source EDB is an opaque binary file; all SHA256 hashes describe bytes, not physical units. Case paths are filesystem names; no forces/displacements are modified.

## Side effects
Creates `00_SOURCE_MANIFEST/PROJECT_CONTEXT.json` and numbered subdirectories *inside the output root explicitly selected by the user*, and optionally a new case-specific folder. It does not copy the EDB, amend its contents, upload data, move previous runs or change the old `OpenSees_Analysis_Results` path. The manifest logs the original EDB absolute path and SHA256 locally; do not upload it to public GitHub.

## Required verification
- A pre-existing manifest with different EDB SHA256 must raise rather than co-mingle results.
- Every case-id must be a single safe path component; no `..`, path separator, or arbitrary absolute path.
- All run-specific output can be assigned to `case_folder` only after its actual producer/reader dependencies have been updated and Windows-tested.
- Existing `analysis_output_folder` remains the backward-compatible production analysis root. New numbered dirs are created and indexed, **not yet used by all modules**.
- Never treat source metadata creation as ETABS–OpenSees physics equivalence or acceptance.

## References
`AGENTS.md`, `engineering/rules/PROVENANCE.md`, `REVIEW_MAIN/07_ETABS_OPENSEES/ISSUE_20261111_CANONICAL_SOURCE_OUTPUT_ROUTING.md`.

## V22 safe destination handling (2026-11-15)

Project initialization checks existing `00_SOURCE_MANIFEST`, `PROJECT_CONTEXT.json` and canonical stage destinations for directory/file symlinks **before** writing project files. Invalid pre-existing project-context JSON is rejected with a descriptive error without updating it. The project context is written using a unique same-directory temporary file and atomic replacement rather than a shared fixed `.tmp` filename. `case_folder()` rejects linked stage/state/case intermediate components. This is a best-effort application-level path guard (not a guarantee against concurrent filesystem races or all NTFS junction/reparse-point types). It does not change source EDB bytes or original workbook content. Regression: `tests/test_project_output_layout_v171.py`.


2026-11-26: `require_import_root` is a read-only preflight used before GUI log writes and by the worker/layout owner. It rejects stage/run descendants and marked clear-beam variants so that a selected analysis model cannot become a new import target. It does not hash or approve engineering results.

## 2026-11-26 — separate import and rebuild contexts

The immutable clear-beam rebuild is not an import. The rebuild tool reserves a new directory under `02_MODEL/REBUILDS/VERIFIED_CLEAR_BEAM/<unique-run>` (or an explicit standalone CLI destination) and writes its running marker. `require_rebuild_root` checks the destination independently of the strict import guard; `create_rebuild_layout` only binds the freshly reserved variant, checks the original EDB SHA again, and writes a variant-local project context with `layout_kind` and `original_export_root`. It does not create analysis-stage directories or update the original manifest. Existing imports, arbitrary nested stages, links, and reused variants remain blocked. No physical model or load parameters change. Regression: `tests/verify_spyder_clear_beam_rebuild.py` exercises the real rebuild entry through the assembly call with synthetic source evidence and a mocked assembly boundary; this does not certify native gravity.
