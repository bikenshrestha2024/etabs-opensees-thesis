# folder_audit.py — source-owned canonical folder inspection

**Authoritative source:** `components/inputs/folder_audit.py`. **Software policy:** `AGENTS.md`, `REVIEW_MAIN/08_SOFTWARE_SECURITY/20261114_CANONICAL_STAGE_FOLDER_AND_MIGRATION_AUDIT.md`, and `components/inputs/output_layout.py`. These are local path/provenance conventions and **not** seismic code clauses or research claims.

## Purpose

Create a repeatable, non-destructive inventory of source export files and the seven numbered analysis stage folders. Distinguish **file organization** from structural acceptance. An empty drift folder, nominally successful gravity or modal log, and an output ZIP are not proof of ETABS–OpenSees equivalence.

## Inputs, outputs and side effects

- `audit_export_structure(export_dir, verify_copies=True)`: accepts a local export root Path or an existing path inside a recognized canonical/legacy stage. Reads **directory listings**, file names and sizes; hashes only the source and categorized **mirror copies** when both are present and SHA checking is selected. Returns JSON-compatible dictionary. It doesn't create files or modify any model data.
- `write_folder_audit(export_dir, verify_copies=True)`: uses the read-only audit above and **creates** timestamped `Folder_Audit_*.json` and `.md` under `01_ETABS_EXPORT/00_MANIFEST/FOLDER_AUDITS/`. Never overwrites an older report. Reports include local absolute paths and must not be committed to public GitHub.
- `22_AUDIT_EXPORT_FOLDERS.py <export_root> [--mirror] [--skip-hash]`: optional `--mirror` creates classified copies with SHA verification using `export_mirror()`; originals and legacy result files remain unmoved. `--skip-hash` only inventories names and presence, so cannot certify mirror identity.
- `09_ORGANIZE_ETABS_EXPORT.py` now additionally writes this audit after its existing mirror and stage-index procedures, preserving its existing return value and console status.

## Classification and observed limitations

- Source flat files may still be required by old import/readers. The audit lists them even when their mirror copies exist, **intentionally**.
- `*.processing.json`, `*.processing.log`, `*.partial` and `*.tmp` are ephemeral run sidecars and excluded from the export mirror.
- Classification follows the existing `export_mirror.classification` heuristic. A module called `Gravity_*.json` in an export root is copied under source-load classification for backward compatibility; no analysis results are moved into `02_GRAVITY` based solely on file names.
- Stage folder presence, immediate child directory and loose file counts are reported; there is no recursive payload inspection, native solver validation, mass verification, or assertion of a valid NBC model.
- Unsupported extensions, confidential source EDB, private manifest names and historical ZIPs aren't copied into Git by these tools.
- Existing copy with different SHA is a **conflict**, not repaired automatically.

## Tests and native evidence

`python -m unittest discover -s tests -p "test_folder_audit.py" -v`; `python -m pytest tests/test_export_mirror.py` for the original mirror behavior; optional Windows smoke tests of existing export root, a partial legacy export and a source/copy hash conflict. Native ETABS/OpenSees engineering comparisons remain separate.

## Risks

A large source mirror incurs I/O cost; avoid running the `--mirror` step on an actively writing export directory. A source-mutating external process can change files between the inventory and copy; keep the input export frozen and review hashes. Result reports contain potentially sensitive absolute filenames, so **do not upload them automatically**. A physical model that passes gravity global equilibrium but differs at individual foundation reactions remains **NOT STRUCTURALLY VALIDATED**.
