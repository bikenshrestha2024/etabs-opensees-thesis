# audit_output_storage.py — Windows project evidence disk footprint audit

[Source](../../../tools/audit_output_storage.py) · Python 3.12 standard library only · Windows Spyder compatible

## Purpose

Report the real disk usage of the user's selected ETABS-to-OpenSees **project output root** without deleting, moving, renaming, hardlinking or overwriting any original file. This provides a defensible answer to the reported ~2 GiB output size and distinguishes repeat evidence packages from unique source results. The in-conversation uploaded ZIPs only establish the contents of those ZIPs, not the full Windows directory size.

## Usage

From a command prompt:

```bat
python tools\audit_output_storage.py --root "D:\Thesis Opensees\ETABS 11-12-2026\1"
```

From Spyder: run the source file without arguments; select the current output folder in the chooser. The tool writes a NEW sibling `Disk_Audit_YYYYMMDD_HHMMSS` folder by default and prints the exact path. Optional `--out "D:\...\Audit_01"` selects a NEW empty destination. Use `--no-hash` for a quicker size-only inventory.

## Inputs, outputs and safety

- Input: only local file paths under the selected output root. No internet, ETABS API or OpenSees invocation, and **no sensitive file upload**.
- `DISK_AUDIT.json`: total actual bytes and file counts, sorted top-level module directories, file extensions, top 50 largest files, exact same-size-and-SHA256 groups, errors, provenance and classification `DISK_FOOTPRINT_ONLY_NOT_ENGINEERING_EQUIVALENCE`.
- `LARGEST_FILES.csv`: original file sizes and relative paths.
- `EXACT_DUPLICATES.csv`: exact SHA-matching candidate groups, *not* a deletion instruction.
- `READ_FIRST.md`: folder-size summary and required engineering retention gates.

The scanner skips symlinks and does not traverse linked folders; it catches inaccessible individual files and records errors rather than inventing their sizes. A duplicate file is only identified when both bytes and SHA256 agree; same-named files from separate solves with different data are unique. Exact duplicates may still be required by provenance or package contracts, so **never delete automatically**.

Every write is isolated in the user-selected NEW report folder and is refused if that folder already contains any file. No source model, workbook, log, analysis result or prior ZIP is changed.

## Reason for addition and validation status

New analysis from 2026-11-12 found 32/76/97 individual result JSON and XLSX files, multiple per-case figures and overlapping organized ZIP bundles. The user's three uploaded review ZIPs total about 142.7 MiB compressed and 353.6 MiB expanded; the all-module ZIP already contains copies of the two subordinate categories. That observation cannot establish whether 2 GiB of **actual local disk use** is justified. This tool supplies the missing local measurement. Script output is a storage audit, not an engineering model acceptance or data-retention approval.

See [Gravity support/load-path review](../../../REVIEW_MAIN/01_GRAVITY/20261112_32_76_97_SUPPORT_AND_LOAD_PATH_REVIEW.md).


## Canonical diagnostics output V15

With `--root <case>` and no explicit `--out`, a new report now belongs to the selected export case under `09_SOFTWARE_DIAGNOSTICS/DISK_AUDITS/RUNS/<UTC>/`, with `JSON/DISK_AUDIT.json`, `CSV/LARGEST_FILES.csv`, `CSV/EXACT_DUPLICATES.csv`, and `REPORT/READ_FIRST.md`. The explicit `--out` option retains the user-selected report root. Legacy flat/sibling reports are preserved, not moved or overwritten. The disk scan precedes the new report output, so the report does not count its own bytes; previously saved audits are counted on future scans. This is a disk-footprint inventory, **not structural or numerical validation**.
