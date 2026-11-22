# Source-matched 12 m workbook reference

**Source:** `components/inputs/model_aligned_reference.py`.

An engineer can register a **local** current workbook against one rebuilt source model *only* after comparing full source EDB SHA256, workbook SHA256, limit-state label, workbook sheet type, and the exported OpenSees first-storey 2 × 12 m X-wall geometry. An ETABS `SCALING SUMMARY` workbook must identify an EDB in its source cell whose bytes are SHA256-identical to the current source EDB. A matching workbook filename or copied 'Copy' suffix is never sufficient.

`register_reference(export_dir, workbook, limit_state=...)` writes only `00_SOURCE_MANIFEST/MODEL_ALIGNED_12M_WORKBOOK.json` and leaves the EDB and XLSX unchanged. The manifest includes the exact source EDB SHA, workbook SHA, state, listed sheets and 12 m geometry verification evidence. The user-uploaded V10.7 workbook is not auto-approved just because it has '12m' in its filename.

`verified_reference(export_dir, state=...)` re-hashes source EDB and original XLSX on every selection, revalidates workbook sheet names and B4 EDB identity, and rejects stale or cross-state evidence. For model variants with `require_model_aligned_workbooks`, `source_workbooks` returns `[None,None]` until this proof exists, then only available recognized sheets from the one exact registered workbook. Older runtime-global ULS/SLS scaling/calculator files are not copied into variants and cannot win a filename ranking.

**Important:** this registers source identity and exported wall geometry, not numerical formula correctness, NBC code certification, full-height wall connectivity, or physical ETABS/OpenSees equivalence. Native EDB model property comparison, slab/beam and rigid-end offsets, reactions and nonlinear convergence remain separate.
