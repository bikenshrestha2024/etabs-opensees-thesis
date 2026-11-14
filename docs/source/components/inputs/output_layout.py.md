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
