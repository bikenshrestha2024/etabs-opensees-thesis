# Excel workbooks

All 68 distributed Excel workbooks are organized here. [Browse every workbook](INDEX.md). No source workbook was
recalculated, redacted, recompressed or edited during publication.

| Folder | Contents |
|---|---|
| `source/` | Original NBC calculator, ULS/SLS scaling workbooks, supplied assignment/full ETABS tables and supplied slab load-path workbook |
| `verification/20261110_primary32/` | Newly generated gravity and ETABS reaction-comparison reports; numerical evidence, not structural acceptance |
| `historical/` | Existing example, calibration, saved-runtime and research workbooks, preserving their previous relative folder hierarchy |

`WORKBOOK_CATALOG.json` records every current path, former path, size and
SHA256. `SOURCE_REGISTRY.json` binds approved source roles to the exact source
EDB hash and workbook hash, without publishing machine-specific paths.
Machine-specific overrides remain in ignored `project_sources.private.json`.

The full ETABS export is 530,969,448 bytes and is stored byte-for-byte through
Git LFS. After cloning, run:

```text
git lfs install
git lfs pull
python 01.py
```

A GitHub ZIP download can contain an LFS pointer instead of the workbook.
The **main ETABS conversion GUI now checks the source workbook automatically**:
in a true Git checkout with Git LFS installed it runs a targeted `git lfs pull`
and independently verifies the workbook SHA256. In a GitHub ZIP without
Git metadata, or when Git LFS fails, it opens a file selector for the
**original unmodified Excel workbook**, validates its SHA256 against the
EDB-bound source registry, and saves the chosen path to the private
`<export>/project_sources.private.json` (never to tracked registry JSON).
A missing, changed, cancelled or mismatched source blocks conversion; the
GUI never treats a pointer as a legitimate XLSX. Manual Git commands are
optional, not prerequisites. The existing ordered `01_WORKFLOW_START.py`
and `01.py` launchers remain unchanged.
[GitHub's ordinary file limit](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)
requires LFS for a file this large.

Historical source snapshots retain their original path strings and frozen
review ledgers. New active code uses this folder. If an old snapshot needs
its previous workbook layout, first inspect the non-destructive plan:

```text
python tools/restore_legacy_excel_paths.py
python tools/restore_legacy_excel_paths.py --restore
```

Existing compatibility files are never overwritten. Original external files
on the user's drives remain unchanged. CSV recorder datasets stay with their
analysis data; this migration covers Excel workbook extensions.

See the [publication decision record](../docs/review/EXCEL_AND_LAUNCHER_PUBLICATION_DECISIONS.md)
and the [ordered launchers](../launchers/README.md).
