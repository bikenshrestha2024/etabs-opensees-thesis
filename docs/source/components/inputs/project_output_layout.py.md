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
