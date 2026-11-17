# 2026-11-17 — direct NBC Excel reference streaming and source identity review

## Scope and evidence

**Active source inspected:** components/inputs/project_workbooks.py, especially registered_project_source (streaming digest precedent), read_explicit_excel_calculation (actual Aw/T extracted from cached Excel cells, source identity and source workbook SHA), and caller components/equivalent_static/calculation_and_gui.py. Test source: tests/verify_esm_explicit_excel_method.py. Source baseline: main commit 67c9ecc2fc761c43e0d13b5a44514938da11578a after XLSX atomic publication PR #97.

## Confirmed defect

NBC-XLSX-01 (P1 software/performance): read_explicit_excel_calculation originally finished by calling hashlib.sha256(path.read_bytes()). This copies the **entire** Excel workbook to an in-memory bytes object solely for a source provenance hash. For a very large ETABS workbook this is an unnecessary memory spike on top of openpyxl's own buffers. The same module already streams registry EDB/workbook hashes in registered_project_source, establishing the correct style.

**Reproduction:** New regression test test_direct_xlsx_sha_streams_without_eager_whole_file_memory in tests/verify_esm_explicit_excel_method.py patches Path.read_bytes to reject entire XLSX reads; confirms exact source workbook SHA256 matches independent hash and verifies source identity remains SAME_EDB_PATH_REFERENCE and code_accepted=False. GitHub PR #98 first RED integrated CI run recorded that assertion failure before the source correction.

**Correction:** replace direct full-file bytes hashing with hashlib.file_digest(workbook_stream, 'sha256') on an explicitly opened binary stream. Python 3.12 standard library; no extra dependencies or network. Existing ULS/SLS, Aw-X/Y and T1-X/Y extraction and matching classification unchanged.

## Semantic data-flow review

1. GUI selection prompts for an actual .xlsx and a single ULS/SLS state.
2. require_source_state(export_dir,state) checks selected state; openpyxl reads cached formula results in read-only/data-only mode, not evaluated formulas.
3. The selected worksheet must expose original source EDB identity and finite positive Aw-X/Y. Optional T1 values are retained only if finite and positive.
4. The source identity is SAME_EDB_PATH_REFERENCE, BYTE_IDENTICAL_EDB_REFERENCE or DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY. A different EDB is a study reference, not silently trusted as the model design source.
5. The full source workbook SHA256 is now calculated without eager full-file memory allocation.
6. The returned code_accepted=False remains a required engineering judgement gate.

## Verification gates

- Source workbook identity, actual selected ULS/SLS, original source EDB and Excel cell addresses must be captured.
- Test exact SHA256, unchanged numerical Aw/T, source mismatch handling and failure on invalid workbook.
- Compare code-dependent effective Aw assumptions and original openings/ETABS geometry separately. No Excel cached formula result proves actual NBC compliance.
- Reconcile 32/76/97 ETABS/OpenSees gravity support reactions and modal/ESM/MRSM T1 and base shear independently; no changes to those calculations were made.
- GitHub CI verifies Python behavior but not native Windows performance for a very large private XLSX.

**Status:** Confirmed software memory defect corrected in branch pending all PR CI; full repository function-by-function semantic review and native engineering gates remain OPEN. No original XLSX or EDB uploaded.
