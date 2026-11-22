# ETABS current analysis and beam-force table provenance

**Source:** `components/inputs/etabs_table_bundle.py`.

The user's current ETABS analysis tables and three separate `Beam Forces Element` workbooks are registered **by exact local path and SHA-256** under the original source EDB's `01_ETABS_EXPORT/00_MANIFEST/PROJECT_SOURCES.private.json`. The registration is on-PC only: no workbook is uploaded to GitHub, renamed, moved or edited. Source model EDB SHA is required. The registry includes sheet-name inventories, file sizes and source-path provenance for each role. Files with the same paths assigned to different roles or identical beam-force workbook contents are rejected.

The role `etabs_full_table` is available through the existing `registered_project_source` resolver, including when the active model is a nested `02_MODEL/REBUILDS/VERIFIED_CLEAR_BEAM` version. `etabs_assignment` is registered only when the chosen source has the required eight ETABS material/frame/offset/loads sheets; otherwise it must be supplied separately. Beam force roles are inventoried but not consumed as solver results without independent element-ID, load-case, coordinate-axis and unit checks.

**This is file registration, not physical ETABS/OpenSees agreement.** Spreadsheet contents, shell properties, wall connectivity, loads, floor weights, end offsets, support reactions, and NLTHA remain separate engineering gates.
