# ESM input import: "File is not a zip file" (2026-11-06)

## Reproduced software failure

The GUI message originates in the Excel reader, not in gravity, wall area, the EDB file, or the OpenSees solver. An XLSX is an OOXML ZIP archive. A file with .xlsx extension containing HTML, CSV, raw text, zero-length bytes or a damaged/incomplete ZIP causes Python openpyxl to raise zipfile.BadZipFile: File is not a zip file.

The 2026-11-06 failure occurred in three ESM paths:
- `source_workbooks` scans discovered and selected workbook candidates; its workbook_info caught OSError/ValueError/KeyError but NOT BadZipFile.
- `scaling_workbook_diagnostics` scanned all *.xlsx files and did not catch BadZipFile.
- `import_project_inputs` opened selected workbooks without isolating malformed files. One corrupt workbook blocked the ENTIRE OpenSees-first sync.

## Implemented correction

All three paths now skip malformed XLSX files while preserving other source inputs, and the diagnostic report states the **full file path**, `INVALID_XLSX_SKIPPED`, original exception and recovery instructions. Never delete, rename, repair or modify original workbooks automatically. Existing source EDB identity and Ultimate/ULS selection remain strict. The OpenSees geometry path runs when the Excel workbook is invalid.

The patch deliberately does not fill absent NBC Aw with zero or unrelated workbook values, and does not change the original ETABS/OpenSees physics.

## Windows remediation

1. Close ESM and other running converter windows, update repository with `git pull --ff-only origin main`, then relaunch the same current export.
2. Click `Why are Aw/period fields blank?` to identify each skipped candidate in `ESM_Source_Diagnostics.txt`.
3. From Windows Explorer, find the **specific path** marked `INVALID_XLSX_SKIPPED`. Verify it opens in Excel. If it is an HTML download, CSV, partial download, or a `~$` lock file, do NOT rely on it; select a valid original Excel workbook under `Excel sources…`. Use Excel File > Save As > Excel Workbook (.xlsx) for a genuine workbook.
4. Click `Sync from OpenSees model`. If geometric Aw is uniform, the program can populate geometry candidates; if first-storey openings exist, the continuous-pier option may provide a **provisional diagnostic** only. It cannot establish code acceptance.
5. If proper X/Y periods are still absent, run source-matched Rayleigh analysis separately. A successful gravity run proves gravity equilibrium, not verified Aw or Rayleigh.

**Test:** `tests/verify_esm_bad_zip_isolation_20261106.py` creates synthetic corrupt XLSX files in the discovered folder, explicitly selected files, with and without valid calculator/scaling workbooks, and asserts the importer continues and original bytes are unchanged. No private .EDB or workbook content was tested in CI.
