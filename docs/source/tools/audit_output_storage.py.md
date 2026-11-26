# audit_output_storage.py — Windows project evidence disk footprint audit

[Source](../../../tools/audit_output_storage.py) · Python 3.12 standard library only · Windows Spyder compatible

## Purpose

Report the real disk usage of the user's selected ETABS-to-OpenSees **project output root** without deleting, moving, renaming, hardlinking or overwriting any original file. This provides a defensible answer to the reported ~2 GiB output size and distinguishes repeat evidence packages from unique source results. The in-conversation uploaded ZIPs only establish the contents of those ZIPs, not the full Windows directory size.

## Usage

From a command prompt:

```bat
python tools\audit_output_storage.py --root "D:\Thesis Opensees\ETABS 11-12-2026\1"
```

Run the script directly by absolute path from any working directory, or run `python -m tools.audit_output_storage` from the repository. In Spyder, run the script without arguments and select the project output folder. The tool prints the new report path under the project's `09_SOFTWARE_DIAGNOSTICS/DISK_AUDITS/RUNS` folder. Use `--out` to name a different report destination or `--no-hash` to skip duplicate hashing.

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


## 2026-11-15 linked-path audit boundary

The static local disk audit refuses a symlinked selected root and any symlink in the report destination's existing ancestor chain **before** resolution, preventing its read-only scanning/writing from silently operating on an unrelated external project directory. Symlinked children are still skipped during the walk. Test fixtures under `tests/test_output_storage_audit.py` verify the source alias and linked report-parent cases leave the external folder untouched. This is a normal Python filesystem guard, not an OS-level race-proof sandbox; disk footprint duplication is not evidence of ETABS/OpenSees correctness.


2026-11-26: `scan_output(..., include_entries=True, validate_files=True)` optionally includes all relative file paths and lightweight format outcomes. The all-module migration audit uses complete enumeration by default and exposes explicit hash and format flags. Format failures and walk errors remain in `scan_errors`; no numerical validation or deletion is implied.


2026-11-26: `--validate-files` now inspects embedded supported members of evidence ZIPs (no extraction), streams worksheet XML in standalone and embedded XLSX/XLSM, counts formula cells without cached results and cached formula errors, and records explicit review-required cases for nested ZIPs and embedded workbooks above 512 MiB. A cached zero is distinct from no cache; no formulas are evaluated and no workbooks are rewritten. Counts include repeated workbook instances, not unique logical models. The all-module audit summarizes these findings and returns review-required exit status 2 when applicable. Tests use synthetic XML and preserve original bytes.

2026-11-26: the four existing mesh, evidence, MRSM review and ESM snapshot manifest formats are independently checked against stored ZIP member SHA256 and declared byte counts. Deduplicated aliases must point to registered members. Invalid/missing references remain review items; a manifest match is byte integrity only. Unknown manifest formats are not represented as verified.
