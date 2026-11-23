# output_layout.py — canonical copy-only stage paths

**Source:** project repository policy, [engineering/rules/PROVENANCE.md](../../../../engineering/rules/PROVENANCE.md) and [MODULE_BOUNDARIES.md](../../../../engineering/rules/MODULE_BOUNDARIES.md), 2026-11-14. No external experimental DOI supports a filesystem organization rule.

**Purpose:** one deterministic source of naming for `01_ETABS_EXPORT`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`. This resolves a **review snapshot parent only**; moving active generated solvers, model files or results is not part of this change.

**Inputs/outputs:** `export_root_for(path)` accepts a Path/string inside a known `OpenSees_Analysis_Results` or stage folder. It returns the nearest identified export root as Path. If no recognizable ancestor exists, it treats the supplied path as an explicit export root. `review_snapshots_for(path, stage)` validates stage and returns `<export>/<stage-folder>/REVIEW_SNAPSHOTS`; caller must explicitly create the destination. Case-sensitive source files are not renumbered or rewritten. Units: filesystem paths only, no engineering units.

**Side effects:** none. No ETABS OAPI, Git LFS, internet/network access, solver or shell load. Does not inspect files or claim model identity. Resolve paths only from selected case root; do not mix case state/configuration or historical results based on a matching folder name.

**Failure modes:** unknown stage raises `ValueError`. The caller remains responsible for matching source SHA, project EDB and all relevant analysis provenance; as with existing legacy exporter, a free-form folder outside a known layout is treated as export root and must be explicitly confirmed by the calling application.

**Validation:** `python -m unittest tests.test_output_layout tests.test_esm_organized_export_gui tests.test_organized_results -v`. CI is software evidence only. On Windows verify an existing live `OpenSees_Analysis_Results/ULS_Model` maps to the correct parent for ESM and gravity, that old result readers keep working, and no private EDB/XLSX moves into a public Git repository.

**Acceptance:** canonical review folder consistency is a presentation/traceability screen, not NBC 105:2025, ETABS/OpenSees or nonlinear structural acceptance.


## Cross-stage index from existing export organizer
The optional `write_stage_index(export_dir)` writes atomically to `01_ETABS_EXPORT/00_MANIFEST/analysis_stage_index.json`, recording the seven canonical stage names, whether each folder exists, number and relative path of saved review snapshots, latest pointer (where present), and whether the historical `OpenSees_Analysis_Results` tree exists. This is invoked by existing `09_ORGANIZE_ETABS_EXPORT.py` after creating its non-destructive audit mirror. It does not create missing stage directories or look inside EDB, Excel or solver files; `engineering_status` is always `NOT_ASSESSED_BY_FILE_INDEX`. A missing stage is not proof no run ever happened in a legacy location. A stage with a folder is not proof a model was solved. Source review: 2026-11-14 UI/folder evidence.


## 2026-11-15 stage index path consistency

`write_stage_index` refuses a selected export root (or its parent path) that is a symlink **before** calling `resolve()`. The stage index now differentiates `legacy_analysis_results_present=false` from `legacy_analysis_results_link_refused=true` when an old `OpenSees_Analysis_Results` path is linked. For ESM, a symlinked `LATEST_ESM_COMBINED_EXPORT.txt` is ignored so an ordinary unlinked `LATEST_ORGANIZED_RESULT.txt` remains discoverable. Previous index consumers retain the original fields; one additive boolean field was introduced. Tests use synthetic temporary paths only; this does not change the canonical output folder mapping or relocate existing result files.


`result_roots()` resolves legacy linear and nonlinear history folders consistently for a stage key, canonical folder name, or legacy alias. When both layouts exist, discovery returns the canonical stage before the corresponding legacy stage.


## 2026-11-23 — Stage-owned new review files from legacy selections

The selected native/legacy analysis-output folder remains a **read-only source** for historical case evidence. `stage_review_owner(export_dir, selected_output, stage)` maps new review publication under the owning `03_ESM` or `05_MRSM` stage when the GUI selected an old `OpenSees_Analysis_Results` location or another stage within the same export. Existing canonical run folders preserve their own local `07_EXPORT_ZIP`; explicit outside-export custom locations remain opt-in overrides. The ESM legacy route comparison writes to `03_ESM/COMPARISONS`, and seismic review ZIPs to `<stage>/07_EXPORT_ZIP` with snapshots in `<stage>/REVIEW_SNAPSHOTS`. No existing files are moved or invalidated; see `tests/test_stage_owned_seismic_legacy_routing.py`. This is **folder provenance only**, not native structural acceptance.


## 2026-11-23 — Stage-filtered saved result discovery

The read-only `result_roots(source, stages=..., include_legacy=...)` honors the requested owning stage even when the user GUI passes a selected directory nested under a different module. A selection inside `03_ESM/REVIEW_SNAPSHOTS` must not be appended to a `MODAL`-only or `MRSM`-only search, because that could mix response evidence from independent stages. A selected case beneath the requested canonical stage, its compatible LTHA/NLTHA aliases, or an explicitly included legacy shared results tree remains discoverable. Unknown unstructured directories are not treated as solved cases solely because they exist. Only directories are selected, never engineering-approved responses: model SHA, support policy, mass policy, state and solver completeness remain reader acceptance gates. This change does not rename, copy or delete any existing results. Regression: `tests/test_unified_output_contract.py`.
