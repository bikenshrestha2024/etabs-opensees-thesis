# project_workbooks.py — source documentation

The Rayleigh reader accepts V126 with the tied-floor displacement evidence for both axes. It checks state, assembled-model and story-weight fingerprints and directional Aw. Where the source-linked first-storey sections verify the reviewed 12 m X wall geometry, the shared importer uses the grouped Aw before comparing the cached Rayleigh result. V123 is retained for historical review. See [Rayleigh and grouped-wall verification](../../../validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md).

2026-11-10 extension: `registered_project_source(export_dir, role)` reads
`project_sources.private.json` in the selected export or code root, or the
`OPENSEES_PROJECT_SOURCES` location. It checks the current EDB and registered
source SHA256 before returning a path; changed sources raise ValueError.
Roles: etabs_assignment, etabs_full_table, nbc_calculator, nbc_engine and optional
etabs_linked_audit. No source file is changed. Unscoped drive-specific workbook
discovery was removed. `_calculator_sync_summary` reads original-engine
labelled adopted T1 (seconds) and Aw (m²), separately from modal/Rayleigh data.

**Python source:** [components/inputs/project_workbooks.py](../../../../components/inputs/project_workbooks.py)
**Git baseline content SHA:** 7fa25b152078d65fe65c964dcd48e18587a0872a
**Subsystem:** ETABS/source inputs and earthquake motions
**Priority:** P1 — verify with unit/integration tests

## Responsibilities and contracts
Part of the inputs implementation subsystem. Check the exact classes/functions, argument names, return structures and imported callers in the linked source before altering its interface. This guide documents engineering verification obligations, not an already-completed API test.

## Source, inputs, units
Document original ETABS export path/SHA, declared kN-m-s model units, stress conversion, local axes, accepted coordinate/section mapping and any third-party scientific input. Do not substitute nominal reinforcement, material grade or a literature benchmark for tested project data.

## Outputs and failure conditions
Capture source commit SHA, model/ground-motion fingerprint, ULS/SLS, record orientation, completed physical duration, solver diagnostics, exception traceback and linked reports. Mark failed or truncated runs and do not include them in thesis rankings.

## Research and standards
Relevant register IDs: R10. Consult [research reference register](../../../00_RESEARCH_REFERENCES.md). These identify potentially applicable publications, not proof of parameter calibration or test reproduction.

## Regression acceptance
Review source syntax and imports, create a focused unit test, then run an isolated OpenSeesPy component or ETABS-comparison benchmark where applicable. For full-building NLTHA require all [thesis acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module documentation index](../../00_SOURCE_GUIDE_INDEX.md)


## Source-verified engineering behavior (2026-11-05)

- `source_workbooks(root,export_dir,limit_state)`: read-only spreadsheet discovery. The EDB identity in `SCALING SUMMARY!B4` is matched using portable Windows-path semantics, not the host OS `Path(...).stem` assumption. Reject a source with a different EDB/floor or state; do not bypass this via a hard-coded filename fallback. If source is ambiguous, return no scaling workbook rather than a guessed Aw.
- `import_project_inputs(...)`: `NBC Calculator!B9/B10/B11/B15/E10` imports site type, Z, I, factor and named system references. `SCALING SUMMARY!B14/B15` imports workbook Aw-X/Y; `C14/C15` contains adopted reference T, NOT a freshly computed Rayleigh period. Each value retains spreadsheet source/sheet/cell in the audit. Workbook formulas are not recalculated by openpyxl.
- `_wall_aw_from_lines(H, lines)`: computes directional NBC §5.1.2 effective first-storey wall index from axis, plane, thickness and contiguous *net* lengths. Must not bridge disconnected pier gaps. `_wall_aw_from_patches(H,base,first,patches)`: checks the wall footprint across each vertical mesh slice and rejects changing footprints/openings rather than unioning separate heights into one fictitious effective section.
- Wall construction includes normal/axis mapping only for axis-aligned shells; rotated, discontinuous, unusual openings or source thickness gaps require independent geometry interpretation. The tool does not replace ETABS plan/detail/rebar reconciliation. The general H from nodes may be unsuitable if basements are included under NBC §5.1.2; independent check of the seismic-base convention is required.
- Rayleigh imports are matched to state, model hash, seismic weight hash and Aw. No change to the source ETABS data or original workbook is allowed.

**New checks:** `tests/verify_esm_aw_period_provenance.py` and `tests/verify_nbc105_periods.py`; synthetic regression proof only. See [full professional parameter manual](../../../review/20261105_PROFESSIONAL_STRUCTURAL_ENGINEERING_PROVENANCE_MANUAL.md). Old baseline SHA is historical, not the current source blob.

Publication extension: the resolver also reads excel/SOURCE_REGISTRY.json with
paths relative to the registry. Git LFS pointers are reported with a pull
instruction. copy_project_workbooks copies the three established small inputs
to export/excel/source and retains verified references to larger source files.


## 2026-11-15 verified context contract source review

Authoritative project workbook source registry fallback previously used Path(__file__).parents[2], incorrect under root exec facade OpenSees_Project_Inputs_V123 and could miss project_sources.private.json / excel/SOURCE_REGISTRY.json. Source-aware _runtime_repo_root now uses _component_source (when root facade) or real component __file__ (when direct import). Preserve labeled Aw/T1 workbook values and EDB matching; no source EDB/XLSX change.

Scope of tests: synthetic direct-module import, exec-root facade, exported-runtime facade path consistency in `tests/test_facade_runtime_context.py`. No native ETABS/OpenSees, source workbook or full engineering model was executed in these path-only regressions.

## 2026-11-17 — explicit NBC Excel reader memory and provenance review

The source-inspected read_explicit_excel_calculation(workbook_path, export_dir, limit_state) uses openpyxl in read-only/data-only mode to extract labelled Aw-X/Y and optional adopted T1X/Y. The method separately classifies same-source EDB path, byte-identical EDB copy and DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY; **code_accepted remains false**. This is source evidence, not NBC design acceptance.

A confirmed memory issue existed in the final provenance check: hashlib.sha256(path.read_bytes()) duplicated the entire Excel source ZIP in Python memory after it had been parsed. On a large user-selected workbook, this creates an avoidable full-file allocation and may induce swapping or failure. The correction uses hashlib.file_digest(open_binary_stream, 'sha256') on Python 3.12, preserving the exact digest, Aw/T extraction, source identity and research-only restrictions. A deterministic test forbids whole-file XLSX Path.read_bytes() and checks the output SHA against an independently computed expected digest.

This correction does NOT change NBC 105:2025 Aw calculations, source piers/opening grouping, ULS/SLS source state, effective period, ESM/MRSM factors, root EDB selection or native OpenSees model assembly. Large workbook parsing may still take time and must be profiled separately. Native ETC/ETABS numerical and 32/76/97 reaction comparisons remain unverified.


## 2026-11-22 — current ETABS Excel source priority

For a model export containing `01_ETABS_EXPORT/00_MANIFEST/PROJECT_SOURCES.private.json`, that exact EDB SHA-256-linked manifest is the **only** source of current NBC calculator and scaling references. The active source roles are `nbc_calculator`, `nbc_scaling_uls`, and `nbc_scaling_sls`. A role not registered is **missing**, not permission to search the repository's `excel/source`, sibling model folders or historical workbooks. Any registered file whose bytes have changed fails closed, and a registered scaling sheet must identify the exact EDB bytes via `SCALING SUMMARY`.

For rebuilt models with `require_model_aligned_workbooks=true`, the stronger `MODEL_ALIGNED_12M_WORKBOOK.json` manifest and native source geometry gate remain authoritative; they take precedence over global repository defaults. This preserves separate ULS/SLS selection and prevents an older 4 × 6 m wall assumption being reintroduced as a current 2 × 12 m X-wall input. An unverified Excel workbook is never silently substituted.

Registration is a prerequisite, not a claim of physical or NBC acceptance. Workbook formula caches are *read* but are not recalculated by openpyxl. A missing or stale result must be re-exported and re-registered against the source EDB and wall geometry; engineering checks remain open.

Regression: `tests/test_current_excel_manifest_all_modules.py`.

## 2026-11-22 direct Excel path identity correction

`read_explicit_excel_calculation()` is a **user-selected research-reference reader**, not equivalent to the stronger current registered workbook manifest. A same-string source EDB pathname no longer earns `SAME_EDB_PATH_REFERENCE` if the actual EDB file is absent. Real byte-identical renamed copies can be labelled `BYTE_IDENTICAL_EDB_REFERENCE`; different or inaccessible files stay `DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY`. No workbook is modified; `code_accepted` remains false. Importantly, a currently accessible same-path EDB alone still does not prove that an older XLSX was calculated from the identical **historical revision**—that requires independent recorded source hashing and model-aligned geometry evidence before production adoption. Regression: `tests/verify_esm_explicit_excel_method.py`.
