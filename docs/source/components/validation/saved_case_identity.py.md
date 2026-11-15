# Saved seismic response source-identity review — V142

**Source:** `components/validation/saved_case_identity.py`. File-content verification only; **not** ETABS/OpenSees physical model equivalence.

## Contract

`current_export_model_sha(export_dir)` hashes the exact serialized source `OpenSees_Complete_Model_Data_V118.json` if present. `recorded_result_model_sha(path, case)` looks for an explicit `00_INPUT_SOURCE/CASE_MANIFEST.json` model SHA in the run directory; otherwise parses MRSM result case JSON or the corresponding saved ESM response META file. No model identity is inferred from filenames, geometries or ULS/SLS labels alone. Only hexadecimal 64-character hashes are accepted as source-model digests.

`identity_screen(rows, expected_model_sha)` labels each review-only seismic drift/deflection row `MATCHED_SERIALIZED_MODEL_SHA_NOT_ETABS_EQUIVALENCE`, `NOT_VERIFIED` or excludes a known **MISMATCH** from plotted rows. Excluded files are **never modified**; a structured `SOURCE_MODEL_SHA_MISMATCH_EXCLUDED` issue records both digests and source path. Rows with missing hashes remain visible as **NOT_VERIFIED** — they are not automatically adopted as valid code-check evidence.

`components/validation/case_review.py::collect` applies this screen after duplicate path/row removal. Workbook and JSON include the current serialized model SHA and count of mismatch-excluded rows. The UI graph therefore does not silently present a proven incompatible model's drift/deflection.

## Limitations / engineering gates

- Two equal serialized model JSON SHA values do not verify a physical EDB match, ETABS source stiffness, native material assignment, load combination, geometric restraints, mass, support selection, story mapping or complete nonlinear record.
- Historical gravity, conventional ESM, and time-history response files sometimes lack emitted model SHA; their values remain explicitly `NOT_VERIFIED` pending project evidence.
- ULS and SLS generally use **different** source stiffness; source matching is performed relative to the single export case selected in V142. To compare two independently exported states, use an explicitly reviewed cross-model comparison with hashes and source metadata instead of merging them as one source.
- A changed current export model invalidates earlier result fingerprint matches; it does not delete archival data.
- Native Windows GUI and source-only acceptance tests remain necessary. Source code tests use synthetic JSON, not physical ETABS evidence.

**No original ETABS `.EDB`, source Excel, or saved solver result file is altered by this reader.**


## 2026-11-14 independent result-payload / manifest conflict gate V11

`source_model_hash_evidence(path, case)` separately extracts the run's `00_INPUT_SOURCE/CASE_MANIFEST.json` SHA256 and the recorded MRSM/Deformation result SHA256 (or ESM drift META SHA256). If two valid hashes disagree, the saved response is **excluded** from V142 plots and reported as `SOURCE_MANIFEST_RESULT_SHA_CONFLICT_EXCLUDED`, even when the manifest alone matches the currently selected model. `recorded_result_model_sha` returns `None` for such conflicting evidence. When only one valid source exists, it remains an identifiable but **not structurally certified** source; source identity does not establish ETABS equivalence.

Regression: `tests/test_saved_case_identity_v142.py` includes mismatched manifest/payload hashes and a subsequent matching response case. No original EDB, serialized model or response is edited.

## V25 — canonical manifest integrity is a hard exclusion (2026-11-15)

`source_model_hash_evidence()` now exposes `invalid_manifest` and `manifest_path`. A present but malformed, unreadable, missing-hash or symlinked `00_INPUT_SOURCE/CASE_MANIFEST.json` cannot be silently downgraded to an absent legacy manifest while an embedded model hash remains apparently verified. `identity_screen()` excludes the corresponding row under `INVALID_RUN_MANIFEST_EXCLUDED`, retains the exact source path and leaves original data unchanged. A genuinely missing legacy manifest is still treated by the established `NOT_VERIFIED`/available-payload policy, not as a fabricated error. This is serialized model *identity* screening, not ETABS equivalence or experimental calibration. Regression: `tests/test_saved_case_identity_v142.py`.
