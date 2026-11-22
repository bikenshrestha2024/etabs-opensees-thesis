# review_zip_paths.py — one ZIP destination contract

**Owner:** `components/inputs/review_zip_paths.py`. **Scope:** archive placement only, not solver files or code/engineering approval.

`review_zip_directory(selected)` returns the nearest canonical case run's `07_EXPORT_ZIP` when the selected source lies under its `02_RESULTS`, `06_REVIEW` or any other case subfolder. The case is evidenced by `00_INPUT_SOURCE/CASE_MANIFEST.json` and a preexisting seventh folder. A pre-manifest run already having `02_RESULTS` and `07_EXPORT_ZIP` also keeps its case-specific folder. For a legacy standalone output root, the destination is `<selected>/07_EXPORT_ZIP`. A named directory already **inside** the seventh folder (e.g. `07_EXPORT_ZIP/Gravity_Evidence_Upload`) is preserved, not collapsed to its parent.

`ensure_review_zip_directory(selected)` creates only this derived ZIP folder, rejects symlink redirects, and never touches EDBs, solved cases, already published archives or older result manifests. ZIP files retain dated names/unique revisions. No automatic relocation/deletion of earlier off-folder ZIPs is performed, because existing exports are immutable evidence and old pointers may be in use.

**Consumers:** `components/validation/seismic_review_bundle.py` (MRSM/ESM auto/manual), `components/ui/organized_results.py` (MRSM and categorized module snapshots), `components/ui/history_review_tools.py` (LTHA/NLTHA review exports), `components/equivalent_static/organized_exports.py`, `components/equivalent_static/evidence_bundle.py`, `components/gravity/comparison_bundle.py`, `components/gravity/mesh_cases.py`, `components/validation/gravity_native_equivalence_preflight.py`, and `tools/ETABS_EQX_EQY_PDELTA_EXPORT.py`. Gravity evidence workflow already has a dedicated named `07_EXPORT_ZIP/Gravity_Evidence_Upload` owner and remains compatible.

**Smoke test:** `python -m pytest -q tests/test_canonical_review_zip_routes_20261122.py tests/verify_seismic_review_bundle.py tests/test_organized_results.py tests/verify_gravity_evidence_workflow.py`. This tests archive routing and source immutability, not physical validity.

**Safety:** The contents and manifest of ZIP exports may contain project information and source paths; destination is local. Nothing is uploaded automatically. A ZIP with successful numerical outputs does not establish validated geometry, mass, material properties or NBC acceptance.
