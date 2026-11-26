# folder_audit.py — source-owned canonical folder inspection

**Authoritative source:** `components/inputs/folder_audit.py`. **Software policy:** `AGENTS.md`, `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261114_CANONICAL_STAGE_FOLDER_AND_MIGRATION_AUDIT.md`, and `components/inputs/output_layout.py`. These are local path/provenance conventions and **not** seismic code clauses or research claims.

## Purpose

Create a repeatable, non-destructive inventory of source export files and the registered numbered analysis and auxiliary stage folders. The audit also identifies loose files directly under stage roots; it never moves active or historical outputs. Distinguish **file organization** from structural acceptance. An empty drift folder, nominally successful gravity or modal log, and an output ZIP are not proof of ETABS–OpenSees equivalence.

## Inputs, outputs and side effects

- `audit_export_structure(export_dir, verify_copies=True)`: accepts a local export root Path or an existing path inside a recognized canonical/legacy stage. Reads **directory listings**, file names and sizes; hashes only the source and categorized **mirror copies** when both are present and SHA checking is selected. Returns JSON-compatible dictionary. It doesn't create files or modify any model data.
- `write_folder_audit(export_dir, verify_copies=True)`: uses the read-only audit above and **creates** timestamped `Folder_Audit_*.json` and `.md` under `01_ETABS_EXPORT/00_MANIFEST/FOLDER_AUDITS/`. Never overwrites an older report. Reports include local absolute paths and must not be committed to public GitHub.
- `22_AUDIT_EXPORT_FOLDERS.py <export_root> [--mirror] [--skip-hash]`: optional `--mirror` creates classified copies with SHA verification using `export_mirror()`; originals and legacy result files remain unmoved. `--skip-hash` only inventories names and presence, so cannot certify mirror identity.

The launcher resolves a path inside a known analysis stage to its owning export root before mirroring or writing the audit.
- `09_ORGANIZE_ETABS_EXPORT.py` now additionally writes this audit after its existing mirror and stage-index procedures, preserving its existing return value and console status.

## Classification and observed limitations

- Source flat files may still be required by old import/readers. The audit lists them even when their mirror copies exist, **intentionally**.
- `*.processing.json`, `*.processing.log`, `*.partial` and `*.tmp` are ephemeral run sidecars and excluded from the export mirror.
- Classification follows the existing `export_mirror.classification` heuristic. A module called `Gravity_*.json` in an export root is copied under source-load classification for backward compatibility; no analysis results are moved into `02_GRAVITY` based solely on file names.
- All canonical analysis and auxiliary stage folder names, immediate child directories and loose file names are reported. `02_MODEL`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`, `REVIEW_MAIN`, and `00_SOURCE_MANIFEST` are registered, not unexpected. Unexpected top-level directories and loose stage files receive separate findings. There is no recursive payload inspection, native solver validation, mass verification, or assertion of a valid NBC model.
- Unsupported extensions, confidential source EDB, private manifest names and historical ZIPs aren't copied into Git by these tools.
- Existing copy with different SHA is a **conflict**, not repaired automatically.

## Tests and native evidence

`python -m unittest discover -s tests -p "test_folder_audit.py" -v`; `python -m pytest tests/test_export_mirror.py` for the original mirror behavior; optional Windows smoke tests of existing export root, a partial legacy export and a source/copy hash conflict. Native ETABS/OpenSees engineering comparisons remain separate.

## Risks

A large source mirror incurs I/O cost; avoid running the `--mirror` step on an actively writing export directory. A source-mutating external process can change files between the inventory and copy; keep the input export frozen and review hashes. Result reports contain potentially sensitive absolute filenames, so **do not upload them automatically**. A physical model that passes gravity global equilibrium but differs at individual foundation reactions remains **NOT STRUCTURALLY VALIDATED**.


## Legacy symlink audit hardening (2026-11-15)

The read-only folder auditor now refuses to traverse `OpenSees_Analysis_Results` when this legacy directory is a symbolic link. It reports `symlinked_legacy_analysis_root=true` and a blocked `SYMLINKED_LEGACY_ANALYSIS_ROOT_BLOCKED` finding. Previously the legacy enumeration relied on `Path.is_dir()`, which follows directory symlinks and could expose names of projects outside the selected ETABS export. A synthetic temporary-folder test checks non-disclosure and absence of derived output writes. The directory itself remains untouched; no solver calculations or legacy result layouts are altered.


## 2026-11-24 — compact-case path risks across every owning stage

`audit_export_structure` now reports `long_case_directories` for the immediate `RUNS/<state>/<case>` path of **every** canonical/auxiliary stage from `ALL_STAGE_FOLDERS`, plus direct historical `OpenSees_Analysis_Results/<case>` directories. This is a bounded metadata-only scan: it does not descend into solver outputs, ZIPs, EDBs, Excel, linked stages, linked state folders or linked cases. It refuses to read through symlinked case directories.

A case is flagged when its folder component exceeds **48 characters** or its path exceeds **220 characters**; 220 is an advisory Windows path budget reserved for future run ID and result filenames, not a claim that Windows always rejects the path. Each report row records source stage, relative folder, case label length, lexical path length, reason and status `REVIEW_ONLY_NO_FILES_CHANGED`. Summary includes `LONG_CASE_DIRECTORY_NAMES` as an ORGANIZATION finding, never structural or solver failure. `write_folder_audit` adds the total to the local Markdown audit.

Use this inventory when checking old 95 m ETABS/ULS long run folders. The folder audit does not shorten or migrate them. A source SHA is required to derive the documented compact new-manifested-run label, and old solver readers/Windows scripts must remain intact until their own migration is validated. **Never commit a generated local audit:** it can contain identifying project paths. Tests: `tests/test_folder_audit.py`.
