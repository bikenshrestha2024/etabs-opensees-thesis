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
