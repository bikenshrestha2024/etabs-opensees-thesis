# V29 — Saved seismic response source-identity audit

Date: 2026-11-15. Main baseline: `9bc2aa1a9bede8dc8932d6b12ea0660e9b20043e`.
Software acceptance: `SOURCE_HASH_READER_HARDENED_NATIVE_EQUIVALENCE_OPEN`.

## Confirmed defects

1. `components/validation/saved_case_identity.py::source_model_hash_evidence` resolved paths before checking whether the original saved result or an intermediate ancestor was a symlink. A linked MRSM JSON file or linked ESM metadata sidecar could be consulted as matching serialized model evidence without an explicit warning.
2. The reader previously discarded malformed explicitly supplied `model_sha256` values as if the hash were simply absent. If the nearby manifest had a valid hash, the result might still appear `MATCHED_SERIALIZED_MODEL_SHA_NOT_ETABS_EQUIVALENCE`. An explicitly invalid claimed hash is negative provenance evidence and must not be silently promoted by an unrelated manifest.
3. `current_export_model_sha` could hash a linked model source file rather than the declared local serialized model.

## Applied code and tests

- Report `linked_source` and exclude linked results or ESM sidecars in `identity_screen` under `LINKED_RESULT_EVIDENCE_EXCLUDED`.
- Report `invalid_payload_sha`; exclude an explicitly present invalid digest under `INVALID_RESULT_MODEL_SHA_EXCLUDED`. Preserve the historical `NOT_VERIFIED` policy when an optional digest is *absent* (None), which is not the same as an invalid value.
- Refuse the linked canonical serialized model file for active model fingerprinting.
- Added focused regression cases in `tests/test_saved_case_identity_v142.py` and corrected an obsolete expectation in `tests/test_post_v8_missing_coverage_v9.py` so a malformed 64-character string cannot appear accepted.
- These changes are read-only and do not alter original EDB, authoritative Excel Aw/T1, native solver results or any historical saved source file.

## Native engineering evidence not established

Equal serialized JSON SHA does not establish actual EDB equivalence, RCC member/wall local axes or stiffness, support topology, slab-frame gravity loads, modal mass, response spectra, real record pairing, damping and sensitivity qualification. Saved visualizations must remain distinct from engineering certification. The known nonlinear X-wall transient issue and 32/76/97 physical support ambiguity remain open.

## Suggested review output under the selected private export

```text
<EXPORT>/08_ETABS_COMPARISONS/RUNS/<STATE>/<CASE>/<UTC_RUN>/
  00_INPUT_SOURCE/   input EDB/model/record provenance and SHA256
  01_LOGS/           native solver log and comparison console
  02_RESULTS/        validated metric tables
  03_EXCEL/          model comparisons by quantities and units
  04_FIGURES/        identity-verified plots only
  05_COMPARISONS/    ETABS-versus-OpenSees signed reaction and modal benchmarks
  06_REVIEW/         saved evidence issues and independent engineering review
  07_EXPORT_ZIP/     source-hashed evidence package
```
This path is the target convention for migrated writers; old report readers are preserved.
