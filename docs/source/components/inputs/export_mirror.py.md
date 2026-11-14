# Categorized ETABS export mirror

**Purpose**: Make the selected original ETABS-to-OpenSees export easier to inspect without breaking the numerous legacy flat-path readers.

**Run**: python 09_ORGANIZE_ETABS_EXPORT.py "<selected-export-folder>"

**Inputs**: selected local ETABS export directory, with generated root-level JSON, CSV, XLSX, XLSM, HTML, Python and text artifacts. The original EDB is not copied or modified. No recursive scan is performed. Private source registries are excluded.

**Outputs**: 01_ETABS_EXPORT with 00_MANIFEST, 01_SOURCE, 02_MAPPING, 03_LOADS, 04_VISUALIZATION, 05_AUDITS, 06_CONFIG, 07_LOGS, 08_PROCESSING and 09_REVIEW *as applicable*. Nonempty categories are created on demand. The JSON manifest includes original/categorized paths, size and SHA256. Existing destination with different content causes explicit error.

**Side effects**: copies generated output bytes locally; source files are untouched. Does not rewrite imports or move/rename files. Not a completed canonical path migration. This approach temporarily duplicates disk usage, so review available space before running on a large export.

**Units**: no numerical data conversion; bytes copied exactly. No scientific equivalence claim.

**Test**: python -m pytest tests/test_export_mirror.py -q (not native solver validation).

**Engineering decision**: downstream open/analysis scripts still use original paths. Only after all readers and writers use a model SHA-aware manifest resolver should the flat paths be deprecated. Source EDB remains read-only.
