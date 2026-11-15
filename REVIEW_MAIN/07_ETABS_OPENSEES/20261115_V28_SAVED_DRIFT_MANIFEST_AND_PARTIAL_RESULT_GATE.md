# V28 — Saved seismic drift source, manifest and completion integrity

Date: 2026-11-15. Base main SHA `d1284fe9a9ee74502b35317dae9bbf20063a396e`.
Classification: `SOURCE_OUTPUT_VALIDATION_HARDENED_ETABS_OPENSEES_NATIVE_EQUIVALENCE_OPEN`.

## Source findings

1. `components/inputs/output_contract.py::record_case_status()` previously required only the correct JSON `schema` and an allowed target status. A copied/edited manifest whose `stage`, `state`, `case_id`, `run_id`, units or source hash did not match the actual folder could be marked `RUNNING`/`COMPLETED_SOLVER_ONLY`. It now calls `inspect_case_manifest()` before mutation and refuses any invalid result with the original bytes unchanged.
2. `inspect_case_manifest()` previously followed a linked `CASE_MANIFEST.json` or linked direct run/manifest folder without explicitly reporting a linked source identity. It now flags `LINKED_CASE_MANIFEST_PATH`, not an automatically valid run; this is read-only.
3. `components/validation/design_checks.py::saved_drift_solver_status()` previously read `solver_status` directly from the closest `CASE_MANIFEST.json`, accepting an incomplete JSON object such as `{"solver_status":"COMPLETED_SOLVER_ONLY","model_sha256":"..."}` as proof of a completed analysis. Now the same complete stage/state/case/run/units/subfolder/source SHA preflight is applied before acknowledging `COMPLETED_SOLVER_ONLY`; invalid manifests yield `INVALID_RUN_MANIFEST` and source drift numeric PASS is withheld as `NOT EVALUATED`.
4. `scan_drift()` previously appended valid early saved rows before hitting later malformed CSV or MRSM JSON rows; rejected file warnings could coexist with misleading earlier PASS rows. V28 buffers each full source-file's relevant rows and only commits them if all parse successfully. Symlinked CSV and MRSM JSON result files are rejected. A JSON file with multiple cases is accepted or rejected as one evidence file.

## Regression evidence and remaining limitations

- `tests/test_unified_output_contract.py`: incorrect case/stage/run identity, invalid units, linked canonical manifest, unchanged source when status write rejected, valid existing status update.
- `tests/test_v135_drift_source_completion_v13.py`: incomplete status+hash-only manifest cannot grant completion; complete canonical run can; tampered stage/case/run metadata blocks; corrupt later CSV/MRSM row excludes all prior rows from that file; valid CSV still parses.
- `.github/workflows/nltha-quality.yml`: new push path trigger for `tests/test_v135_drift_source_completion_v13.py` so a test-only correction runs on main.
- The initial V28 source commit's old test failed because the historical fixture explicitly expected a schema-less manifest to certify completion. The fixture was corrected to construct a full canonical manifest. This failure was software behavior, not an ETABS/OpenSees solver fault.

### Engineering judgment
A manifest-verified `COMPLETED_SOLVER_ONLY` is a **software provenance gate**, never NBC 105:2025 acceptance. The saved response still requires: exact source EDB/workbook/model SHA equivalence, signed load/reaction and seismic mass agreement, mode shape/period comparison, mesh connectivity and support DOFs, native linear/drift results and independent engineering review. None of those are demonstrated by these tests.

### Structured native result path
```text
<SELECTED_LOCAL_EXPORT>/05_MRSM/RUNS/<ULS_OR_SLS>/<CASE>/<RUN_ID>/
    00_INPUT_SOURCE/CASE_MANIFEST.json
    01_LOGS/
    02_RESULTS/MRSM_Results_V132.json
    03_EXCEL/
    04_FIGURES/
    05_COMPARISONS/
    06_REVIEW/
    07_EXPORT_ZIP/
```
For ESM use `03_ESM` and `Drift_Check_*.csv`; for other stages preserve their canonical ownership. Existing `OpenSees_Analysis_Results` historical read compatibility is retained. No original ETABS EDB/Excel, real seismic records or saved result folders were moved or edited in this source review.
